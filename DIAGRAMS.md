# 📊 Project Pluto - Visual Diagrams

## 🗺️ System Overview Diagram

```
╔═══════════════════════════════════════════════════════════════════════╗
║                         🪐 PROJECT PLUTO                              ║
║              Offline Voice Assistant Test Architecture                ║
╚═══════════════════════════════════════════════════════════════════════╝

    👤 USER                          🖥️  LAPTOP
     │                                  │
     │ speaks                           │
     ▼                                  │
┌─────────────────┐                    │
│  🎤 MICROPHONE  │◀───────────────────┘
└────────┬────────┘
         │ Raw Audio (16kHz)
         ▼
╔════════════════════════════════════════════════════════════════════╗
║                    STT WORKER (Vosk)                               ║
║  ┌──────────┐   ┌──────┐   ┌────────────┐   ┌──────────────────┐ ║
║  │ PyAudio  │──▶│ VAD  │──▶│ Vosk Model │──▶│ Text Transcript  │ ║
║  │ Capture  │   │Energy│   │   ~40MB    │   │                  │ ║
║  └──────────┘   └──────┘   └────────────┘   └──────────────────┘ ║
╚════════════════════════════════════════════════════════════════════╝
         │ {"type": "transcript", "text": "hello"}
         ▼
    ┌─────────────────┐
    │  QUEUE 1: STT→LLM │  (Thread-safe, max 10 items)
    └─────────┬───────┘
         │ Transcript
         ▼
╔════════════════════════════════════════════════════════════════════╗
║                  LLM WORKER (Ollama + Qwen2.5)                     ║
║  ┌────────────┐   ┌──────────┐   ┌─────────────┐  ┌───────────┐  ║
║  │  Receive   │──▶│  Ollama  │──▶│  Qwen2.5    │──▶│ Response  │  ║
║  │ Transcript │   │ HTTP API │   │  1.5B-q4    │  │   Text    │  ║
║  └────────────┘   └──────────┘   └─────────────┘  └───────────┘  ║
╚════════════════════════════════════════════════════════════════════╝
         │ {"type": "response", "text": "Hi there!"}
         ▼
    ┌─────────────────┐
    │  QUEUE 2: LLM→TTS │  (Thread-safe, max 10 items)
    └─────────┬───────┘
         │ Response
         ▼
╔════════════════════════════════════════════════════════════════════╗
║                   TTS WORKER (Piper)                               ║
║  ┌────────────┐   ┌──────────┐   ┌──────────┐   ┌─────────────┐  ║
║  │  Receive   │──▶│  Piper   │──▶│   WAV    │──▶│  PyAudio    │  ║
║  │  Response  │   │  ONNX    │   │  22kHz   │   │  Playback   │  ║
║  └────────────┘   └──────────┘   └──────────┘   └─────────────┘  ║
╚════════════════════════════════════════════════════════════════════╝
         │ Audio Output
         ▼
┌─────────────────┐
│  🔊 SPEAKERS    │
└─────────────────┘
         │
         ▼
     👤 USER hears response

═══════════════════════════════════════════════════════════════════════

         ⏱️  METRICS LOGGER (Continuous Monitoring)
    ┌─────────────────────────────────────────────────────┐
    │  📊 Latencies | 💾 Memory | 📦 Queue Depths         │
    │  ├─ STT: 100-200ms                                  │
    │  ├─ LLM: 500-1500ms  ⚠️  BOTTLENECK                │
    │  ├─ TTS: 200-500ms                                  │
    │  └─ Total: 800-2200ms                               │
    │                                                      │
    │  Output: CSV + JSON + Console + Summary             │
    └─────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════
```

---

## 🧵 Thread Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       MAIN PROCESS                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  Main Thread (Orchestrator)                                │   │
│  │  - Initialize workers                                      │   │
│  │  - Monitor system health                                   │   │
│  │  - Handle shutdown signals                                 │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  STT Worker Thread (daemon)                                │   │
│  │  while running:                                            │   │
│  │      audio_data = stream.read()                            │   │
│  │      if is_speech(audio_data):                             │   │
│  │          text = vosk.recognize(audio_data)                 │   │
│  │          stt_to_llm_queue.put(text)                        │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  LLM Worker Thread (daemon)                                │   │
│  │  while running:                                            │   │
│  │      transcript = stt_to_llm_queue.get(timeout=1)          │   │
│  │      response = ollama.generate(transcript)                │   │
│  │      llm_to_tts_queue.put(response)                        │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  TTS Worker Thread (daemon)                                │   │
│  │  while running:                                            │   │
│  │      response = llm_to_tts_queue.get(timeout=1)            │   │
│  │      wav = piper.synthesize(response)                      │   │
│  │      audio.play(wav)                                       │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  Health Monitor Thread (daemon, optional)                  │   │
│  │  while running:                                            │   │
│  │      time.sleep(health_check_interval)                     │   │
│  │      log_memory_usage()                                    │   │
│  │      log_queue_depths()                                    │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Queue Message Flow

```
CONVERSATION CYCLE (Single User Query → Response)

Time   Component      Action                    Queue State
─────  ────────────   ───────────────────────   ────────────────────────
0ms    User           Starts speaking           Empty
...    STT            Capturing audio           Empty
2000ms STT            Silence detected          Empty
2150ms STT            Vosk inference complete   Empty
2151ms STT            put(transcript)           Q1: [transcript]

2152ms LLM            get(transcript)           Q1: Empty
2153ms LLM            Ollama API call...        Q1: Empty, Q2: Empty
2850ms LLM            Response received         Q1: Empty, Q2: Empty
2851ms LLM            put(response)             Q1: Empty, Q2: [response]

2852ms TTS            get(response)             Q1: Empty, Q2: Empty
2853ms TTS            Piper synthesis...        Q1: Empty, Q2: Empty
3150ms TTS            WAV ready, playing        Q1: Empty, Q2: Empty
4000ms TTS            Playback complete         Q1: Empty, Q2: Empty

═══════════════════════════════════════════════════════════════════════
Total Latency: 4000ms (from speech start to playback end)
User-Perceived Latency: 2000ms (from silence to speech start)
```

---

## 📈 Latency Waterfall

```
User speaks: "Hello"
│
├─ [0ms ─────────────── 2000ms] User Speaking + Silence Detection
│                                (STT waiting for silence)
│
└─▶ Speech Ends (t=2000ms)
    │
    ├─ [2000ms ── 2150ms] STT Processing (Vosk Inference)
    │                     ├─ Audio buffering: 50ms
    │                     ├─ Vosk recognition: 100ms
    │                     └─ Queue put: <1ms
    │
    └─▶ Transcript Ready: "hello" (t=2150ms)
        │
        ├─ [2150ms ─────────── 2850ms] LLM Processing (Ollama)
        │                               ├─ Queue get: <1ms
        │                               ├─ HTTP call: 10ms
        │                               ├─ Qwen2.5 inference: 680ms
        │                               └─ Queue put: <1ms
        │
        └─▶ Response Ready: "Hi there!" (t=2850ms)
            │
            ├─ [2850ms ──── 3150ms] TTS Processing (Piper)
            │                        ├─ Queue get: <1ms
            │                        ├─ Piper synthesis: 250ms
            │                        ├─ WAV write: 50ms
            │                        └─ Playback start: <1ms
            │
            └─▶ User Hears Response (t=3150ms)
                │
                └─ [3150ms ── 4000ms] Audio Playback Duration
                                      (depends on response length)

═══════════════════════════════════════════════════════════════════════
Breakdown:
  STT:   150ms  (6.5% of total)
  LLM:   700ms  (30% of total) ⚠️ BOTTLENECK
  TTS:   300ms  (13% of total)
  Play:  850ms  (36% of total, unavoidable)
  Other: 300ms  (13%, user speaking time not counted)
Total: 2300ms (user-perceived latency from silence to hearing response)
```

---

## 🏗️ Directory Structure

```
pluto/
│
├── 📄 README.md                    # Project overview
├── 📄 QUICKSTART.md                # 5-minute setup guide
├── 📄 DOCUMENTATION.md             # Complete technical reference
├── 📄 ARCHITECTURE.md              # Design decisions
├── 📄 DIAGRAMS.md                  # This file - visual references
├── 📄 FILE_INDEX.md                # Navigation guide
│
├── 📄 run.py                       # Entry point
├── 📄 requirements.txt             # Python dependencies
├── 📄 setup.py                     # Package configuration
├── 📄 .env.example                 # Environment template
├── 📄 .gitignore                   # Git exclusions
├── 📄 LICENSE                      # MIT License
│
├── 📁 src/                         # Source code
│   ├── 📄 __init__.py              # Package initialization
│   ├── 📄 config.py                # Configuration system
│   ├── 📄 metrics_logger.py        # Performance tracking
│   ├── 📄 orchestrator.py          # Main coordinator
│   │
│   └── 📁 workers/                 # Worker modules
│       ├── 📄 __init__.py          # Worker exports
│       ├── 📄 stt_worker.py        # Speech-to-Text (Vosk)
│       ├── 📄 llm_worker.py        # Language Model (Ollama)
│       └── 📄 tts_worker.py        # Text-to-Speech (Piper)
│
├── 📁 models/                      # Model storage (download separately)
│   ├── 📄 .gitkeep                 # Preserve directory
│   ├── 📁 vosk-model-small-en-us-0.15/  (download)
│   └── 📄 en_US-lessac-medium.onnx      (download)
│
├── 📁 logs/                        # Metrics output
│   ├── 📄 .gitkeep                 # Preserve directory
│   ├── 📄 metrics_YYYYMMDD_HHMMSS.csv
│   ├── 📄 metrics_YYYYMMDD_HHMMSS.json
│   └── 📄 summary_YYYYMMDD_HHMMSS.txt
│
└── 📁 tests/                       # Test suite
    └── 📄 test_integration.py      # Integration tests
```

---

## 🔄 State Transition Diagram

```
                    ┌─────────────────────┐
                    │   UNINITIALIZED     │
                    └──────────┬──────────┘
                               │ orchestrator.initialize()
                               ▼
                    ┌─────────────────────┐
              ┌────▶│    INITIALIZING     │────┐
              │     └──────────┬──────────┘    │ Worker fails
              │                │ All workers   │
              │                │ start OK      ▼
              │                ▼            ┌──────────┐
              │     ┌─────────────────────┐ │  ERROR   │
              │     │      READY          │ └──────────┘
              │     └──────────┬──────────┘
              │                │ orchestrator.run()
              │                ▼
              │     ┌─────────────────────┐
              │     │      RUNNING        │◀────┐
              │     │  (Processing audio) │     │ Continuous
              │     └──────────┬──────────┘     │ operation
              │                │                │
              │                ├────────────────┘
              │                │
              │                │ SIGINT / SIGTERM / Ctrl+C
              │                ▼
              │     ┌─────────────────────┐
              └─────│    SHUTTING DOWN    │
                    │ (Cleanup resources) │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      STOPPED        │
                    └─────────────────────┘
```

---

## 📊 Memory Usage Over Time

```
Memory (MB)
3000 │                                  ┌─ LLM Peak (inference)
     │                                  │
2500 │                    ┌─────────────┤
     │                    │             │
2000 │         ┌──────────┤             └─ LLM Idle
     │         │          │
1500 │    ┌────┤          │
     │    │    │          └─ TTS Active
1000 │    │    │
     │    │    └─ STT Active
 500 │    │
     │────┘─ Baseline (orchestrator + config)
   0 └────┬────┬────┬────┬────┬────┬────┬────▶ Time
        Init  STT  LLM  TTS Conv Conv Conv  Idle
             warm warm warm  #1   #2   #3

Baseline: ~50MB (Python + orchestrator)
+ STT:    ~150MB (Vosk model loaded)
+ LLM:    ~2GB (Qwen2.5 during inference, ~1.5GB idle)
+ TTS:    ~200MB (Piper model loaded)
Peak:     ~2.5GB (LLM inference + all components)
```

---

## 🎯 Bottleneck Identification

```
COMPONENT LATENCY COMPARISON (Typical Values)

STT (Vosk)           ████ 150ms          ⚡ Fast
                     

LLM (Qwen2.5)        ████████████████████████████ 850ms  ⚠️  BOTTLENECK
                     

TTS (Piper)          ███████ 300ms       ✅ Acceptable
                     

Audio Playback       ██████████████████ 600ms    ⏸️  Unavoidable
                     (depends on response length)


0ms        200ms      400ms      600ms      800ms     1000ms
├──────────┼──────────┼──────────┼──────────┼──────────┤

OPTIMIZATION PRIORITIES:
1. 🔴 LLM inference (try smaller model, better quantization, GPU?)
2. 🟡 TTS synthesis (try smaller Piper model for speed)
3. 🟢 STT already optimal for offline use
```

---

## 🔌 External Dependencies

```
                    ╔══════════════════════════╗
                    ║    PLUTO COMPONENTS      ║
                    ╚══════════════════════════╝
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐      ┌──────────────┐      ┌──────────────┐
│ Vosk Library  │      │   Ollama     │      │    Piper     │
│  (Embedded)   │      │   Server     │      │   Binary     │
└───────┬───────┘      └──────┬───────┘      └──────┬───────┘
        │                     │                      │
        ▼                     ▼                      ▼
┌───────────────┐      ┌──────────────┐      ┌──────────────┐
│ Vosk Model    │      │  Qwen2.5     │      │ Piper Model  │
│ vosk-model-   │      │  Model       │      │ en_US-lessac │
│ small-en-us   │      │  (pulled)    │      │ -medium.onnx │
│ ~40MB         │      │  ~1GB        │      │ ~60MB        │
└───────────────┘      └──────────────┘      └──────────────┘

Download locations:
• Vosk: https://alphacephei.com/vosk/models
• Ollama: ollama pull qwen2.5:1.5b-instruct-q4_K_M
• Piper: https://github.com/rhasspy/piper/releases
```

---

**All diagrams represent the actual implemented architecture.**  
See [ARCHITECTURE.md](ARCHITECTURE.md) for design rationale and [DOCUMENTATION.md](DOCUMENTATION.md) for code reference.
