# 🚀 Project Pluto - Quick Start Guide

Get up and running with Pluto in under 5 minutes!

## ⚡ Prerequisites

- **Python 3.8+** installed
- **Ollama** installed and running
- **Piper TTS** binary installed
- **Microphone** connected

## 📦 1. Install Dependencies

```powershell
# Navigate to project directory
cd C:\Users\Asus\Desktop\pluto

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Python packages
pip install -r requirements.txt
```

## 🤖 2. Download Models

### Vosk STT Model (~40MB)
```powershell
# Download from: https://alphacephei.com/vosk/models
# Example: vosk-model-small-en-us-0.15.zip

# Extract to:
mkdir models
# Extract vosk-model-small-en-us-0.15 to models/
```

### Piper TTS Model
```powershell
# Download from: https://github.com/rhasspy/piper/releases
# Example: en_US-lessac-medium.onnx

# Place in models/ directory
```

### Qwen2.5 LLM Model
```powershell
# Pull model with Ollama
ollama pull qwen2.5:0.5b-instruct-q4_K_M
```

## 🎯 3. Configure Paths

Edit `src/config.py` if your model paths differ:

```python
VOSK_CONFIG = {
    "model_path": "./models/vosk-model-small-en-us-0.15",  # Your Vosk model
    ...
}

PIPER_CONFIG = {
    "piper_binary": "piper",  # Or full path: C:/path/to/piper.exe
    "model_path": "./models/en_US-lessac-medium.onnx",  # Your Piper model
    ...
}
```

## 🎙️ 4. Start Ollama Server

```powershell
# Start Ollama in separate terminal
ollama serve
```

## 🪐 5. Run Pluto!

```powershell
# Start the assistant
python run.py
```

You should see:
```
╔═══════════════════════════════════════════════════════════════════╗
║                     🪐 PROJECT PLUTO 🪐                          ║
║            Offline Voice Assistant Test Architecture             ║
╚═══════════════════════════════════════════════════════════════════╝

🎤 STT Worker initializing...
✅ STT Worker initialized
🧠 LLM Worker initializing...
✅ LLM Worker initialized
🔊 TTS Worker initializing...
✅ TTS Worker initialized

🎙️  PLUTO IS READY - Start speaking!
```

## 🗣️ 6. Talk to Pluto

1. **Speak** into your microphone
2. **Wait** for silence detection
3. **Listen** to Pluto's response
4. **View metrics** in `logs/` directory

## ⏹️ 7. Stop Pluto

Press `Ctrl+C` to gracefully shutdown:
```
📊 PLUTO SESSION SUMMARY
========================================================================
⏱️  Runtime: 120.5s
💬 Conversations: 5

🎤 STT Latency: Mean: 150ms | Min: 120ms | Max: 200ms
🧠 LLM Latency: Mean: 850ms | Min: 700ms | Max: 1000ms
🔊 TTS Latency: Mean: 300ms | Min: 250ms | Max: 350ms
```

## 🐛 Common Issues

### "Vosk model not found"
- Download model from https://alphacephei.com/vosk/models
- Extract to `models/` directory
- Update `VOSK_CONFIG["model_path"]` in `src/config.py`

### "Cannot connect to Ollama"
- Start Ollama server: `ollama serve`
- Check it's running on `http://localhost:11434`
- Pull model: `ollama pull qwen2.5:0.5b-instruct-q4_K_M`

### "Piper binary not found"
- Download from https://github.com/rhasspy/piper/releases
- Add to system PATH or set full path in config
- Verify: `piper --version`

### "No microphone detected"
- Check microphone is connected and recognized by Windows
- Test in Sound Settings
- Verify PyAudio installation: `pip install pyaudio`

## 📊 Next Steps

- **View logs**: Check `logs/` for CSV/JSON metrics
- **Run tests**: `pytest tests/test_integration.py -v`
- **Customize**: Edit `src/config.py` for your preferences
- **Read docs**: See `DOCUMENTATION.md` for complete reference

---

🎉 **Congratulations!** You're now running an offline voice assistant!

For detailed technical information, see [DOCUMENTATION.md](DOCUMENTATION.md)
