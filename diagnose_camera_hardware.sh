#!/bin/bash
#
# Camera Hardware Diagnostic Script
# Diagnoses "pipeline camera frontend timeout" errors
#

echo "========================================"
echo "🔍 CAMERA HARDWARE DIAGNOSTIC"
echo "========================================"

echo ""
echo "1️⃣ Checking if camera is detected..."
vcgencmd get_camera

echo ""
echo "2️⃣ Camera status from system:"
libcamera-hello --list-cameras 2>&1 | head -20

echo ""
echo "3️⃣ Checking for camera processes..."
if pgrep -f "rpicam|libcamera" > /dev/null; then
    echo "   ⚠️  Camera processes running:"
    ps aux | grep -E "rpicam|libcamera" | grep -v grep
    echo ""
    echo "   Killing them..."
    pkill -9 rpicam
    pkill -9 libcamera
    sleep 2
else
    echo "   ✅ No camera processes running"
fi

echo ""
echo "4️⃣ Testing camera with minimal command..."
echo "   Running: rpicam-hello -t 2000 --nopreview"
echo "   (This will take 2 seconds)"
echo ""

timeout 5 rpicam-hello -t 2000 --nopreview 2>&1

RESULT=$?

echo ""
echo ""
echo "========================================"
echo "📊 DIAGNOSTIC RESULTS"
echo "========================================"

if [ $RESULT -eq 0 ]; then
    echo ""
    echo "✅ CAMERA WORKING!"
    echo ""
    echo "The camera hardware is fine."
    echo "The timeout was likely caused by:"
    echo "  - Another process using the camera"
    echo "  - Temporary glitch"
    echo ""
    echo "You can now run: python run.py"
    echo ""
else
    echo ""
    echo "❌ CAMERA TIMEOUT/ERROR DETECTED"
    echo ""
    echo "Possible causes:"
    echo ""
    echo "1. 🔌 CABLE CONNECTION (Most Common)"
    echo "   - Power off Raspberry Pi"
    echo "   - Disconnect camera cable"
    echo "   - Check for damage/bent pins"
    echo "   - Reconnect cable firmly (blue side up)"
    echo "   - Power back on"
    echo ""
    echo "2. ⚙️  CAMERA NOT ENABLED"
    echo "   Run: sudo raspi-config"
    echo "   → Interface Options → Camera → Enable"
    echo "   → Reboot"
    echo ""
    echo "3. 🔄 DRIVER ISSUE"
    echo "   Run: sudo reboot"
    echo "   (Simple reboot often fixes driver timeouts)"
    echo ""
    echo "4. 🛠️  FIRMWARE UPDATE NEEDED"
    echo "   Run: sudo apt update && sudo apt full-upgrade"
    echo "   Run: sudo rpi-update"
    echo "   Reboot"
    echo ""
    echo "5. 🔧 HARDWARE FAILURE"
    echo "   If none of the above work:"
    echo "   - Try a different camera cable"
    echo "   - Test with another camera module"
    echo "   - Check camera connector on Pi (bent pins?)"
    echo ""
fi

echo "========================================"
echo ""
echo "🔍 Quick Tests You Can Run:"
echo ""
echo "  # Test 1: List cameras"
echo "  libcamera-hello --list-cameras"
echo ""
echo "  # Test 2: Quick 1-second test"
echo "  rpicam-hello -t 1000"
echo ""
echo "  # Test 3: Check camera status"
echo "  vcgencmd get_camera"
echo ""
echo "  # Test 4: Run this diagnostic again"
echo "  bash diagnose_camera_hardware.sh"
echo ""
echo "========================================"
