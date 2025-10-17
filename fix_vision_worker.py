#!/usr/bin/env python3
"""
Script to update vision_worker.py with proper camera cleanup
Run this on your Raspberry Pi after pulling latest changes
"""

import shutil
from pathlib import Path

# Define the path
worker_path = Path("src/workers/vision_worker.py")

# Backup original
backup_path = worker_path.with_suffix(".py.backup")
if worker_path.exists():
    shutil.copy(worker_path, backup_path)
    print(f"✅ Backed up original to: {backup_path}")

# The improved vision worker code
IMPROVED_CODE = '''"""
Vision Worker - Face Detection Module
Uses YuNet ONNX model for face detection via OpenCV DNN
Integrates with Raspberry Pi camera using rpicam
"""

import cv2
import numpy as np
import subprocess
import threading
import queue
import time
import logging
import signal
import os
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, List

sys.path.append(str(Path(__file__).parent.parent))

from config import VISION_CONFIG, WORKER_CONFIG


class VisionWorker:
    """Vision worker for face detection and tracking"""
    
    def __init__(self, output_queue: queue.Queue):
        """Initialize vision worker"""
        self.output_queue = output_queue
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(__name__)
        
        # Camera process
        self.camera_process = None
        
        # Face detection
        self.detector = None
        self.locked_face_id = None
        self.locked_face_bbox = None
        self.frames_since_detection = 0
        self.last_greeting_time = 0
        
        # Performance tracking
        self.frame_count = 0
        self.detection_count = 0
        self.start_time = time.time()
        
        self.logger.info("Vision Worker initialized")
    
    def _load_detector(self) -> bool:
        """Load YuNet face detection model"""
        try:
            model_path = Path(VISION_CONFIG['model_path'])
            
            if not model_path.exists():
                self.logger.error(f"❌ YuNet model not found: {model_path}")
                self.logger.info("💡 Run: python download_yunet_model.py")
                return False
            
            self.logger.info(f"📦 Loading YuNet model from: {model_path}")
            
            # Create face detector
            self.detector = cv2.FaceDetectorYN.create(
                str(model_path),
                "",
                (VISION_CONFIG['frame_width'], VISION_CONFIG['frame_height']),
                score_threshold=VISION_CONFIG['confidence_threshold'],
                nms_threshold=VISION_CONFIG['nms_threshold'],
                top_k=VISION_CONFIG.get('top_k', 5),
                backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
                target_id=cv2.dnn.DNN_TARGET_CPU
            )
            
            self.logger.info("✅ YuNet model loaded successfully")
            self.logger.info(f"   Backend: OpenCV DNN (CPU)")
            self.logger.info(f"   Input size: {VISION_CONFIG['frame_width']}x{VISION_CONFIG['frame_height']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load YuNet model: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def _start_camera(self) -> bool:
        """Start Raspberry Pi camera using rpicam-vid"""
        try:
            # First, check if camera is available
            self.logger.info("📷 Checking camera availability...")
            try:
                check_result = subprocess.run(
                    ["rpicam-hello", "--list-cameras"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if check_result.returncode != 0:
                    self.logger.error("❌ Camera not detected")
                    self.logger.info("💡 Enable camera: sudo raspi-config → Interface → Camera")
                    return False
                
                self.logger.info("✅ Camera detected")
                
            except subprocess.TimeoutExpired:
                self.logger.error("❌ Camera check timeout")
                return False
            except FileNotFoundError:
                self.logger.error("❌ rpicam-hello not found")
                self.logger.info("💡 Install: sudo apt-get install rpicam-apps")
                return False
            
            # Start camera stream
            self.logger.info("📷 Starting Raspberry Pi camera...")
            
            cmd = [
                "rpicam-vid",
                "--width", str(VISION_CONFIG['frame_width']),
                "--height", str(VISION_CONFIG['frame_height']),
                "--framerate", str(VISION_CONFIG['camera_fps']),
                "--timeout", "0",  # Run indefinitely
                "--nopreview",  # No preview window
                "--codec", "yuv420",  # Raw YUV format
                "-o", "-"  # Output to stdout
            ]
            
            self.logger.info(f"   Command: {' '.join(cmd)}")
            
            # Start process with process group for proper cleanup
            self.camera_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Wait a moment for camera to initialize
            self.logger.info("   Waiting for camera initialization...")
            time.sleep(2)
            
            # Check if process started successfully
            if self.camera_process.poll() is not None:
                stderr = self.camera_process.stderr.read().decode()
                self.logger.error(f"❌ Camera failed to start: {stderr}")
                return False
            
            self.logger.info("✅ Camera started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Camera startup failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def _stop_camera(self):
        """Properly stop camera process"""
        if self.camera_process:
            try:
                self.logger.info("📷 Stopping camera...")
                
                # Send SIGTERM to process group
                try:
                    os.killpg(os.getpgid(self.camera_process.pid), signal.SIGTERM)
                except ProcessLookupError:
                    self.logger.warning("Process already terminated")
                    return
                
                # Wait for graceful shutdown
                try:
                    self.camera_process.wait(timeout=3)
                    self.logger.info("✅ Camera stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    self.logger.warning("⚠️  Force killing camera process")
                    try:
                        os.killpg(os.getpgid(self.camera_process.pid), signal.SIGKILL)
                        self.camera_process.wait()
                    except ProcessLookupError:
                        pass
                
                self.camera_process = None
                
                # Give camera time to fully release
                self.logger.info("   Waiting for camera to release...")
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ Error stopping camera: {e}")
    
    def _read_frame(self) -> Optional[np.ndarray]:
        """Read one frame from camera stream"""
        try:
            if not self.camera_process or self.camera_process.poll() is not None:
                return None
            
            # Calculate frame size for YUV420
            width = VISION_CONFIG['frame_width']
            height = VISION_CONFIG['frame_height']
            frame_size = width * height * 3 // 2  # YUV420 = 1.5 bytes per pixel
            
            # Read raw YUV data
            raw_frame = self.camera_process.stdout.read(frame_size)
            
            if len(raw_frame) != frame_size:
                return None
            
            # Convert YUV420 to RGB
            yuv = np.frombuffer(raw_frame, dtype=np.uint8)
            yuv = yuv.reshape((height * 3 // 2, width))
            
            # Convert YUV to BGR (OpenCV format)
            frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"❌ Frame read error: {e}")
            return None
    
    def _detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """Detect faces in frame"""
        try:
            if self.detector is None:
                return []
            
            # Detect faces
            _, faces = self.detector.detect(frame)
            
            if faces is None:
                return []
            
            # Extract bounding boxes and scores
            results = []
            for face in faces:
                x, y, w, h = face[:4].astype(int)
                score = float(face[-1])
                results.append((x, y, w, h, score))
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Detection error: {e}")
            return []
    
    def _calculate_face_distance(self, center1: Tuple[int, int], center2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two face centers"""
        dx = center1[0] - center2[0]
        dy = center1[1] - center2[1]
        return np.sqrt(dx*dx + dy*dy)
    
    def _should_lock_face(self, face_bbox: Tuple[int, int, int, int]) -> bool:
        """Check if should lock onto this face"""
        # If no face locked, can lock
        if self.locked_face_id is None:
            return True
        
        # If face already locked, check if this is the same face
        if self.locked_face_bbox:
            x1, y1, w1, h1 = self.locked_face_bbox
            x2, y2, w2, h2 = face_bbox
            
            # Calculate distance between face centers
            center1 = (x1 + w1/2, y1 + h1/2)
            center2 = (x2 + w2/2, y2 + h2/2)
            distance = self._calculate_face_distance(center1, center2)
            
            # If within threshold, same face
            if distance < VISION_CONFIG.get('tracking_distance_threshold', 100):
                return True
        
        return False
    
    def _process_detections(self, faces: List[Tuple[int, int, int, int, float]]):
        """Process detected faces and send events"""
        if not faces:
            # No faces detected
            self.frames_since_detection += 1
            
            # If locked face lost for too long
            if (self.locked_face_id is not None and 
                self.frames_since_detection > VISION_CONFIG.get('face_lost_timeout_frames', 15)):
                
                self.logger.info(f"👋 Face lost (ID: {self.locked_face_id})")
                
                # Send face lost event
                event = {
                    'type': 'face_lost',
                    'face_id': self.locked_face_id,
                    'timestamp': time.time()
                }
                self.output_queue.put(event)
                
                # Reset lock
                self.locked_face_id = None
                self.locked_face_bbox = None
            
            return
        
        # Faces detected
        self.frames_since_detection = 0
        
        # Get largest face (closest person)
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h, score = largest_face
        
        # Check if should lock onto this face
        if self._should_lock_face((x, y, w, h)):
            
            was_locked = self.locked_face_id is not None
            
            # Update locked face
            if self.locked_face_id is None:
                self.locked_face_id = self.detection_count
                self.logger.info(f"🔒 Locked onto face (ID: {self.locked_face_id})")
            
            self.locked_face_bbox = (x, y, w, h)
            self.detection_count += 1
            
            # Check if should send greeting
            current_time = time.time()
            time_since_greeting = current_time - self.last_greeting_time
            should_greet = (
                VISION_CONFIG.get('greeting_enabled', True) and
                not was_locked and  # New lock
                time_since_greeting > VISION_CONFIG.get('greeting_cooldown', 10.0)
            )
            
            if should_greet:
                self.last_greeting_time = current_time
                
                # Send new face event with greeting request
                event = {
                    'type': 'face_detected',
                    'face_id': self.locked_face_id,
                    'bbox': (x, y, w, h),
                    'confidence': score,
                    'request_greeting': True,
                    'timestamp': current_time
                }
                self.output_queue.put(event)
                
                self.logger.info(f"👋 New face detected - greeting requested (ID: {self.locked_face_id})")
            else:
                # Send face update event (no greeting)
                event = {
                    'type': 'face_update',
                    'face_id': self.locked_face_id,
                    'bbox': (x, y, w, h),
                    'confidence': score,
                    'timestamp': current_time
                }
                self.output_queue.put(event)
    
    def _run(self):
        """Main vision processing loop"""
        try:
            self.logger.info("🎥 Vision Worker starting...")
            
            # Load detector
            if not self._load_detector():
                self.logger.error("❌ Failed to load YuNet model")
                return
            
            # Start camera
            if not self._start_camera():
                self.logger.error("❌ Failed to start camera")
                return
            
            self.logger.info("✅ Vision Worker warmup complete")
            self.logger.info("👁️  Watching for faces...")
            
            self.start_time = time.time()
            frame_skip_counter = 0
            
            # Main loop
            while self.running:
                try:
                    # Read frame
                    frame = self._read_frame()
                    
                    if frame is None:
                        self.logger.warning("⚠️  Failed to read frame")
                        time.sleep(0.1)
                        continue
                    
                    self.frame_count += 1
                    
                    # Skip frames for performance
                    frame_skip_counter += 1
                    if frame_skip_counter < VISION_CONFIG.get('frame_skip', 2):
                        continue
                    frame_skip_counter = 0
                    
                    # Detect faces
                    faces = self._detect_faces(frame)
                    
                    # Process detections
                    self._process_detections(faces)
                    
                    # Log FPS periodically
                    if self.frame_count % 100 == 0:
                        elapsed = time.time() - self.start_time
                        fps = self.frame_count / elapsed
                        self.logger.debug(f"📊 Vision FPS: {fps:.1f}, Detections: {self.detection_count}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Error in vision loop: {e}")
                    time.sleep(0.1)
            
        except Exception as e:
            self.logger.error(f"❌ Vision worker error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        finally:
            # Clean up
            self._stop_camera()
            self.logger.info("✅ Vision Worker stopped")
    
    def start(self):
        """Start vision worker thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, name="VisionWorker", daemon=True)
            self.thread.start()
            self.logger.info("Vision Worker thread started")
    
    def stop(self):
        """Stop vision worker thread"""
        if self.running:
            self.logger.info("Stopping Vision Worker...")
            self.running = False
            
            # Stop camera first
            self._stop_camera()
            
            # Wait for thread
            if self.thread:
                self.thread.join(timeout=5)
                if self.thread.is_alive():
                    self.logger.warning("Vision Worker thread did not stop gracefully")
            
            self.logger.info("Vision Worker stopped")
    
    def get_status(self) -> Dict:
        """Get worker status"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        return {
            'running': self.running,
            'frames_processed': self.frame_count,
            'detections': self.detection_count,
            'fps': fps,
            'locked_face_id': self.locked_face_id,
            'locked': self.locked_face_id is not None
        }
'''

# Write improved code
worker_path.write_text(IMPROVED_CODE)
print(f"✅ Updated vision_worker.py with improved camera cleanup")
print(f"   - Added proper process group management")
print(f"   - Added SIGTERM/SIGKILL handling")
print(f"   - Added 1-second delay after camera stop")
print("\nChanges:")
print("  • Camera now properly releases after Ctrl+C")
print("  • rpicam-hello should work immediately after stopping Pluto")
print("  • Better logging throughout")
print("\nTest with:")
print("  python run.py")
print("  # Press Ctrl+C")
print("  rpicam-hello --list-cameras  # Should work now!")

