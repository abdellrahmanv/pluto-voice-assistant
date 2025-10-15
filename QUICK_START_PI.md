# 🍓 Pluto Voice Assistant - Raspberry Pi Quick Start

## Prerequisites
- Raspberry Pi 4 (recommended) with 64-bit Raspberry Pi OS
- Microphone and speaker connected
- Internet connection

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
- ✅ Install system dependencies (Python, PortAudio, espeak-ng)
- ✅ Create Python virtual environment
- ✅ Install all Python packages (Whisper, PyAudio, etc.)
- ✅ Download and install Piper TTS (ARM64 version)
- ✅ Download the voice model

**Estimated time:** 10-15 minutes

### 3. Install Ollama (If Not Already Installed)

Open a **new terminal** and run:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Then download the Qwen model:

```bash
ollama pull qwen2.5:1.5b-instruct-q4_K_M
```

**Estimated time:** 5-10 minutes

### 4. Run Pluto!

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
  Whisper: tiny (39M params, ~1GB RAM, ~1s latency, good accuracy)
  Ollama: qwen2.5:1.5b-instruct-q4_K_M
  Piper:  /home/pi/pluto-voice-assistant/models/en_US-lessac-medium.onnx

======================================================================

[2025-10-15 12:00:00] [INFO] Starting workers...
[2025-10-15 12:00:01] [INFO] STT worker ready
[2025-10-15 12:00:02] [INFO] LLM worker ready
[2025-10-15 12:00:03] [INFO] TTS worker ready
[2025-10-15 12:00:04] [INFO] 🎤 Listening... (say something!)
```

## Troubleshooting

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

- **STT (Whisper tiny):** ~1-2 seconds per phrase
- **LLM (Qwen 1.5B):** ~2-3 seconds per response
- **TTS (Piper):** ~0.5 seconds
- **Total response time:** ~4-6 seconds

## Running on Boot (Optional)

To make Pluto start automatically on boot, see `RASPBERRY_PI_DEPLOYMENT.md` for systemd service setup.

## Need Help?

Check the full documentation:
- `RASPBERRY_PI_DEPLOYMENT.md` - Detailed deployment guide
- `README.md` - Project overview
- `DOCUMENTATION.md` - Architecture and troubleshooting

---

**Enjoy your voice assistant! 🎉**
