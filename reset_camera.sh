#!/bin/bash
#
# Emergency Camera Reset Script
# Run this if camera gets stuck and won't start
#

echo "========================================="
echo "🔧 EMERGENCY CAMERA RESET"
echo "========================================="

echo ""
echo "1️⃣ Killing all rpicam processes..."
pkill -9 rpicam-vid 2>/dev/null
pkill -9 rpicam-hello 2>/dev/null  
pkill -9 rpicam 2>/dev/null
sleep 1

echo ""
echo "2️⃣ Checking for remaining processes..."
if pgrep rpicam > /dev/null; then
    echo "   ⚠️  Some processes still running:"
    ps aux | grep rpicam | grep -v grep
else
    echo "   ✅ No rpicam processes found"
fi

echo ""
echo "3️⃣ Testing camera..."
timeout 3 rpicam-hello -t 1000 --nopreview 2>&1 | head -5

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✅ CAMERA RESET SUCCESSFUL"
    echo "========================================="
    echo ""
    echo "You can now run: python run.py"
else
    echo ""
    echo "========================================="
    echo "❌ CAMERA STILL STUCK"
    echo "========================================="
    echo ""
    echo "Try:"
    echo "  1. Reboot: sudo reboot"
    echo "  2. Check camera cable connection"
    echo "  3. Run: vcgencmd get_camera"
fi
