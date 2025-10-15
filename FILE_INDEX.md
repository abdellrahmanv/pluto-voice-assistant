# 📑 Project Pluto - File Index

Quick navigation guide to all project files.

---

## 📖 Documentation Files

| File | Purpose | Read When... |
|------|---------|--------------|
| **README.md** | Project overview, quick intro | Starting with the project |
| **QUICKSTART.md** | 5-minute setup guide | Want to get running fast |
| **DOCUMENTATION.md** | Complete technical reference | Need detailed code docs |
| **ARCHITECTURE.md** | Design decisions and rationale | Understanding "why" choices made |
| **DIAGRAMS.md** | Visual system representations | Visual learner, need overview |
| **FILE_INDEX.md** | This file - navigation | Looking for specific file |

---

## 🚀 Entry Points

| File | Purpose | Command |
|------|---------|---------|
| **run.py** | Main application entry point | `python run.py` |
| **tests/test_integration.py** | Test suite runner | `pytest tests/test_integration.py -v` |

---

## ⚙️ Core Source Files

### Configuration & Infrastructure

| File | LOC | Purpose | Key Contents |
|------|-----|---------|--------------|
| **src/config.py** | ~350 | Centralized configuration | All settings, model paths, parameters |
| **src/metrics_logger.py** | ~250 | Performance tracking | CSV/JSON export, statistics |
| **src/orchestrator.py** | ~200 | System coordination | Thread management, lifecycle |

### Worker Modules

| File | LOC | Purpose | Technology |
|------|-----|---------|------------|
| **src/workers/stt_worker.py** | ~200 | Speech-to-Text | Vosk + PyAudio |
| **src/workers/llm_worker.py** | ~180 | Language Model | Ollama API + Qwen2.5 |
| **src/workers/tts_worker.py** | ~190 | Text-to-Speech | Piper + PyAudio |

### Package Initialization

| File | LOC | Purpose |
|------|-----|---------|
| **src/__init__.py** | ~10 | Main package metadata |
| **src/workers/__init__.py** | ~5 | Worker exports |

---

## 🗂️ Configuration Files

| File | Purpose | Notes |
|------|---------|-------|
| **requirements.txt** | Python dependencies | Use with `pip install -r` |
| **setup.py** | Package installation config | For `pip install -e .` |
| **.env.example** | Environment variable template | Copy to `.env` and customize |
| **.gitignore** | Git exclusions | Prevents model/log commits |
| **LICENSE** | MIT License | Open source terms |

---

## 📁 Directory Structure Reference

```
pluto/
├── 📄 Documentation (6 files)          # Start here
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── DOCUMENTATION.md
│   ├── ARCHITECTURE.md
│   ├── DIAGRAMS.md
│   └── FILE_INDEX.md (this file)
│
├── 📄 Config Files (5 files)           # Setup & dependencies
│   ├── requirements.txt
│   ├── setup.py
│   ├── .env.example
│   ├── .gitignore
│   └── LICENSE
│
├── 📄 Entry Points (1 file)            # Run from here
│   └── run.py
│
├── 📁 src/ (7 files)                   # Core implementation
│   ├── config.py                       # ⚙️  Configuration
│   ├── metrics_logger.py               # 📊 Performance tracking
│   ├── orchestrator.py                 # 🎯 Main coordinator
│   ├── __init__.py
│   └── workers/
│       ├── stt_worker.py               # 🎤 Speech recognition
│       ├── llm_worker.py               # 🧠 Language model
│       ├── tts_worker.py               # 🔊 Speech synthesis
│       └── __init__.py
│
├── 📁 models/                          # Download separately
│   ├── .gitkeep
│   ├── vosk-model-small-en-us-0.15/   # ~40MB
│   └── en_US-lessac-medium.onnx       # ~60MB
│
├── 📁 logs/                            # Generated at runtime
│   ├── .gitkeep
│   ├── metrics_*.csv                   # Time-series data
│   ├── metrics_*.json                  # Structured export
│   └── summary_*.txt                   # Statistical summary
│
└── 📁 tests/                           # Test suite
    └── test_integration.py             # ~280 lines
```

---

## 🎯 File Purposes by Use Case

### "I want to run the project"
1. **QUICKSTART.md** - Setup instructions
2. **run.py** - Execute this
3. **src/config.py** - Customize paths if needed

### "I want to understand the code"
1. **ARCHITECTURE.md** - Design overview
2. **DIAGRAMS.md** - Visual representations
3. **src/orchestrator.py** - Entry logic
4. **src/workers/** - Component implementations

### "I want to customize behavior"
1. **src/config.py** - All tunable parameters
2. **.env.example** - Environment variables
3. **src/workers/stt_worker.py** - VAD thresholds
4. **src/workers/llm_worker.py** - LLM parameters

### "I want to monitor performance"
1. **src/metrics_logger.py** - Metrics collection
2. **logs/metrics_*.csv** - Time-series data
3. **logs/summary_*.txt** - Statistical analysis

### "I want to test components"
1. **tests/test_integration.py** - Run tests
2. **pytest** - Test framework

### "I want to deploy to Raspberry Pi"
1. **ARCHITECTURE.md** - Performance considerations
2. **logs/** - Analyze laptop metrics first
3. **src/config.py** - Adjust for Pi hardware

---

## 📊 File Size Reference

| Category | Files | Total LOC | Description |
|----------|-------|-----------|-------------|
| Documentation | 6 | ~3,500 | All .md files |
| Source Code | 7 | ~1,370 | Python implementation |
| Tests | 1 | ~280 | Integration tests |
| Config | 5 | ~100 | Setup and dependencies |
| **Total** | **19** | **~5,250** | Complete project |

---

## 🔍 Finding Specific Functionality

### Audio Processing
- **Capture**: `src/workers/stt_worker.py` → `_process_audio()`
- **VAD**: `src/workers/stt_worker.py` → `_detect_speech()`
- **Playback**: `src/workers/tts_worker.py` → `_play_wav()`

### Model Integration
- **Vosk**: `src/workers/stt_worker.py` → `initialize()`
- **Ollama**: `src/workers/llm_worker.py` → `_generate()`
- **Piper**: `src/workers/tts_worker.py` → `_synthesize()`

### Queue Operations
- **STT→LLM**: `src/orchestrator.py` → `stt_to_llm_queue`
- **LLM→TTS**: `src/orchestrator.py` → `llm_to_tts_queue`

### Metrics Collection
- **Logging**: `src/metrics_logger.py` → `log_metric()`
- **Export**: `src/metrics_logger.py` → `export_json()`, `_save_summary()`
- **Statistics**: `src/metrics_logger.py` → `get_statistics()`

### System Control
- **Startup**: `src/orchestrator.py` → `initialize()`, `start()`
- **Shutdown**: `src/orchestrator.py` → `shutdown()`
- **Health**: `src/orchestrator.py` → `_health_monitor()`

---

## 📝 Editing Workflow

### Changing Model Paths
1. Edit `src/config.py`
2. Update `VOSK_CONFIG["model_path"]`
3. Update `PIPER_CONFIG["model_path"]`
4. Restart application

### Adjusting Performance Thresholds
1. Edit `src/config.py`
2. Modify `METRICS_CONFIG` values
3. Restart application
4. Check logs for new warnings

### Adding New Metrics
1. Edit `src/metrics_logger.py`
2. Add new metric type in `log_metric()` calls
3. Update `_check_thresholds()` if needed
4. Verify in CSV output

### Testing Changes
1. Make code modifications
2. Run `pytest tests/test_integration.py -v`
3. Fix any failing tests
4. Run full application with `python run.py`

---

## 🗺️ Code Flow Trace

**User speaks → Response heard**

1. `run.py` → Launches application
2. `src/orchestrator.py` → Initializes system
3. `src/workers/stt_worker.py` → Captures audio, recognizes speech
4. `src/orchestrator.py` → Routes through queue 1
5. `src/workers/llm_worker.py` → Generates response
6. `src/orchestrator.py` → Routes through queue 2
7. `src/workers/tts_worker.py` → Synthesizes and plays audio
8. `src/metrics_logger.py` → Records all latencies
9. `logs/*.csv` → Metrics saved

---

## 🏷️ Tags for Quick Search

**Performance**: `src/metrics_logger.py`, `src/config.py` (METRICS_CONFIG)  
**Audio**: `src/workers/stt_worker.py`, `src/workers/tts_worker.py`  
**AI/ML**: `src/workers/llm_worker.py`, `src/workers/stt_worker.py`  
**Threading**: `src/orchestrator.py`, all workers  
**Configuration**: `src/config.py`, `.env.example`  
**Testing**: `tests/test_integration.py`  
**Documentation**: All `.md` files  

---

**Navigation Tip**: Use your editor's file search (`Ctrl+P` in VS Code) to jump directly to files mentioned in this index.

Return to [README.md](README.md) for project overview.
