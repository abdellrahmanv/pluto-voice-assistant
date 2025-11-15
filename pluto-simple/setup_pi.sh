#!/bin/bash
# 🪐 Pluto Simple - Raspberry Pi Setup Script
# Automatic installation and configuration

echo "╔═══════════════════════════════════════════════════════╗"
echo "║   🪐 PLUTO SIMPLE - Raspberry Pi Setup              ║"
echo "║   Scenario-Based Voice Agent Installation            ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        exit 1
    fi
fi

echo "📦 Step 1/6: Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo "📦 Step 2/6: Installing Python dependencies..."
sudo apt-get install -y python3 python3-pip python3-dev

echo ""
echo "📦 Step 3/6: Installing audio libraries..."
sudo apt-get install -y portaudio19-dev espeak flac

echo ""
echo "📦 Step 4/6: Installing Python packages..."
pip3 install --upgrade pip
pip3 install SpeechRecognition pyttsx3 pyaudio

echo ""
echo "📦 Step 5/6: Configuring audio devices..."
# Test audio output
echo "Testing audio output..."
espeak "Audio test successful" 2>/dev/null || echo "⚠️  espeak not working, but continuing..."

# Check microphone
if arecord -l | grep -q "card"; then
    echo "✅ Microphone detected"
else
    echo "⚠️  No microphone detected - please connect one"
fi

echo ""
echo "📦 Step 6/6: Setting up Pluto Simple..."
chmod +x simple_agent.py

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║   ✅ INSTALLATION COMPLETE!                          ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "🎤 To test audio:"
echo "   espeak 'Hello from Pluto'"
echo ""
echo "🚀 To run Pluto Simple:"
echo "   python3 simple_agent.py"
echo ""
echo "📝 Configuration tips:"
echo "   - Make sure your microphone is connected"
echo "   - Make sure speakers/headphones are connected"
echo "   - Test with: arecord -l (list microphones)"
echo "   - Test with: aplay -l (list speakers)"
echo ""
echo "💡 First time setup:"
echo "   1. Connect USB microphone (or use built-in)"
echo "   2. Connect speakers or 3.5mm audio jack"
echo "   3. Run: python3 simple_agent.py"
echo "   4. Say 'Hey Pluto' to start!"
echo ""
