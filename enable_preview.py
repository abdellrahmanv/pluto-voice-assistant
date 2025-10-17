#!/usr/bin/env python3
"""
Direct update to vision_worker.py to add preview window
This version directly replaces the file with preview-enabled code
"""

from pathlib import Path
import shutil

# Backup original
worker_path = Path("src/workers/vision_worker.py")
backup_path = Path("src/workers/vision_worker.py.backup_before_preview")

if worker_path.exists() and not backup_path.exists():
    shutil.copy(worker_path, backup_path)
    print(f"✅ Backed up original to: {backup_path}")

# The complete vision_worker.py with preview support
VISION_WORKER_WITH_PREVIEW = '''"""
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
        
        # Preview window
        self.show_preview = VISION_CONFIG.get('show_preview', False)
        self.preview_window = None
        
        self.logger.info("Vision Worker initialized")
        if self.show_preview:
            self.logger.info("📺 Preview mode enabled")
    
    def _load_detector(self) -> bool:
        """Load YuNet face detection model"""
        try:
            model_path = Path(VISION_CONFIG['model_path'])
            
            if not model_path.exists():
                self.logger.error(f"❌ YuNet model not found: {model_path}")
                self.logger.info("💡 Run: python download_yunet_model.py")
                return False
            
            self.logger.info(f"📦 Loading YuNet model from: {model_path}")
            
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
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load YuNet: {e}")
            return False
    
    def _start_camera(self) -> bool:
        """Start Raspberry Pi camera"""
        try:
            self.logger.info("📷 Starting camera...")
            
            cmd = [
                "rpicam-vid",
                "--width", str(VISION_CONFIG['frame_width']),
                "--height", str(VISION_CONFIG['frame_height']),
                "--framerate", str(VISION_CONFIG['camera_fps']),
                "--timeout", "0",
                "--nopreview",
                "--codec", "yuv420",
                "-o", "-"
            ]
            
            self.camera_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8,
                preexec_fn=os.setsid
            )
            
            time.sleep(2)
            
            if self.camera_process.poll() is not None:
                stderr = self.camera_process.stderr.read().decode()
                self.logger.error(f"❌ Camera failed: {stderr}")
                return False
            
            self.logger.info("✅ Camera started")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Camera error: {e}")
            return False
    
    def _stop_camera(self):
        """Stop camera process"""
        if self.camera_process:
            try:
                self.logger.info("📷 Stopping camera...")
                os.killpg(os.getpgid(self.camera_process.pid), signal.SIGTERM)
                
                try:
                    self.camera_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(self.camera_process.pid), signal.SIGKILL)
                    self.camera_process.wait()
                
                self.camera_process = None
                time.sleep(1)
                self.logger.info("✅ Camera stopped")
            except Exception as e:
                self.logger.error(f"❌ Camera stop error: {e}")
    
    def _read_frame(self) -> Optional[np.ndarray]:
        """Read frame from camera"""
        try:
            if not self.camera_process or self.camera_process.poll() is not None:
                return None
            
            width = VISION_CONFIG['frame_width']
            height = VISION_CONFIG['frame_height']
            frame_size = width * height * 3 // 2
            
            raw_frame = self.camera_process.stdout.read(frame_size)
            if len(raw_frame) != frame_size:
                return None
            
            yuv = np.frombuffer(raw_frame, dtype=np.uint8)
            yuv = yuv.reshape((height * 3 // 2, width))
            frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
            
            return frame
        except:
            return None
    
    def _detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """Detect faces"""
        try:
            if self.detector is None:
                return []
            
            _, faces = self.detector.detect(frame)
            if faces is None:
                return []
            
            results = []
            for face in faces:
                x, y, w, h = face[:4].astype(int)
                score = float(face[-1])
                results.append((x, y, w, h, score))
            
            return results
        except:
            return []
    
    def _draw_preview(self, frame: np.ndarray, faces: List[Tuple[int, int, int, int, float]]) -> np.ndarray:
        """Draw preview with detections"""
        if not self.show_preview or frame is None:
            return frame
        
        display = frame.copy()
        
        # Draw faces
        for i, (x, y, w, h, conf) in enumerate(faces):
            # Color: green if locked, orange otherwise
            if self.locked_face_id is not None and i == 0:
                color = (0, 255, 0)
                label = f"LOCKED ID:{self.locked_face_id} ({conf:.2f})"
            else:
                color = (255, 128, 0)
                label = f"DETECTED ({conf:.2f})"
            
            # Box
            cv2.rectangle(display, (x, y), (x+w, y+h), color, 2)
            
            # Label
            label_y = y - 10 if y > 30 else y + h + 20
            (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(display, (x, label_y-lh-5), (x+lw, label_y+5), color, -1)
            cv2.putText(display, label, (x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        
        # Status
        if self.locked_face_id is not None:
            status = f"STATE: LOCKED (Face ID: {self.locked_face_id})"
            color = (0, 255, 0)
        else:
            status = "STATE: SCANNING..."
            color = (255, 128, 0)
        cv2.putText(display, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # FPS
        elapsed = time.time() - self.start_time if self.start_time else 0
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        cv2.putText(display, f"FPS: {fps:.1f}", (10, display.shape[0]-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        
        # Greeting status
        if self.last_greeting_time > 0:
            since = time.time() - self.last_greeting_time
            cooldown = VISION_CONFIG.get('greeting_cooldown', 10.0)
            if since < cooldown:
                cv2.putText(display, f"GREETED: {since:.1f}s ago", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)
        
        return display
    
    def _show_preview(self, frame: np.ndarray):
        """Show preview window"""
        if not self.show_preview or frame is None:
            return
        
        try:
            window_name = VISION_CONFIG.get('preview_window_name', 'Pluto Vision')
            
            if self.preview_window is None:
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(window_name, 640, 480)
                self.preview_window = window_name
                self.logger.info(f"📺 Preview window opened: {window_name}")
            
            cv2.imshow(window_name, frame)
            cv2.waitKey(1)
        except Exception as e:
            self.logger.error(f"Preview error: {e}")
            self.show_preview = False
    
    def _close_preview(self):
        """Close preview window"""
        if self.preview_window:
            try:
                cv2.destroyWindow(self.preview_window)
                self.preview_window = None
                self.logger.info("📺 Preview window closed")
            except:
                pass
    
    def _process_detections(self, faces: List[Tuple[int, int, int, int, float]]):
        """Process detections and send events"""
        if not faces:
            self.frames_since_detection += 1
            
            if (self.locked_face_id is not None and 
                self.frames_since_detection > VISION_CONFIG.get('face_lost_timeout_frames', 15)):
                
                self.logger.info(f"👋 Face lost (ID: {self.locked_face_id})")
                
                event = {
                    'type': 'face_lost',
                    'face_id': self.locked_face_id,
                    'timestamp': time.time()
                }
                self.output_queue.put(event)
                
                self.locked_face_id = None
                self.locked_face_bbox = None
            return
        
        self.frames_since_detection = 0
        
        # Get largest face
        largest = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h, score = largest
        
        was_locked = self.locked_face_id is not None
        
        if self.locked_face_id is None:
            self.locked_face_id = self.detection_count
            self.logger.info(f"🔒 Locked onto face (ID: {self.locked_face_id})")
        
        self.locked_face_bbox = (x, y, w, h)
        self.detection_count += 1
        
        # Check greeting
        current_time = time.time()
        time_since = current_time - self.last_greeting_time
        should_greet = (
            VISION_CONFIG.get('greeting_enabled', True) and
            not was_locked and
            time_since > VISION_CONFIG.get('greeting_cooldown', 10.0)
        )
        
        if should_greet:
            self.last_greeting_time = current_time
            event = {
                'type': 'face_detected',
                'face_id': self.locked_face_id,
                'bbox': (x, y, w, h),
                'confidence': score,
                'request_greeting': True,
                'timestamp': current_time
            }
            self.output_queue.put(event)
            self.logger.info(f"👋 New face - greeting (ID: {self.locked_face_id})")
    
    def _run(self):
        """Main loop"""
        try:
            self.logger.info("🎥 Vision Worker starting...")
            
            if not self._load_detector():
                return
            
            if not self._start_camera():
                return
            
            self.logger.info("✅ Vision Worker ready")
            self.logger.info("👁️  Watching for faces...")
            
            self.start_time = time.time()
            skip = 0
            
            while self.running:
                try:
                    frame = self._read_frame()
                    if frame is None:
                        time.sleep(0.1)
                        continue
                    
                    self.frame_count += 1
                    
                    skip += 1
                    if skip < VISION_CONFIG.get('frame_skip', 2):
                        continue
                    skip = 0
                    
                    # Detect
                    faces = self._detect_faces(frame)
                    
                    # Process
                    self._process_detections(faces)
                    
                    # Preview
                    if self.show_preview:
                        preview = self._draw_preview(frame, faces)
                        self._show_preview(preview)
                    
                    if self.frame_count % 100 == 0:
                        elapsed = time.time() - self.start_time
                        fps = self.frame_count / elapsed
                        self.logger.debug(f"📊 FPS: {fps:.1f}, Detections: {self.detection_count}")
                
                except Exception as e:
                    self.logger.error(f"Loop error: {e}")
                    time.sleep(0.1)
        
        except Exception as e:
            self.logger.error(f"Vision error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        finally:
            self._close_preview()
            self._stop_camera()
            self.logger.info("✅ Vision Worker stopped")
    
    def start(self):
        """Start worker"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop worker"""
        if self.running:
            self.running = False
            self._close_preview()
            self._stop_camera()
            if self.thread:
                self.thread.join(timeout=5)
    
    def get_status(self) -> Dict:
        """Get status"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        return {
            'running': self.running,
            'frames': self.frame_count,
            'detections': self.detection_count,
            'fps': fps,
            'locked_id': self.locked_face_id,
            'locked': self.locked_face_id is not None
        }
'''

# Write the file
worker_path.write_text(VISION_WORKER_WITH_PREVIEW)

print("\n" + "="*70)
print("✅ VISION WORKER UPDATED WITH PREVIEW SUPPORT!")
print("="*70)
print("\n📺 Preview Features:")
print("  • Live camera window with face detection")
print("  • Green boxes = locked face")
print("  • Orange boxes = detected faces")
print("  • State indicator (SCANNING/LOCKED)")
print("  • FPS counter")
print("  • Greeting cooldown timer")
print("\n🚀 Now run:")
print("  python run.py")
print("\n📺 A window will open showing the camera feed with overlays!")
print("\n⚙️  To disable preview, edit src/config.py:")
print("  VISION_CONFIG['show_preview'] = False")
print("\n" + "="*70 + "\n")
