#!/usr/bin/env python3
"""
Quick test: Can OpenCV show windows in your current environment?
"""

import cv2
import numpy as np
import os

print("="*70)
print("TESTING OPENCV GUI IN YOUR ENVIRONMENT")
print("="*70)

# Check 1: DISPLAY variable
display = os.environ.get('DISPLAY')
print(f"\n1️⃣ DISPLAY environment: {display if display else '❌ NOT SET'}")

# Check 2: SSH connection
ssh = os.environ.get('SSH_CONNECTION')
ssh_client = os.environ.get('SSH_CLIENT')
if ssh or ssh_client:
    print(f"2️⃣ Connection type: ⚠️ SSH SESSION DETECTED")
    print(f"   SSH_CONNECTION: {ssh}")
    print(f"   SSH_CLIENT: {ssh_client}")
else:
    print(f"2️⃣ Connection type: ✅ Local or VNC")

# Check 3: Try to create a window
print(f"\n3️⃣ Testing OpenCV window creation...")
try:
    # Create a simple test image
    img = np.zeros((240, 320, 3), dtype=np.uint8)
    cv2.putText(img, "TEST WINDOW", (50, 120), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Try to show it
    window_name = "OpenCV Test"
    cv2.namedWindow(window_name)
    cv2.imshow(window_name, img)
    
    print("   ✅ Window created successfully!")
    print("   📺 You should see a test window now...")
    print("\n   Press ANY KEY in the window to close it")
    print("   (If you don't see a window, that's the problem!)")
    
    cv2.waitKey(5000)  # Wait 5 seconds or until key press
    cv2.destroyAllWindows()
    
    print("\n✅ OpenCV GUI works in your environment!")
    print("\n📺 The preview window SHOULD work when you run Pluto.")
    print("   If you can't see this test window, you won't see Pluto's preview either.")
    
except Exception as e:
    print(f"   ❌ FAILED: {e}")
    print("\n" + "="*70)
    print("🔴 PROBLEM FOUND: OpenCV cannot display windows!")
    print("="*70)
    
    if ssh or ssh_client:
        print("""
This is because you're connected via SSH!

🔧 SOLUTIONS:

Option 1: Enable X11 Forwarding (recommended for testing)
---------------------------------------------------------
Disconnect and reconnect with X11 forwarding:
  ssh -X pi@your_raspberry_ip

Then run this test again to verify.

Option 2: Use VNC instead of SSH
---------------------------------
1. Install VNC server on Pi:
   sudo apt-get install realvnc-vnc-server
   
2. Enable VNC:
   sudo raspi-config
   → Interface Options → VNC → Enable

3. Connect with VNC viewer from your PC
   Then GUI windows will work!

Option 3: Use Headless Mode (saves frames to files)
----------------------------------------------------
Run this instead:
  python enable_headless_preview.py
  
Then Pluto will save preview images to files you can download:
  scp pi@raspberry:~/pluto-voice-assistant/preview_frames/*.jpg .
""")
    else:
        print("""
🔧 SOLUTIONS:

1. Install OpenCV with GUI support:
   sudo apt-get install python3-opencv libqt5gui5 libqt5widgets5

2. Or reinstall opencv in your virtual environment:
   pip install opencv-contrib-python

3. Make sure you have a display connected or VNC enabled
""")

print("\n" + "="*70)
