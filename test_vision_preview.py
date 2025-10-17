#!/usr/bin/env python3
"""
Test Vision Preview - Shows what the camera sees with face detection
Run this independently to test camera and face detection
"""

import cv2
import numpy as np
import subprocess
import time
import sys
from pathlib import Path

# Configuration
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
CAMERA_FPS = 10
MODEL_PATH = "models/face_detection_yunet_2023mar_int8bq.onnx"

def start_camera():
    """Start Raspberry Pi camera"""
    print("📷 Starting camera...")
    cmd = [
        "rpicam-vid",
        "--width", str(CAMERA_WIDTH),
        "--height", str(CAMERA_HEIGHT),
        "--framerate", str(CAMERA_FPS),
        "--timeout", "0",
        "--nopreview",
        "--codec", "yuv420",
        "-o", "-"
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=10**8
    )
    
    time.sleep(2)
    
    if process.poll() is not None:
        print("❌ Camera failed to start")
        return None
    
    print("✅ Camera started")
    return process

def read_frame(process):
    """Read one frame from camera"""
    frame_size = CAMERA_WIDTH * CAMERA_HEIGHT * 3 // 2
    raw_frame = process.stdout.read(frame_size)
    
    if len(raw_frame) != frame_size:
        return None
    
    yuv = np.frombuffer(raw_frame, dtype=np.uint8)
    yuv = yuv.reshape((CAMERA_HEIGHT * 3 // 2, CAMERA_WIDTH))
    frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
    
    return frame

def main():
    print("\n" + "="*70)
    print("👁️  PLUTO VISION PREVIEW TEST")
    print("="*70 + "\n")
    
    # Load face detector
    print("📦 Loading YuNet model...")
    model_path = Path(MODEL_PATH)
    
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        print("💡 Run: python download_yunet_model.py")
        return 1
    
    try:
        detector = cv2.FaceDetectorYN.create(
            str(model_path),
            "",
            (CAMERA_WIDTH, CAMERA_HEIGHT),
            score_threshold=0.6,
            nms_threshold=0.3,
            top_k=5,
            backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
            target_id=cv2.dnn.DNN_TARGET_CPU
        )
        print("✅ YuNet model loaded\n")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return 1
    
    # Start camera
    camera = start_camera()
    if not camera:
        return 1
    
    print("\n" + "="*70)
    print("📺 LIVE PREVIEW WINDOW")
    print("="*70)
    print("\nWindow will show:")
    print("  🟢 Green boxes = Detected faces")
    print("  📊 Confidence scores")
    print("  ⏱️  FPS counter")
    print("\n👁️  Press 'q' to quit")
    print("="*70 + "\n")
    
    # Create window
    window_name = "Pluto Vision - Face Detection Test"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 640, 480)
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Read frame
            frame = read_frame(camera)
            if frame is None:
                print("⚠️  Failed to read frame")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            
            # Detect faces
            _, faces = detector.detect(frame)
            
            # Draw detections
            if faces is not None:
                for face in faces:
                    x, y, w, h = face[:4].astype(int)
                    confidence = float(face[-1])
                    
                    # Draw bounding box (green)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Draw label
                    label = f"Face {confidence:.2f}"
                    label_y = y - 10 if y > 30 else y + h + 20
                    
                    # Label background
                    (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(frame, (x, label_y - label_h - 5), (x + label_w, label_y + 5), (0, 255, 0), -1)
                    
                    # Label text
                    cv2.putText(frame, label, (x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                
                # Status text
                status = f"DETECTED: {len(faces)} face(s)"
                cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                # No faces
                cv2.putText(frame, "SCANNING...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 128, 0), 2)
            
            # FPS counter
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            fps_text = f"FPS: {fps:.1f}"
            cv2.putText(frame, fps_text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show frame
            cv2.imshow(window_name, frame)
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n👋 Quitting...")
                break
            
            # Print status every 100 frames
            if frame_count % 100 == 0:
                face_count = len(faces) if faces is not None else 0
                print(f"📊 Frames: {frame_count} | FPS: {fps:.1f} | Faces: {face_count}")
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    
    finally:
        # Cleanup
        print("\n🛑 Cleaning up...")
        cv2.destroyAllWindows()
        
        if camera:
            camera.terminate()
            camera.wait()
            print("✅ Camera stopped")
        
        print("\n" + "="*70)
        print("✅ PREVIEW TEST COMPLETE")
        print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
