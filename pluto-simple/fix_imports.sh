#!/bin/bash
# Quick fix for "module not found" errors on Raspberry Pi

echo "🔧 Installing missing Python packages..."

# Try with --break-system-packages flag (for newer Raspberry Pi OS)
pip3 install --break-system-packages SpeechRecognition pyttsx3 pyaudio

# If that fails, try without the flag
if [ $? -ne 0 ]; then
    echo "Trying alternative installation method..."
    pip3 install SpeechRecognition pyttsx3 pyaudio
fi

# Verify
echo ""
echo "🔍 Checking installations..."
python3 -c "import speech_recognition; print('✅ SpeechRecognition OK')" 2>/dev/null || echo "❌ SpeechRecognition FAILED"
python3 -c "import pyttsx3; print('✅ pyttsx3 OK')" 2>/dev/null || echo "❌ pyttsx3 FAILED"
python3 -c "import pyaudio; print('✅ pyaudio OK')" 2>/dev/null || echo "❌ pyaudio FAILED"

echo ""
echo "If any package failed, try manually:"
echo "  sudo apt-get install python3-pip portaudio19-dev"
echo "  pip3 install --user SpeechRecognition pyttsx3 pyaudio"
