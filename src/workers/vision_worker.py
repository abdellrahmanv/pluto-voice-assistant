"""
Vision Worker - Face Detection Module
Uses YuNet ONNX model for face detection via OpenCV DNN
Integrates with Raspberry Pi camera using rpicam
"""

import cv2
import numpy as np
import queue
import threading
import time
import subprocess
import io
from pathlib import Path
from typing import Optional, Tuple, Dict, List

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import VISION_CONFIG, WORKER_CONFIG


class VisionWorker:
    """Vision worker for face detection and tracking"""
    
    def __init__(self, output_queue: queue.Queue):
        """
        Initialize vision worker
        
        Args:
            output_queue: Queue for sending face detection events
        """
        self.output_queue = output_queue
        self.running = False
        self.thread = None
        self.warmup_complete = False
        
        # Face tracking state
        self.locked_face_id = None
        self.locked_face_bbox = None
        self.locked_face_center = None
        self.frames_without_face = 0
        self.frames_with_face = 0
        self.detection_count = 0
        self.fps = 0
        
        # YuNet detector
        self.detector = None
        self.model_path = VISION_CONFIG['model_path']
        
        # Camera process
        self.camera_process = None
        self.frame_buffer = None
        
        print("🎥 Vision Worker initialized")
        
    def start(self) -> bool:
        """Start the vision worker thread"""
        if self.running:
            print("⚠️  Vision worker already running")
            return False

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("✅ Vision Worker thread started")
        return True

    def stop(self):
        """Stop the vision worker"""
        print("🛑 Stopping Vision Worker...")
        self.running = False

        # Close preview window
        try:
            cv2.destroyAllWindows()
        except:
            pass

        # Stop camera with proper cleanup (prevents "failed to acquire camera" error)
        if self.camera_process:
            try:
                import signal
                import os
                
                print("   🛑 Stopping camera...")
                
                # Immediate force kill - don't wait for graceful shutdown
                try:
                    pgid = os.getpgid(self.camera_process.pid)
                    os.killpg(pgid, signal.SIGKILL)  # Use SIGKILL immediately
                    print("   📡 Sent SIGKILL to camera process group")
                except Exception as e:
                    # Fallback to direct kill
                    self.camera_process.kill()
                    print(f"   📡 Sent SIGKILL to camera process")
                
                # Short wait (0.5s max)
                try:
                    self.camera_process.wait(timeout=0.5)
                    print("   ✅ Camera stopped")
                except subprocess.TimeoutExpired:
                    print("   ⚠️  Camera process stubborn")
                    pass  # Continue anyway
                    
                # Nuclear cleanup: kill ALL rpicam processes (non-blocking)
                subprocess.Popen(['pkill', '-9', 'rpicam'], 
                               stderr=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL)
                               
            except Exception as e:
                print(f"   ⚠️  Camera cleanup: {e}")
                # Last resort
                try:
                    subprocess.Popen(['pkill', '-9', 'rpicam'], 
                                   stderr=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL)
                except:
                    pass

        if self.thread:
            self.thread.join(timeout=5)

        print("✅ Vision Worker stopped")

    def _load_detector(self) -> bool:
        """Load YuNet face detection model"""
        try:
            if not Path(self.model_path).exists():
                print(f"❌ YuNet model not found at: {self.model_path}")
                print(f"   Run: python download_yunet_model.py")
                return False
                
            print(f"📦 Loading YuNet model from: {self.model_path}")
            
            # Initialize YuNet detector
            self.detector = cv2.FaceDetectorYN.create(
                model=str(self.model_path),
                config="",
                input_size=(VISION_CONFIG['frame_width'], VISION_CONFIG['frame_height']),
                score_threshold=VISION_CONFIG['confidence_threshold'],
                nms_threshold=VISION_CONFIG['nms_threshold'],
                top_k=VISION_CONFIG['max_faces'],
                backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
                target_id=cv2.dnn.DNN_TARGET_CPU
            )
            
            # Set thread count for efficiency
            cv2.setNumThreads(VISION_CONFIG['num_threads'])
            
            print(f"✅ YuNet model loaded successfully")
            print(f"   Backend: OpenCV DNN (CPU)")
            print(f"   Threads: {VISION_CONFIG['num_threads']}")
            print(f"   Input size: {VISION_CONFIG['frame_width']}x{VISION_CONFIG['frame_height']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load YuNet model: {e}")
            return False
            
    def _start_camera(self) -> bool:
        """Start Raspberry Pi camera using rpicam-vid"""
        try:
            width = VISION_CONFIG['frame_width']
            height = VISION_CONFIG['frame_height']
            fps = VISION_CONFIG['camera_fps']
            
            # rpicam-vid command for streaming to stdout
            cmd = [
                'rpicam-vid',
                '--width', str(width),
                '--height', str(height),
                '--framerate', str(fps),
                '--timeout', '0',  # Run indefinitely
                '--codec', 'yuv420',  # Raw YUV format
                '--output', '-',  # Output to stdout
                '--nopreview',  # No preview window
                '--denoise', 'cdn_off',  # Disable denoise for speed
            ]
            
            print(f"📷 Starting Raspberry Pi camera...")
            print(f"   Command: {' '.join(cmd)}")

            # Start camera in its own process group for proper cleanup
            import os
            self.camera_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=width * height * 3 // 2,  # YUV420 buffer size
                preexec_fn=os.setsid  # Create new process group
            )

            # Wait for camera to initialize
            time.sleep(2)

            print("✅ Camera started")
            return True

        except FileNotFoundError:
            print("❌ rpicam-vid not found. Install with: sudo apt-get install rpicam-apps")
            return False
        except Exception as e:
            print(f"❌ Failed to start camera: {e}")
            return False
            
    def _read_frame(self) -> Optional[np.ndarray]:
        """Read a frame from the camera stream"""
        try:
            if not self.camera_process or self.camera_process.poll() is not None:
                return None
                
            width = VISION_CONFIG['frame_width']
            height = VISION_CONFIG['frame_height']
            
            # Read YUV420 frame (1.5 bytes per pixel)
            frame_size = width * height * 3 // 2
            raw_data = self.camera_process.stdout.read(frame_size)
            
            if len(raw_data) != frame_size:
                return None
                
            # Convert YUV420 to RGB
            yuv = np.frombuffer(raw_data, dtype=np.uint8).reshape((height * 3 // 2, width))
            frame = cv2.cvtColor(yuv, cv2.COLOR_YUV420p2BGR)
            
            return frame
            
        except Exception as e:
            print(f"⚠️  Frame read error: {e}")
            return None
            
    def _detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces in frame
        
        Returns:
            List of detected faces with bounding boxes and confidence
        """
        if self.detector is None:
            return []
            
        try:
            # Detect faces
            _, faces = self.detector.detect(frame)
            
            if faces is None or len(faces) == 0:
                return []
                
            # Parse detection results
            detected_faces = []
            for face in faces:
                # face format: [x, y, w, h, x_re, y_re, x_le, y_le, x_nt, y_nt, x_rcm, y_rcm, x_lcm, y_lcm, conf]
                x, y, w, h = map(int, face[:4])
                confidence = float(face[14])
                
                # Calculate center
                center_x = x + w // 2
                center_y = y + h // 2
                
                detected_faces.append({
                    'bbox': (x, y, w, h),
                    'center': (center_x, center_y),
                    'confidence': confidence,
                    'area': w * h
                })
                
            # Sort by area (largest first - closest person)
            detected_faces.sort(key=lambda f: f['area'], reverse=True)
            
            return detected_faces
            
        except Exception as e:
            print(f"⚠️  Detection error: {e}")
            return []
            
    def _calculate_face_distance(self, center1: Tuple[int, int], center2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two face centers"""
        dx = center1[0] - center2[0]
        dy = center1[1] - center2[1]
        return np.sqrt(dx*dx + dy*dy)
        
    def _track_and_lock_face(self, detected_faces: List[Dict]) -> Dict[str, any]:
        """
        Track faces and maintain lock on primary face
        
        Returns:
            Event dict with face tracking state
        """
        event = {
            'timestamp': time.time(),
            'faces_detected': len(detected_faces),
            'locked_face': None,
            'state': 'idle'
        }
        
        # No faces detected
        if len(detected_faces) == 0:
            self.frames_without_face += 1
            self.frames_with_face = 0
            
            # Check if we should unlock
            if self.locked_face_id is not None:
                if self.frames_without_face >= VISION_CONFIG['face_lost_timeout_frames']:
                    print(f"👋 Face lost for {self.frames_without_face} frames - unlocking")
                    self.locked_face_id = None
                    self.locked_face_bbox = None
                    self.locked_face_center = None
                    event['state'] = 'face_lost'
                else:
                    event['state'] = 'locked_tracking'
            else:
                event['state'] = 'idle'
                
            return event
            
        # Faces detected
        self.frames_with_face += 1
        self.frames_without_face = 0
        
        # If no face is locked, lock onto the largest (closest) face
        if self.locked_face_id is None:
            # Need consistent detection before locking
            if self.frames_with_face >= VISION_CONFIG['lock_threshold_frames']:
                largest_face = detected_faces[0]
                self.locked_face_id = time.time()  # Use timestamp as ID
                self.locked_face_bbox = largest_face['bbox']
                self.locked_face_center = largest_face['center']
                
                print(f"🔒 Locked onto new face (ID: {self.locked_face_id:.2f})")
                print(f"   Position: {self.locked_face_center}")
                print(f"   Confidence: {largest_face['confidence']:.2f}")
                
                event['state'] = 'face_locked'
                event['locked_face'] = {
                    'id': self.locked_face_id,
                    'bbox': self.locked_face_bbox,
                    'center': self.locked_face_center,
                    'confidence': largest_face['confidence']
                }
        else:
            # Track locked face
            # Find face closest to locked position
            min_distance = float('inf')
            closest_face = None
            
            for face in detected_faces:
                distance = self._calculate_face_distance(
                    self.locked_face_center,
                    face['center']
                )
                
                if distance < min_distance:
                    min_distance = distance
                    closest_face = face
                    
            # Update locked face position if within threshold
            if min_distance < VISION_CONFIG['tracking_distance_threshold']:
                self.locked_face_bbox = closest_face['bbox']
                self.locked_face_center = closest_face['center']
                
                event['state'] = 'locked_tracking'
                event['locked_face'] = {
                    'id': self.locked_face_id,
                    'bbox': self.locked_face_bbox,
                    'center': self.locked_face_center,
                    'confidence': closest_face['confidence']
                }
            else:
                # Locked face moved too far - likely left
                print(f"⚠️  Locked face moved too far (distance: {min_distance:.1f}px)")
                event['state'] = 'locked_tracking'
                
        return event
        
    def _show_preview(self, frame: np.ndarray, faces: List[Dict], state: str):
        """
        Show preview window with face detection boxes (works with VNC)
        
        Args:
            frame: Current camera frame
            faces: List of detected faces with bounding boxes
            state: Current vision state (idle, face_locked, etc.)
        """
        if not VISION_CONFIG.get('show_preview', False):
            return
        
        # Clone frame to draw on
        display_frame = frame.copy()
        
        # Draw faces
        if VISION_CONFIG.get('draw_boxes', True):
            for face in faces:
                bbox = face['bbox']
                x, y, w, h = bbox
                confidence = face['confidence']
                
                # Color: Green for locked face, Blue for others
                is_locked = (self.locked_face_id is not None and 
                            face.get('id') == self.locked_face_id)
                color = (0, 255, 0) if is_locked else (255, 0, 0)  # BGR
                thickness = 3 if is_locked else 2
                
                # Draw rectangle
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, thickness)
                
                # Draw label
                if VISION_CONFIG.get('draw_labels', True):
                    if is_locked:
                        label = f"LOCKED {confidence:.2f}"
                    else:
                        label = f"Face {confidence:.2f}"
                    
                    # Background for text
                    (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(display_frame, (x, y-25), (x+text_w+5, y), color, -1)
                    cv2.putText(display_frame, label, (x+3, y-8), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw status info at top
        status_text = f"State: {state} | Faces: {len(faces)} | FPS: {self.fps:.1f}"
        cv2.putText(display_frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Show in window
        window_name = VISION_CONFIG.get('preview_window_name', 'Pluto Vision')
        cv2.imshow(window_name, display_frame)
        cv2.waitKey(1)  # Required for window to update

    def _run(self):
        """Main vision worker loop"""
        print("🎥 Vision Worker running...")
        
        # Load detector
        if not self._load_detector():
            print("❌ Failed to initialize detector - Vision Worker disabled")
            self.running = False
            return
            
        # Start camera
        if not self._start_camera():
            print("❌ Failed to start camera - Vision Worker disabled")
            self.running = False
            return
            
        self.warmup_complete = True
        print("✅ Vision Worker warmup complete")
        
        # Main loop
        frame_count = 0
        start_time = time.time()
        frame_skip_counter = 0
        
        while self.running:
            try:
                loop_start = time.time()
                
                # Read frame
                frame = self._read_frame()
                if frame is None:
                    print("⚠️  Failed to read frame - restarting camera")
                    self._start_camera()
                    time.sleep(1)
                    continue
                    
                frame_count += 1
                
                # Skip frames for efficiency (process every Nth frame)
                frame_skip_counter += 1
                if frame_skip_counter < VISION_CONFIG['frame_skip']:
                    time.sleep(0.001)  # Small delay
                    continue
                    
                frame_skip_counter = 0
                
                # Detect faces
                detected_faces = self._detect_faces(frame)
                self.detection_count += 1
                
                # Track and lock faces
                event = self._track_and_lock_face(detected_faces)

                # Show preview window (VNC/GUI)
                self._show_preview(frame, detected_faces, event['state'])

                # Send event to orchestrator
                try:
                    self.output_queue.put_nowait(event)
                except queue.Full:
                    pass  # Skip if queue is full                # Calculate FPS
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    self.fps = 30 / elapsed if elapsed > 0 else 0
                    start_time = time.time()
                    
                # Sleep to maintain target frame rate
                elapsed = time.time() - loop_start
                target_delay = 1.0 / VISION_CONFIG['camera_fps']
                if elapsed < target_delay:
                    time.sleep(target_delay - elapsed)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Vision loop error: {e}")
                time.sleep(1)
                
        print("🛑 Vision Worker loop ended")
        
    def get_status(self) -> Dict:
        """Get worker status"""
        return {
            'name': 'Vision',
            'running': self.running,
            'warmup_complete': self.warmup_complete,
            'fps': self.fps,
            'detections': self.detection_count,
            'locked': self.locked_face_id is not None,
            'locked_face_id': self.locked_face_id,
            'frames_without_face': self.frames_without_face,
            'frames_with_face': self.frames_with_face
        }
