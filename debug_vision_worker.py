#!/usr/bin/env python3
"""
Debug script to find why vision worker fails to initialize
Run this on your Raspberry Pi to see the exact error
"""

import sys
import traceback
from pathlib import Path

print("=" * 70)
print("🔍 VISION WORKER INITIALIZATION DEBUG")
print("=" * 70)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("\n1️⃣ Testing basic imports...")
try:
    import cv2
    print(f"   ✅ OpenCV: {cv2.__version__}")
except ImportError as e:
    print(f"   ❌ OpenCV not installed: {e}")
    print("      Run: pip install opencv-python")
    sys.exit(1)

try:
    import numpy as np
    print(f"   ✅ NumPy: {np.__version__}")
except ImportError as e:
    print(f"   ❌ NumPy not installed: {e}")
    print("      Run: pip install numpy")
    sys.exit(1)

print("\n2️⃣ Testing config import...")
try:
    from config import VISION_CONFIG
    print(f"   ✅ VISION_CONFIG loaded")
    print(f"      Model: {VISION_CONFIG.get('model_path')}")
    print(f"      Resolution: {VISION_CONFIG.get('frame_width')}x{VISION_CONFIG.get('frame_height')}")
except Exception as e:
    print(f"   ❌ Failed to import VISION_CONFIG: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n3️⃣ Checking YuNet model file...")
import os
model_path = VISION_CONFIG.get('model_path')
if os.path.exists(model_path):
    size = os.path.getsize(model_path)
    print(f"   ✅ Model exists: {model_path}")
    print(f"      Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
else:
    print(f"   ❌ Model NOT found: {model_path}")
    print("      Run: python download_yunet_model.py")
    sys.exit(1)

print("\n4️⃣ Testing YuNet model loading...")
try:
    detector = cv2.FaceDetectorYN.create(
        model=model_path,
        config="",
        input_size=(320, 240),
        score_threshold=0.6,
        nms_threshold=0.3,
        top_k=5000
    )
    print(f"   ✅ YuNet detector created successfully")
except Exception as e:
    print(f"   ❌ Failed to create YuNet detector: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n5️⃣ Testing camera command...")
import subprocess
camera_cmd = VISION_CONFIG.get('camera_command', ['rpicam-vid', '--version'])
try:
    # Just test if rpicam-vid exists
    result = subprocess.run(['rpicam-vid', '--version'], 
                          capture_output=True, 
                          timeout=3)
    if result.returncode == 0:
        print(f"   ✅ rpicam-vid is available")
    else:
        print(f"   ⚠️  rpicam-vid returned code {result.returncode}")
except FileNotFoundError:
    print(f"   ❌ rpicam-vid not found")
    print("      Run: sudo apt install -y rpicam-apps")
except Exception as e:
    print(f"   ⚠️  Could not test camera: {e}")

print("\n6️⃣ Testing vision worker import...")
try:
    from workers.vision_worker import VisionWorker
    print(f"   ✅ VisionWorker class imported")
except Exception as e:
    print(f"   ❌ Failed to import VisionWorker: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n7️⃣ Testing vision worker initialization...")
import queue
try:
    test_queue = queue.Queue()
    print(f"   Creating VisionWorker with test queue...")
    
    vision_worker = VisionWorker(test_queue)
    print(f"   ✅ VisionWorker created successfully!")
    print(f"      Worker object: {vision_worker}")
    print(f"      Has start method: {hasattr(vision_worker, 'start')}")
    
except Exception as e:
    print(f"   ❌ VisionWorker initialization failed!")
    print(f"      Error: {e}")
    print(f"\n   Full traceback:")
    traceback.print_exc()
    print(f"\n   💡 This is the error you're seeing!")
    sys.exit(1)

print("\n8️⃣ Testing vision worker start (dry run)...")
try:
    # Don't actually start it, just check if the method exists
    if hasattr(vision_worker, 'start'):
        print(f"   ✅ start() method exists")
        # Check if it's a BaseWorker
        print(f"   Worker type: {type(vision_worker).__name__}")
        print(f"   Base classes: {[c.__name__ for c in type(vision_worker).__mro__]}")
    else:
        print(f"   ❌ No start() method found!")
except Exception as e:
    print(f"   ⚠️  Error checking start method: {e}")

print("\n" + "=" * 70)
print("✅ ALL CHECKS PASSED!")
print("=" * 70)
print("\n💡 If you got here, the vision worker should initialize fine.")
print("   The error might be in orchestrator integration.")
print("\n🎯 Try running: python run.py")
print("=" * 70)
