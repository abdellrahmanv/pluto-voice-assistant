#!/usr/bin/env python3
"""
Test if OpenCV GUI window works via VNC
Run this to verify the preview window will work
"""

import cv2
import numpy as np
import time

print("=" * 70)
print("🖼️  TESTING OPENCV WINDOW VIA VNC")
print("=" * 70)

print("\n1️⃣ Creating test image...")
# Create a test image (blue background with text)
img = np.zeros((480, 640, 3), dtype=np.uint8)
img[:, :] = (255, 100, 0)  # Blue background

# Draw some test elements
cv2.putText(img, "Pluto Vision Test", (150, 240), 
           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
cv2.rectangle(img, (200, 300), (440, 400), (0, 255, 0), 3)
cv2.putText(img, "If you see this, GUI works!", (160, 360), 
           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

print("   ✅ Test image created")

print("\n2️⃣ Opening window via VNC...")
try:
    window_name = "Pluto Vision - VNC Test"
    cv2.imshow(window_name, img)
    print(f"   ✅ Window '{window_name}' opened")
    print("\n   👀 CHECK YOUR VNC VIEWER NOW!")
    print("   You should see a blue window with text")
    print("   If you don't see it, OpenCV GUI won't work via VNC")
    
    print("\n⏱️  Window will stay open for 10 seconds...")
    for i in range(10, 0, -1):
        print(f"   Closing in {i}...", end='\r')
        cv2.waitKey(1000)  # Wait 1 second
    
    print("\n\n3️⃣ Closing window...")
    cv2.destroyAllWindows()
    print("   ✅ Window closed")
    
    print("\n" + "=" * 70)
    print("✅ GUI WINDOW TEST PASSED")
    print("=" * 70)
    print("\nThe preview window WILL work when you run Pluto!")
    print("If you SAW the blue window, everything is working correctly.")
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nThis means OpenCV GUI won't work via VNC.")
    print("Solutions:")
    print("  1. Make sure you're using VNC (not SSH)")
    print("  2. Set DISPLAY variable: export DISPLAY=:0")
    print("  3. Install: sudo apt-get install python3-opencv")
    print("\n" + "=" * 70)
