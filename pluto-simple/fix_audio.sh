#!/bin/bash
# Fix ALSA audio configuration for USB card 3

echo "🔧 Fixing ALSA audio configuration..."

# Create ALSA config file
sudo tee /etc/asound.conf > /dev/null << 'EOF'
# Use USB card 3 as default
pcm.!default {
    type hw
    card 3
}

ctl.!default {
    type hw
    card 3
}

# USB card 3 specific config
pcm.usb3 {
    type hw
    card 3
    device 0
}
EOF

echo "✅ ALSA config created: /etc/asound.conf"

# Reload ALSA
sudo alsa force-reload 2>/dev/null || echo "   (alsa reload skipped)"

# List audio devices
echo ""
echo "📋 Available audio devices:"
aplay -l

echo ""
echo "✅ Audio fix complete!"
echo ""
echo "Now test:"
echo "  speaker-test -D plughw:3,0 -c 2 -t wav"
