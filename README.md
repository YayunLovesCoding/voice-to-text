# 🎤 Voice-to-Text System

A fast, local voice-to-text system for macOS that works globally across all applications. Similar to ChatGPT's voice feature, but runs entirely on your MacBook using OpenAI's Whisper model.

## ✨ Features

- **Global hotkey**: Works in any application (Notes, Slack, Terminal, etc.)
- **Instant text**: Transcribed text appears immediately via clipboard paste
- **Local processing**: Uses Whisper model locally - no internet required
- **High accuracy**: Uses Whisper "small" model for fast, accurate transcription
- **Native macOS app**: Runs as a menu bar app with a clean, native feel
- **Multilingual**: Supports English and Chinese (auto-detects, converts traditional to simplified)

## 🚀 Quick Start

There are **two ways** to use this tool:

### Method 1: Standalone App (⭐ Recommended)

Run as a native macOS app - no terminal needed, launches like any other app!

#### 1. Clone and Setup
```bash
cd ~/Documents/GitHub
git clone https://github.com/YayunLovesCoding/voice-to-text.git
cd voice-to-text

# Install PortAudio (required for microphone access)
brew install portaudio

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Build the App
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Build the app (takes 2-3 minutes)
python3 build_app.py
```

This creates `VoiceToText.app` in the `dist/` folder.

#### 3. Launch the App
```bash
# Open the app
open dist/VoiceToText.app
```

Or simply double-click `VoiceToText.app` in Finder!

**💡 Tip**: Drag `VoiceToText.app` to your Applications folder or Dock for easy access.

---

### Method 2: Run Python Script (For Developers)

Run directly from the terminal - useful for development, debugging, or customization.

#### Setup
```bash
cd ~/Documents/GitHub/voice-to-text
source venv/bin/activate  # Activate virtual environment
python3 voice_to_text.py
```

**Note**: You need to keep the terminal window open while using this method.

#### Enable Debug Logging
```bash
export VOICE_TO_TEXT_DEBUG=true
python3 voice_to_text.py
```

Log file will be created at `~/voicetotext_app.log` and accessible from the app menu.

---

## 🎯 How to Use

1. **Start the app** - You'll see a 🎙️ icon in your menu bar
2. **Position your cursor** anywhere you want text to appear
3. **Press and hold Control+Option** to start recording
   - Icon changes to 🔴
   - You'll hear a "ping" sound
4. **Speak clearly** - say whatever you want transcribed
5. **Release Control+Option** to stop recording
   - You'll hear a "pop" sound
   - Processing indicator ⏳ appears briefly
6. **Text appears instantly** at your cursor position!
   - You'll hear a "tink" sound when complete

## 🔐 Required Permissions

When you first run the app, macOS will request permissions:

### 1. Microphone Access
- macOS will show: **"VoiceToText would like to access the microphone"**
- **Click "OK"** to allow microphone access

### 2. Accessibility Access
- macOS will show: **"VoiceToText would like to control this computer using accessibility features"**
- **Click "OK"** and you'll be taken to System Settings
- **Enable the checkbox** next to VoiceToText

### Manual Permission Setup (if needed):
1. Go to **System Settings** → **Privacy & Security** → **Privacy**
2. Click **Microphone** → Enable VoiceToText
3. Click **Accessibility** → Enable VoiceToText

**Important**: If using the Python script method, you'll need to grant permissions to your Terminal app instead.

## 🔧 System Requirements

- **macOS** (tested on macOS Ventura and newer)
- **Python 3.8+**
- **Homebrew** (for installing PortAudio)
- **Microphone access** (built-in or external microphone)
- **~2GB disk space** (for model and dependencies)

## 🔧 Troubleshooting

### "Stream closed" or audio errors
- Check microphone permissions in System Settings
- Try unplugging/replugging external microphones
- Restart the application

### Text doesn't appear
- Ensure Accessibility permissions are enabled
- Try clicking into the target application first
- Check that the app is running (🎙️ icon in menu bar)

### Hotkey not working
- Ensure Accessibility permissions are enabled for VoiceToText (or Terminal if using script)
- Try quitting and restarting the app
- Check that no other app is using Control+Option

### App won't open or crashes immediately
- Make sure you've granted both Microphone and Accessibility permissions
- Check Console.app for crash logs
- Try rebuilding the app: `python3 build_app.py`

### Building the app fails
- Ensure you're in the virtual environment: `source venv/bin/activate`
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Try cleaning build artifacts: `rm -rf build dist *.spec` then rebuild

## 🛠️ Technical Details

- **Speech Recognition**: OpenAI Faster-Whisper (small model, optimized for speed)
- **Audio Processing**: PyAudio with 16kHz sampling
- **Global Hotkeys**: pynput library for keyboard monitoring
- **Text Insertion**: Clipboard paste via AppleScript (preserves cursor position)
- **Languages**: Supports English and Chinese (auto-detects, converts traditional to simplified)
- **UI**: rumps (macOS native menu bar app)
- **Packaging**: PyInstaller for standalone app bundling

## 📦 Building the App

The `build_app.py` script uses PyInstaller to create a standalone macOS application:

```bash
source venv/bin/activate
python3 build_app.py
```

This will:
1. Collect all dependencies (Whisper model, OpenCC, etc.)
2. Bundle everything into a single `.app` package
3. Create `VoiceToText.app` in the `dist/` folder

**Build time**: ~2-3 minutes on most machines

**App size**: ~500MB (includes the Whisper model and all dependencies)

## 🎛️ Customization

### Change the Hotkey
Edit `voice_to_text.py` line 57:
```python
# Current: Control+Option
self.hotkey = {Key.ctrl, Key.alt}

# Example alternatives:
# Control+Shift: self.hotkey = {Key.ctrl, Key.shift}
# Command+Option: self.hotkey = {Key.cmd, Key.alt}
```

After changing, rebuild the app: `python3 build_app.py`

### Use a Different Whisper Model
Edit `voice_to_text.py` line 134:
```python
# Current: "small" (fast, accurate)
self.model = faster_whisper.WhisperModel("small", device="cpu", compute_type="int8")

# Options: "tiny", "base", "small", "medium", "large"
# Larger models = more accurate but slower
```

## 🤝 Contributing

Feel free to submit issues and feature requests! This project is designed to be simple, fast, and user-friendly.

## 📄 License

MIT License - feel free to use and modify!