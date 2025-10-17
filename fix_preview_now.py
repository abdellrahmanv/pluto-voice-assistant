#!/usr/bin/env python3
"""
Direct patch to add preview functionality to vision_worker.py
This will ADD the preview methods without replacing the whole file
"""

from pathlib import Path
import re

worker_path = Path("src/workers/vision_worker.py")

if not worker_path.exists():
    print(f"❌ ERROR: {worker_path} not found!")
    exit(1)

content = worker_path.read_text()

# Check if already has preview
if '_show_preview' in content:
    print("✅ Preview code already exists in vision_worker.py")
    exit(0)

print("🔧 Adding preview functionality to vision_worker.py...")

# 1. Add preview initialization in __init__
init_addition = """
        # Preview window
        self.preview_window = None
        if VISION_CONFIG.get('show_preview', False):
            self.preview_window = VISION_CONFIG.get('preview_window_name', 'Pluto Vision')
            self.logger.info(f"📺 Preview window enabled: {self.preview_window}")
"""

# Find the __init__ method and add after logger initialization
content = re.sub(
    r'(self\.logger = logging\.getLogger\(__name__\))',
    r'\1' + init_addition,
    content
)

# 2. Add preview methods before the _run method
preview_methods = '''
    def _draw_preview(self, frame: np.ndarray, faces: List[Tuple[int, int, int, int, float]]) -> np.ndarray:
        """Draw detection boxes and info on frame"""
        if frame is None:
            return None
        
        display = frame.copy()
        
        # Draw face boxes
        for i, (x, y, w, h, conf) in enumerate(faces):
            # Green for locked face, orange for detected faces
            if self.locked_face_id is not None and i == 0:
                color = (0, 255, 0)  # Green
                label = f"LOCKED ID:{self.locked_face_id} ({conf:.2f})"
            else:
                color = (0, 165, 255)  # Orange
                label = f"DETECTED ({conf:.2f})"
            
            cv2.rectangle(display, (x, y), (x+w, y+h), color, 2)
            cv2.putText(display, label, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Status info
        if self.locked_face_id is not None:
            status = f"STATE: LOCKED (ID: {self.locked_face_id})"
            color = (0, 255, 0)
        else:
            status = "STATE: SCANNING"
            color = (0, 165, 255)
        
        cv2.putText(display, status, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # FPS counter
        if VISION_CONFIG.get('preview_fps_display', True):
            elapsed = time.time() - self.start_time if self.start_time else 0
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            cv2.putText(display, f"FPS: {fps:.1f}", (10, display.shape[0]-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return display
    
    def _show_preview(self, frame: np.ndarray, faces: List[Tuple[int, int, int, int, float]]):
        """Display preview window with detections"""
        if not VISION_CONFIG.get('show_preview', False) or frame is None:
            return
        
        try:
            display = self._draw_preview(frame, faces)
            if display is not None:
                cv2.imshow(self.preview_window, display)
                cv2.waitKey(1)  # Process window events
        except Exception as e:
            self.logger.error(f"Preview display error: {e}")
    
    def _close_preview(self):
        """Close preview window"""
        if self.preview_window:
            try:
                cv2.destroyWindow(self.preview_window)
                self.logger.info("📺 Preview window closed")
            except:
                pass
'''

# Insert preview methods before _run method
content = re.sub(
    r'(\n    def _run\(self\):)',
    preview_methods + r'\1',
    content
)

# 3. Add preview call in the main loop (after face detection)
# Find the line where faces are processed
if 'self._process_detections(faces)' in content:
    content = content.replace(
        'self._process_detections(faces)',
        '''self._process_detections(faces)
                    
                    # Show preview window
                    self._show_preview(frame, faces)'''
    )

# 4. Add preview cleanup in stop method
content = re.sub(
    r'(def stop\(self\):.*?)(if self\.camera_process:)',
    r'\1self._close_preview()\n        \2',
    content,
    flags=re.DOTALL
)

# Write the updated file
worker_path.write_text(content)

print("\n" + "="*70)
print("✅ PREVIEW FUNCTIONALITY ADDED TO vision_worker.py")
print("="*70)
print("""
Changes made:
✅ Added preview window initialization in __init__
✅ Added _draw_preview() method - draws boxes and labels
✅ Added _show_preview() method - displays the window
✅ Added _close_preview() method - cleanup
✅ Integrated preview display in main detection loop
✅ Added cleanup call in stop() method

🚀 Now run Pluto:
   python run.py

📺 A window will open showing:
   • Green boxes around locked faces
   • Orange boxes around detected faces
   • Face ID and confidence labels
   • Current state (SCANNING/LOCKED)
   • FPS counter

Press Ctrl+C to stop (window will close automatically)
""")
print("="*70 + "\n")
