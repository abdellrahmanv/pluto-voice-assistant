# 👁️ Vision System Setup Guide

## Overview

Pluto's vision system enables **reflex agent behavior** - the assistant detects faces, locks onto people, initiates conversations, and stays focused during interactions.

**Key Features:**
- 🎯 **Face detection** using YuNet ONNX model (INT8 quantized)
- 🔒 **Face locking** - locks onto one person, ignores others
- 💬 **Auto-greeting** - initiates conversation when detecting new faces
- 🎬 **Vision-driven interaction** - only listens when face is present
- 📷 **Raspberry Pi camera** integration via `rpicam-vid`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PLUTO ORCHESTRATOR                       │
│                  (Reflex Agent Controller)                  │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┼────────┬─────────┬─────────┐
    │        │        │         │         │
┌───▼───┐ ┌─▼──┐  ┌──▼──┐  ┌───▼────┐ ┌──▼───┐
│Vision │ │STT │  │ LLM │  │  TTS   │ │Metrics│
│Worker │ │    │  │     │  │        │ │Logger │
└───┬───┘ └────┘  └─────┘  └────────┘ └───────┘
    │
    │ Face Detection Events
    ▼
Agent State Machine:
  IDLE → FACE_DETECTED → LOCKED_IN → GREETING → LISTENING
```

---

## 📦 Components

### 1. YuNet Face Detector
- **Model**: `face_detection_yunet_2023mar_int8bq.onnx`
- **Size**: ~2.5 MB
- **Quantization**: INT8 block-quantized for efficiency
- **Backend**: OpenCV DNN (CPU)
- **Performance**: ~60-120ms per frame on Raspberry Pi 4

### 2. Vision Worker
- **File**: `src/workers/vision_worker.py`
- **Function**: Captures frames, detects faces, tracks people
- **Output**: Face detection events to orchestrator

### 3. Agent State Manager
- **File**: `src/agent_state.py`
- **Function**: Manages conversation states and transitions
- **States**: `IDLE`, `FACE_DETECTED`, `LOCKED_IN`, `GREETING`, `LISTENING`, `PROCESSING`, `RESPONDING`, `FACE_LOST`

---

## 🛠️ Installation

### Automatic (Recommended)

Run the setup script on Raspberry Pi:

```bash
chmod +x setup_pi.sh
./setup_pi.sh
```

This will:
- ✅ Install `rpicam-apps` for camera access
- ✅ Install OpenCV and dependencies
- ✅ Download YuNet model
- ✅ Test camera availability

### Manual Installation

If automatic setup fails:

#### 1. Install Camera Tools

```bash
sudo apt-get update
sudo apt-get install -y rpicam-apps libcamera-apps libcamera-dev
```

#### 2. Install OpenCV

```bash
# System package (faster)
sudo apt-get install -y python3-opencv libopencv-dev

# OR via pip (more recent)
pip install opencv-python>=4.8.0
```

#### 3. Download YuNet Model

```bash
python download_yunet_model.py
```

This downloads the model to `models/face_detection_yunet_2023mar_int8bq.onnx`.

#### 4. Test Camera

```bash
# Test camera with 2-second preview
rpicam-hello --timeout 2000

# Test video streaming
rpicam-vid --width 640 --height 480 --timeout 5000 --output test.h264
```

---

## ⚙️ Configuration

Edit `src/config.py` to customize vision settings:

```python
VISION_CONFIG = {
    # Camera settings
    "frame_width": 320,           # Resolution (320x240 recommended)
    "frame_height": 240,
    "camera_fps": 10,             # Target FPS (10 recommended for efficiency)
    "frame_skip": 2,              # Process every Nth frame
    
    # Detection settings
    "confidence_threshold": 0.6,  # Min confidence (0.5-0.8 recommended)
    "nms_threshold": 0.3,         # Non-maximum suppression
    "max_faces": 5,               # Max faces to detect
    
    # Tracking settings
    "lock_threshold_frames": 3,   # Frames before locking (stability)
    "face_lost_timeout_frames": 15,  # Frames before unlocking (1.5s @ 10fps)
    "tracking_distance_threshold": 100,  # Max pixel distance for tracking
    
    # Greeting behavior
    "greeting_enabled": True,
    "greeting_cooldown": 10.0,    # Seconds between greetings
    "greeting_message": "Hi there! How can I help you today?",
    
    # Performance
    "num_threads": 2,             # OpenCV threads (1-2 recommended)
    "priority": 10,               # Process nice value
}
```

### Key Parameters Explained

| Parameter | Description | Recommended Value |
|-----------|-------------|-------------------|
| `frame_width` x `frame_height` | Camera resolution | 320x240 (balance speed/accuracy) |
| `camera_fps` | Target frames per second | 10 (low for efficiency) |
| `frame_skip` | Process every Nth frame | 2 (5fps effective) |
| `confidence_threshold` | Min face confidence | 0.6 (reduce false positives) |
| `lock_threshold_frames` | Frames to confirm face | 3 (0.3s stability check) |
| `face_lost_timeout_frames` | Frames before unlock | 15 (1.5s tolerance) |
| `tracking_distance_threshold` | Max movement distance | 100px (track moving faces) |

---

## 🚀 Usage

### Starting Pluto with Vision

```bash
source .venv/bin/activate
python run.py
```

Expected output:
```
═══════════════════════════════════════════════════════════════
            🪐 PROJECT PLUTO 🪐                          
      Vision-Driven Reflex Agent Voice Assistant               
                                                                   
  Pipeline: Vision → STT → LLM → TTS                              
  Behavior: Detects faces, initiates conversation, stays focused  
═══════════════════════════════════════════════════════════════

🎥 Vision Worker initialized
📦 Loading YuNet model from: models/face_detection_yunet_2023mar_int8bq.onnx
✅ YuNet model loaded successfully
📷 Starting Raspberry Pi camera...
✅ Camera started
✅ Vision Worker warmup complete

👁️  PLUTO IS READY - Looking for people to talk to!
   Press Ctrl+C to stop
```

### Interaction Flow

1. **Idle State**: Vision worker scans for faces
2. **Face Detected**: Locks onto closest person
3. **Greeting**: "Hi there! How can I help you today?"
4. **Listening**: STT activates, waiting for response
5. **Conversation**: Normal STT → LLM → TTS loop
6. **Face Lost**: If person leaves, system resets to Idle

---

## 🐛 Troubleshooting

### Camera Not Found

**Symptom**: `rpicam-vid not found` or camera fails to start

**Solution**:
```bash
# Install rpicam-apps
sudo apt-get install rpicam-apps

# Test camera
rpicam-hello --timeout 2000

# Check camera is enabled
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

### Model Not Found

**Symptom**: `YuNet model not found at: models/face_detection...`

**Solution**:
```bash
# Download model manually
python download_yunet_model.py

# Verify file exists
ls -lh models/face_detection_yunet_2023mar_int8bq.onnx
```

### Low FPS / Performance Issues

**Symptoms**: Vision FPS < 5, laggy detection

**Solutions**:

1. **Reduce resolution**:
   ```python
   "frame_width": 320,  # Try 240 or 160
   "frame_height": 240,  # Try 180 or 120
   ```

2. **Increase frame skip**:
   ```python
   "frame_skip": 3,  # Process every 3rd frame (3.3fps effective)
   ```

3. **Reduce threads**:
   ```python
   "num_threads": 1,  # Single thread for face detection
   ```

4. **Lower camera FPS**:
   ```python
   "camera_fps": 5,  # Reduce to 5fps
   ```

### False Positives (Detecting Non-Faces)

**Symptom**: Locks onto objects, shadows, or patterns

**Solution**:
```python
# Increase confidence threshold
"confidence_threshold": 0.7,  # Higher = stricter (default: 0.6)

# Reduce max faces
"max_faces": 3,  # Focus on most prominent faces
```

### Face Unlocking Too Quickly

**Symptom**: Loses lock when person turns head slightly

**Solution**:
```python
# Increase timeout
"face_lost_timeout_frames": 25,  # 2.5s @ 10fps (default: 15)

# Increase tracking distance
"tracking_distance_threshold": 150,  # Allow more movement (default: 100)
```

### Repeated Greetings

**Symptom**: Greets same person multiple times

**Solution**:
```python
# Increase cooldown
"greeting_cooldown": 30.0,  # 30 seconds between greetings (default: 10)
```

### OpenCV Import Error

**Symptom**: `ModuleNotFoundError: No module named 'cv2'`

**Solution**:
```bash
# Activate virtual environment
source .venv/bin/activate

# Install OpenCV
pip install opencv-python>=4.8.0

# OR use system package
sudo apt-get install python3-opencv
```

---

## 📊 Performance Metrics

Vision metrics are logged automatically:

### Console Output
```
👁️  Vision FPS: Mean: 8.5 | Min: 7.2 | Max: 10.1
```

### CSV Log (`logs/metrics_YYYYMMDD_HHMMSS.csv`)
```csv
timestamp,component,metric_type,value,unit
1697567890.123,vision,fps,8.5,fps
1697567890.123,vision,faces_detected,1,count
1697567890.123,vision,face_locked,1,bool
```

### Metrics Tracked
- **FPS**: Frames processed per second
- **Faces Detected**: Number of faces per frame
- **Face Locked**: Boolean (0/1) if locked onto person
- **Events**: `face_locked`, `face_lost`, `greeting_sent`

---

## 🔧 Advanced Configuration

### Disable Vision (Audio-Only Mode)

In `src/orchestrator.py`:
```python
orchestrator = PlutoOrchestrator(enable_vision=False)
```

Or modify `run.py` to pass parameter.

### Custom Greeting Message

In `src/config.py`:
```python
"greeting_message": "Hello! I'm Pluto, your voice assistant. What can I do for you?",
```

### CPU Affinity (Performance Tuning)

Pin vision worker to specific CPU cores:
```python
"cpu_affinity": [0, 1],  # Use cores 0-1 for vision
```

Apply in code:
```python
import os
os.sched_setaffinity(0, VISION_CONFIG["cpu_affinity"])
```

---

## 🧪 Testing Vision System

### Test Face Detection Only

Create `test_vision.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import queue
from workers.vision_worker import VisionWorker

# Create worker
output_queue = queue.Queue()
worker = VisionWorker(output_queue)

# Start worker
worker.start()

# Monitor events
try:
    while True:
        event = output_queue.get(timeout=1)
        print(f"Event: {event}")
except KeyboardInterrupt:
    worker.stop()
```

Run:
```bash
python test_vision.py
```

### Expected Output

When face detected:
```
🔒 Locked onto new face (ID: 1697567890.45)
   Position: (160, 120)
   Confidence: 0.87
```

When face lost:
```
👋 Face lost for 15 frames - unlocking
```

---

## 📚 Additional Resources

- **YuNet Paper**: [YuNet: A Tiny Millisecond-level Face Detector](https://arxiv.org/abs/2202.02534)
- **OpenCV Zoo**: [github.com/opencv/opencv_zoo](https://github.com/opencv/opencv_zoo)
- **Raspberry Pi Camera Docs**: [rpicam-apps documentation](https://www.raspberrypi.com/documentation/computers/camera_software.html)

---

## ❓ FAQ

**Q: Can I use a USB webcam instead of Pi camera?**  
A: Yes! Modify `vision_worker.py` to use OpenCV's `cv2.VideoCapture(0)` instead of `rpicam-vid`.

**Q: Does it work with multiple people?**  
A: It detects multiple faces but **locks onto only one person** (closest/largest face). Others are ignored until that person leaves.

**Q: What's the detection range?**  
A: Faces 40-300 pixels (roughly 0.5m - 5m from camera at 320x240 resolution).

**Q: Can it recognize specific people?**  
A: No - YuNet only detects faces, not identity. For recognition, you'd need to add a face recognition model.

**Q: How much CPU does it use?**  
A: ~15-20% of one CPU core on Raspberry Pi 4 at 320x240@5fps (effective).

---

**Need help?** Check the main [DOCUMENTATION.md](DOCUMENTATION.md) or open an issue on GitHub.
