#!/bin/bash
# Audio diagnostics for Raspberry Pi

echo "🔍 AUDIO DIAGNOSTICS"
echo "===================="
echo ""

# Check microphone
echo "🎤 MICROPHONE DEVICES:"
arecord -l
echo ""

# Check speakers
echo "🔊 SPEAKER DEVICES:"
aplay -l
echo ""

# Check ALSA
echo "📊 ALSA MIXER:"
amixer
echo ""

# Test microphone recording
echo "🎙️ TESTING MICROPHONE (5 seconds)..."
echo "   Say something..."
arecord -d 5 -f cd /tmp/test_mic.wav 2>/dev/null
if [ -f /tmp/test_mic.wav ]; then
    echo "✅ Microphone recording successful!"
    
    # Test playback
    echo ""
    echo "🔊 TESTING SPEAKER PLAYBACK..."
    echo "   You should hear your recording..."
    aplay /tmp/test_mic.wav
    echo "✅ Speaker playback complete!"
    
    rm /tmp/test_mic.wav
else
    echo "❌ Microphone test failed!"
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
