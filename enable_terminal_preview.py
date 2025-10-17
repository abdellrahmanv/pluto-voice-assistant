#!/usr/bin/env python3
"""
Terminal-based preview for SSH - Shows camera feed as ASCII art in terminal
Works perfectly over SSH connections!
"""

from pathlib import Path
import shutil

worker_path = Path("src/workers/vision_worker.py")
backup_path = Path("src/workers/vision_worker.py.backup_terminal")

if worker_path.exists() and not backup_path.exists():
    shutil.copy(worker_path, backup_path)
    print(f"✅ Backed up to: {backup_path}")

content = worker_path.read_text()

# Remove any existing preview code
content = content.replace('self._show_preview(frame, faces)', '')
content = content.replace('self._close_preview()', '')

# Add terminal preview methods
terminal_preview = '''
    def _draw_terminal_preview(self, frame: np.ndarray, faces: List[Tuple[int, int, int, int, float]]):
        """Display camera preview in terminal (works over SSH!)"""
        if not VISION_CONFIG.get('show_preview', False) or frame is None:
            return
        
        try:
            # Resize for terminal (smaller for better display)
            h, w = frame.shape[:2]
            term_w = 80  # Terminal width
            term_h = int(h * term_w / w / 2)  # Adjust for character aspect ratio
            
            small = cv2.resize(frame, (term_w, term_h))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            
            # ASCII characters from dark to light
            chars = " .:-=+*#%@"
            
            # Clear terminal and move cursor to top
            print("\\033[2J\\033[H", end='')
            
            # Build ASCII art
            output = []
            output.append("="*80)
            output.append("📹 PLUTO VISION PREVIEW (Live Camera Feed)")
            output.append("="*80)
            
            # Draw ASCII frame
            for y in range(term_h):
                row = ""
                for x in range(term_w):
                    pixel = gray[y, x]
                    char_idx = int(pixel / 255 * (len(chars) - 1))
                    row += chars[char_idx]
                output.append(row)
            
            output.append("-"*80)
            
            # Face detection info
            if faces:
                if self.locked_face_id is not None:
                    output.append(f"🟢 LOCKED ON FACE ID: {self.locked_face_id}")
                    for i, (x, y, w, h, conf) in enumerate(faces):
                        if i == 0:
                            output.append(f"   └─ Tracking: {w}x{h}px @ ({x},{y}) confidence: {conf:.2f}")
                else:
                    output.append(f"🟠 DETECTED {len(faces)} FACE(S):")
                    for i, (x, y, w, h, conf) in enumerate(faces):
                        output.append(f"   {i+1}. Position: ({x},{y}) Size: {w}x{h}px Conf: {conf:.2f}")
            else:
                output.append("⚪ SCANNING - No faces detected")
            
            # FPS
            elapsed = time.time() - self.start_time if self.start_time else 0
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            output.append(f"📊 FPS: {fps:.1f} | Frames: {self.frame_count}")
            output.append("="*80)
            output.append("Press Ctrl+C to stop")
            
            print("\\n".join(output), flush=True)
            
        except Exception as e:
            self.logger.error(f"Terminal preview error: {e}")
'''

# Find where to insert (before _run method)
import re
content = re.sub(
    r'(\n    def _run\(self\):)',
    terminal_preview + r'\1',
    content
)

# Add terminal preview call in the detection loop
if 'self._process_detections(faces)' in content:
    content = content.replace(
        'self._process_detections(faces)',
        '''self._process_detections(faces)
                    
                    # Terminal preview (works over SSH!)
                    self._draw_terminal_preview(frame, faces)'''
    )

# Remove GUI preview initialization if exists
content = re.sub(
    r'self\.preview_window = .*?\n.*?self\.logger\.info\(f"📺.*?\n',
    '',
    content
)

worker_path.write_text(content)

print("\n" + "="*70)
print("✅ TERMINAL PREVIEW ENABLED (SSH Compatible!)")
print("="*70)
print("""
🎯 What you'll see in your SSH terminal:

   ================================
   📹 PLUTO VISION PREVIEW
   ================================
   [ASCII art of camera feed here]
   --------------------------------
   🟢 LOCKED ON FACE ID: 12345
      └─ Tracking: 120x140px @ (100,80) confidence: 0.98
   📊 FPS: 5.2 | Frames: 156
   ================================
   Press Ctrl+C to stop

🚀 Run Pluto now:
   python run.py

📺 The camera feed will display as ASCII art directly in your SSH terminal!
   • Face detection boxes shown as text coordinates
   • Lock status displayed in real-time
   • FPS and frame count
   • All in the same terminal window!

No GUI needed - works perfectly over SSH! 🎉
""")
print("="*70 + "\n")
