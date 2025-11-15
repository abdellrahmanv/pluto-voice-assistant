#!/bin/bash
# Install Google TTS for MUCH better, natural voice

echo "🎙️ Installing Google TTS for better voice quality..."

# Install gTTS (Google Text-to-Speech)
pip3 install --break-system-packages gTTS pygame 2>/dev/null || pip3 install gTTS pygame

# Install mpg123 for audio playback
sudo apt-get install -y mpg123

echo "✅ Google TTS installed!"
echo ""
echo "Now use: python3 simple_agent_gtts.py"
echo "This version has MUCH better, natural human voice!"
