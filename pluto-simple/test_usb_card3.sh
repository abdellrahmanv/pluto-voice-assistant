#!/bin/bash
# Quick test if USB card 3 works

echo "🔍 Testing USB card 3..."
echo ""

# Check if card 3 exists
if aplay -l | grep -q "card 3"; then
    echo "✅ USB card 3 detected!"
    aplay -l | grep "card 3"
    echo ""
    
    # Test speaker output
    echo "🔊 Testing speakers (you should hear noise)..."
    speaker-test -D plughw:3,0 -c 2 -t wav -l 1
    
    echo ""
    echo "🎤 Testing microphone..."
    arecord -D plughw:3,0 -d 3 -f cd /tmp/test.wav 2>&1
    
    if [ -f /tmp/test.wav ]; then
        echo "✅ Recording successful!"
        echo "🔊 Playing back recording..."
        aplay -D plughw:3,0 /tmp/test.wav
        rm /tmp/test.wav
    else
        echo "❌ Recording failed"
    fi
else
    echo "❌ USB card 3 NOT found!"
    echo ""
    echo "Available cards:"
    aplay -l
    echo ""
    echo "💡 Try:"
    echo "   - Check USB connection"
    echo "   - Run: lsusb"
    echo "   - Replug the USB device"
fi
