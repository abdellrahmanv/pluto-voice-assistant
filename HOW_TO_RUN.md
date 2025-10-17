# 🚀 PROJECT PLUTO - COMPLETE SETUP & RUN GUIDE

## ⚡ QUICK START (5 Steps)

### Step 1: Create Virtual Environment (RECOMMENDED)
```powershell
# Navigate to project
cd C:\Users\Asus\Desktop\pluto

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Verify activation (should show pluto\venv path)
python -c "import sys; print(sys.prefix)"
```

### Step 2: Install Python Dependencies
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# If PyAudio fails on Windows, use pipwin:
pip install pipwin
pipwin install pyaudio
```

### Step 3: Download Models

#### A) Vosk STT Model (~40MB)
```powershell
# Download from: https://alphacephei.com/vosk/models
# Recommended: vosk-model-small-en-us-0.15.zip

# After download, extract to models/ directory
# Result: C:\Users\Asus\Desktop\pluto\models\vosk-model-small-en-us-0.15\
```

**Direct download link**: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

#### B) Piper TTS Model (~60MB)
```powershell
# Download from: https://github.com/rhasspy/piper/releases
# Go to latest release → Assets → Download:
#   - en_US-lessac-medium.onnx
#   - en_US-lessac-medium.onnx.json

# Place both files in models/ directory
# Result: C:\Users\Asus\Desktop\pluto\models\en_US-lessac-medium.onnx
```

**Direct release page**: https://github.com/rhasspy/piper/releases/tag/v1.2.0

#### C) Install Piper Binary
```powershell
# Download piper.exe for Windows from:
# https://github.com/rhasspy/piper/releases

# Extract piper.exe and add to PATH, or:
# Place in project root: C:\Users\Asus\Desktop\pluto\piper.exe

# Verify installation:
piper --version
```

#### D) Qwen2.5 LLM Model (~1GB)
```powershell
# First, install Ollama from: https://ollama.ai/download

# Start Ollama server (in separate terminal):
ollama serve

# Pull the model (in another terminal):
ollama pull qwen2.5:0.5b-instruct-q4_K_M

# Verify:
ollama list
# Should show: qwen2.5:0.5b-instruct-q4_K_M
```

### Step 4: Verify Configuration
```powershell
# Check your models are in the right place:
ls models\

# Should show:
#   vosk-model-small-en-us-0.15\
#   en_US-lessac-medium.onnx
#   en_US-lessac-medium.onnx.json

# If paths differ, edit src\config.py and update:
#   VOSK_CONFIG["model_path"]
#   PIPER_CONFIG["model_path"]
```

### Step 5: RUN PLUTO! 🎉
```powershell
# Make sure:
# 1. Virtual environment is activated (venv)
# 2. Ollama server is running (ollama serve)
# 3. Microphone is connected

# Start Pluto:
python run.py

# You should see:
# ╔═══════════════════════════════════════════════════╗
# ║           🪐 PROJECT PLUTO 🪐                    ║
# ╚═══════════════════════════════════════════════════╝
# 🎤 STT Worker initializing...
# ✅ STT Worker initialized
# 🧠 LLM Worker initializing...
# ✅ LLM Worker initialized
# 🔊 TTS Worker initializing...
# ✅ TTS Worker initialized
# 🎙️  PLUTO IS READY - Start speaking!
```

---

## 🔧 TROUBLESHOOTING

### Issue: "Vosk model not found"
```powershell
# Download and extract model:
# https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

# Extract to: C:\Users\Asus\Desktop\pluto\models\vosk-model-small-en-us-0.15\

# Verify structure:
ls models\vosk-model-small-en-us-0.15\
# Should contain: am/, conf/, graph/, ivector/, etc.
```

### Issue: "Cannot connect to Ollama"
```powershell
# Start Ollama server in separate terminal:
ollama serve

# Test it's running:
curl http://localhost:11434/api/tags

# If port 11434 blocked, check firewall
```

### Issue: "Piper binary not found"
```powershell
# Option 1: Add piper to PATH
# Download from: https://github.com/rhasspy/piper/releases
# Extract piper.exe
# Add folder to Windows PATH environment variable

# Option 2: Use full path in config
# Edit src\config.py:
PIPER_CONFIG = {
    "piper_binary": "C:/path/to/piper.exe",  # Full path
    ...
}
```

### Issue: "PyAudio installation fails"
```powershell
# Use pipwin (Windows-specific package manager):
pip install pipwin
pipwin install pyaudio

# Or download wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Then: pip install PyAudio‑0.2.13‑cp311‑cp311‑win_amd64.whl
```

### Issue: "No microphone detected"
```powershell
# Check Windows Sound Settings:
# 1. Right-click speaker icon → Sound settings
# 2. Input → Test your microphone
# 3. Ensure default input device is set

# Test PyAudio devices:
python -c "import pyaudio; p = pyaudio.PyAudio(); print(f'Devices: {p.get_device_count()}')"
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

### Adjust VAD Sensitivity
If Pluto doesn't detect your speech, edit `src\config.py`:

```python
AUDIO_CONFIG = {
    "energy_threshold": 200,  # Lower = more sensitive (default: 300)
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
```powershell
ollama serve
# Keep this running
```

### Terminal 2: Pluto Application
```powershell
cd C:\Users\Asus\Desktop\pluto
.\venv\Scripts\Activate.ps1
python run.py

# Talk to Pluto, press Ctrl+C when done
```

### Terminal 3: Monitoring (Optional)
```powershell
# Watch logs in real-time
Get-Content logs\metrics_*.csv -Wait -Tail 10
```

---

## ✅ VERIFICATION CHECKLIST

Before running, ensure:
- [ ] Virtual environment activated (`.\venv\Scripts\Activate.ps1`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Vosk model extracted to `models\vosk-model-small-en-us-0.15\`
- [ ] Piper model in `models\en_US-lessac-medium.onnx`
- [ ] Piper binary accessible (`piper --version` works)
- [ ] Ollama server running (`ollama serve` in separate terminal)
- [ ] Qwen2.5 model pulled (`ollama list` shows it)
- [ ] Microphone connected and working (test in Windows settings)
- [ ] Speakers/headphones connected

---

## 🎯 FIRST RUN EXPECTED OUTPUT

```
╔═══════════════════════════════════════════════════════════════════╗
║                     🪐 PROJECT PLUTO 🪐                          ║
║            Offline Voice Assistant Test Architecture             ║
║                                                                   ║
║  Pipeline: Vosk (STT) → Qwen2.5 (LLM) → Piper (TTS)             ║
║  Purpose: Validate integration logic and measure performance     ║
╚═══════════════════════════════════════════════════════════════════╝

==================================================================
🪐 PROJECT PLUTO - Voice Assistant Orchestrator
==================================================================

🚀 Initializing workers...

⚙️  Configuration Summary:
   Vosk Model: vosk-model-small-en-us-0.15
   Piper Model: en_US-lessac-medium.onnx
   Ollama Model: qwen2.5:0.5b-instruct-q4_K_M
   Sample Rate: 16000 Hz
   Queue Size: 10
   Metrics: CSV=True, JSON=True

🎤 STT Worker initializing...
   Loading Vosk model from: .\models\vosk-model-small-en-us-0.15
   Opening audio input: 16000Hz
✅ STT Worker initialized
   STT warmup: Processing silent audio...
   STT warmup complete: 120ms

🧠 LLM Worker initializing...
   Checking Ollama server at: http://localhost:11434
   Model 'qwen2.5:0.5b-instruct-q4_K_M' ready
✅ LLM Worker initialized
   LLM warmup: Running test inference...
   LLM warmup complete: 650ms

🔊 TTS Worker initializing...
   Piper model found: .\models\en_US-lessac-medium.onnx
   Piper version: 1.2.0
✅ TTS Worker initialized
   TTS warmup: Synthesizing test audio...
   TTS warmup complete: 280ms

✅ All workers initialized successfully

==================================================================
🎙️  PLUTO IS READY - Start speaking!
   Press Ctrl+C to stop
==================================================================

🎤 Listening for speech...
```

**Now speak into your microphone!**

Example conversation:
```
🎙️  Speech detected...
   📝 Recognized: "hello pluto"
  🎤 STT: 150ms
   🤔 Thinking about: "hello pluto"
   💭 Response: "Hello! How can I help you today?"
  🧠 LLM: 850ms
   🗣️  Speaking: "Hello! How can I help you today?"
  🔊 TTS: 300ms
  ⏱️  total: 1300ms

🎤 Listening for speech...
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

- **QUICKSTART.md**: 5-minute setup summary
- **DOCUMENTATION.md**: Complete API reference (29KB)
- **ARCHITECTURE.md**: Design decisions (11KB)
- **DIAGRAMS.md**: Visual architecture (24KB)
- **FILE_INDEX.md**: Navigation guide (8KB)
- **MASTER_DOCUMENT.md**: Comprehensive overview (14KB+)

---

**🎉 You're ready to run Project Pluto!**

**Command to start**: `python run.py`  
**Stop**: `Ctrl+C`  
**Check metrics**: `Get-Content logs\summary_*.txt`

Good luck testing your offline voice assistant! 🚀
