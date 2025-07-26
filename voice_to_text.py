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
import whisper
import pyautogui
from pynput import keyboard
from pynput.keyboard import Key


class VoiceToText:
    def __init__(self):
        self.recording = False
        self.audio_frames = []
        self.audio_stream = None
        self.p = None
        self.model = None
        
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
        print("✅ Ready! Press Control+Option 🎤 to start/stop recording")
    
    def setup_audio(self):
        """Initialize PyAudio"""
        self.p = pyaudio.PyAudio()
    
    def load_whisper_model(self):
        """Load Whisper model"""
        print("📥 Loading Whisper model (small for better performance)...")
        self.model = whisper.load_model("small")
        print("✅ Whisper model loaded")
    
    def start_recording(self):
        """Start audio recording"""
        if self.recording:
            return
            
        print("🔴 Recording started...")
        self.recording = True
        self.audio_frames = []
        
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
            
        except Exception as e:
            print(f"❌ Failed to start recording: {e}")
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
        """Convert audio to text using Whisper"""
        try:
            print("🤖 Converting speech to text...")
            result = self.model.transcribe(
                audio_file,
                language="en",
                fp16=False,
                verbose=False
            )
            text = result["text"].strip()
            
            if text:
                print(f"📝 Transcribed: {text}")
                self.type_text(text)
            else:
                print("❌ No speech detected")
                
        except Exception as e:
            print(f"Speech-to-text error: {e}")
    
    def type_text(self, text):
        """Type the text at current cursor position"""
        try:
            time.sleep(0.1)
            pyautogui.typewrite(text)
            print("✅ Text typed successfully")
        except Exception as e:
            print(f"Typing error: {e}")
    
    def on_key_press(self, key):
        """Handle key press events"""
        try:
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