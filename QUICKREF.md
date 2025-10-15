# 🚀 QUICK START - Project Pluto

## Installation Complete! ✅

All dependencies have been automatically installed:
- ✅ Piper TTS (binary + voice model)
- ✅ Vosk STT (speech recognition model)
- ✅ Python packages (all 7 installed)
- ✅ Ollama + Qwen2.5 (installed by you)

---

## Run Pluto in 3 Commands

### Terminal 1 (Ollama Server):
```powershell
ollama serve
```

### Terminal 2 (Pluto Voice Assistant):
```powershell
.\venv\Scripts\Activate.ps1
python run.py
```

**That's it!** Speak into your microphone and get AI-powered responses.

---

## Automated Installation Scripts

### Install Everything (Fresh Setup):
```powershell
.\setup_all.ps1
```
Runs Piper + Vosk installation automatically (~3 minutes)

### Individual Components:
```powershell
.\install_piper.ps1  # Just Piper TTS
.\install_vosk.ps1   # Just Vosk STT
```

---

## Verification & Testing

### Pre-Flight Check:
```powershell
.\check_setup.ps1
```
Verifies all components are ready to run

### Test Python Packages:
```powershell
.\venv\Scripts\Activate.ps1
python verify_install.py
```
Should show: 🎉 All 7 packages installed!

---

## File Locations

| Component | Path |
|-----------|------|
| **Piper Binary** | `piper/piper.exe` |
| **Piper Voice** | `models/en_US-lessac-medium.onnx` |
| **Vosk Model** | `models/vosk-model-small-en-us-0.15/` |
| **Config** | `src/config.py` |
| **Main Entry** | `run.py` |
| **Logs** | `logs/metrics_*.csv` |

---

## Interaction Flow

```
🎤 You speak
    ↓
🔊 Vosk STT → Converts speech to text
    ↓
🤖 Qwen2.5 LLM → Generates intelligent response
    ↓
🗣️ Piper TTS → Converts text to speech
    ↓
🔈 Audio output (you hear the response)
```

**Latency:** ~1-3 seconds total round-trip

---

## Example Voice Interaction

**You:** "What is the weather like today?"

**Pluto (processes):**
- Vosk: Transcribes to text
- Qwen2.5: Generates response
- Piper: Speaks response

**Output:** Voice response from AI assistant

All metrics logged to `logs/` directory!

---

## Troubleshooting

### Ollama not responding?
```powershell
ollama list  # Check model is installed
ollama serve # Start server
```

### Audio not working?
Check `src/config.py`:
- `VOSK_CONFIG` → Microphone settings
- `PIPER_CONFIG` → Speaker settings

### Want to re-install?
```powershell
.\setup_all.ps1  # Runs full installation again
```

---

## Documentation

- **Complete Guide:** `AUTOMATED_SETUP.md`
- **How to Run:** `HOW_TO_RUN.md`
- **Architecture:** `ARCHITECTURE.md`
- **API Reference:** `DOCUMENTATION.md`
- **Quick Start:** `QUICKSTART.md`

---

## Performance Metrics

Pluto automatically tracks:
- ⏱️ **Latency:** STT, LLM, TTS response times
- 💾 **Memory:** RAM usage per worker
- 📊 **Queue Depth:** Message backlog
- 🔄 **Throughput:** Messages processed

View in: `logs/metrics_TIMESTAMP.csv`

---

## What's Next?

1. **Test basic interaction:** Ask simple questions
2. **Review metrics:** Check logs for performance
3. **Customize config:** Adjust in `src/config.py`
4. **Read docs:** Explore full documentation
5. **Build features:** Add your own capabilities!

---

**Project Pluto is ready! 🪐**

Just run `ollama serve` + `python run.py` and start talking!

---

*Last updated: October 15, 2025*
