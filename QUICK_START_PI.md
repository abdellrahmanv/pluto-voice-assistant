# 🍓 Pluto Vision-Driven Reflex Agent - Raspberry Pi Quick Start

## Prerequisites
- **Raspberry Pi 4** (4GB RAM recommended) with 64-bit Raspberry Pi OS
- **Raspberry Pi Camera** (Camera Module v2 or compatible)
- **Microphone** and **speaker** connected
- Internet connection (for initial setup only)

## One-Command Installation

```bash
git clone https://github.com/abdellrahmanv/pluto-voice-assistant.git && cd pluto-voice-assistant && chmod +x setup_pi.sh && ./setup_pi.sh
```

## Step-by-Step Installation

### 1. Clone the Repository
```bash
git clone https://github.com/abdellrahmanv/pluto-voice-assistant.git
cd pluto-voice-assistant
```

### 2. Run the Setup Script
```bash
chmod +x setup_pi.sh
./setup_pi.sh
```

**This will automatically:**
- ✅ Install system dependencies (Python, PortAudio, espeak-ng, camera tools)
- ✅ Install camera support (rpicam-apps, libcamera-apps)
- ✅ Create Python virtual environment
- ✅ Install all Python packages (Whisper, OpenCV, PyAudio, etc.)
- ✅ Download YuNet face detection model (~2.5MB)
- ✅ Download and install Piper TTS (ARM64 version)
- ✅ Test camera connectivity

**Estimated time:** 15-20 minutes

### 3. Install Ollama (If Not Already Installed)

Open a **new terminal** and run:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Then download the Qwen model:

```bash
ollama pull qwen2.5:0.5b-instruct-q4_k_M
```

**Estimated time:** 3-5 minutes

### 4. Test Camera (Important!)

Before running Pluto, verify camera is working:

```bash
rpicam-hello --timeout 2000
```

**Expected:** 2-second camera preview window  
**If fails:** See troubleshooting section below

### 5. Run Pluto!

**Terminal 1** - Start Ollama:
```bash
ollama serve
```

**Terminal 2** - Start Pluto:
```bash
cd ~/pluto-voice-assistant
source .venv/bin/activate
python run.py
```

## Expected Output

```
╔═══════════════════════════════════════════════════════════════════╗
║                     🪐 PROJECT PLUTO 🪐                          ║
║           Vision-Driven Reflex Agent Voice Assistant             ║
╚═══════════════════════════════════════════════════════════════════╝

🪐 PROJECT PLUTO - Configuration Summary
======================================================================

📁 Paths:
  Project Root: /home/pi/pluto-voice-assistant
  Models Dir:   /home/pi/pluto-voice-assistant/models
  Logs Dir:     /home/pi/pluto-voice-assistant/logs

🎤 Audio:
  Sample Rate:  16000 Hz
  Channels:     1

🤖 Models:
  Vision: face_detection_yunet_2023mar_int8bq.onnx
  Whisper: tiny (39M params, ~1GB RAM, ~1s latency, good accuracy)
  Ollama: qwen2.5:0.5b-instruct-q4_k_M
  Piper:  /home/pi/pluto-voice-assistant/models/en_US-lessac-medium.onnx

======================================================================

[2025-10-15 12:00:00] [INFO] Starting workers...
[2025-10-15 12:00:01] [INFO] 👁️  Vision worker initializing...
[2025-10-15 12:00:02] [INFO] ✅ Vision Worker initialized (YuNet loaded)
[2025-10-15 12:00:03] [INFO] 🎤 STT worker initializing...
[2025-10-15 12:00:04] [INFO] ✅ STT Worker initialized (Whisper tiny)
[2025-10-15 12:00:05] [INFO] ⏸️  STT paused (waiting for face detection)
[2025-10-15 12:00:06] [INFO] 🧠 LLM worker ready
[2025-10-15 12:00:07] [INFO] 🔊 TTS worker ready
[2025-10-15 12:00:08] [INFO] 👁️  Waiting for someone to appear...
```

### When You Step Into View:

```
[2025-10-15 12:00:15] [INFO] 👁️  Face detected at (120, 95, 80, 80)
[2025-10-15 12:00:16] [INFO] 🔒 Face locked (ID: face_001)
[2025-10-15 12:00:16] [INFO] 🎉 Greeting: "Hi there! How can I help you today?"
[2025-10-15 12:00:17] [INFO] ▶️  STT resumed (listening for response)
[2025-10-15 12:00:20] [INFO] 🎤 You said: "What's the weather today?"
[2025-10-15 12:00:22] [INFO] 🧠 Thinking...
[2025-10-15 12:00:24] [INFO] 💬 Response: "I'm sorry, I don't have internet access..."
[2025-10-15 12:00:25] [INFO] 🔊 Playing audio...
```

## Troubleshooting

### "Camera not detected"
**Solution 1:** Check camera connection:
```bash
vcgencmd get_camera
# Expected: supported=1 detected=1
```

**Solution 2:** Enable camera in raspi-config:
```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable → Reboot
```

**Solution 3:** Test camera:
```bash
rpicam-hello --timeout 2000
# Should show 2-second preview
```

**For detailed camera troubleshooting, see VISION_SETUP.md**

### "YuNet model not found"
**Solution:** Manually download the model:
```bash
python download_yunet_model.py
# Expected location: models/face_detection_yunet_2023mar_int8bq.onnx
# Expected size: ~2.5MB
```

### "Vision worker fails but audio works"
**This is normal!** Pluto falls back to audio-only mode if camera isn't available.  
To intentionally disable vision, edit `src/config.py`:
```python
VISION_CONFIG = {
    "greeting_enabled": False,
    ...
}
```

### "Ollama connection refused"
**Solution:** Make sure Ollama is running in another terminal:
```bash
ollama serve
```

### "Microphone not found"
**Solution:** Check your microphone is connected:
```bash
arecord -l
```

### "Piper binary not found"
**Solution:** Re-run the Piper installation:
```bash
chmod +x install_piper_pi.sh
./install_piper_pi.sh
```

### "Whisper model downloading too slow"
**Solution:** The first run downloads the Whisper model (~39MB). Be patient, it only happens once.

## Performance on Raspberry Pi 4

- **Vision (YuNet):** 5-10 FPS, 60-120ms per frame, ~100MB RAM
- **STT (Whisper tiny):** 100-200ms per phrase, ~150MB RAM
- **LLM (Qwen 0.5B):** 500-1500ms per response, ~2GB RAM
- **TTS (Piper):** 200-500ms, ~200MB RAM
- **Total response time:** ~1-2 seconds from speech to audio
- **Peak memory usage:** ~3GB

### Vision Behavior
- **Face detection:** Continuous at 5-10 FPS (effective rate with frame skipping)
- **Face locking:** Requires 3 consecutive frames (~0.3s) to lock
- **Loss tolerance:** 15 frames (~1.5s) before unlocking
- **Greeting cooldown:** 10 seconds to prevent repeated greetings

## Running on Boot (Optional)

To make Pluto start automatically on boot, see `RASPBERRY_PI_DEPLOYMENT.md` for systemd service setup.

## Understanding the Reflex Agent

### State Machine Flow:
```
IDLE → FACE_DETECTED → LOCKED_IN → GREETING → LISTENING → PROCESSING → RESPONDING → FACE_LOST → IDLE
```

### Key Behaviors:
1. **Proactive Greeting**: Pluto initiates conversation when detecting a face
2. **Person Locking**: Ignores background faces once locked onto you
3. **Occlusion Tolerance**: Stays locked if you briefly move out of frame (< 1.5s)
4. **Auto Reset**: Returns to IDLE when you leave for > 1.5s

### Customizing Behavior:
Edit `src/config.py`:
```python
VISION_CONFIG = {
    "greeting_message": "Hello! How may I assist you?",  # Custom greeting
    "greeting_cooldown": 15.0,  # Seconds between greetings
    "confidence_threshold": 0.6,  # Face detection sensitivity (0.5-0.9)
    "lock_threshold_frames": 3,  # Frames to confirm face (reliability)
    "face_lost_timeout_frames": 15,  # Frames before unlocking (tolerance)
    ...
}
```

## Need Help?

Check the full documentation:
- `VISION_SETUP.md` - Comprehensive vision system guide (troubleshooting, tuning)
- `ARCHITECTURE.md` - System design and reflex agent architecture
- `QUICKSTART.md` - General quick start guide
- `README.md` - Project overview
- `HOW_TO_RUN.md` - Detailed runtime instructions

---

**Enjoy your vision-driven reflex agent! 👁️🤖🎉**
