#!/bin/bash
# Audio diagnostics for Raspberry Pi - USB Card 3

echo "🔍 AUDIO DIAGNOSTICS - USB CARD 3"
echo "===================================="
echo ""

# Check microphone
echo "🎤 MICROPHONE DEVICES:"
arecord -l
echo ""

# Check speakers
echo "🔊 SPEAKER DEVICES:"
aplay -l
echo ""

# Test microphone recording on card 3
echo "🎙️ TESTING MICROPHONE on USB CARD 3 (5 seconds)..."
echo "   Say something..."
arecord -D plughw:3,0 -d 5 -f cd /tmp/test_mic.wav 2>/dev/null
if [ -f /tmp/test_mic.wav ]; then
    echo "✅ Microphone recording successful on card 3!"
    
    # Test playback on card 3
    echo ""
    echo "🔊 TESTING SPEAKER PLAYBACK on USB CARD 3..."
    echo "   You should hear your recording..."
    aplay -D plughw:3,0 /tmp/test_mic.wav
    echo "✅ Speaker playback complete on card 3!"
    
    rm /tmp/test_mic.wav
else
    echo "❌ Microphone test failed on card 3!"
fi

echo ""
echo "📋 TROUBLESHOOTING TIPS:"
echo ""
echo "If microphone not detected:"
echo "  1. Check USB connection"
echo "  2. Run: sudo usermod -a -G audio \$USER"
echo "  3. Reboot: sudo reboot"
echo ""
echo "If speakers not working:"
echo "  1. Check volume: alsamixer (press F6 to select card)"
echo "  2. Test with: speaker-test -t wav -c 2"
echo "  3. Check connections (3.5mm jack or HDMI)"
echo ""
echo "Set default audio device:"
echo "  sudo raspi-config"
echo "  > System Options > Audio"
echo ""
