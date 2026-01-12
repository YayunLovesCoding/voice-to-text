#!/bin/bash
# Watch the VoiceToText log file in real-time
echo "📝 Watching VoiceToText log file..."
echo "Press Control+Option in the app to test the hotkey"
echo "----------------------------------------"
tail -f ~/voicetotext_app.log
