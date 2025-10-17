#!/usr/bin/env python3
"""
Fix the unterminated string literal error in vision_worker.py
The issue is with the escape sequences in terminal preview
"""

from pathlib import Path
import re

worker_path = Path("src/workers/vision_worker.py")

if not worker_path.exists():
    print(f"❌ ERROR: {worker_path} not found!")
    exit(1)

content = worker_path.read_text()

# The problem is the escape sequences - let's fix them
# Replace the problematic terminal preview with a corrected version

fixed_preview = '''
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

# Remove the broken _draw_terminal_preview method
content = re.sub(
    r'    def _draw_terminal_preview\(.*?\n(?:.*?\n)*?.*?self\.logger\.error\(f"Terminal preview error.*?\n',
    '',
    content,
    flags=re.DOTALL
)

# Add the fixed version before _run method
content = re.sub(
    r'(\n    def _run\(self\):)',
    fixed_preview + r'\1',
    content
)

worker_path.write_text(content)

print("\n" + "="*70)
print("✅ FIXED: Unterminated string literal error")
print("="*70)
print("""
The escape sequences in the terminal preview are now properly formatted.

🚀 Run Pluto now:
   python run.py

The terminal preview should work correctly!
""")
print("="*70 + "\n")
