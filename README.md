# 🪐 Project Pluto - Voice Assistant Test Architecture

> **Modular, Event-Driven Voice Assistant for Local Deployment Testing**

## 🎯 Objective

Pluto is a test deployment system for a voice assistant architecture combining:
- **Vosk** (Speech-to-Text)
- **Qwen2.5** via Ollama (Large Language Model)
- **Piper** (Text-to-Speech)

This laptop deployment validates integration logic, measures performance metrics, and identifies bottlenecks before Raspberry Pi 4 deployment.

---

## 🏗️ Architecture Overview

```
┌─────────────┐
│ Microphone  │
└─────┬───────┘
      │ (Audio Stream)
      ▼
┌─────────────┐
│  Vosk STT   │ ← stt_worker.py
└─────┬───────┘
      │ (Recognized Text)
      ▼
┌─────────────┐
│ input_queue │ ← Thread-safe queue
└─────┬───────┘
      ▼
┌─────────────┐
│ Qwen2.5 LLM │ ← llm_worker.py (via Ollama API)
└─────┬───────┘
      │ (Generated Response)
      ▼
┌──────────────┐
│ output_queue │ ← Thread-safe queue
└─────┬────────┘
      ▼
┌─────────────┐
│  Piper TTS  │ ← tts_worker.py
└─────┬───────┘
      │ (Audio Output)
      ▼
┌─────────────┐
│   Speaker   │
└─────────────┘
```

### 🧩 Core Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **STT Worker** | `stt_worker.py` | Captures audio, converts to text via Vosk |
| **LLM Worker** | `llm_worker.py` | Processes text, generates responses via Qwen2.5 |
| **TTS Worker** | `tts_worker.py` | Synthesizes speech from text via Piper |
| **Orchestrator** | `orchestrator.py` | Coordinates workers, manages queues, monitors health |
| **Metrics Logger** | `metrics_logger.py` | Records performance data, generates reports |
| **Configuration** | `config.py` | Centralized settings management |

---

## 📁 Project Structure

```
pluto/
├── src/
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── stt_worker.py          # Vosk speech recognition
│   │   ├── llm_worker.py          # Ollama/Qwen2.5 inference
│   │   └── tts_worker.py          # Piper text-to-speech
│   ├── orchestrator.py            # Main control loop
│   ├── config.py                  # Configuration management
│   ├── metrics_logger.py          # Performance tracking
│   └── __init__.py
├── models/                        # Model storage directory
│   ├── vosk/                      # Vosk models (download separately)
│   └── piper/                     # Piper voices (download separately)
├── logs/                          # Metric logs and reports
├── tests/                         # Unit tests
│   └── test_integration.py
├── requirements.txt               # Python dependencies
├── setup.py                       # Installation script
├── run.py                         # Main entry point
├── .env.example                   # Environment variables template
├── .gitignore
├── README.md                      # This file
├── QUICKSTART.md                  # 5-minute setup
└── DOCUMENTATION.md               # Detailed docs
```

---

## 🚀 Quick Start

See **QUICKSTART.md** for detailed setup instructions.

### Prerequisites
- Python 3.8+
- Ollama installed and running
- Microphone and speakers

### Installation
```powershell
cd Desktop\pluto
pip install -r requirements.txt
ollama pull qwen2.5:1.5b-q4
python run.py
```

---

## 📊 Performance Tracking

Every operation is measured and logged:
- 🎤 STT Latency
- 🧠 LLM Inference Time  
- 🔊 TTS Synthesis Time
- 💾 Memory Usage
- ⏱️ Total Conversation Time

Results saved to `logs/` directory in CSV, JSON, and text formats.

---

## 📖 Documentation

- **README.md** (this file) - Project overview
- **QUICKSTART.md** - Fast setup guide
- **DOCUMENTATION.md** - Complete technical reference
- **ARCHITECTURE.md** - Design decisions
- **DIAGRAMS.md** - Visual diagrams
- **FILE_INDEX.md** - File navigation

---

**🪐 Project Pluto - Testing the future of offline voice assistants**

*Built with reasoning and performance in mind.*
