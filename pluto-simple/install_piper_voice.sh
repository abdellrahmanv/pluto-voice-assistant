#!/bin/bash
# Install Piper TTS - Natural offline voice (same as full Pluto!)

echo "🎙️ Installing Piper TTS - Natural Human Voice (Offline)"
echo ""

# Install Piper TTS
echo "📦 Step 1/3: Installing Piper TTS..."
pip3 install --break-system-packages piper-tts 2>/dev/null || pip3 install piper-tts

# Download voice model
echo ""
echo "📦 Step 2/3: Downloading natural voice model..."
mkdir -p ~/.local/share/piper/voices
cd ~/.local/share/piper/voices

# Download en_US-lessac-medium (high quality natural voice)
wget -q --show-progress https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

echo ""
echo "📦 Step 3/3: Testing voice..."
echo "Hello from Piper" | piper --model en_US-lessac-medium.onnx --output-raw | aplay -r 22050 -f S16_LE -t raw -

echo ""
echo "✅ Piper TTS installed successfully!"
echo ""
echo "🚀 Now run: python3 simple_agent_piper.py"
echo "   This has natural human voice AND works offline!"
