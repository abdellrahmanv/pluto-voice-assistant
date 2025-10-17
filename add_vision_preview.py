#!/usr/bin/env python3
"""
Add live preview window to vision_worker.py
This shows face detection in real-time with labels
"""

import shutil
from pathlib import Path

# Backup original
worker_path = Path("src/workers/vision_worker.py")
backup_path = worker_path.with_suffix(".py.backup2")

if worker_path.exists():
    shutil.copy(worker_path, backup_path)
    print(f"✅ Backed up original to: {backup_path}")

# Read current content
content = worker_path.read_text()

# Add preview-related imports after existing imports
preview_imports = """
# Preview window support (optional)
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
"""

# Find where to insert preview initialization
preview_init = """
        # Preview window
        self.show_preview = VISION_CONFIG.get('show_preview', False) and OPENCV_AVAILABLE
        self.preview_window = None
        if self.show_preview:
            self.logger.info("📺 Preview mode enabled")
"""

# Add preview display method
preview_method = '''
    
    def _draw_preview(self, frame: np.ndarray, faces: List[Tuple[int, int, int, int, float]]) -> np.ndarray:
        """Draw preview with face detection boxes and labels"""
        if not self.show_preview or frame is None:
            return frame
        
        display_frame = frame.copy()
        
        # Draw each detected face
        for i, (x, y, w, h, confidence) in enumerate(faces):
            # Determine color based on lock status
            if self.locked_face_id is not None and i == 0:
                color = (0, 255, 0)  # Green for locked face
                label_prefix = "🔒 LOCKED"
            else:
                color = (255, 128, 0)  # Orange for other faces
                label_prefix = "DETECTED"
            
            # Draw bounding box
            if VISION_CONFIG.get('draw_boxes', True):
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)
            
            # Draw label with ID and confidence
            if VISION_CONFIG.get('draw_labels', True):
                if self.locked_face_id is not None and i == 0:
                    label = f"{label_prefix} ID:{self.locked_face_id} ({confidence:.2f})"
                else:
                    label = f"{label_prefix} ({confidence:.2f})"
                
                # Calculate label position
                label_y = y - 10 if y > 30 else y + h + 20
                
                # Draw label background
                (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(display_frame, 
                            (x, label_y - label_h - 5), 
                            (x + label_w, label_y + 5), 
                            color, -1)
                
                # Draw label text
                cv2.putText(display_frame, label, (x, label_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw status overlay
        status_y = 30
        if self.locked_face_id is not None:
            status = f"STATE: LOCKED (Face ID: {self.locked_face_id})"
            color = (0, 255, 0)
        else:
            status = "STATE: SCANNING..."
            color = (255, 128, 0)
        
        cv2.putText(display_frame, status, (10, status_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw FPS counter
        if VISION_CONFIG.get('preview_fps_display', True):
            elapsed = time.time() - self.start_time if self.start_time else 0
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            fps_text = f"FPS: {fps:.1f}"
            cv2.putText(display_frame, fps_text, (10, display_frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw greeting status
        if hasattr(self, 'last_greeting_time') and self.last_greeting_time > 0:
            time_since = time.time() - self.last_greeting_time
            cooldown = VISION_CONFIG.get('greeting_cooldown', 10.0)
            if time_since < cooldown:
                greeting_text = f"GREETED: {time_since:.1f}s ago (cooldown: {cooldown:.0f}s)"
                cv2.putText(display_frame, greeting_text, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        return display_frame
    
    def _show_preview(self, frame: np.ndarray):
        """Display preview window"""
        if not self.show_preview or frame is None:
            return
        
        try:
            window_name = VISION_CONFIG.get('preview_window_name', 'Pluto Vision')
            
            # Create window if first time
            if self.preview_window is None:
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(window_name, 640, 480)
                self.preview_window = window_name
            
            # Display frame
            cv2.imshow(window_name, frame)
            cv2.waitKey(1)  # Process window events
            
        except Exception as e:
            self.logger.error(f"Preview error: {e}")
            self.show_preview = False
    
    def _close_preview(self):
        """Close preview window"""
        if self.preview_window:
            try:
                cv2.destroyWindow(self.preview_window)
                self.preview_window = None
            except:
                pass
'''

# Insert into the file
lines = content.split('\n')
new_lines = []
imports_done = False
init_done = False
run_method_found = False

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Add preview imports after other imports
    if not imports_done and 'from config import' in line:
        new_lines.append('')
        new_lines.append(preview_imports)
        imports_done = True
    
    # Add preview init in __init__
    if not init_done and 'self.logger.info("Vision Worker initialized")' in line:
        new_lines.append('')
        for preview_line in preview_init.strip().split('\n'):
            new_lines.append(preview_line)
        init_done = True
    
    # Add preview methods before _run method
    if not run_method_found and 'def _run(self):' in line:
        for preview_line in preview_method.split('\n'):
            new_lines.append(preview_line)
        new_lines.append('')
        run_method_found = True

# Now modify the _run method to use preview
final_content = '\n'.join(new_lines)

# Add preview display calls in the _run loop
final_content = final_content.replace(
    '# Detect faces\n                    faces = self._detect_faces(frame)',
    '''# Detect faces
                    faces = self._detect_faces(frame)
                    
                    # Draw and show preview
                    if self.show_preview:
                        preview_frame = self._draw_preview(frame, faces)
                        self._show_preview(preview_frame)'''
)

# Add preview cleanup in stop method
final_content = final_content.replace(
    'self.logger.info("Vision Worker stopped")',
    '''self._close_preview()
            self.logger.info("Vision Worker stopped")'''
)

# Write updated content
worker_path.write_text(final_content)

print("\n" + "="*70)
print("✅ Vision Worker Updated with Live Preview!")
print("="*70)
print("\n📺 New Features Added:")
print("  • Live camera preview window")
print("  • Face detection bounding boxes (green=locked, orange=detected)")
print("  • Face ID and confidence labels")
print("  • State indicator (SCANNING/LOCKED)")
print("  • FPS counter")
print("  • Greeting cooldown timer")
print("\n⚙️  Configuration (in src/config.py):")
print("  VISION_CONFIG['show_preview'] = True   # Enable/disable")
print("  VISION_CONFIG['draw_boxes'] = True     # Show bounding boxes")
print("  VISION_CONFIG['draw_labels'] = True    # Show labels")
print("\n🚀 Run with:")
print("  python run.py")
print("\nA window titled 'Pluto Vision - Face Detection' will appear showing:")
print("  🟢 Green box = Locked face (currently talking to)")
print("  🟠 Orange box = Detected face (not locked)")
print("  📊 FPS counter bottom-left")
print("  ⏱️  Greeting cooldown status")
print("\n" + "="*70 + "\n")
