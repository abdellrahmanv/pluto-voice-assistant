# 🪐 Project Pluto - Vision-Driven Reflex Agent Voice Assistant

> **Proactive, Face-Detecting Voice Assistant for Raspberry Pi**

## 🎯 What is Pluto?

Pluto is a **reflex agent** voice assistant that combines:
- **YuNet Face Detection** (Vision - initiates interaction)
- **Whisper** (Speech-to-Text)
- **Qwen2.5:0.5b** via Ollama (Large Language Model)
- **Piper** (Text-to-Speech)

### Key Features

✨ **Vision-Driven**: Detects faces and initiates conversations automatically  
🔒 **Person Locking**: Locks onto one person, ignores background distractions  
🎯 **Reflex Behavior**: Greets people proactively when detected  
🚀 **Optimized for Pi**: Runs on Raspberry Pi 4 with camera support  
📴 **Fully Offline**: All processing happens locally, no internet required

---

## 🏗️ Architecture Overview

```
┌──────────────┐
│ Pi Camera    │
└──────┬───────┘
       │ (Video Stream)
       ▼
┌──────────────┐
│ YuNet Vision │ ← vision_worker.py
└──────┬───────┘
       │ (Face Detected!)
       ▼
┌──────────────┐     Greeting: "Hi there!"
│ Orchestrator │ ────────────────────────┐
└──────┬───────┘                         │
       │                                 ▼
       │ Activates                  ┌─────────┐
       ▼                            │   LLM   │
┌──────────────┐                   └────┬────┘
│  Whisper STT │                        │
└──────┬───────┘                        ▼
       │                           ┌──────────┐
       └──────────────────────────▶│ Piper TTS│
                                   └────┬─────┘
                                        ▼
                                   ┌─────────┐
                                   │ Speaker │
                                   └─────────┘
```

### 🧩 Core Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **Vision Worker** | `vision_worker.py` | Detects faces, locks onto people, triggers greetings |
| **STT Worker** | `stt_worker.py` | Captures audio, converts to text via Whisper |
| **LLM Worker** | `llm_worker.py` | Processes text, generates responses via Qwen2.5 |
| **TTS Worker** | `tts_worker.py` | Synthesizes speech from text via Piper |
| **Agent State** | `agent_state.py` | Manages conversation states and transitions |
| **Orchestrator** | `orchestrator.py` | Coordinates 4 workers, manages vision-driven logic |
| **Metrics Logger** | `metrics_logger.py` | Records performance data, generates reports |
| **Configuration** | `config.py` | Centralized settings management |

---

## 📁 Project Structure

```
pluto/
├── src/
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── vision_worker.py       # YuNet face detection
│   │   ├── stt_worker.py          # Whisper speech recognition
│   │   ├── llm_worker.py          # Ollama/Qwen2.5 inference
│   │   └── tts_worker.py          # Piper text-to-speech
│   ├── orchestrator.py            # 4-worker coordination + reflex logic
│   ├── agent_state.py             # State machine for conversation flow
│   ├── config.py                  # Configuration management
│   ├── metrics_logger.py          # Performance tracking
│   └── __init__.py
├── models/                        # Model storage directory
│   ├── face_detection_yunet_2023mar_int8bq.onnx  # YuNet face detector
│   ├── whisper/                   # Whisper models (auto-downloaded)
│   └── piper/                     # Piper voices (download separately)
├── logs/                          # Metric logs and reports
├── tests/                         # Unit tests
│   └── test_integration.py
├── download_yunet_model.py        # YuNet model downloader
├── requirements.txt               # Python dependencies
├── setup_pi.sh                    # Raspberry Pi setup script
├── run.py                         # Main entry point
├── .gitignore
├── README.md                      # This file
├── QUICKSTART.md                  # 5-minute setup guide
├── ARCHITECTURE.md                # System design documentation
└── VISION_SETUP.md                # Vision system detailed guide
```

---

## 🚀 Quick Start

See **QUICKSTART.md** for detailed setup instructions.

### Prerequisites
- **Raspberry Pi 4** (4GB RAM recommended)
- **Raspberry Pi Camera** (libcamera-compatible)
- Python 3.8+
- Ollama installed and running
- Microphone and speakers

### Installation (Raspberry Pi)
```bash
cd ~/pluto
chmod +x setup_pi.sh
./setup_pi.sh  # Installs camera drivers, downloads models, sets up environment
python run.py
```

### What Happens When You Run?
1. 👁️ **Vision system starts** - Camera activates, begins scanning for faces
2. 🔍 **Detection** - When a face is detected, Pluto locks onto that person
3. 👋 **Greeting** - Pluto automatically says "Hi there! How can I help you today?"
4. 🎤 **Listening** - STT activates, waiting for your response
5. 💬 **Conversation** - Continue talking naturally
6. 😴 **Reset** - When you leave, Pluto returns to IDLE and waits for the next person

---

## 📊 Performance Tracking

Every operation is measured and logged:
- 👁️ **Vision**: Face detection FPS, face lock events
- 🎤 **STT**: Whisper latency (100-200ms)
- 🧠 **LLM**: Qwen2.5 inference time (500-1500ms)
- 🔊 **TTS**: Piper synthesis time (200-500ms)
- 💾 **Memory**: Per-component usage (~3GB total on Pi 4)
- ⏱️ **Total**: End-to-end conversation time

Results saved to `logs/` directory in CSV, JSON, and text formats.

### Typical Performance (Raspberry Pi 4)
- **Vision**: 5-10 FPS, 60-120ms per detection
- **STT**: 100-200ms for short phrases
- **LLM**: 500-1500ms depending on response complexity
- **TTS**: 200-500ms for typical responses
- **Total latency**: ~1-2 seconds from speech to audio response

---

## 📖 Documentation

- **README.md** (this file) - Project overview
- **QUICKSTART.md** - Fast setup guide  
- **ARCHITECTURE.md** - 4-worker reflex agent design
- **VISION_SETUP.md** - Comprehensive vision system guide
- **HOW_TO_RUN.md** - Detailed runtime instructions

---

## 🤖 Reflex Agent Behavior

Pluto follows a **state machine** for natural interaction:

```
IDLE → FACE_DETECTED → LOCKED_IN → GREETING → LISTENING → PROCESSING → RESPONDING → FACE_LOST → IDLE
```

**Key Behaviors:**
- 🔒 **Face Locking**: Once locked onto a person, ignores other faces in background
- ⏱️ **Loss Tolerance**: Allows 1.5 seconds of face absence before unlocking (handles brief occlusions)
- 🚫 **Greeting Cooldown**: 10-second cooldown prevents repeated greetings to same person
- ⏸️ **STT Pause/Resume**: Microphone only activates after face is locked and greeting sent (saves CPU)

---

**🪐 Project Pluto - Vision-driven reflex agent for proactive human-computer interaction**

*Built with reasoning and performance in mind.*
