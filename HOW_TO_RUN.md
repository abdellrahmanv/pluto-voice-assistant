# 🚀 PROJECT PLUTO - VISION-DRIVEN REFLEX AGENT - COMPLETE RUN GUIDE

## ⚡ QUICK START (Raspberry Pi)

### Step 1: Automated Setup
```bash
# Navigate to project
cd ~/pluto-voice-assistant

# Run setup script (installs everything: camera drivers, Python packages, models)
chmod +x setup_pi.sh
./setup_pi.sh
```

**This script installs:**
- rpicam-apps (camera support)
- libcamera-apps
- Python dependencies (OpenCV, Whisper, PyAudio, etc.)
- YuNet face detection model
- Piper TTS

### Step 2: Test Camera (CRITICAL!)
```bash
# Verify camera is working BEFORE starting Pluto
rpicam-hello --timeout 2000

# Expected: 2-second camera preview window
# If fails, see troubleshooting section below
```

### Step 3: Download Models

Models are mostly handled by `setup_pi.sh`, but verify:

#### A) YuNet Face Detection (~2.5MB)
```bash
# Auto-downloaded by setup_pi.sh, or manually:
python download_yunet_model.py

# Verify:
ls -lh models/face_detection_yunet_2023mar_int8bq.onnx
# Expected: ~2.5MB
```

#### B) Whisper STT (~39MB)
```bash
# Auto-downloaded on first run, or manually:
python -c "import whisper; whisper.load_model('tiny')"

# Cached in: ~/.cache/whisper/tiny.pt
```

#### C) Piper TTS Model (~63MB)
```bash
# Download from: https://github.com/rhasspy/piper/releases
# Download both files:
#   - en_US-lessac-medium.onnx
#   - en_US-lessac-medium.onnx.json

wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx.json

# Place in models/ directory
mv en_US-lessac-medium.onnx* models/
```

#### D) Qwen2.5 LLM Model (~310MB)
```bash
# Install Ollama (if not done by setup_pi.sh):
curl -fsSL https://ollama.com/install.sh | sh

# Pull model:
ollama pull qwen2.5:0.5b-instruct-q4_k_M

# Verify:
ollama list
# Should show: qwen2.5:0.5b-instruct-q4_k_M
```

### Step 4: Verify Configuration
```bash
# Check models are in place:
ls -lh models/

# Expected output:
#   face_detection_yunet_2023mar_int8bq.onnx (~2.5MB)
#   en_US-lessac-medium.onnx (~63MB)
#   en_US-lessac-medium.onnx.json (~few KB)

# If paths differ, edit src/config.py:
#   VISION_CONFIG["model_path"]
#   PIPER_CONFIG["model_path"]
```

### Step 5: RUN PLUTO! 👁️🎉
```bash
# Make sure:
# 1. Camera is working (rpicam-hello test passed)
# 2. Ollama server is running (ollama serve in separate terminal)
# 3. Microphone and speakers connected

# Start Pluto:
python run.py
```

**Expected Output:**
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

**When you step into camera view:**
```
👁️  Face detected at (120, 95, 80, 80)
🔒 Face locked (ID: face_001)
� Greeting: "Hi there! How can I help you today?"
▶️  STT resumed (listening for response)

🎤 Listening for speech...
```

---

## 🔧 TROUBLESHOOTING

### Issue: "Camera not detected" 🎥
```bash
# Check camera connection:
vcgencmd get_camera
# Expected: supported=1 detected=1

# If detected=0:
# 1. Enable camera in raspi-config
sudo raspi-config
# Interface Options → Camera → Enable → Reboot

# 2. Check cable connection (yellow to yellow on board)

# 3. Test camera:
rpicam-hello --timeout 2000
# Should show 2-second preview

# For detailed troubleshooting, see VISION_SETUP.md
```

### Issue: "YuNet model not found"
```bash
# Download manually:
python download_yunet_model.py

# Verify location:
ls -lh models/face_detection_yunet_2023mar_int8bq.onnx
# Expected: ~2.5MB file

# Check config path:
grep "model_path" src/config.py | grep yunet
```

### Issue: "Vision worker fails but audio works"
**This is normal fallback behavior!**

Pluto automatically falls back to audio-only mode if vision fails. To intentionally disable vision:

```python
# Edit src/config.py:
VISION_CONFIG = {
    "greeting_enabled": False,  # Disables auto-greeting
    ...
}
```

Or comment out in `src/orchestrator.py`:
```python
# self.enable_vision = False  # Change to False
```

### Issue: "Cannot connect to Ollama"
```bash
# Start Ollama server in separate terminal:
ollama serve

# Test it's running:
curl http://localhost:11434/api/tags

# Check Ollama service:
systemctl status ollama  # If installed as service
```

### Issue: "Piper model not found"
```bash
# Download both files:
cd models/
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx.json

# Verify both exist:
ls -lh en_US-lessac-medium.onnx*
```

### Issue: "No microphone detected"
```bash
# Check audio devices:
arecord -l

# Expected: List of USB/audio devices

# Test recording:
arecord -d 3 test.wav
aplay test.wav

# Install audio tools if missing:
sudo apt-get install alsa-utils
```

### Issue: "Whisper model download fails"
```bash
# Manually download:
python -c "import whisper; whisper.load_model('tiny')"

# Check cached model:
ls -lh ~/.cache/whisper/tiny.pt
# Expected: ~39MB

# If internet issues, download elsewhere and copy to cache
```

---

## 📊 RUNNING TESTS

```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Run all tests:
pytest tests\test_integration.py -v

# Run specific test:
pytest tests\test_integration.py::TestMetricsLogger::test_metric_logging -v

# With coverage report:
pytest tests\test_integration.py --cov=src --cov-report=html
# Open htmlcov\index.html in browser
```

---

## 📈 VIEWING METRICS

After running conversations, check the logs:

```powershell
# List generated log files
ls logs\

# View CSV metrics (import in Excel or pandas)
Get-Content logs\metrics_*.csv | Select-Object -First 20

# View JSON metrics
Get-Content logs\metrics_*.json | ConvertFrom-Json

# View summary
Get-Content logs\summary_*.txt
```

**Analyze in Python:**
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load metrics
df = pd.read_csv('logs/metrics_20241015_120000.csv')

# Plot latencies
stt = df[(df['component'] == 'stt') & (df['metric_type'] == 'latency')]
plt.plot(stt['timestamp'], stt['value'])
plt.title('STT Latency Over Time')
plt.ylabel('Latency (ms)')
plt.show()
```

---

## ⚙️ ADVANCED CONFIGURATION

### Customize Greeting Behavior
```python
# Edit src/config.py:
VISION_CONFIG = {
    "greeting_enabled": True,  # Set False to disable auto-greeting
    "greeting_message": "Hello! How may I assist you?",  # Custom greeting
    "greeting_cooldown": 15.0,  # Seconds between greetings (prevents spam)
    ...
}
```

### Adjust Face Detection Sensitivity
```python
VISION_CONFIG = {
    "confidence_threshold": 0.5,  # Lower = more sensitive (more false positives)
    "confidence_threshold": 0.8,  # Higher = less sensitive (may miss faces)
    "lock_threshold_frames": 5,  # More frames = more reliable lock (slower)
    "face_lost_timeout_frames": 20,  # More tolerance = stays locked longer
    ...
}
```

### Change Camera Resolution/FPS
```python
VISION_CONFIG = {
    "frame_width": 640,  # Higher resolution (more CPU usage)
    "frame_height": 480,
    "camera_fps": 15,  # Higher FPS (more CPU usage)
    "frame_skip": 1,  # Process every frame (no skipping)
    ...
}
```

### Speed Up LLM Responses
```python
OLLAMA_CONFIG = {
    "max_tokens": 50,  # Shorter responses (default: 100)
    "temperature": 0.5,  # More deterministic (default: 0.7)
    ...
}
```

### Use Faster TTS Model
Download smaller Piper model and update:
```python
PIPER_CONFIG = {
    "model_path": "./models/en_US-lessac-low.onnx",  # Faster, lower quality
    ...
}
```

### Disable Vision (Audio-Only Mode)
If you don't have a camera or want pure audio interaction:
```python
# Option 1: In src/config.py
VISION_CONFIG = {
    "greeting_enabled": False,
    ...
}

# Option 2: In src/orchestrator.py
class Orchestrator:
    def __init__(self, ...):
        self.enable_vision = False  # Change from True to False
```

---

## 🛑 STOPPING PLUTO

```powershell
# Press Ctrl+C in terminal where Pluto is running

# You'll see graceful shutdown:
# 🛑 Shutting down...
# 🔄 Shutting down workers...
# 🎤 STT Worker stopping...
# ✅ STT Worker stopped
# 🧠 LLM Worker stopping...
# ✅ LLM Worker stopped
# 🔊 TTS Worker stopping...
# ✅ TTS Worker stopped
# 📊 Saving metrics...
# ✅ Metrics saved to: logs/
# 🪐 PLUTO SHUTDOWN COMPLETE

# Also stop Ollama server in other terminal:
# Ctrl+C in terminal running "ollama serve"
```

---

## 📱 RECOMMENDED WORKFLOW

### Terminal 1: Ollama Server
```bash
ollama serve
# Keep this running
```

### Terminal 2: Pluto Application
```bash
cd ~/pluto-voice-assistant
source .venv/bin/activate
python run.py

# Step into camera view, talk to Pluto, press Ctrl+C when done
```

### Terminal 3: Monitoring (Optional)
```bash
# Watch logs in real-time
tail -f logs/metrics_*.csv

# Or watch vision events:
tail -f logs/metrics_*.txt | grep "Vision"
```

## 🤖 Understanding the Reflex Agent

### State Machine Flow:
```
IDLE → FACE_DETECTED → LOCKED_IN → GREETING → LISTENING → PROCESSING → RESPONDING → FACE_LOST → IDLE
```

### Key Behaviors:
1. **Proactive Greeting**: Pluto detects you and initiates conversation
2. **Face Locking**: Locks onto one person, ignores background distractions
3. **Occlusion Tolerance**: Stays locked if you briefly move out of frame (< 1.5s)
4. **Auto Reset**: Returns to IDLE when you leave for > 1.5s
5. **STT Pause/Resume**: Microphone only active when face is locked (saves CPU)

### Debugging Vision:
```bash
# Enable vision debug mode in src/config.py:
VISION_CONFIG = {
    "debug": True,  # Prints detailed face detection info
    ...
}

# Watch vision worker logs:
python run.py 2>&1 | grep "Vision"
```

---

## ✅ VERIFICATION CHECKLIST

Before running, ensure:
- [ ] **Raspberry Pi Camera connected** and enabled (`vcgencmd get_camera` shows detected=1)
- [ ] **Camera test passed** (`rpicam-hello --timeout 2000` works)
- [ ] **Virtual environment activated** (`source .venv/bin/activate`)
- [ ] **Dependencies installed** (via `setup_pi.sh` or `pip install -r requirements.txt`)
- [ ] **YuNet model downloaded** (`models/face_detection_yunet_2023mar_int8bq.onnx` exists, ~2.5MB)
- [ ] **Whisper model cached** (`~/.cache/whisper/tiny.pt` exists, ~39MB)
- [ ] **Piper model downloaded** (`models/en_US-lessac-medium.onnx` + `.json` exist)
- [ ] **Ollama server running** (`ollama serve` in separate terminal)
- [ ] **Qwen2.5 model pulled** (`ollama list` shows `qwen2.5:0.5b-instruct-q4_k_M`)
- [ ] **Microphone connected** and working (`arecord -l` shows devices)
- [ ] **Speakers/headphones connected** (`aplay -l` shows devices)

---

## 🎯 FIRST RUN EXPECTED OUTPUT

### Startup Sequence:

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

👁️  Vision:
  Model: face_detection_yunet_2023mar_int8bq.onnx
  Resolution: 320x240 @ 10fps (effective: 5fps with frame_skip=2)
  Detection Threshold: 0.6
  Lock Threshold: 3 frames (~0.3s)

🎤 Audio:
  Sample Rate: 16000 Hz
  Channels: 1

🤖 Models:
  Vision: YuNet (INT8 quantized, 2.5MB)
  Whisper: tiny (39M params, ~150MB RAM, ~200ms latency)
  Ollama: qwen2.5:0.5b-instruct-q4_k_M (~2GB RAM)
  Piper: en_US-lessac-medium.onnx (~200MB RAM)

======================================================================

🚀 Initializing workers...

👁️  Vision Worker initializing...
   Loading YuNet model from: models/face_detection_yunet_2023mar_int8bq.onnx
   Starting rpicam-vid: 320x240 @ 10fps YUV420
   Camera warmup...
✅ Vision Worker initialized
   Vision warmup: Processing test frame...
   Vision warmup complete: 85ms

🎤 STT Worker initializing...
   Loading Whisper tiny model (cached)...
   Opening audio input: 16000Hz
✅ STT Worker initialized
   STT warmup: Processing silent audio...
   STT warmup complete: 180ms
⏸️  STT paused (waiting for face detection)

🧠 LLM Worker initializing...
   Checking Ollama server at: http://localhost:11434
   Model 'qwen2.5:0.5b-instruct-q4_k_M' ready
✅ LLM Worker initialized
   LLM warmup: Running test inference...
   LLM warmup complete: 1200ms

🔊 TTS Worker initializing...
   Piper model found: models/en_US-lessac-medium.onnx
✅ TTS Worker initialized
   TTS warmup: Synthesizing test audio...
   TTS warmup complete: 350ms

✅ All workers initialized successfully

======================================================================
👁️  PLUTO IS READY - Waiting for someone to appear...
   Press Ctrl+C to stop
======================================================================

👁️  Vision: Scanning at 8.2 FPS, no faces detected...
```

### Interaction Sequence (When You Appear):

```
👁️  Face detected at (120, 95, 80, 80) confidence=0.78
👁️  Face detected at (121, 96, 80, 80) confidence=0.81 (frame 2/3)
👁️  Face detected at (122, 96, 80, 80) confidence=0.79 (frame 3/3)
🔒 Face locked (ID: face_001)
🎉 Greeting: "Hi there! How can I help you today?"
  👁️  Vision trigger → LLM: 0ms
  🧠 LLM: 1100ms
  🔊 TTS: 420ms
  ⏱️  total (greeting): 1520ms
▶️  STT resumed (listening for response)

🎤 Listening for speech...

🎙️  Speech detected...
   📝 Recognized: "what time is it"
  🎤 STT: 180ms
   🤔 Thinking about: "what time is it"
   💭 Response: "I'm sorry, I don't have access to real-time information..."
  🧠 LLM: 950ms
   🗣️  Speaking response...
  🔊 TTS: 380ms
  ⏱️  total: 1510ms

🎤 Listening for speech...

<You leave the camera view>

👁️  Face lost (1/15 frames)
👁️  Face lost (5/15 frames)
👁️  Face lost (10/15 frames)
👁️  Face lost (15/15 frames) - unlocking
🔓 Face unlocked (ID: face_001) - person left
⏸️  STT paused (no face detected)
👁️  Waiting for someone to appear...
```

---

## 🔄 DEVELOPMENT WORKFLOW

### Making Code Changes
```powershell
# 1. Edit files in src/
# 2. Run tests
pytest tests\test_integration.py -v

# 3. Test manually
python run.py

# 4. Check metrics
Get-Content logs\summary_*.txt
```

### Adding New Features
See `DOCUMENTATION.md` for detailed guides on:
- Adding new metrics
- Adding new workers
- Modifying configuration
- Creating new tests

---

## 📚 ADDITIONAL RESOURCES

- **QUICKSTART.md**: Fast setup guide for beginners
- **QUICK_START_PI.md**: Raspberry Pi-specific quick start
- **ARCHITECTURE.md**: 4-worker reflex agent design documentation
- **VISION_SETUP.md**: Comprehensive vision system guide (63KB, troubleshooting, tuning)
- **README.md**: Project overview and key features

---

## 🎉 You're Ready to Run Pluto!

### Quick Reference:
**Command to start**: `python run.py`  
**Stop**: `Ctrl+C`  
**Check metrics**: `cat logs/summary_*.txt`  
**Test camera**: `rpicam-hello --timeout 2000`  
**Vision docs**: See `VISION_SETUP.md` for detailed troubleshooting

### What to Expect:
1. 👁️ **System starts** - Camera activates, vision worker begins scanning
2. 🔍 **You appear** - Face detected after 3 consecutive frames (~0.3s)
3. 🔒 **Face locked** - Pluto locks onto you, ignores background
4. 👋 **Auto-greeting** - "Hi there! How can I help you today?"
5. 🎤 **Listening** - STT activates, waiting for your response
6. 💬 **Conversation** - Continue naturally
7. 😴 **You leave** - After 1.5s, Pluto returns to IDLE

Good luck with your vision-driven reflex agent! 🚀👁️🤖
