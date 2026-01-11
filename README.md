# 🎤 Voice-to-Text System

A fast, local voice-to-text system for macOS that works globally across all applications. Similar to ChatGPT's voice feature, but runs entirely on your MacBook using OpenAI's Whisper model.

## ✨ Features

- **Global hotkey**: Works in any application (Notes, Slack, Terminal, etc.)
- **Instant text**: Transcribed text appears immediately via clipboard paste
- **Local processing**: Uses Whisper model locally - no internet required
- **High accuracy**: Uses Whisper "small" model for fast, accurate transcription
- **Simple setup**: Just clone and run!

## 🚀 Quick Setup

### 1. Clone the Repository
```bash
cd ~/Documents/GitHub
git clone https://github.com/YayunLovesCoding/voice-to-text.git
cd voice-to-text
```

### 2. Install Dependencies
```bash
# Install PortAudio (required for microphone access)
brew install portaudio

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 3. Run the Application
```bash
cd ~/Documents/GitHub/voice-to-text
source venv/bin/activate  # ← Don't forget this step!
python3 voice_to_text.py
```

## 🎯 How to Use

1. **Start the app** - You'll see a 🎙️ icon in your menu bar
2. **Position your cursor** anywhere you want text to appear
3. **Press and hold Control+Option** to start recording (icon changes to 🔴, you'll hear a "ping" sound)
4. **Speak clearly** - say whatever you want transcribed
5. **Release Control+Option** to stop recording (you'll hear a "pop" sound)
6. **Text appears instantly** at your cursor position!

### Debug Mode (Optional)
To enable detailed logging for troubleshooting:
```bash
export VOICE_TO_TEXT_DEBUG=true
python3 voice_to_text.py
```
Log file will be created at `~/voicetotext_app.log` and accessible from the app menu.

## 🔧 System Requirements

- **macOS** (tested on macOS Ventura and newer)
- **Python 3.8+**
- **Homebrew** (for installing PortAudio)
- **Microphone access** (built-in or external microphone)

## 🔐 Required Permissions

When you first run the app, macOS will request permissions:

### 1. Microphone Access
- macOS will show: "Terminal would like to access the microphone"
- **Click "OK"** to allow microphone access

### 2. Accessibility Access
- macOS will show: "Terminal would like to control this computer using accessibility features"
- **Click "OK"** and you'll be taken to System Preferences
- **Enable the checkbox** next to Terminal (or your terminal app)

### Manual Permission Setup (if needed):
1. Go to **System Preferences** → **Security & Privacy** → **Privacy**
2. Click **Microphone** → Enable your terminal app
3. Click **Accessibility** → Enable your terminal app

## 🎛️ Hotkey

- **Control+Option**: Start/stop recording
- Works globally in any application
- No conflicts with system shortcuts

## 📝 Example Usage

```bash
# Start the app
cd ~/Documents/GitHub/voice-to-text
source venv/bin/activate
python3 voice_to_text.py

# You'll see:
# 🚀 Voice-to-Text starting up...
# 📥 Loading Whisper model (small for better performance)...
# ✅ Whisper model loaded
# ✅ Ready! Press Control+Option 🎤 to start/stop recording
# 🎯 Listening for Control+Option 🎤 ... (Ctrl+C to quit)

# Now use Control+Option to record in any app!
```

## 🔧 Troubleshooting

### "Stream closed" or audio errors
- Check microphone permissions in System Preferences
- Try unplugging/replugging external microphones
- Restart the application

### Text appears slowly or character-by-character
- This should not happen with the latest version
- The app now uses instant clipboard paste

### "Command not found: python"
- Use `python3` instead of `python`
- Make sure you've activated the virtual environment: `source venv/bin/activate`

### Hotkey not working
- Ensure Accessibility permissions are enabled
- Try quitting and restarting the app
- Check that no other app is using Control+Option

## 🛠️ Technical Details

- **Speech Recognition**: OpenAI Faster-Whisper (small model, optimized for speed)
- **Audio Processing**: PyAudio with 16kHz sampling
- **Global Hotkeys**: pynput library for keyboard monitoring
- **Text Insertion**: Clipboard paste via AppleScript (preserves cursor position)
- **Languages**: Supports English and Chinese (auto-detects, converts traditional to simplified)
- **UI**: Menu bar app using rumps (macOS native feel)

## 🤝 Contributing

Feel free to submit issues and feature requests! This project is designed to be simple and fast.

## 📄 License

MIT License - feel free to use and modify!