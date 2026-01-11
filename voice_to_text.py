#!/usr/bin/env python3
"""
Clean Voice-to-Text System
Simple, fast English voice-to-text with Control+Option hotkey.

Usage:
- Press Control+Option to start recording
- Press Control+Option again to stop and convert to text
- The text will be automatically typed at your cursor position
"""

import os
import time
import threading
import tempfile
import wave
import pyaudio
import faster_whisper
import opencc
import pyautogui
import pyperclip
import subprocess
from pynput import keyboard
from pynput.keyboard import Key


class VoiceToText:
    def __init__(self):
        self.recording = False
        self.audio_frames = []
        self.audio_stream = None
        self.p = None
        self.model = None
        self.pasting = False  # Flag to prevent hotkey conflicts during pasting
        self.audio_initialized = False
        
        # Audio settings
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        
        # Hotkey: Control+Option
        self.hotkey = {Key.ctrl, Key.alt}
        self.pressed_keys = set()
        
        print("🚀 Voice-to-Text starting up...")
        self.setup_audio()
        self.load_whisper_model()
        self.cc = opencc.OpenCC('t2s')  # Traditional to Simplified converter
        print("✅ Ready! Press Control+Option 🎤 to start/stop recording")
    
    def setup_audio(self):
        """Initialize PyAudio with error handling"""
        try:
            if self.p:
                self.p.terminate()
            self.p = pyaudio.PyAudio()
            self.audio_initialized = True
            print("🎵 Audio system initialized")
        except Exception as e:
            print(f"❌ Failed to initialize audio: {e}")
            print("💡 Try restarting the application or checking audio permissions")
            self.audio_initialized = False
    
    def load_whisper_model(self):
        """Load Faster-Whisper model"""
        print("📥 Loading Faster-Whisper model (small for speed/accuracy balance)...")
        # 'small' is accurate and fast with faster-whisper implementation
        # cpu_threads=4 usually good for M1/M2/M3
        self.model = faster_whisper.WhisperModel("small", device="cpu", compute_type="int8")
        print("✅ Faster-Whisper model loaded")
    
    
    
    def start_recording(self):
        """Start audio recording with auto-recovery"""
        if self.recording:
            return
        
        # Check if audio system is initialized
        if not self.audio_initialized:
            print("🔄 Audio not initialized, attempting to reinitialize...")
            self.setup_audio()
            if not self.audio_initialized:
                print("❌ Cannot start recording - audio system unavailable")
                return
            
        print("🔴 Recording started...")
        # Play start sound
        subprocess.Popen(["afplay", "/System/Library/Sounds/Ping.aiff"])
        self.recording = True
        self.audio_frames = []
        
        # Try to start recording with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.audio_stream = self.p.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    frames_per_buffer=self.chunk,
                    input_device_index=None  # Use default microphone
                )
                
                threading.Thread(target=self._record_audio, daemon=True).start()
                return  # Success!
                
            except Exception as e:
                print(f"❌ Recording attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    print("🔄 Reinitializing audio and retrying...")
                    time.sleep(1)
                    self.setup_audio()
                else:
                    print("💡 Check microphone permissions and try again")
                    self.recording = False
    
    def _record_audio(self):
        """Record audio in background thread"""
        while self.recording and self.audio_stream:
            try:
                if self.audio_stream.is_active():
                    data = self.audio_stream.read(self.chunk, exception_on_overflow=False)
                    self.audio_frames.append(data)
                else:
                    break
            except Exception as e:
                if self.recording:  # Only print error if we're still supposed to be recording
                    print(f"Recording error: {e}")
                break
    
    def stop_recording(self):
        """Stop recording and process speech-to-text"""
        if not self.recording:
            return
            
        print("⏹️  Recording stopped, processing...")
        # Play stop sound
        subprocess.Popen(["afplay", "/System/Library/Sounds/Pop.aiff"])
        self.recording = False
        
        # Give a moment for the recording thread to finish
        time.sleep(0.1)
        
        if self.audio_stream:
            try:
                if self.audio_stream.is_active():
                    self.audio_stream.stop_stream()
                self.audio_stream.close()
            except Exception as e:
                print(f"Stream cleanup error: {e}")
            finally:
                self.audio_stream = None
        
        # Check if we have any audio data
        if not self.audio_frames:
            print("❌ No audio data recorded")
            return
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            try:
                with wave.open(temp_file.name, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(self.p.get_sample_size(self.format))
                    wf.setframerate(self.rate)
                    wf.writeframes(b''.join(self.audio_frames))
                
                self.process_speech_to_text(temp_file.name)
                
            except Exception as e:
                print(f"Error processing audio: {e}")
            finally:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
    
    def process_speech_to_text(self, audio_file):
        """Convert audio to text using Faster-Whisper"""
        try:
            print("🤖 Converting speech to text...")
            segments, info = self.model.transcribe(
                audio_file,
                beam_size=5,
                vad_filter=True  # Built-in VAD to ignore silence
            )
            
            # Combine all segments
            text = " ".join([segment.text for segment in segments]).strip()
            
            if text:
                # Check for Chinese and convert to Simplified if needed
                if info.language == "zh":
                    print("🇨🇳 Detected Chinese, converting to Simplified...")
                    text = self.cc.convert(text)
                
                print(f"📝 Transcribed ({info.language}): {text}")
                self.type_text(text)
            else:
                print("❌ No speech detected")
                
        except Exception as e:
            print(f"Speech-to-text error: {e}")
    
    def type_text(self, text):
        """Insert text at current cursor position using fastest method"""
        # Set pasting flag to prevent hotkey conflicts
        self.pasting = True
        
        try:
            # Method 1: AppleScript paste (most reliable)
            # Save current clipboard
            original_clipboard = pyperclip.paste()
            
            # Copy our text to clipboard
            pyperclip.copy(text)
            time.sleep(0.1)  # Give clipboard time to update
            
            # Use AppleScript for reliable paste
            result = subprocess.run([
                'osascript', '-e', 
                'tell application "System Events" to keystroke "v" using command down'
            ], capture_output=True, timeout=3)
            
            if result.returncode == 0:
                print("✅ Text pasted instantly")
                # Play success sound
                subprocess.Popen(["afplay", "/System/Library/Sounds/Tink.aiff"])
            else:
                if "osascript is not allowed to send keystrokes" in str(result.stderr):
                    print("\n⚠️  PERMISSION ERROR: The application needs Accessibility permissions to paste text.")
                    print("👉 Go to System Settings > Privacy & Security > Accessibility")
                    print("👉 Add and enable your Terminal / Editor application")
                raise Exception(f"AppleScript failed: {result.stderr}")
            
            # Restore original clipboard
            time.sleep(0.1)
            pyperclip.copy(original_clipboard)
            
        except Exception as e:
            print(f"Paste failed: {e}")
            
            # Method 2: Direct typing with very small interval
            try:
                pyautogui.typewrite(text, interval=0.001)  # Faster typing
                print("✅ Text typed quickly")
                
            except Exception as e2:
                print(f"Quick typing failed: {e2}")
                
                # Method 3: Last resort - reliable slow typing
                pyautogui.typewrite(text, interval=0.01)
                print("✅ Text typed (reliable method)")
        
        finally:
            # Always reset pasting flag
            self.pasting = False
    
    def on_key_press(self, key):
        """Handle key press events"""
        try:
            # Skip hotkey detection when we're pasting to avoid conflicts
            if self.pasting:
                return
                
            self.pressed_keys.add(key)
            if self.hotkey.issubset(self.pressed_keys):
                if not self.recording:
                    self.start_recording()
                else:
                    self.stop_recording()
        except Exception as e:
            print(f"Key press error: {e}")
    
    def on_key_release(self, key):
        """Handle key release events"""
        try:
            self.pressed_keys.discard(key)
        except Exception:
            pass
    
    def run(self):
        """Start the global hotkey listener"""
        try:
            listener = keyboard.Listener(
                on_press=self.on_key_press, 
                on_release=self.on_key_release
            )
            listener.start()
            print("🎯 Listening for Control+Option 🎤 ... (Ctrl+C to quit)")
            
            while True:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up resources...")
        
        # Stop any active recording
        if self.recording:
            self.recording = False
            
        # Clean up audio stream
        if self.audio_stream:
            try:
                if self.audio_stream.is_active():
                    self.audio_stream.stop_stream()
                self.audio_stream.close()
            except:
                pass
            finally:
                self.audio_stream = None
        
        # Terminate PyAudio
        if hasattr(self, 'p') and self.p:
            self.p.terminate()
            
        print("🧹 Cleanup complete")


if __name__ == "__main__":
    try:
        app = VoiceToText()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        exit(1)