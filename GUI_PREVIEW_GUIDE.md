# 📹 GUI Preview Window - Setup Guide

## What's New

You now have a **visual preview window** that shows:
- 📹 Live camera feed
- 🟦 Blue boxes around detected faces
- 🟩 **Green box** around the LOCKED face (the person Pluto is talking to)
- 📊 Status bar: State, Face count, FPS
- 🏷️ Labels: "LOCKED 0.95" or "Face 0.87" (confidence scores)

---

## Requirements

✅ You're using **VNC** (remote desktop) - Perfect!  
✅ Config already enabled: `show_preview: True`  
✅ Code just pushed to GitHub

---

## How to Use

### On Raspberry Pi (via VNC):

```bash
# 1. Pull latest code
cd ~/pluto-voice-assistant
git pull

# 2. Run the system
python run.py

# 3. A window will pop up showing:
#    - Camera view
#    - Face detection boxes
#    - Which face is locked (green box)
#    - FPS and state info
```

---

## What You'll See

```
┌─────────────────────────────────────────┐
│ State: face_locked | Faces: 1 | FPS: 5.2│ ← Status bar
│                                         │
│                                         │
│        ┌──────────────┐                │
│        │ LOCKED 0.95  │  ← Green label │
│        └──────────────┘                │
│        ┏━━━━━━━━━━━━━━┓                │
│        ┃              ┃  ← Green box   │
│        ┃   👤 Face   ┃     (locked)   │
│        ┃              ┃                │
│        ┗━━━━━━━━━━━━━━┛                │
│                                         │
│  Pluto Vision - Face Detection          │
└─────────────────────────────────────────┘
```

### Color Coding:
- 🟦 **Blue box** = Face detected (not locked yet)
- 🟩 **Green box** = LOCKED face (Pluto is focused on this person)
- 🟩 **Thick green** = Currently talking to this person

---

## Configuration

In `src/config.py`, you can adjust:

```python
VISION_CONFIG = {
    # ...
    "show_preview": True,           # Enable/disable window
    "preview_window_name": "Pluto Vision - Face Detection",
    "draw_boxes": True,            # Show bounding boxes
    "draw_labels": True,           # Show confidence scores
}
```

---

## Troubleshooting

### Window doesn't appear?
```bash
# Check if preview is enabled
grep "show_preview" src/config.py

# Should show: "show_preview": True
```

### Window appears but freezes?
- VNC connection might be slow
- Try reducing resolution in config:
  ```python
  "frame_width": 320,   # Lower = faster
  "frame_height": 240,
  ```

### Can't see the window in SSH?
- You **must** use VNC (remote desktop)
- SSH terminal won't show GUI windows
- Alternative: Use the ASCII preview (terminal art)

---

## What the Window Shows

1. **Top left**: Status information
   - Current state (idle, face_locked, locked_tracking)
   - Number of faces detected
   - Current FPS

2. **Blue boxes**: Any face detected in frame
3. **Green box**: The face Pluto has locked onto
4. **Labels**: Confidence score (0.0 to 1.0)
   - 0.60 = minimum to detect
   - 0.90+ = very confident

---

## Performance Impact

- **Minimal**: Drawing boxes adds ~5-10ms per frame
- **FPS**: Should still maintain 4-5 fps
- **CPU**: +2-3% for display operations

If performance is slow:
1. Set `show_preview: False` in config
2. Reduce camera resolution
3. Increase `frame_skip` value

---

## Quick Test

```bash
# After git pull:
python run.py

# Look for:
# - "🎥 Vision Worker running..."
# - A window pops up showing camera
# - Stand in front of camera
# - Blue box appears around your face
# - After ~1 second, box turns GREEN (locked)
# - Status shows "State: face_locked"
```

---

**Pushed to GitHub**: Commit `f971c03`  
**Ready to use**: Just `git pull` and run!

🎉 Enjoy your visual feedback!
