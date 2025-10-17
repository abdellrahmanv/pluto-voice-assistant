# 📊 Project Pluto - Visual Diagrams# 📊 Project Pluto - Visual Diagrams



## 🗺️ System Overview Diagram - Vision-Driven Reflex Agent## 🗺️ System Overview Diagram



``````

╔═══════════════════════════════════════════════════════════════════════╗╔═══════════════════════════════════════════════════════════════════════╗

║                         🪐 PROJECT PLUTO v2.0                         ║║                         🪐 PROJECT PLUTO                              ║

║         Vision-Driven Reflex Agent Voice Assistant                    ║║              Offline Voice Assistant Test Architecture                ║

║              (4-Worker Architecture + Face Detection)                 ║╚═══════════════════════════════════════════════════════════════════════╝

╚═══════════════════════════════════════════════════════════════════════╝

    👤 USER                          🖥️  LAPTOP

    👤 USER                          📹 CAMERA                🎤 MICROPHONE     │                                  │

     │                                  │                          │     │ speaks                           │

     │ appears                          │ rpicam-vid               │ (paused until     ▼                                  │

     ▼                                  ▼  @ 320x240, 10fps        │  face locked)┌─────────────────┐                    │

┌──────────────────────────────────────────────────────┐             ││  🎤 MICROPHONE  │◀───────────────────┘

│              VISION WORKER (YuNet)                   │             │└────────┬────────┘

│  ┌────────────┐  ┌─────────────┐  ┌───────────────┐ │             │         │ Raw Audio (16kHz)

│  │  rpicam    │─▶│ YuNet INT8  │─▶│  Face Lock    │ │             │         ▼

│  │  Process   │  │  Detector   │  │    Logic      │ │             │╔════════════════════════════════════════════════════════════════════╗

│  │  Capture   │  │   2.5MB     │  │  (Track ID)   │ │             │║                    STT WORKER (Vosk)                               ║

│  └────────────┘  └─────────────┘  └───────────────┘ │             │║  ┌──────────┐   ┌──────┐   ┌────────────┐   ┌──────────────────┐ ║

│           Terminal Preview (SSH): ASCII Art          │             │║  │ PyAudio  │──▶│ VAD  │──▶│ Vosk Model │──▶│ Text Transcript  │ ║

└──────────────┬───────────────────────────────────────┘             │║  │ Capture  │   │Energy│   │   ~40MB    │   │                  │ ║

               │ {"type": "face_detected", "face_id": 12345}         │║  └──────────┘   └──────┘   └────────────┘   └──────────────────┘ ║

               ▼                                                     │╚════════════════════════════════════════════════════════════════════╝

      ┌─────────────────────┐                                        │         │ {"type": "transcript", "text": "hello"}

      │ QUEUE: Vision→Orch  │ (Face events)                          │         ▼

      └──────────┬──────────┘                                        │    ┌─────────────────┐

                 │                                                   │    │  QUEUE 1: STT→LLM │  (Thread-safe, max 10 items)

                 ▼                                                   │    └─────────┬───────┘

╔═══════════════════════════════════════════════════════════════════════╗         │ Transcript

║                     🪐 ORCHESTRATOR                                   ║         ▼

║          (State Manager + Worker Coordinator)                         ║╔════════════════════════════════════════════════════════════════════╗

║                                                                        ║║                  LLM WORKER (Ollama + Qwen2.5)                     ║

║  ┌──────────────────┐     ┌────────────────────────────────┐         ║║  ┌────────────┐   ┌──────────┐   ┌─────────────┐  ┌───────────┐  ║

║  │  Agent State     │     │  Face Event Processor          │         ║║  │  Receive   │──▶│  Ollama  │──▶│  Qwen2.5    │──▶│ Response  │  ║

║  │  Machine         │     │  • face_detected → Greet      │         ║║  │ Transcript │   │ HTTP API │   │  1.5B-q4    │  │   Text    │  ║

║  │  IDLE → LOCKED   │     │  • face_lost → Reset          │         ║║  └────────────┘   └──────────┘   └─────────────┘  └───────────┘  ║

║  │  → GREETING →... │     │  • Controls STT pause/resume  │         ║╚════════════════════════════════════════════════════════════════════╝

║  └──────────────────┘     └────────────────────────────────┘         ║         │ {"type": "response", "text": "Hi there!"}

║                                                                        ║         ▼

║  Face locked? → Resume STT ────────────────────────────────────┐      ║    ┌─────────────────┐

║  Face lost? → Pause STT, Clear history                         │      ║    │  QUEUE 2: LLM→TTS │  (Thread-safe, max 10 items)

╚═══════════════════════════════════════════════════════════════│══════╝    └─────────┬───────┘

                                                                 │         │ Response

                 ┌───────────────────────────────────────────────┘         ▼

                 │ {"type": "greeting", "text": "Hi there!"}╔════════════════════════════════════════════════════════════════════╗

                 ▼║                   TTS WORKER (Piper)                               ║

╔═══════════════════════════════════════════════════════════════════════╗║  ┌────────────┐   ┌──────────┐   ┌──────────┐   ┌─────────────┐  ║

║                    STT WORKER (Whisper Tiny)                          ║║  │  Receive   │──▶│  Piper   │──▶│   WAV    │──▶│  PyAudio    │  ║

║  ┌──────────┐   ┌──────┐   ┌────────────┐   ┌──────────────────┐    ║║  │  Response  │   │  ONNX    │   │  22kHz   │   │  Playback   │  ║

║  │ PyAudio  │──▶│ VAD  │──▶│  Whisper   │──▶│ Text Transcript  │    ║║  └────────────┘   └──────────┘   └──────────┘   └─────────────┘  ║

║  │ Capture  │   │Energy│   │  Tiny 39MB │   │                  │    ║╚════════════════════════════════════════════════════════════════════╝

║  └──────────┘   └──────┘   └────────────┘   └──────────────────┘    ║         │ Audio Output

║                          ⏸️ PAUSE/RESUME Control                       ║         ▼

╚═══════════════════════════════════════════════════════════════════════╝┌─────────────────┐

         │ {"type": "transcript", "text": "what's the weather"}│  🔊 SPEAKERS    │

         ▼└─────────────────┘

    ┌─────────────────────┐         │

    │  QUEUE: STT→LLM     │  (Thread-safe, max 10)         ▼

    └─────────┬───────────┘     👤 USER hears response

         │ Transcript or Greeting

         ▼═══════════════════════════════════════════════════════════════════════

╔═══════════════════════════════════════════════════════════════════════╗

║                  LLM WORKER (Ollama + Qwen2.5)                        ║         ⏱️  METRICS LOGGER (Continuous Monitoring)

║  ┌────────────┐   ┌──────────┐   ┌─────────────┐  ┌───────────┐     ║    ┌─────────────────────────────────────────────────────┐

║  │  Receive   │──▶│  Ollama  │──▶│ Qwen2.5:0.5b│──▶│ Response  │     ║    │  📊 Latencies | 💾 Memory | 📦 Queue Depths         │

║  │ Text Input │   │ HTTP API │   │     q4_k_M  │  │   Text    │     ║    │  ├─ STT: 100-200ms                                  │

║  └────────────┘   └──────────┘   └─────────────┘  └───────────┘     ║    │  ├─ LLM: 500-1500ms  ⚠️  BOTTLENECK                │

║          Context: Face present? Keep history                          ║    │  ├─ TTS: 200-500ms                                  │

╚═══════════════════════════════════════════════════════════════════════╝    │  └─ Total: 800-2200ms                               │

         │ {"type": "response", "text": "It's sunny today!"}    │                                                      │

         ▼    │  Output: CSV + JSON + Console + Summary             │

    ┌─────────────────────┐    └─────────────────────────────────────────────────────┘

    │  QUEUE: LLM→TTS     │  (Thread-safe, max 10)

    └─────────┬───────────┘═══════════════════════════════════════════════════════════════════════

         │ Response```

         ▼

╔═══════════════════════════════════════════════════════════════════════╗---

║                   TTS WORKER (Piper)                                  ║

║  ┌────────────┐   ┌──────────┐   ┌──────────┐   ┌─────────────┐     ║## 🧵 Thread Architecture

║  │  Receive   │──▶│  Piper   │──▶│   WAV    │──▶│  PyAudio    │     ║

║  │  Response  │   │  en_US   │   │  Audio   │   │  Playback   │     ║```

║  └────────────┘   └──────────┘   └──────────┘   └─────────────┘     ║┌─────────────────────────────────────────────────────────────────────┐

╚═══════════════════════════════════════════════════════════════════════╝│                       MAIN PROCESS                                  │

         │ Audio Output├─────────────────────────────────────────────────────────────────────┤

         ▼│                                                                     │

    🔊 SPEAKER ──▶ 👤 USER hears response│  ┌────────────────────────────────────────────────────────────┐   │

```│  │  Main Thread (Orchestrator)                                │   │

│  │  - Initialize workers                                      │   │

---│  │  - Monitor system health                                   │   │

│  │  - Handle shutdown signals                                 │   │

## 🔄 State Machine Diagram│  └────────────────────────────────────────────────────────────┘   │

│                                                                     │

```│  ┌────────────────────────────────────────────────────────────┐   │

╔════════════════════════════════════════════════════════════════════╗│  │  STT Worker Thread (daemon)                                │   │

║              PLUTO REFLEX AGENT STATE MACHINE                      ║│  │  while running:                                            │   │

╚════════════════════════════════════════════════════════════════════╝│  │      audio_data = stream.read()                            │   │

│  │      if is_speech(audio_data):                             │   │

    ┌─────────────────────────────────────────────────────────┐│  │          text = vosk.recognize(audio_data)                 │   │

    │                                                         ││  │          stt_to_llm_queue.put(text)                        │   │

    │   ┌─────────┐                                           ││  └────────────────────────────────────────────────────────────┘   │

    │   │  IDLE   │◀──────────────────────────────────────┐   ││                                                                     │

    │   │         │  Face lost timeout (1.5s)             │   ││  ┌────────────────────────────────────────────────────────────┐   │

    │   │ Vision: │  OR person leaves                     │   ││  │  LLM Worker Thread (daemon)                                │   │

    │   │Scanning │                                       │   ││  │  while running:                                            │   │

    │   │ STT:    │                                       │   ││  │      transcript = stt_to_llm_queue.get(timeout=1)          │   │

    │   │ Paused  │                                       │   ││  │      response = ollama.generate(transcript)                │   │

    │   └────┬────┘                                   ┌───┴────────┐│  │      llm_to_tts_queue.put(response)                        │   │

    │        │                                        │ FACE_LOST  ││  └────────────────────────────────────────────────────────────┘   │

    │        │ Face detected (3+ frames)              │            ││                                                                     │

    │        │                                        │ • Clear    ││  ┌────────────────────────────────────────────────────────────┐   │

    │        ▼                                        │   history  ││  │  TTS Worker Thread (daemon)                                │   │

    │   ┌──────────────┐                             │ • Unlock   ││  │  while running:                                            │   │

    │   │FACE_DETECTED │                             │   face     ││  │      response = llm_to_tts_queue.get(timeout=1)            │   │

    │   │              │                             │ • Pause STT││  │      wav = piper.synthesize(response)                      │   │

    │   │ • Assign ID  │                             └────────────┘│  │      audio.play(wav)                                       │   │

    │   │ • Lock face  │                                      ▲│  └────────────────────────────────────────────────────────────┘   │

    │   └──────┬───────┘                                      ││                                                                     │

    │          │                                              ││  ┌────────────────────────────────────────────────────────────┐   │

    │          │ Orchestrator prepares                        ││  │  Health Monitor Thread (daemon, optional)                  │   │

    │          ▼                                              ││  │  while running:                                            │   │

    │   ┌──────────────┐                                      ││  │      time.sleep(health_check_interval)                     │   │

    │   │  LOCKED_IN   │                                      ││  │      log_memory_usage()                                    │   │

    │   │              │                                      ││  │      log_queue_depths()                                    │   │

    │   │ Face locked  │                                      ││  └────────────────────────────────────────────────────────────┘   │

    │   │ to person    │                                      ││                                                                     │

    │   └──────┬───────┘                                      │└─────────────────────────────────────────────────────────────────────┘

    │          │                                              │```

    │          │ Inject greeting                              │

    │          ▼                                              │---

    │   ┌──────────────┐                                      │

    │   │   GREETING   │                                      │## 📦 Queue Message Flow

    │   │              │                                      │

    │   │ LLM generates│                                      │```

    │   │ welcome msg  │                                      │CONVERSATION CYCLE (Single User Query → Response)

    │   └──────┬───────┘                                      │

    │          │                                              │Time   Component      Action                    Queue State

    │          │ TTS plays greeting                           │─────  ────────────   ───────────────────────   ────────────────────────

    │          ▼                                              │0ms    User           Starts speaking           Empty

    │   ┌──────────────┐                                      │...    STT            Capturing audio           Empty

    │   │  LISTENING   │◀─────────────┐                       │2000ms STT            Silence detected          Empty

    │   │              │              │                       │2150ms STT            Vosk inference complete   Empty

    │   │ STT: Active  │              │ TTS done              │2151ms STT            put(transcript)           Q1: [transcript]

    │   │ Waiting for  │              │                       │

    │   │ user speech  │              │                       │2152ms LLM            get(transcript)           Q1: Empty

    │   └──────┬───────┘              │                       │2153ms LLM            Ollama API call...        Q1: Empty, Q2: Empty

    │          │                  ┌───┴────────┐              │2850ms LLM            Response received         Q1: Empty, Q2: Empty

    │          │ User speaks      │ RESPONDING │              │2851ms LLM            put(response)             Q1: Empty, Q2: [response]

    │          ▼                  │            │              │

    │   ┌──────────────┐          │ TTS plays  │              │2852ms TTS            get(response)             Q1: Empty, Q2: Empty

    │   │ PROCESSING   │          │ response   │              │2853ms TTS            Piper synthesis...        Q1: Empty, Q2: Empty

    │   │              │──────────▶            │              │3150ms TTS            WAV ready, playing        Q1: Empty, Q2: Empty

    │   │ LLM thinking │ Response  └────────────┘              │4000ms TTS            Playback complete         Q1: Empty, Q2: Empty

    │   └──────────────┘ ready                                │

    │                                                          │═══════════════════════════════════════════════════════════════════════

    │   Vision Worker: Continuously tracking face in background│Total Latency: 4000ms (from speech start to playback end)

    │   • If face lost for 1.5s → FACE_LOST state             │User-Perceived Latency: 2000ms (from silence to speech start)

    │   • Tracks face position, updates metrics               │```

    └─────────────────────────────────────────────────────────┘

```---



---## 📈 Latency Waterfall



## 🎯 Vision System Flow```

User speaks: "Hello"

```│

╔════════════════════════════════════════════════════════════════════╗├─ [0ms ─────────────── 2000ms] User Speaking + Silence Detection

║                  VISION WORKER - FACE DETECTION FLOW               ║│                                (STT waiting for silence)

╚════════════════════════════════════════════════════════════════════╝│

└─▶ Speech Ends (t=2000ms)

  START: Camera Initialization    │

         │    ├─ [2000ms ── 2150ms] STT Processing (Vosk Inference)

         ▼    │                     ├─ Audio buffering: 50ms

    ┌─────────────────────┐    │                     ├─ Vosk recognition: 100ms

    │  Start rpicam-vid   │    │                     └─ Queue put: <1ms

    │  • Resolution: 320x240    │

    │  • FPS: 10          │    └─▶ Transcript Ready: "hello" (t=2150ms)

    │  • Format: RGB24    │        │

    └──────────┬──────────┘        ├─ [2150ms ─────────── 2850ms] LLM Processing (Ollama)

               │        │                               ├─ Queue get: <1ms

               ▼        │                               ├─ HTTP call: 10ms

    ┌─────────────────────┐        │                               ├─ Qwen2.5 inference: 680ms

    │  Load YuNet Model   │        │                               └─ Queue put: <1ms

    │  • INT8 quantized   │        │

    │  • Size: 2.5MB      │        └─▶ Response Ready: "Hi there!" (t=2850ms)

    │  • Input: 320x240   │            │

    └──────────┬──────────┘            ├─ [2850ms ──── 3150ms] TTS Processing (Piper)

               │            │                        ├─ Queue get: <1ms

               ▼            │                        ├─ Piper synthesis: 250ms

    ╔═══════════════════════════════════════════╗            │                        ├─ WAV write: 50ms

    ║        MAIN DETECTION LOOP                ║            │                        └─ Playback start: <1ms

    ║                                           ║            │

    ║  ┌──────────────────┐                    ║            └─▶ User Hears Response (t=3150ms)

    ║  │  Read Frame      │                    ║                │

    ║  │  from Camera     │                    ║                └─ [3150ms ── 4000ms] Audio Playback Duration

    ║  └────────┬─────────┘                    ║                                      (depends on response length)

    ║           │                               ║

    ║           ▼                               ║═══════════════════════════════════════════════════════════════════════

    ║  ┌──────────────────┐   Skip?            ║Breakdown:

    ║  │  Frame Skip      │────Yes──▶ Continue ║  STT:   150ms  (6.5% of total)

    ║  │  (Process 1/3)   │                    ║  LLM:   700ms  (30% of total) ⚠️ BOTTLENECK

    ║  └────────┬─────────┘                    ║  TTS:   300ms  (13% of total)

    ║           │ No                            ║  Play:  850ms  (36% of total, unavoidable)

    ║           ▼                               ║  Other: 300ms  (13%, user speaking time not counted)

    ║  ┌──────────────────┐                    ║Total: 2300ms (user-perceived latency from silence to hearing response)

    ║  │ YuNet Inference  │                    ║```

    ║  │ (~50-80ms)       │                    ║

    ║  └────────┬─────────┘                    ║---

    ║           │                               ║

    ║           ▼                               ║## 🏗️ Directory Structure

    ║  ┌──────────────────┐                    ║

    ║  │  Faces Detected? │────No──▶           ║```

    ║  └────────┬─────────┘         │          ║pluto/

    ║           │ Yes                ▼          ║│

    ║           ▼          ┌─────────────────┐ ║├── 📄 README.md                    # Project overview

    ║  ┌──────────────────┐│  Check Face     │ ║├── 📄 QUICKSTART.md                # 5-minute setup guide

    ║  │  Filter by       ││  Lost Timeout   │ ║├── 📄 DOCUMENTATION.md             # Complete technical reference

    ║  │  Confidence      ││  (1.5s)         │ ║├── 📄 ARCHITECTURE.md              # Design decisions

    ║  │  (threshold:0.6) │└─────────┬───────┘ ║├── 📄 DIAGRAMS.md                  # This file - visual references

    ║  └────────┬─────────┘           │        ║├── 📄 FILE_INDEX.md                # Navigation guide

    ║           │              Timeout?│        ║│

    ║           ▼                      ▼        ║├── 📄 run.py                       # Entry point

    ║  ┌──────────────────┐   ┌──────────────┐ ║├── 📄 requirements.txt             # Python dependencies

    ║  │  Face Locked?    │   │ Emit:        │ ║├── 📄 setup.py                     # Package configuration

    ║  └────────┬─────────┘   │ face_lost    │ ║├── 📄 .env.example                 # Environment template

    ║           │              │ Unlock face  │ ║├── 📄 .gitignore                   # Git exclusions

    ║     No    │   Yes        └──────────────┘ ║├── 📄 LICENSE                      # MIT License

    ║    ┌──────┴──────┐                        ║│

    ║    ▼             ▼                        ║├── 📁 src/                         # Source code

    ║ ┌─────────┐  ┌──────────┐                ║│   ├── 📄 __init__.py              # Package initialization

    ║ │  NEW    │  │ TRACKING │                ║│   ├── 📄 config.py                # Configuration system

    ║ │  FACE   │  │ EXISTING │                ║│   ├── 📄 metrics_logger.py        # Performance tracking

    ║ └────┬────┘  │   FACE   │                ║│   ├── 📄 orchestrator.py          # Main coordinator

    ║      │       └─────┬────┘                ║│   │

    ║      ▼             ▼                      ║│   └── 📁 workers/                 # Worker modules

    ║ ┌────────────────────────┐               ║│       ├── 📄 __init__.py          # Worker exports

    ║ │ Assign ID,             │               ║│       ├── 📄 stt_worker.py        # Speech-to-Text (Vosk)

    ║ │ Lock onto face         │               ║│       ├── 📄 llm_worker.py        # Language Model (Ollama)

    ║ │ Emit: face_detected    │               ║│       └── 📄 tts_worker.py        # Text-to-Speech (Piper)

    ║ └────────────────────────┘               ║│

    ║      │             │                      ║├── 📁 models/                      # Model storage (download separately)

    ║      ▼             ▼                      ║│   ├── 📄 .gitkeep                 # Preserve directory

    ║ ┌────────────────────────────────┐       ║│   ├── 📁 vosk-model-small-en-us-0.15/  (download)

    ║ │  Terminal Preview (Optional)   │       ║│   └── 📄 en_US-lessac-medium.onnx      (download)

    ║ │  • Draw ASCII art frame        │       ║│

    ║ │  • Show detection boxes        │       ║├── 📁 logs/                        # Metrics output

    ║ │  • Display FPS, state          │       ║│   ├── 📄 .gitkeep                 # Preserve directory

    ║ └────────────────────────────────┘       ║│   ├── 📄 metrics_YYYYMMDD_HHMMSS.csv

    ║                │                          ║│   ├── 📄 metrics_YYYYMMDD_HHMMSS.json

    ║                ▼                          ║│   └── 📄 summary_YYYYMMDD_HHMMSS.txt

    ║           Loop back ──────────────────────╫──┐│

    ╚═══════════════════════════════════════════╝  │└── 📁 tests/                       # Test suite

                                                    │    └── 📄 test_integration.py      # Integration tests

                                                    │```

    ┌───────────────────────────────────────────────┘

    │---

    ▼

  STOP: Camera Cleanup (SIGTERM → SIGKILL if needed)## 🔄 State Transition Diagram

```

```

---                    ┌─────────────────────┐

                    │   UNINITIALIZED     │

## 🔗 Data Flow Sequence                    └──────────┬──────────┘

                               │ orchestrator.initialize()

```                               ▼

╔════════════════════════════════════════════════════════════════════╗                    ┌─────────────────────┐

║              END-TO-END INTERACTION SEQUENCE                       ║              ┌────▶│    INITIALIZING     │────┐

╚════════════════════════════════════════════════════════════════════╝              │     └──────────┬──────────┘    │ Worker fails

              │                │ All workers   │

TIME    VISION          ORCHESTRATOR    STT         LLM         TTS              │                │ start OK      ▼

────────────────────────────────────────────────────────────────────              │                ▼            ┌──────────┐

t=0s    Scanning...     State: IDLE     PAUSED      -           -              │     ┌─────────────────────┐ │  ERROR   │

        (5 fps)              │     │      READY          │ └──────────┘

              │     └──────────┬──────────┘

t=0.2s  Face detected!                │                │ orchestrator.run()

        face_id: 123                  │                ▼

        ─────────────▶                │     ┌─────────────────────┐

              │     │      RUNNING        │◀────┐

t=0.3s                  State: LOCKED              │     │  (Processing audio) │     │ Continuous

                        Lock face 123              │     └──────────┬──────────┘     │ operation

                        Inject greeting              │                │                │

                        ──────────────────────────▶ "Hi there!"              │                ├────────────────┘

              │                │

t=0.4s                                                          LLM thinks              │                │ SIGINT / SIGTERM / Ctrl+C

                                                                (2-3s)              │                ▼

              │     ┌─────────────────────┐

t=2.7s                                              Response:               └─────│    SHUTTING DOWN    │

                                                    "Hello! How                    │ (Cleanup resources) │

                                                     can I help?"                    └──────────┬──────────┘

                                                    ──────────▶                               │

                               ▼

t=2.8s                                                          Piper                    ┌─────────────────────┐

                                                                synthesizes                    │      STOPPED        │

                                                                (300ms)                    └─────────────────────┘

```

t=3.1s                  State: GREETING                         Playing...

                                                                🔊---



t=4.5s  Tracking face   State: LISTENING  RESUMED## 📊 Memory Usage Over Time

        (background)    Resume STT        Listening...

                        ──────────────▶```

Memory (MB)

t=5.0s                                    User speaks:3000 │                                  ┌─ LLM Peak (inference)

                                          "What's the     │                                  │

                                          weather?"2500 │                    ┌─────────────┤

     │                    │             │

t=5.8s                                    Transcription2000 │         ┌──────────┤             └─ LLM Idle

                                          complete     │         │          │

                                          ──────────▶1500 │    ┌────┤          │

     │    │    │          └─ TTS Active

t=5.9s                  State: PROCESSING             LLM thinks1000 │    │    │

                                          ──────────▶ (3s)     │    │    └─ STT Active

 500 │    │

t=8.9s                                                Response:     │────┘─ Baseline (orchestrator + config)

                                                      "It's    0 └────┬────┬────┬────┬────┬────┬────┬────▶ Time

                                                      sunny!"        Init  STT  LLM  TTS Conv Conv Conv  Idle

                                                      ──────────▶             warm warm warm  #1   #2   #3



t=9.0s                  State: RESPONDING                       SynthesizingBaseline: ~50MB (Python + orchestrator)

                                                                (250ms)+ STT:    ~150MB (Vosk model loaded)

+ LLM:    ~2GB (Qwen2.5 during inference, ~1.5GB idle)

t=9.3s                                                          Playing 🔊+ TTS:    ~200MB (Piper model loaded)

                                                                ───────────▶Peak:     ~2.5GB (LLM inference + all components)

```

t=10.5s                 State: LISTENING  Listening

                        (loop continues)  again...---



...## 🎯 Bottleneck Identification



t=15.0s Face lost!```

        (timeout 1.5s)COMPONENT LATENCY COMPARISON (Typical Values)

        ─────────────▶

STT (Vosk)           ████ 150ms          ⚡ Fast

t=15.1s                 State: FACE_LOST                     

                        Pause STT

                        Clear historyLLM (Qwen2.5)        ████████████████████████████ 850ms  ⚠️  BOTTLENECK

                        ──────────────▶  PAUSED                     

                        

t=15.2s Scanning...     State: IDLE      PAUSED      -          -TTS (Piper)          ███████ 300ms       ✅ Acceptable

        (loop restarts)                     

```

Audio Playback       ██████████████████ 600ms    ⏸️  Unavoidable

---                     (depends on response length)



## 📊 Performance Breakdown - Raspberry Pi 4

0ms        200ms      400ms      600ms      800ms     1000ms

```├──────────┼──────────┼──────────┼──────────┼──────────┤

╔════════════════════════════════════════════════════════════════════╗

║           COMPONENT PERFORMANCE (Raspberry Pi 4, 4GB RAM)          ║OPTIMIZATION PRIORITIES:

╚════════════════════════════════════════════════════════════════════╝1. 🔴 LLM inference (try smaller model, better quantization, GPU?)

2. 🟡 TTS synthesis (try smaller Piper model for speed)

VISION WORKER (YuNet)3. 🟢 STT already optimal for offline use

┌─────────────────────────────────────────────────────────────┐```

│  Camera Read        │████░░░░░░░░░░░░░░░░░░░░░░░░│  10-20ms │

│  YuNet Inference    │███████████░░░░░░░░░░░░░░░░░│  50-80ms │---

│  Face Tracking      │██░░░░░░░░░░░░░░░░░░░░░░░░░░│   5-10ms │

│  Event Queue        │█░░░░░░░░░░░░░░░░░░░░░░░░░░░│   1-2ms  │## 🔌 External Dependencies

│  TOTAL/FRAME        │████████████████░░░░░░░░░░░░│  66-112ms│

└─────────────────────────────────────────────────────────────┘```

CPU: 15-25% (single core)  |  Memory: ~50MB  |  FPS: ~5 (effective)                    ╔══════════════════════════╗

                    ║    PLUTO COMPONENTS      ║

STT WORKER (Whisper Tiny)                    ╚══════════════════════════╝

┌─────────────────────────────────────────────────────────────┐                               │

│  Audio Capture      │████░░░░░░░░░░░░░░░░░░░░░░░░│  20-50ms │        ┌──────────────────────┼──────────────────────┐

│  VAD Detection      │██░░░░░░░░░░░░░░░░░░░░░░░░░░│   5-15ms │        │                      │                      │

│  Whisper Inference  │████████████████████████████│ 500-1000ms│        ▼                      ▼                      ▼

│  Queue Output       │█░░░░░░░░░░░░░░░░░░░░░░░░░░░│   1-5ms  │┌───────────────┐      ┌──────────────┐      ┌──────────────┐

│  TOTAL/UTTERANCE    │████████████████████████████│ 526-1070ms││ Vosk Library  │      │   Ollama     │      │    Piper     │

└─────────────────────────────────────────────────────────────┘│  (Embedded)   │      │   Server     │      │   Binary     │

CPU: 70-90% (during transcription)  |  Memory: ~200MB└───────┬───────┘      └──────┬───────┘      └──────┬───────┘

        │                     │                      │

LLM WORKER (Qwen2.5:0.5b)        ▼                     ▼                      ▼

┌─────────────────────────────────────────────────────────────┐┌───────────────┐      ┌──────────────┐      ┌──────────────┐

│  Ollama API Call    │███░░░░░░░░░░░░░░░░░░░░░░░░░│  50-100ms││ Vosk Model    │      │  Qwen2.5     │      │ Piper Model  │

│  Token Generation   │████████████████████████████│ 2000-4000ms││ vosk-model-   │      │  Model       │      │ en_US-lessac │

│  Streaming Buffer   │██░░░░░░░░░░░░░░░░░░░░░░░░░░│  10-50ms ││ small-en-us   │      │  (pulled)    │      │ -medium.onnx │

│  Queue Output       │█░░░░░░░░░░░░░░░░░░░░░░░░░░░│   1-5ms  ││ ~40MB         │      │  ~1GB        │      │ ~60MB        │

│  TOTAL/RESPONSE     │████████████████████████████│ 2061-4155ms│└───────────────┘      └──────────────┘      └──────────────┘

└─────────────────────────────────────────────────────────────┘

CPU: 80-100% (during generation)  |  Memory: ~400MB  |  Tokens/s: 5-8Download locations:

• Vosk: https://alphacephei.com/vosk/models

TTS WORKER (Piper)• Ollama: ollama pull qwen2.5:0.5b-instruct-q4_k_M

┌─────────────────────────────────────────────────────────────┐• Piper: https://github.com/rhasspy/piper/releases

│  Text Parsing       │██░░░░░░░░░░░░░░░░░░░░░░░░░░│  10-20ms │```

│  Piper Synthesis    │████████████████░░░░░░░░░░░░│ 200-400ms│

│  WAV Generation     │███░░░░░░░░░░░░░░░░░░░░░░░░░│  20-50ms │---

│  Audio Playback     │█████░░░░░░░░░░░░░░░░░░░░░░░│  30-80ms │

│  TOTAL/SENTENCE     │████████████████████░░░░░░░░│ 260-550ms│**All diagrams represent the actual implemented architecture.**  

└─────────────────────────────────────────────────────────────┘See [ARCHITECTURE.md](ARCHITECTURE.md) for design rationale and [DOCUMENTATION.md](DOCUMENTATION.md) for code reference.

CPU: 40-60% (during synthesis)  |  Memory: ~100MB

SYSTEM TOTALS
┌─────────────────────────────────────────────────────────────┐
│  Idle (Vision only) │ CPU: 5-10%    Memory: 250MB            │
│  Active (All)       │ CPU: 90-100%  Memory: 800MB-1GB        │
│  Face→Greeting      │ ~1-2 seconds                           │
│  User→Response      │ ~4-7 seconds (end-to-end)              │
└─────────────────────────────────────────────────────────────┘

BOTTLENECKS (in order):
1. 🔴 LLM Inference    (2-4s) - MAJOR bottleneck
2. 🟠 STT Processing   (0.5-1s) - Secondary bottleneck  
3. 🟢 Vision Detection (66-112ms) - Minimal impact
4. 🟢 TTS Synthesis    (260-550ms) - Acceptable
```

---

## 🧪 Testing & Monitoring

### Test Scenarios

```
╔════════════════════════════════════════════════════════════════════╗
║                     CRITICAL TEST SCENARIOS                        ║
╚════════════════════════════════════════════════════════════════════╝

TEST 1: Vision System Performance
┌────────────────────────────────────────────────────────┐
│  1. Start system with vision worker only               │
│  2. Move face in/out of camera view                    │
│  3. Monitor:                                           │
│     • Face detection latency (should be <100ms)        │
│     • False positive rate (should be <5%)              │
│     • FPS (should maintain ~5 fps)                     │
│     • CPU usage (should be <30%)                       │
│  4. Run for 10 minutes, check stability                │
└────────────────────────────────────────────────────────┘

TEST 2: Face Lock/Unlock Behavior  
┌────────────────────────────────────────────────────────┐
│  1. Appear in front of camera                          │
│  2. Verify greeting plays within 2 seconds             │
│  3. Walk away from camera                              │
│  4. Verify face_lost event after 1.5s timeout          │
│  5. Return to camera                                   │
│  6. Verify new greeting (fresh conversation)           │
└────────────────────────────────────────────────────────┘

TEST 3: End-to-End Latency
┌────────────────────────────────────────────────────────┐
│  Measure: Face appears → Greeting plays                │
│  Expected: 1-2 seconds                                 │
│  Measure: User speaks → Response plays                 │
│  Expected: 4-7 seconds                                 │
└────────────────────────────────────────────────────────┘

TEST 4: Long-Running Stability
┌────────────────────────────────────────────────────────┐
│  1. Run system for 1 hour                              │
│  2. Simulate 10+ face lock/unlock cycles               │
│  3. Monitor:                                           │
│     • Memory leaks (should stay <1.2GB)                │
│     • CPU temperature (should stay <75°C)              │
│     • Camera process cleanup (no zombie processes)     │
│     • Queue overflow (should never happen)             │
└────────────────────────────────────────────────────────┘

TEST 5: Multiple Face Handling
┌────────────────────────────────────────────────────────┐
│  1. Have 2+ people in frame                            │
│  2. Verify locks onto closest/largest face             │
│  3. Verify ignores other faces while locked            │
│  4. Locked person leaves, verify unlock                │
│  5. Verify locks onto remaining person                 │
└────────────────────────────────────────────────────────┘
```

---

## 📈 Metrics Dashboard (Conceptual)

```
╔════════════════════════════════════════════════════════════════════╗
║                    PLUTO METRICS DASHBOARD                         ║
║                   (logs/metrics_*.csv/json)                        ║
╚════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────┐
│ VISION METRICS                                                  │
├─────────────────────────────────────────────────────────────────┤
│  FPS:           █████ 5.2                                       │
│  Latency:       ████████ 67ms                                   │
│  Face Locked:   🟢 YES (ID: 12345)                              │
│  Lock Duration: 45.3s                                           │
│  Face Count:    █ 1                                             │
├─────────────────────────────────────────────────────────────────┤
│ STT METRICS                                                     │
├─────────────────────────────────────────────────────────────────┤
│  Latency:       ████████████████ 823ms                          │
│  Status:        🟢 ACTIVE (Listening)                           │
│  Last Text:     "what's the weather"                            │
├─────────────────────────────────────────────────────────────────┤
│ LLM METRICS                                                     │
├─────────────────────────────────────────────────────────────────┤
│  Latency:       ██████████████████████████ 3214ms               │
│  Tokens:        ████ 42                                         │
│  Last Response: "It's sunny and 75°F today!"                    │
├─────────────────────────────────────────────────────────────────┤
│ TTS METRICS                                                     │
├─────────────────────────────────────────────────────────────────┤
│  Latency:       ███████ 312ms                                   │
│  Audio Length:  ██████ 2.8s                                     │
│  Status:        🔊 PLAYING                                      │
├─────────────────────────────────────────────────────────────────┤
│ SYSTEM METRICS                                                  │
├─────────────────────────────────────────────────────────────────┤
│  CPU:           ████████████████████████ 92%                    │
│  Memory:        ████████████████ 847 MB                         │
│  Temperature:   ████████████ 68°C                               │
│  Queue Sizes:   Vision:2  STT→LLM:0  LLM→TTS:1                  │
│  Uptime:        02:34:12                                        │
└─────────────────────────────────────────────────────────────────┘

Key Performance Indicators (KPIs):
✅ Vision FPS > 4                    ✅ Achieved (5.2)
✅ Face detection < 100ms            ✅ Achieved (67ms)
⚠️  STT latency < 800ms              ⚠️  Borderline (823ms)
❌ LLM latency < 2000ms              ❌ Exceeded (3214ms)
✅ TTS latency < 500ms               ✅ Achieved (312ms)
✅ Memory < 1GB                      ✅ Achieved (847MB)
⚠️  CPU < 80% (sustainable)          ⚠️  High (92%)
```

---

**Last Updated**: October 17, 2025  
**Diagram Version**: 2.0 (Vision-Driven Architecture)
