import multiprocessing
import socket
import sys
import os
import time
import threading
import tempfile
import wave
import pyaudio
import faster_whisper
import opencc
import pyperclip
import subprocess
import rumps
from pynput import keyboard
from pynput.keyboard import Key

# Icons
ICON_IDLE = "🎙️"
ICON_RECORDING = "🔴"

# Enable debug logging (set to False to disable)
DEBUG = os.environ.get('VOICE_TO_TEXT_DEBUG', 'False').lower() in ('true', '1', 'yes')
LOG_FILE = os.path.expanduser("~/voicetotext_app.log") if DEBUG else None

def log(message):
    """Write log messages to a file and console (if DEBUG is enabled)"""
    if DEBUG and LOG_FILE:
        with open(LOG_FILE, 'a') as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
    if DEBUG:
        print(message)

class VoiceToTextApp(rumps.App):
    def __init__(self):
        log("VoiceToText App Starting...")
        
        super(VoiceToTextApp, self).__init__("Voice2Text", icon=None, title=ICON_IDLE)
        
        self.recording = False
        self.audio_frames = []
        self.audio_stream = None
        self.p = None
        self.model = None
        self.pasting = False
        self.audio_initialized = False
        
        # Audio settings
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        
        # Hotkey: Control+Option
        self.hotkey = {Key.ctrl, Key.alt}
        self.pressed_keys = set()
        self.hotkey_active = False  # Debounce flag
        
        log(f"Hotkey configured: Control+Option")
        
        self.setup_audio()
        self.check_accessibility_permissions()
        
        # Load model in a separate thread to not block UI startup
        threading.Thread(target=self.load_whisper_model, daemon=True).start()
        
        self.cc = opencc.OpenCC('t2s')
        
        # Start Hotkey Listener
        log("Starting keyboard listener...")
        self.listener_thread = threading.Thread(target=self.start_listener, daemon=True)
        self.listener_thread.start()

        # Menu Items
        menu_items = [
            rumps.MenuItem("Status: Ready", callback=None),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]
        
        if DEBUG and LOG_FILE:
            menu_items.insert(2, rumps.MenuItem(f"Open Log File", callback=self.open_log))
            menu_items.insert(3, rumps.separator)
        
        self.menu = menu_items
        
        log("App initialization complete!")

    def open_log(self, _):
        """Open the log file in default text editor"""
        if LOG_FILE and os.path.exists(LOG_FILE):
            subprocess.run(['open', '-a', 'TextEdit', LOG_FILE])

    def check_accessibility_permissions(self):
        """Check if app has accessibility permissions (required for keyboard monitoring)"""
        log("Checking accessibility permissions...")
        try:
            result = subprocess.run(
                ['osascript', '-e', 
                 'tell application "System Events" to get name of every window of process "Finder"'],
                capture_output=True,
                timeout=2
            )
            
            if result.returncode != 0:
                log("WARNING: Accessibility permissions may not be granted!")
                rumps.notification(
                    "Permissions Required",
                    "Voice2Text needs Accessibility access",
                    "Go to System Settings → Privacy & Security → Accessibility"
                )
            else:
                log("Accessibility permissions granted")
        except Exception as e:
            log(f"Could not verify accessibility permissions: {e}")

    def setup_audio(self):
        try:
            if self.p:
                self.p.terminate()
            self.p = pyaudio.PyAudio()
            self.audio_initialized = True
            log("Audio system initialized")
        except Exception as e:
            log(f"Failed to initialize audio: {e}")
            self.audio_initialized = False

    def load_whisper_model(self):
        self.title = "⏳" # Loading state
        log("Loading Whisper model...")
        try:
            self.model = faster_whisper.WhisperModel("small", device="cpu", compute_type="int8")
            log("Whisper model loaded")
            self.title = ICON_IDLE
            self.menu["Status: Ready"].title = "Status: Ready"
        except Exception as e:
            log(f"Failed to load model: {e}")
            self.title = "⚠️" 

    def start_recording(self):
        if self.recording:
            return
        
        if not self.audio_initialized:
            self.setup_audio()
            if not self.audio_initialized:
                rumps.notification("Error", "Audio Error", "Could not initialize microphone.")
                return
            
        log("Recording started")
        subprocess.Popen(["afplay", "/System/Library/Sounds/Ping.aiff"])
        self.recording = True
        self.title = ICON_RECORDING
        self.menu["Status: Ready"].title = "Status: Recording..."
        self.audio_frames = []
        
        try:
            self.audio_stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            threading.Thread(target=self._record_audio, daemon=True).start()
        except Exception as e:
            log(f"Recording failed: {e}")
            self.recording = False
            self.title = ICON_IDLE

    def _record_audio(self):
        while self.recording and self.audio_stream:
            try:
                if self.audio_stream.is_active():
                    data = self.audio_stream.read(self.chunk, exception_on_overflow=False)
                    self.audio_frames.append(data)
                else:
                    break
            except:
                break

    def stop_recording(self):
        if not self.recording:
            return
            
        log("Recording stopped")
        subprocess.Popen(["afplay", "/System/Library/Sounds/Pop.aiff"])
        self.recording = False
        self.title = "⏳" # Processing state
        self.menu["Status: Ready"].title = "Status: Processing..."
        
        time.sleep(0.1)
        if self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            except:
                pass
            self.audio_stream = None
        
        if not self.audio_frames:
            self.title = ICON_IDLE
            return
        
        # Save and process in separate thread
        threading.Thread(target=self.process_audio, args=(self.audio_frames,), daemon=True).start()

    def process_audio(self, frames):
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                with wave.open(temp_file.name, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(self.p.get_sample_size(self.format))
                    wf.setframerate(self.rate)
                    wf.writeframes(b''.join(frames))
                
                # Transcribe
                log("Transcribing audio...")
                if self.model:
                    segments, info = self.model.transcribe(temp_file.name, beam_size=5, vad_filter=True)
                    text = " ".join([segment.text for segment in segments]).strip()
                    
                    if text:
                        # Convert traditional Chinese to simplified if detected
                        if info.language == "zh":
                            text = self.cc.convert(text)
                        
                        log(f"Transcribed: {text}")
                        self.type_text(text)
                    else:
                        log("No speech detected")
                
                os.unlink(temp_file.name)
        except Exception as e:
            log(f"Processing error: {e}")
        finally:
            self.title = ICON_IDLE
            self.menu["Status: Ready"].title = "Status: Ready"

    def type_text(self, text):
        """Type the transcribed text using clipboard paste"""
        self.pasting = True
        try:
            original_clipboard = pyperclip.paste()
            pyperclip.copy(text)
            time.sleep(0.1)
            subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "v" using command down'], capture_output=True)
            subprocess.Popen(["afplay", "/System/Library/Sounds/Tink.aiff"])
            time.sleep(0.1)
            pyperclip.copy(original_clipboard)
        except Exception as e:
            log(f"Paste failed: {e}")
        finally:
            self.pasting = False

    def start_listener(self):
        """Start the keyboard listener"""
        log("Keyboard listener starting...")
        try:
            listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            listener.start()
            log("Keyboard listener started successfully")
            listener.join()
        except Exception as e:
            log(f"Keyboard listener failed: {e}")
            rumps.notification("Error", "Keyboard Listener Error", f"Failed to start: {e}")

    def on_key_press(self, key):
        """Handle key press events"""
        if self.pasting:
            return
        try:
            self.pressed_keys.add(key)
            log(f"Key pressed: {key}, Current keys: {self.pressed_keys}")
            
            if self.hotkey.issubset(self.pressed_keys):
                # Debounce: Only trigger if not already active
                if not self.hotkey_active:
                    log("Hotkey detected - toggling recording")
                    self.hotkey_active = True
                    if not self.recording:
                        self.start_recording()
                    else:
                        self.stop_recording()
        except Exception as e:
            log(f"Key press error: {e}")

    def on_key_release(self, key):
        """Handle key release events"""
        try:
            self.pressed_keys.discard(key)
            log(f"Key released: {key}")
            # Reset debounce flag if hotkey combo is broken
            if not self.hotkey.issubset(self.pressed_keys):
                self.hotkey_active = False
        except Exception as e:
            log(f"Key release error: {e}")


if __name__ == "__main__":
    # CRITICAL: Must be first line in main block for PyInstaller
    multiprocessing.freeze_support()
    
    # Initialize log file if DEBUG is enabled
    if DEBUG and LOG_FILE:
        with open(LOG_FILE, 'w') as f:
            f.write(f"VoiceToText App Log - Started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n")
        log(f"Debug mode enabled. Log file: {LOG_FILE}")
    
    # Enforce Singleton (Prevent duplicate instances)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 56789))
        log("No other instance running")
    except socket.error:
        print("⚠️ App is already running. Exiting.")
        sys.exit(0)

    # Run the App
    log("Starting app...")
    app = VoiceToTextApp()
    app.run()