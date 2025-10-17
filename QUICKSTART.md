# 🚀 Project Pluto - Quick Start Guide

Get your vision-driven reflex agent running in under 10 minutes!

## ⚡ Prerequisites

- **Raspberry Pi 4** (4GB RAM recommended)
- **Raspberry Pi Camera** (libcamera-compatible)
- **Python 3.8+** installed
- **Ollama** installed and running
- **Piper TTS** installed
- **Microphone** and **speakers** connected

## 📦 1. Install Dependencies (Raspberry Pi)

```bash
# Navigate to project directory
cd ~/pluto

# Run automated setup script (installs camera drivers, Python packages, models)
chmod +x setup_pi.sh
./setup_pi.sh

# This script installs:
# - rpicam-apps (camera support)
# - libcamera-apps
# - OpenCV with camera backends
# - Python dependencies
# - YuNet face detection model
# - Whisper tiny model
# - Piper TTS
```

**Manual Setup (if needed):**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

## 🤖 2. Download Models

### YuNet Face Detection (~2.5MB)
```bash
# Auto-downloaded by setup_pi.sh, or manually:
python download_yunet_model.py
# Downloads to: models/face_detection_yunet_2023mar_int8bq.onnx
```

### Whisper STT (~39MB)
```bash
# Auto-downloaded on first run, or manually:
python -c "import whisper; whisper.load_model('tiny')"
```

### Piper TTS Model
```bash
# Download from: https://github.com/rhasspy/piper/releases
# Example: en_US-lessac-medium.onnx + en_US-lessac-medium.onnx.json

# Place both files in models/ directory
```

### Qwen2.5 LLM Model (~310MB)
```bash
# Pull model with Ollama
ollama pull qwen2.5:0.5b-instruct-q4_k_M
```

## 🎯 3. Test Camera

```bash
# Test camera before starting Pluto
rpicam-hello --timeout 2000

# You should see a 2-second camera preview
# If this fails, troubleshoot camera connection first
```

## ⚙️ 4. Configure Settings (Optional)

Edit `src/config.py` for customization:

```python
VISION_CONFIG = {
    "greeting_message": "Hi there! How can I help you today?",  # Customize greeting
    "greeting_enabled": True,  # Set False to disable auto-greeting
    "confidence_threshold": 0.6,  # Face detection sensitivity
    ...
}

PIPER_CONFIG = {
    "model_path": "./models/en_US-lessac-medium.onnx",  # Your Piper model
    ...
}
```

## 🎙️ 5. Start Ollama Server

```bash
# Start Ollama in separate terminal
ollama serve
```

## 🪐 6. Run Pluto!

```bash
# Start the assistant
python run.py
```

You should see:
```
╔═══════════════════════════════════════════════════════════════════╗
║                     🪐 PROJECT PLUTO 🪐                          ║
║           Vision-Driven Reflex Agent Voice Assistant             ║
╚═══════════════════════════════════════════════════════════════════╝

👁️  Vision Worker initializing...
✅ Vision Worker initialized (YuNet loaded)
🎤 STT Worker initializing...
✅ STT Worker initialized (Whisper tiny)
⏸️  STT paused (waiting for face detection)
🧠 LLM Worker initializing...
✅ LLM Worker initialized (Qwen2.5:0.5b)
🔊 TTS Worker initializing...
✅ TTS Worker initialized (Piper)

👁️  Waiting for someone to appear...
```

**When you step in front of the camera:**
```
👁️  Face detected! Locking onto person...
🔒 Face locked (ID: face_001)
🎉 Greeting: "Hi there! How can I help you today?"
▶️  STT resumed (listening for response)
```

## 🗣️ 7. Interact with Pluto

1. **Step into view** of the camera (Pluto detects your face)
2. **Wait for greeting** - Pluto automatically says hello
3. **Speak** your question or request into the microphone
4. **Wait** for Pluto's audio response
5. **Continue conversation** naturally
6. **Step away** when done - Pluto resets to IDLE and waits for next person

### 🔒 Face Locking Behavior
- Once locked onto you, Pluto **ignores other faces** in the background
- If you briefly move out of frame (< 1.5s), Pluto **stays locked** (handles occlusions)
- If you leave for > 1.5s, Pluto **unlocks** and returns to waiting mode
- Greeting cooldown prevents repeated "Hi there!" if you re-enter quickly (10 seconds)

## ⏹️ 8. Stop Pluto

Press `Ctrl+C` to gracefully shutdown:
```
📊 PLUTO SESSION SUMMARY
========================================================================
⏱️  Runtime: 240.5s
💬 Conversations: 3

👁️  Vision FPS: Mean: 8.5fps | Detections: 145 | Locks: 3
🎤 STT Latency: Mean: 180ms | Min: 120ms | Max: 250ms
🧠 LLM Latency: Mean: 1200ms | Min: 800ms | Max: 1800ms
🔊 TTS Latency: Mean: 350ms | Min: 250ms | Max: 500ms
```

## 🐛 Common Issues

### "Camera not detected"
- Test camera: `rpicam-hello --timeout 2000`
- Check connection: `vcgencmd get_camera` (should show `detected=1`)
- Enable camera in `raspi-config`: Interface Options → Camera → Enable
- See **VISION_SETUP.md** for detailed troubleshooting

### "YuNet model not found"
- Run: `python download_yunet_model.py`
- Expected location: `models/face_detection_yunet_2023mar_int8bq.onnx`
- Check file size: ~2.5MB

### "Cannot connect to Ollama"
- Start Ollama server: `ollama serve`
- Check it's running: `curl http://localhost:11434`
- Pull model: `ollama pull qwen2.5:0.5b-instruct-q4_k_M`

### "Whisper model download fails"
- Manually download: `python -c "import whisper; whisper.load_model('tiny')"`
- Check internet connection (first-time download only)
- Expected size: ~39MB

### "Piper not found"
- Install: `pip install piper-tts`
- Download model from https://github.com/rhasspy/piper/releases
- Place `.onnx` and `.onnx.json` files in `models/` directory

### "No microphone detected"
- Test: `arecord -l` (should list devices)
- Check USB microphone connection
- Install audio tools: `sudo apt-get install alsa-utils`

### "Vision worker fails but audio works"
- This is expected! Pluto falls back to audio-only mode
- Vision requires Raspberry Pi + camera hardware
- To disable vision intentionally, see VISION_SETUP.md

## 📊 Next Steps

- **View logs**: Check `logs/` for CSV/JSON metrics
- **Tune vision**: Edit `VISION_CONFIG` in `src/config.py`
- **Customize greeting**: Change `greeting_message` parameter
- **Read architecture**: See `ARCHITECTURE.md` for system design
- **Advanced setup**: See `VISION_SETUP.md` for vision tuning

## 🔧 Advanced Configuration

### Disable Vision (Audio-Only Mode)
```python
# In src/config.py
VISION_CONFIG = {
    "greeting_enabled": False,  # Disables auto-greeting
    ...
}

# Or in orchestrator.py, comment out:
# self.enable_vision = True  # Change to False
```

### Customize Greeting Behavior
```python
VISION_CONFIG = {
    "greeting_message": "Hello! What can I do for you?",  # Custom greeting
    "greeting_cooldown": 15.0,  # 15 seconds between greetings
    "lock_threshold_frames": 5,  # More frames = more reliable lock
    ...
}
```

### Adjust Face Detection Sensitivity
```python
VISION_CONFIG = {
    "confidence_threshold": 0.5,  # Lower = more sensitive (more false positives)
    "confidence_threshold": 0.8,  # Higher = less sensitive (may miss faces)
    ...
}
```

---

🎉 **Congratulations!** You're now running a vision-driven reflex agent!

For detailed technical information, see:
- **ARCHITECTURE.md** - System design
- **VISION_SETUP.md** - Vision system deep dive
- **HOW_TO_RUN.md** - Detailed runtime instructions
