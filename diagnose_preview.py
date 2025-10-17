#!/usr/bin/env python3
"""
Diagnose why preview window isn't showing
"""

import sys
import os

print("\n" + "="*70)
print("🔍 PREVIEW WINDOW DIAGNOSTICS")
print("="*70 + "\n")

# Test 1: Check DISPLAY variable
print("1️⃣ Checking X11 DISPLAY environment...")
display = os.environ.get('DISPLAY')
if display:
    print(f"   ✅ DISPLAY is set: {display}")
else:
    print(f"   ❌ DISPLAY not set")
    print(f"   💡 Fix: export DISPLAY=:0")
    print(f"   💡 Or run: export DISPLAY=:0.0")

# Test 2: Check OpenCV
print("\n2️⃣ Checking OpenCV installation...")
try:
    import cv2
    print(f"   ✅ OpenCV version: {cv2.__version__}")
    
    # Check GUI support
    print("\n3️⃣ Checking OpenCV GUI support...")
    try:
        # Try to create a simple window
        test_window = "OpenCV Test"
        cv2.namedWindow(test_window, cv2.WINDOW_NORMAL)
        
        # Create a test image
        import numpy as np
        test_img = np.zeros((240, 320, 3), dtype=np.uint8)
        cv2.putText(test_img, "OpenCV GUI Test", (50, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Try to show it
        cv2.imshow(test_window, test_img)
        cv2.waitKey(2000)  # Show for 2 seconds
        cv2.destroyAllWindows()
        
        print(f"   ✅ OpenCV GUI works!")
        print(f"   💡 You should have seen a window for 2 seconds")
        
    except Exception as e:
        print(f"   ❌ OpenCV GUI failed: {e}")
        print(f"\n   Possible fixes:")
        print(f"   1. Install GUI support: sudo apt-get install python3-opencv")
        print(f"   2. Install Qt backend: sudo apt-get install libqt5gui5")
        print(f"   3. Or use GTK: sudo apt-get install python3-pyqt5")
        
except ImportError as e:
    print(f"   ❌ OpenCV not installed: {e}")
    print(f"   💡 Install: pip install opencv-python")

# Test 4: Check if running over SSH
print("\n4️⃣ Checking connection type...")
ssh_connection = os.environ.get('SSH_CONNECTION')
ssh_client = os.environ.get('SSH_CLIENT')

if ssh_connection or ssh_client:
    print(f"   ⚠️  Running over SSH")
    print(f"   SSH_CONNECTION: {ssh_connection}")
    print(f"   SSH_CLIENT: {ssh_client}")
    print(f"\n   💡 For GUI over SSH:")
    print(f"   1. Connect with: ssh -X pi@raspberry")
    print(f"   2. Or use VNC for full desktop")
    print(f"   3. Or run directly on Pi with monitor")
else:
    print(f"   ✅ Local session (not SSH)")

# Test 5: Check config
print("\n5️⃣ Checking Pluto config...")
try:
    sys.path.insert(0, 'src')
    from config import VISION_CONFIG
    
    show_preview = VISION_CONFIG.get('show_preview', False)
    if show_preview:
        print(f"   ✅ show_preview = {show_preview}")
    else:
        print(f"   ❌ show_preview = {show_preview}")
        print(f"   💡 Edit src/config.py and set:")
        print(f"      VISION_CONFIG['show_preview'] = True")
        
except Exception as e:
    print(f"   ❌ Config error: {e}")

# Test 6: Check vision worker code
print("\n6️⃣ Checking vision_worker.py for preview code...")
try:
    with open('src/workers/vision_worker.py', 'r') as f:
        content = f.read()
        
    has_preview = '_show_preview' in content and '_draw_preview' in content
    
    if has_preview:
        print(f"   ✅ Preview methods found in vision_worker.py")
    else:
        print(f"   ❌ Preview methods NOT found in vision_worker.py")
        print(f"   💡 Run: python enable_preview.py")
        
except Exception as e:
    print(f"   ❌ Error reading vision_worker.py: {e}")

print("\n" + "="*70)
print("📋 SUMMARY")
print("="*70)

print("""
For preview to work, you need:
1. ✅ DISPLAY environment variable set
2. ✅ OpenCV with GUI support (cv2.imshow works)
3. ✅ show_preview = True in config.py
4. ✅ Preview code in vision_worker.py
5. ✅ Either local session OR ssh -X connection

Common solutions:
- If over SSH: Use 'ssh -X pi@raspberry' or VNC
- If local but no window: Check DISPLAY with 'echo $DISPLAY'
- If DISPLAY empty: Run 'export DISPLAY=:0' before python run.py
- If OpenCV GUI fails: sudo apt-get install python3-opencv libqt5gui5

Alternative: Use VNC Viewer to connect to Pi desktop, then run from terminal there
""")

print("="*70 + "\n")
