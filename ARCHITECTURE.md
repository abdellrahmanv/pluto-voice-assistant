# 🏗️ Project Pluto - Architecture Documentation# 🏗️ Project Pluto - Architecture Documentation# 🏗️ Project Pluto - Architecture Documentation



## 🎯 Design Philosophy - Vision-Driven Reflex Agent



Project Pluto is a **vision-driven reflex agent** voice assistant built on four core principles:## 🎯 Design Philosophy - Reflex Agent## 🎯 Design Philosophy



### 1. **Reactive Behavior**

The system reacts to environmental stimuli (face detection) rather than waiting passively for voice commands. When it sees a person, it initiates interaction - making it feel more natural and engaging.

Project Pluto is a **vision-driven reflex agent** voice assistant built on four core principles:Project Pluto is built on three core principles:

### 2. **Modularity**

Each component (Vision, STT, LLM, TTS) is an independent worker with clear responsibilities and interfaces. Workers can be swapped or disabled without breaking the system.



### 3. **Event-Driven Architecture**### 1. **Reactive Behavior**### 1. **Modularity**

Workers communicate through thread-safe queues, enabling:

- Asynchronous processingThe system reacts to environmental stimuli (face detection) rather than waiting passively for voice commands. When it sees a person, it initiates interaction.Each component (STT, LLM, TTS) is an independent worker with clear responsibilities and interfaces.

- Natural backpressure handling

- Clean separation of concerns

- Easy debugging and monitoring

### 2. **Modularity**### 2. **Queue-Based Communication**

### 4. **State-Machine Control**

An explicit state machine manages conversation flow:Each component (Vision, STT, LLM, TTS) is an independent worker with clear responsibilities and interfaces. Workers can be swapped or disabled without breaking the system.Workers communicate through thread-safe queues, enabling:

```

IDLE → FACE_DETECTED → LOCKED_IN → GREETING → LISTENING → PROCESSING → RESPONDING → [loop or FACE_LOST]- Asynchronous processing

```

### 3. **Event-Driven Architecture**- Natural backpressure handling

---

Workers communicate through thread-safe queues, enabling:- Easy debugging and monitoring

## 🏛️ System Architecture

- Asynchronous processing- Clean separation of concerns

```

┌─────────────────────────────────────────────────────────────────────────┐- Natural backpressure handling

│                      🪐 PLUTO ORCHESTRATOR                              │

│           (4-Worker Coordinator + Agent State Manager)                  │- Clean separation of concerns### 3. **Comprehensive Metrics**

│                                                                          │

│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│- Easy debugging and monitoringEvery operation is measured to identify bottlenecks before deploying to resource-constrained hardware (Raspberry Pi 4).

│  │ Agent State  │  │ Vision Event │  │ STT→LLM     │  │ LLM→TTS     ││

│  │   Manager    │  │    Queue     │  │  Queue      │  │  Queue      ││

│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘│

└───────┬──────────────────┬────────────────┬─────────────────┬───────────┘### 4. **State-Machine Control**---

        │                  │                │                 │

   ┌────▼────┐       ┌─────▼─────┐    ┌────▼────┐      ┌─────▼─────┐An explicit state machine manages conversation flow:

   │ VISION  │       │    STT    │    │   LLM   │      │    TTS    │

   │ WORKER  │       │  WORKER   │    │  WORKER │      │  WORKER   │`IDLE → FACE_DETECTED → LOCKED_IN → GREETING → LISTENING → PROCESSING → RESPONDING → [loop or FACE_LOST]`## 🏛️ System Architecture

   │         │       │           │    │         │      │           │

   │ YuNet   │       │  Whisper  │    │ Qwen2.5 │      │   Piper   │

   │Face Det │       │  Tiny     │    │  0.5b   │      │  en_US    │

   └────┬────┘       └───────────┘    └─────────┘      └───────────┘---```

        │

   ┌────▼────┐┌─────────────────────────────────────────────────────────────────┐

   │ rpicam  │

   │  -vid   │## 🏛️ System Architecture│                      🪐 PLUTO ORCHESTRATOR                      │

   └─────────┘

```│                  (Thread Management & Coordination)              │



### Worker Overview```└─────────────────────────────────────────────────────────────────┘



| Worker | Technology | Input | Output | Thread Type |┌─────────────────────────────────────────────────────────────────┐                                │

|--------|-----------|-------|--------|-------------|

| **Vision** | YuNet (ONNX) + rpicam | Camera stream | Face events | Dedicated |│                   🪐 PLUTO ORCHESTRATOR                         │         ┌──────────────────────┼──────────────────────┐

| **STT** | Whisper tiny | Microphone | Transcript | Dedicated |

| **LLM** | Qwen2.5:0.5b | Text | Response | Dedicated |│         (4-Worker Coordinator + Agent State Manager)            │         │                      │                      │

| **TTS** | Piper en_US | Text | Audio | Dedicated |

└─────────┬───────────────────────────────────────────────────────┘    ┌────▼────┐          ┌─────▼─────┐         ┌─────▼─────┐

---

          │    │   STT   │──Queue──▶│    LLM    │──Queue──▶│    TTS    │

## 🔄 Complete Interaction Flow - Reflex Agent Behavior

    ┌─────┼─────┬─────────┬─────────┬─────────┐    │  Vosk   │          │  Qwen2.5  │          │   Piper   │

### 1. IDLE STATE - Vision Scanning

```    │     │     │         │         │         │    └─────────┘          └───────────┘          └───────────┘

┌─────────────────────────────────────────────────────────────┐

│ Vision Worker: Scanning for faces                          │┌───▼──┐┌─▼───┐┌─▼──┐  ┌──▼──┐  ┌───▼────┐ ┌──▼───┐         │                      │                      │

│ • Camera: rpicam-vid @ 320x240, 10fps (5 effective fps)   │

│ • YuNet detector running on every frame                    ││Vision││ STT ││LLM │  │ TTS │  │Metrics │ │ Agent│         └──────────────────────┼──────────────────────┘

│ • STT Worker: PAUSED (not listening)                       │

│ • Agent State: IDLE                                        ││Worker││     ││    │  │     │  │ Logger │ │State │                                │

└─────────────────────────────────────────────────────────────┘

                           │└──┬───┘└─────┘└────┘  └─────┘  └────────┘ └──────┘                         ┌──────▼──────┐

                           ▼ Face detected for 3+ frames

```   │                         │   METRICS   │



### 2. FACE_DETECTED → LOCKED_IN   │ Face Detection Events                         │   LOGGER    │

```

┌─────────────────────────────────────────────────────────────┐   │                         └─────────────┘

│ Vision Event: face_detected                                │

│ • Assign face_id to detected person                        │   ▼```

│ • Lock onto largest/closest face                           │

│ • Agent State: IDLE → FACE_DETECTED → LOCKED_IN            │Face Locking Logic:

│ • Action: Orchestrator prepares to greet                   │

└─────────────────────────────────────────────────────────────┘• Detect face → Lock onto person---

                           │

                           ▼ Orchestrator initiates greeting• Ignore other faces while locked

```

• Unlock when person leaves## 🔄 Data Flow

### 3. GREETING STATE

```• Auto-greet on new lock

┌─────────────────────────────────────────────────────────────┐

│ Orchestrator: Injects greeting message                     │```### Stage 1: Speech Input (STT Worker)

│ • Message: "Hi there! How can I help you today?"           │

│ • Flow: Orchestrator → LLM Queue (bypasses STT)            │```

│ • LLM generates friendly greeting response                 │

│ • Agent State: LOCKED_IN → GREETING                        │---User speaks ──▶ PyAudio captures audio ──▶ VAD detects speech

└─────────────────────────────────────────────────────────────┘

                           │    ──▶ Vosk recognizes text ──▶ Queue: {"type": "transcript", "text": "..."}

                           ▼ TTS plays greeting

```## 🔄 Data Flow - Reflex Agent Behavior```



### 4. LISTENING STATE

```

┌─────────────────────────────────────────────────────────────┐### Complete Interaction Cycle### Stage 2: Language Processing (LLM Worker)

│ TTS: Plays greeting audio                                  │

│ • Audio output to speaker                                  │```

│ • STT Worker: RESUMED (now actively listening)             │

│ • Agent State: GREETING → LISTENING                        │```Queue receives transcript ──▶ Ollama API call ──▶ Qwen2.5 generates response

│ • User can now speak                                       │

└─────────────────────────────────────────────────────────────┘┌─────────────────────────────────────────────────────────────────┐    ──▶ Queue: {"type": "response", "text": "..."}

                           │

                           ▼ User speaks│ 1. IDLE STATE - Vision Worker Scanning                         │```

```

│    Vision detects faces every 200ms (5 effective FPS)           │

### 5. CONVERSATION LOOP

```└────────────┬────────────────────────────────────────────────────┘### Stage 3: Speech Output (TTS Worker)

┌─────────────────────────────────────────────────────────────┐

│ Normal Conversation:                                       │             │```

│ • User speaks → STT transcribes                            │

│ • Transcript → LLM processes                               │             ▼ Face detected for 3+ framesQueue receives response ──▶ Piper synthesizes WAV ──▶ PyAudio plays audio

│ • Response → TTS synthesizes                               │

│ • Audio plays → Back to listening                          │┌─────────────────────────────────────────────────────────────────┐    ──▶ User hears response

│                                                            │

│ Agent States: LISTENING ⇄ PROCESSING ⇄ RESPONDING          ││ 2. FACE_DETECTED → LOCKED_IN                                    │```

│ Vision: Continues tracking locked face in background       │

└─────────────────────────────────────────────────────────────┘│    Agent State: IDLE → FACE_DETECTED → LOCKED_IN                │

                           │

                           ▼ Face lost for 1.5+ seconds│    Action: Lock onto largest face (closest person)              │---

```

└────────────┬────────────────────────────────────────────────────┘

### 6. FACE_LOST → IDLE

```             │## 🧩 Component Deep Dive

┌─────────────────────────────────────────────────────────────┐

│ Vision Event: face_lost                                    │             ▼ Orchestrator initiates greeting

│ • No face detected for timeout period (1.5s default)       │

│ • Agent State: [any] → FACE_LOST → IDLE                    │┌─────────────────────────────────────────────────────────────────┐### 1. Configuration System (`src/config.py`)

│ • Actions:                                                 │

│   - STT Worker PAUSED                                      ││ 3. GREETING STATE                                                │

│   - Conversation history cleared                           │

│   - Face lock released                                     ││    Orchestrator injects: "Hi there! How can I help you today?"  │**Purpose**: Centralized configuration management

│   - Back to scanning mode                                  │

└─────────────────────────────────────────────────────────────┘│    Message flows: Orchestrator → LLM Queue (bypass STT)         │

```

│    Agent State: LOCKED_IN → GREETING                             │**Key Features**:

---

└────────────┬────────────────────────────────────────────────────┘- Model paths and parameters

## 🧩 Component Deep Dive

             │- Audio settings (16kHz for Vosk compatibility)

### 1. Vision Worker (`src/workers/vision_worker.py`)

             ▼ LLM generates greeting response- Queue configurations

**Technology**: YuNet face detection (INT8 quantized ONNX model, 2.5MB)

┌─────────────────────────────────────────────────────────────────┐- Worker warmup settings

**Camera**: rpicam-vid (Raspberry Pi native)

```bash│ 4. TTS PLAYS GREETING                                            │- Metrics thresholds

rpicam-vid -t 0 --width 320 --height 240 --framerate 10 --codec yuv420 -o -

```│    LLM → TTS Queue → Audio Output                               │



**Responsibilities**:│    Agent State: GREETING → LISTENING                             │**Design Decision**: 

- Capture camera frames via rpicam subprocess

- Run YuNet face detection on each frame│    Action: STT worker resumed (now actively listening)           │Single source of truth prevents configuration drift. All workers import settings from here.

- Track detected faces with unique IDs

- Implement face locking logic (lock onto first/closest person)└────────────┬────────────────────────────────────────────────────┘

- Send face events to orchestrator

- Manage face loss timeout             │---

- Optional: Terminal preview (ASCII art for SSH)

             ▼ User speaks

**Key Parameters** (`VISION_CONFIG`):

```python┌─────────────────────────────────────────────────────────────────┐### 2. STT Worker (`src/workers/stt_worker.py`)

{

    'resolution': (320, 240),          # Camera resolution│ 5. NORMAL CONVERSATION LOOP                                      │

    'confidence_threshold': 0.6,       # Min face confidence

    'face_lost_timeout': 1.5,          # Seconds before "face lost"│    User speaks → STT transcribes → LLM responds → TTS speaks    │**Technology**: Vosk (offline speech recognition)

    'nms_threshold': 0.3,              # Non-max suppression

    'frame_skip': 2,                   # Process every 3rd frame│    Agent State: LISTENING ⇄ PROCESSING ⇄ RESPONDING             │

    'buffer_size': 10**6,              # Camera buffer

    'show_preview': True,              # Terminal preview│    Vision: Continues tracking locked face in background          │**Thread**: Dedicated audio capture thread

}

```└────────────┬────────────────────────────────────────────────────┘



**Performance Notes**:             │**Responsibilities**:

- YuNet INT8: ~50-80ms per frame on RPi 4

- Effective FPS: ~5 fps (with frame skip)             ▼ Face lost for 1.5+ seconds- Continuous audio stream monitoring

- CPU usage: ~15-25% single core

- Memory: ~50MB┌─────────────────────────────────────────────────────────────────┐- Voice Activity Detection (VAD) using energy threshold



**Events Emitted**:│ 6. FACE_LOST → IDLE                                              │- Speech segment extraction

```python

{│    Agent State: [any] → FACE_LOST → IDLE                        │- Vosk inference

    'type': 'face_detected',

    'face_id': 12345,│    Action: STT paused, conversation history cleared              │- Transcript queuing

    'bbox': (x, y, w, h),

    'confidence': 0.95,│    Vision: Back to scanning mode                                 │

    'timestamp': 1697520000.123

}└────────────┬────────────────────────────────────────────────────┘**Key Parameters**:



{             │- **Sample Rate**: 16kHz (Vosk requirement)

    'type': 'face_tracked',

    'face_id': 12345,             └─────────────── Loop back to step 1- **Chunk Size**: 4096 samples (~256ms at 16kHz)

    'bbox': (x, y, w, h),

    'confidence': 0.93,```- **Energy Threshold**: 300 (tunable for noise floor)

    'timestamp': 1697520000.323

}- **Silence Threshold**: 20 chunks (~5 seconds)



{---

    'type': 'face_lost',

    'face_id': 12345,**Design Decision**: 

    'timestamp': 1697520002.500

}## 🧩 Component Deep DiveEnergy-based VAD is lightweight and sufficient for controlled environments. More sophisticated VAD (WebRTC VAD) could be added for noisy environments.

```



---

### 1. Vision Worker**Performance Considerations**:

### 2. Agent State Manager (`src/agent_state.py`)

- Model size: ~40MB (small model) for laptop testing

**Purpose**: Centralized state machine for conversation flow

**Technology**: YuNet ONNX + Raspberry Pi camera (rpicam-vid)- Inference latency: 100-200ms typical

**States**:

```python- Memory footprint: ~150MB

class AgentState(Enum):

    IDLE = "idle"                    # No face, not listening**Key Features**:

    FACE_DETECTED = "face_detected"  # Face found, preparing

    LOCKED_IN = "locked_in"          # Locked onto person- Face detection using INT8 quantized model (2.5MB)---

    GREETING = "greeting"            # Playing greeting

    LISTENING = "listening"          # Waiting for user speech- Face locking: Locks onto one person, ignores others

    PROCESSING = "processing"        # LLM thinking

    RESPONDING = "responding"        # TTS speaking- Tracking: Follows face across frames (100px tolerance)### 3. LLM Worker (`src/workers/llm_worker.py`)

    FACE_LOST = "face_lost"          # Person left

```- Loss detection: 1.5s timeout before unlocking



**State Transitions**:**Technology**: Ollama + Qwen2.5 1.5B (4-bit quantized)

```

IDLE → FACE_DETECTED → LOCKED_IN → GREETING → LISTENING**Performance**: 60-120ms per frame, ~15-20% CPU, 100MB memory

                                                   ↓

                                                   ↓**Thread**: Queue processing thread

FACE_LOST ← ← ← ← ← RESPONDING ← PROCESSING ← ← ← ↓

     ↓### 2. Agent State Manager

     ↓

   IDLE (loop restarts)**Responsibilities**:

```

**Purpose**: Explicit state machine for conversation control- Monitor STT→LLM queue

**Tracked Data**:

- Current state- Call Ollama API

- Locked face ID

- Last face detection time**States**: `IDLE` → `FACE_DETECTED` → `LOCKED_IN` → `GREETING` → `LISTENING` → `PROCESSING` → `RESPONDING` → `FACE_LOST`- Manage conversation history

- Conversation active flag

- Queue responses for TTS

---

### 3. STT Worker  

### 3. STT Worker (`src/workers/stt_worker.py`)

**Key Parameters**:

**Technology**: OpenAI Whisper (tiny model, 39MB)

**Technology**: Whisper (tiny) + PyAudio- **Model**: `qwen2.5:0.5b-instruct-q4_k_M` (quantized for speed)

**Key Features**:

- **Pause/Resume Control**: Can be paused when no face is locked- **Temperature**: 0.7 (balanced creativity)

- Continuous audio stream monitoring

- Voice Activity Detection (VAD) using energy threshold**Vision Integration**: Pause/resume based on face presence- **Max Tokens**: 100 (concise responses)

- Speech segment extraction

- Whisper inference- **Timeout**: 30 seconds

- Transcript queuing

**Performance**: 100-200ms latency, 150MB memory- **History**: Last 10 exchanges

**Performance Notes**:

- Whisper tiny: ~500ms-1s per utterance on RPi 4

- Memory: ~200MB

- CPU: ~70-90% during transcription### 4. LLM Worker**Design Decision**: 



---Ollama provides clean API abstraction. 4-bit quantization reduces memory and increases speed while maintaining quality for conversational use.



### 4. LLM Worker (`src/workers/llm_worker.py`)**Technology**: Ollama + Qwen2.5:0.5b (q4_k_M)



**Technology**: Qwen2.5:0.5b-instruct-q4_k_M via Ollama**Performance Considerations**:



**Responsibilities**:**Vision Integration**: Receives vision-triggered greetings- Model size: ~1GB on disk

- Receive transcripts or greeting triggers

- Call Ollama API with conversation context- Inference latency: 500-1500ms (CPU-dependent)

- Stream responses token-by-token

- Queue complete responses for TTS**Performance**: 500-1500ms latency, 2GB memory (primary bottleneck)- Memory footprint: ~2GB during inference



**Performance Notes**:- **Bottleneck candidate**: Likely slowest component on Raspberry Pi

- Response time: ~2-4 seconds for short answers

- Tokens/second: ~5-8 on RPi 4### 5. TTS Worker

- Memory: ~400MB

---

**Greeting Logic**:

```python**Technology**: Piper (en_US-lessac-medium)

if event['type'] == 'greeting':

    # Orchestrator-injected greeting### 4. TTS Worker (`src/workers/tts_worker.py`)

    response = llm("Hi there! How can I help you today?")

```**Performance**: 200-500ms latency, 200MB memory



---**Technology**: Piper (neural TTS with ONNX runtime)



### 5. TTS Worker (`src/workers/tts_worker.py`)### 6. Orchestrator



**Technology**: Piper (en_US-lessac-medium, 63MB)**Thread**: Queue processing thread



**Performance Notes**:**Responsibilities**:

- Synthesis: ~200-400ms per sentence

- Memory: ~100MB- 4-worker coordination**Responsibilities**:

- CPU: ~40-60% during synthesis

- Vision event monitoring- Monitor LLM→TTS queue

---

- Greeting injection- Synthesize speech with Piper

### 6. Orchestrator (`src/orchestrator.py`)

- State transitions- Play audio through PyAudio

**Purpose**: Coordinate all workers and manage conversation flow

- Clean up temporary files

**Responsibilities**:

- Initialize all 4 workers---

- Manage 3 queues (vision→orch, stt→llm, llm→tts)

- Process vision events**Key Parameters**:

- Implement state machine logic

- Control STT pause/resume## 📊 Performance (Raspberry Pi 4)- **Model**: `en_US-lessac-medium.onnx` (quality/speed balance)

- Inject greeting messages

- Handle graceful shutdown- **Output**: 22kHz WAV



**Main Loop**:| Component | Latency | Memory | CPU Usage |- **Voice**: Default (configurable)

```python

while running:|-----------|---------|--------|-----------|

    # Check vision queue

    if vision_event:| Vision | 60-120ms | 100MB | 15-20% (continuous) |**Design Decision**: 

        if event['type'] == 'face_detected':

            state.lock_face(event['face_id'])| STT | 100-200ms | 150MB | Burst only |Piper chosen for offline capability and natural voice quality. Medium model balances quality and speed.

            inject_greeting()  # Bypass STT

        elif event['type'] == 'face_lost':| LLM | 500-1500ms | 2GB | 50-60% (burst) |

            state.unlock_face()

            stt_worker.pause()| TTS | 200-500ms | 200MB | Burst only |**Performance Considerations**:

    

    # Monitor other queues, handle errors| **Total** | 0.8-2.2s | ~2.5-3GB | 20% idle, 70-80% active |- Model size: ~60MB

```

- Synthesis latency: 200-500ms

---

---- Memory footprint: ~200MB

## 📊 Performance Metrics & Benchmarking

- Real-time factor: 0.2-0.5 (faster than real-time)

### Raspberry Pi 4 Benchmarks (4GB RAM)

## 🎯 Reflex Agent Behavior

| Component | Metric | Value | Notes |

|-----------|--------|-------|-------|---

| **Vision** | Latency | 50-80ms | Per frame (YuNet INT8) |

| | FPS | ~5 fps | Effective (with frame skip) |### Pattern 1: New Person

| | CPU | 15-25% | Single core |

| | Memory | ~50MB | Worker + model |1. Face detected → lock (0.3s)### 5. Metrics Logger (`src/metrics_logger.py`)

| **STT** | Latency | 500ms-1s | Per utterance (Whisper tiny) |

| | CPU | 70-90% | During transcription |2. Greet: "Hi there!"

| | Memory | ~200MB | Worker + model |

| **LLM** | Latency | 2-4s | Short responses (Qwen 0.5b) |3. Listen for response**Purpose**: Performance measurement and bottleneck identification

| | Tokens/sec | 5-8 | Ollama inference |

| | CPU | 80-100% | During generation |4. Conversation loop

| | Memory | ~400MB | Ollama + model |

| **TTS** | Latency | 200-400ms | Per sentence (Piper) |**Tracked Metrics**:

| | CPU | 40-60% | During synthesis |

| | Memory | ~100MB | Worker + model |### Pattern 2: Person Leaves- **STT Latency**: Time from audio end to transcript



### System Metrics1. Face lost for 1.5s- **LLM Latency**: Time from transcript to response

- **Total Memory**: ~800MB-1GB (all workers)

- **Idle CPU**: ~5-10% (vision scanning only)2. Stop listening- **TTS Latency**: Time from response to audio start

- **Active CPU**: ~90-100% (during LLM inference)

- **Face Detection to Greeting**: ~1-2 seconds3. Reset to IDLE- **Total Latency**: Full conversation round-trip

- **End-to-End Response**: ~4-7 seconds (user speaks → audio reply)

- **Memory Usage**: RAM consumption (MB)

### Bottlenecks Identified

1. **LLM Inference** (largest bottleneck)### Pattern 3: Multiple People- **Queue Depth**: Backpressure indicators

   - 2-4 seconds for simple responses

   - Can spike to 8-10s for complex queries1. Locked to Person A- **Error Counts**: Component failures

   - Mitigation: Use smaller model, limit context

2. Person B enters → ignored

2. **STT Processing** (secondary bottleneck)

   - 500ms-1s transcription time3. Only unlocks if Person A leaves**Output Formats**:

   - Mitigation: Already using "tiny" model

1. **CSV**: Time-series data for analysis

3. **Vision Processing** (minimal impact)

   - 50-80ms per frame is acceptable---2. **JSON**: Structured export for processing

   - Frame skip keeps CPU usage low

3. **Console**: Real-time feedback

### Testing Recommendations

## 🔧 Configuration Highlights4. **Summary**: Statistical analysis

**1. Vision System Stress Test**

```bash

# Test face detection performance

python -c "- **Resolution**: 320x240 (speed/accuracy balance)**Design Decision**: 

from src.workers.vision_worker import VisionWorker

import queue, time- **FPS**: 5 effective (with frame skip=2)Multiple output formats support different analysis needs. CSV for time-series plotting, JSON for programmatic access, console for immediate feedback.



q = queue.Queue()- **Lock confirmation**: 3 frames (0.3s)

worker = VisionWorker(q)

worker.start()- **Lost timeout**: 15 frames (1.5s)---



# Monitor for 60 seconds- **Greeting cooldown**: 10 seconds

start = time.time()

events = 0### 6. Orchestrator (`src/orchestrator.py`)

while time.time() - start < 60:

    try:---

        event = q.get(timeout=0.1)

        events += 1**Purpose**: System coordination and lifecycle management

    except:

        pass**For detailed vision setup**, see [VISION_SETUP.md](VISION_SETUP.md)



print(f'Events/sec: {events/60:.2f}')**Responsibilities**:

worker.stop()

"**For full original architecture details**, see `ARCHITECTURE.md.backup`- Worker initialization and startup

```

- Thread management

**2. End-to-End Latency Test**- Queue wiring

```bash- Health monitoring

# Measure face detection → greeting time- Graceful shutdown

python test_latency.py --metric greeting_latency- Signal handling



# Measure full conversation turn**Monitoring Features**:

python test_latency.py --metric conversation_turn- Worker status checks

```- Queue depth monitoring

- Memory tracking

**3. Memory Profiling**- Conversation counting

```bash

# Monitor memory usage over time**Design Decision**: 

python -m memory_profiler run.pyCentralized orchestrator simplifies system control. Alternative would be distributed coordination, but adds complexity unnecessary for 3-component system.

```

---

**4. CPU Profiling**

```bash## 🔌 Queue Architecture

# Identify CPU hotspots

python -m cProfile -s cumtime run.py### Queue 1: STT → LLM

```**Purpose**: Deliver transcripts to language model



---**Message Format**:

```python

## 🔧 Configuration Files{

    'type': 'transcript',

### `src/config.py`    'text': 'recognized speech text',

Centralized configuration for all components:    'timestamp': 1234567890.123,

- Model paths    'latency_ms': 150.0

- Audio settings}

- Queue configurations```

- Worker parameters

- Metrics thresholds**Size Limit**: 10 items (prevents memory buildup)

- **Vision settings** (NEW)

**Timeout**: 1 second for blocking operations

---

---

## 📈 Metrics Logging

### Queue 2: LLM → TTS

### Tracked Metrics (`src/metrics_logger.py`)**Purpose**: Deliver responses to speech synthesis



**Vision Metrics** (NEW):**Message Format**:

- `vision_fps`: Actual frames processed per second```python

- `vision_latency_ms`: YuNet inference time{

- `face_count`: Number of faces detected    'type': 'response',

- `face_locked`: Boolean, face lock status    'text': 'generated response text',

- `face_lock_duration_s`: How long face has been locked    'timestamp': 1234567890.456,

    'latency_ms': 850.0

**STT Metrics**:}

- `stt_latency_ms`: Transcription time```

- `stt_paused`: Boolean, worker state

**Size Limit**: 10 items

**LLM Metrics**:

- `llm_latency_ms`: Response generation time**Timeout**: 1 second

- `llm_tokens`: Response length

---

**TTS Metrics**:

- `tts_latency_ms`: Synthesis time## 🎛️ Configuration Philosophy

- `audio_duration_ms`: Output audio length

### Why 16kHz Audio?

**System Metrics**:Vosk requires 16kHz sample rate. All audio pipelines configured to match.

- `cpu_percent`: Overall CPU usage

- `memory_mb`: RAM consumption### Why Queue Size = 10?

- `queue_sizes`: Backlog in each queuePrevents memory buildup while allowing some buffering. Chosen empirically.



### Output Formats### Why 4-bit Quantization?

- CSV: `logs/metrics_YYYYMMDD_HHMMSS.csv`Reduces LLM memory footprint by ~4x with minimal quality loss for conversational tasks.

- JSON: `logs/metrics_YYYYMMDD_HHMMSS.json`

### Why Medium TTS Model?

---Balances naturalness and speed. Small models sound robotic, large models too slow for real-time.



## 🚀 Deployment Considerations---



### Raspberry Pi 4 Optimization## 🚦 Error Handling Strategy

1. **Use INT8 quantized models** (YuNet, Whisper if available)

2. **Enable frame skipping** (vision: process every 3rd frame)### Worker-Level

3. **Limit LLM context** (max 2-3 conversation turns)- Each worker catches and logs its own exceptions

4. **Use swap** if memory exceeds 3.5GB- Continues running despite individual failures

5. **Monitor temperature** (CPU throttling at 80°C)- Metrics track error frequency



### Scaling Options### Queue-Level

- **Horizontal**: Offload LLM to external server- Timeout-based deadlock prevention

- **Vertical**: Upgrade to RPi 5 (2-3x faster)- Empty queue handling (non-blocking)

- **Hybrid**: Keep vision/STT/TTS local, LLM remote- Full queue detection (backpressure signal)



---### System-Level

- Graceful shutdown on SIGINT/SIGTERM

## 🐛 Debugging & Troubleshooting- Resource cleanup (audio streams, files)

- Metrics export before exit

### Common Issues

---

**Vision Worker**

- Camera timeout: Check `rpicam-vid` process cleanup## 📊 Performance Baseline (Laptop)

- Low FPS: Increase frame_skip or reduce resolution

- False detections: Increase confidence_threshold**Expected Latencies**:

- STT: 100-200ms

**STT Worker**- LLM: 500-1500ms ⚠️ *bottleneck*

- Not listening: Check if paused due to no face lock- TTS: 200-500ms

- Slow transcription: Reduce audio chunk size- **Total**: 800-2200ms (0.8-2.2 seconds)



**LLM Worker****Expected Memory**:

- Slow responses: Use smaller model or reduce context- STT: ~150MB

- Ollama errors: Check service is running- LLM: ~2GB during inference

- TTS: ~200MB

**State Machine**- Orchestrator: ~50MB

- Stuck in state: Check logs for failed transitions- **Total**: ~2.5GB peak

- No greeting: Verify orchestrator greeting injection

**Target for Raspberry Pi 4** (4GB RAM):

### Debug Mode- Need to optimize LLM inference

```bash- Consider smaller model or quantization

# Enable verbose logging- May need swap file for memory headroom

export LOG_LEVEL=DEBUG

python run.py---

```

## 🔮 Future Architecture Considerations

---

### Scalability

## 📚 Related Documentation- Add worker pools for parallel processing

- Implement priority queues for urgent requests

- [VISION_SETUP.md](VISION_SETUP.md) - Vision system setup guide- Consider async/await for I/O operations

- [QUICKSTART.md](QUICKSTART.md) - Quick setup instructions  

- [HOW_TO_RUN.md](HOW_TO_RUN.md) - Detailed usage guide### Reliability

- [README.md](README.md) - Project overview- Add worker health checks and auto-restart

- Implement circuit breakers for failing components

---- Add request timeout and retry logic



**Last Updated**: October 17, 2025  ### Features

**Architecture Version**: 2.0 (Vision-Driven Reflex Agent)- Wake word detection (Porcupine/Snowboy)

- Multi-turn conversation context
- Voice customization and cloning
- Streaming TTS for faster perceived latency

---

## 🎓 Design Lessons

### What Worked Well
✅ Queue-based architecture: Clean separation, easy debugging  
✅ Centralized config: Single source of truth  
✅ Comprehensive metrics: Visibility into performance  
✅ Worker abstraction: Easy to swap components

### What Could Improve
⚠️ LLM inference latency: Needs optimization for Raspberry Pi  
⚠️ VAD tuning: May need adjustment for different environments  
⚠️ No streaming: Full responses before speaking (latency perception)

### Alternative Architectures Considered
- **Event bus**: Too complex for 3 components
- **Shared memory**: Harder to debug, less portable
- **ZeroMQ**: Overkill for single-process system
- **Async/await**: Harder to reason about with audio threads

---

**Conclusion**: Queue-based worker architecture provides optimal balance of simplicity, debuggability, and performance for voice assistant use case.

See [DIAGRAMS.md](DIAGRAMS.md) for visual representations of these concepts.
