#!/usr/bin/env python3
"""
Alternative: Save preview frames to image files instead of showing window
Use this if GUI doesn't work over SSH
"""

from pathlib import Path
import shutil

# Backup
worker_path = Path("src/workers/vision_worker.py")
backup_path = Path("src/workers/vision_worker.py.backup_headless")

if worker_path.exists() and not backup_path.exists():
    shutil.copy(worker_path, backup_path)
    print(f"✅ Backed up to: {backup_path}")

content = worker_path.read_text()

# Add headless preview (saves images instead of showing window)
headless_preview = '''
    def _save_preview_frame(self, frame: np.ndarray, faces: List[Tuple[int, int, int, int, float]]):
        """Save preview frame to file (headless mode)"""
        if not VISION_CONFIG.get('show_preview', False) or frame is None:
            return
        
        try:
            # Only save every 30 frames to avoid too many files
            if self.frame_count % 30 != 0:
                return
            
            preview_dir = Path("preview_frames")
            preview_dir.mkdir(exist_ok=True)
            
            display = frame.copy()
            
            # Draw faces
            for i, (x, y, w, h, conf) in enumerate(faces):
                if self.locked_face_id is not None and i == 0:
                    color = (0, 255, 0)
                    label = f"LOCKED ID:{self.locked_face_id} ({conf:.2f})"
                else:
                    color = (255, 128, 0)
                    label = f"DETECTED ({conf:.2f})"
                
                cv2.rectangle(display, (x, y), (x+w, y+h), color, 2)
                cv2.putText(display, label, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Status
            if self.locked_face_id is not None:
                status = f"STATE: LOCKED (ID: {self.locked_face_id})"
                color = (0, 255, 0)
            else:
                status = "STATE: SCANNING"
                color = (255, 128, 0)
            cv2.putText(display, status, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # FPS
            elapsed = time.time() - self.start_time if self.start_time else 0
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            cv2.putText(display, f"FPS: {fps:.1f}", (10, display.shape[0]-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            
            # Save
            filename = preview_dir / f"preview_{self.frame_count:06d}.jpg"
            cv2.imwrite(str(filename), display)
            
            # Keep only last 10 images
            images = sorted(preview_dir.glob("preview_*.jpg"))
            if len(images) > 10:
                for old_img in images[:-10]:
                    old_img.unlink()
            
            if self.frame_count == 30:
                self.logger.info(f"📸 Saving preview frames to: {preview_dir}/")
                self.logger.info(f"   View with: scp pi@raspberry:~/pluto/preview_frames/*.jpg .")
        
        except Exception as e:
            self.logger.error(f"Preview save error: {e}")
'''

# Find where to insert
if '_show_preview' in content:
    # Already has GUI preview, add headless option
    content = content.replace(
        'def _show_preview(self, frame',
        headless_preview + '\n    def _show_preview(self, frame'
    )
else:
    # Add headless preview
    content = content.replace(
        'def _process_detections(',
        headless_preview + '\n    def _process_detections('
    )

# Use headless preview in the loop
if 'self._show_preview(preview)' in content:
    content = content.replace(
        'self._show_preview(preview)',
        'self._save_preview_frame(frame, faces)  # Headless: saves to files'
    )
else:
    content = content.replace(
        '# Process\n                    self._process_detections(faces)',
        '''# Process
                    self._process_detections(faces)
                    
                    # Headless preview (saves frames to files)
                    if VISION_CONFIG.get('show_preview', False):
                        self._save_preview_frame(frame, faces)'''
    )

worker_path.write_text(content)

print("\n" + "="*70)
print("✅ HEADLESS PREVIEW MODE ENABLED")
print("="*70)
print("""
This mode saves preview frames to files instead of showing a window.
Perfect for SSH connections without X11 forwarding!

📸 How it works:
  • Saves 1 frame every 30 frames to preview_frames/
  • Keeps only the last 10 images
  • Shows detection boxes, labels, FPS, state

🚀 Run Pluto:
  python run.py

📁 View saved frames:
  # On your PC (from different terminal):
  scp pi@raspberry:~/pluto-voice-assistant/preview_frames/*.jpg .
  
  # Or check on Pi:
  ls -lh preview_frames/
  
  # Transfer to PC and view:
  # Windows: Use WinSCP or FileZilla
  # Linux/Mac: Use scp command above

💡 Files saved as:
  preview_frames/preview_000030.jpg
  preview_frames/preview_000060.jpg
  preview_frames/preview_000090.jpg
  ...

Each file shows what the vision system sees at that moment!
""")
print("="*70 + "\n")
