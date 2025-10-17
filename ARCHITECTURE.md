# 🏗️ Project Pluto - Architecture Documentation# 🏗️ Project Pluto - Architecture Documentation



## 🎯 Design Philosophy - Reflex Agent## 🎯 Design Philosophy



Project Pluto is a **vision-driven reflex agent** voice assistant built on four core principles:Project Pluto is built on three core principles:



### 1. **Reactive Behavior**### 1. **Modularity**

The system reacts to environmental stimuli (face detection) rather than waiting passively for voice commands. When it sees a person, it initiates interaction.Each component (STT, LLM, TTS) is an independent worker with clear responsibilities and interfaces.



### 2. **Modularity**### 2. **Queue-Based Communication**

Each component (Vision, STT, LLM, TTS) is an independent worker with clear responsibilities and interfaces. Workers can be swapped or disabled without breaking the system.Workers communicate through thread-safe queues, enabling:

- Asynchronous processing

### 3. **Event-Driven Architecture**- Natural backpressure handling

Workers communicate through thread-safe queues, enabling:- Easy debugging and monitoring

- Asynchronous processing- Clean separation of concerns

- Natural backpressure handling

- Clean separation of concerns### 3. **Comprehensive Metrics**

- Easy debugging and monitoringEvery operation is measured to identify bottlenecks before deploying to resource-constrained hardware (Raspberry Pi 4).



### 4. **State-Machine Control**---

An explicit state machine manages conversation flow:

`IDLE → FACE_DETECTED → LOCKED_IN → GREETING → LISTENING → PROCESSING → RESPONDING → [loop or FACE_LOST]`## 🏛️ System Architecture



---```

┌─────────────────────────────────────────────────────────────────┐

## 🏛️ System Architecture│                      🪐 PLUTO ORCHESTRATOR                      │

│                  (Thread Management & Coordination)              │

```└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐                                │

│                   🪐 PLUTO ORCHESTRATOR                         │         ┌──────────────────────┼──────────────────────┐

│         (4-Worker Coordinator + Agent State Manager)            │         │                      │                      │

└─────────┬───────────────────────────────────────────────────────┘    ┌────▼────┐          ┌─────▼─────┐         ┌─────▼─────┐

          │    │   STT   │──Queue──▶│    LLM    │──Queue──▶│    TTS    │

    ┌─────┼─────┬─────────┬─────────┬─────────┐    │  Vosk   │          │  Qwen2.5  │          │   Piper   │

    │     │     │         │         │         │    └─────────┘          └───────────┘          └───────────┘

┌───▼──┐┌─▼───┐┌─▼──┐  ┌──▼──┐  ┌───▼────┐ ┌──▼───┐         │                      │                      │

│Vision││ STT ││LLM │  │ TTS │  │Metrics │ │ Agent│         └──────────────────────┼──────────────────────┘

│Worker││     ││    │  │     │  │ Logger │ │State │                                │

└──┬───┘└─────┘└────┘  └─────┘  └────────┘ └──────┘                         ┌──────▼──────┐

   │                         │   METRICS   │

   │ Face Detection Events                         │   LOGGER    │

   │                         └─────────────┘

   ▼```

Face Locking Logic:

• Detect face → Lock onto person---

• Ignore other faces while locked

• Unlock when person leaves## 🔄 Data Flow

• Auto-greet on new lock

```### Stage 1: Speech Input (STT Worker)

```

---User speaks ──▶ PyAudio captures audio ──▶ VAD detects speech

    ──▶ Vosk recognizes text ──▶ Queue: {"type": "transcript", "text": "..."}

## 🔄 Data Flow - Reflex Agent Behavior```



### Complete Interaction Cycle### Stage 2: Language Processing (LLM Worker)

```

```Queue receives transcript ──▶ Ollama API call ──▶ Qwen2.5 generates response

┌─────────────────────────────────────────────────────────────────┐    ──▶ Queue: {"type": "response", "text": "..."}

│ 1. IDLE STATE - Vision Worker Scanning                         │```

│    Vision detects faces every 200ms (5 effective FPS)           │

└────────────┬────────────────────────────────────────────────────┘### Stage 3: Speech Output (TTS Worker)

             │```

             ▼ Face detected for 3+ framesQueue receives response ──▶ Piper synthesizes WAV ──▶ PyAudio plays audio

┌─────────────────────────────────────────────────────────────────┐    ──▶ User hears response

│ 2. FACE_DETECTED → LOCKED_IN                                    │```

│    Agent State: IDLE → FACE_DETECTED → LOCKED_IN                │

│    Action: Lock onto largest face (closest person)              │---

└────────────┬────────────────────────────────────────────────────┘

             │## 🧩 Component Deep Dive

             ▼ Orchestrator initiates greeting

┌─────────────────────────────────────────────────────────────────┐### 1. Configuration System (`src/config.py`)

│ 3. GREETING STATE                                                │

│    Orchestrator injects: "Hi there! How can I help you today?"  │**Purpose**: Centralized configuration management

│    Message flows: Orchestrator → LLM Queue (bypass STT)         │

│    Agent State: LOCKED_IN → GREETING                             │**Key Features**:

└────────────┬────────────────────────────────────────────────────┘- Model paths and parameters

             │- Audio settings (16kHz for Vosk compatibility)

             ▼ LLM generates greeting response- Queue configurations

┌─────────────────────────────────────────────────────────────────┐- Worker warmup settings

│ 4. TTS PLAYS GREETING                                            │- Metrics thresholds

│    LLM → TTS Queue → Audio Output                               │

│    Agent State: GREETING → LISTENING                             │**Design Decision**: 

│    Action: STT worker resumed (now actively listening)           │Single source of truth prevents configuration drift. All workers import settings from here.

└────────────┬────────────────────────────────────────────────────┘

             │---

             ▼ User speaks

┌─────────────────────────────────────────────────────────────────┐### 2. STT Worker (`src/workers/stt_worker.py`)

│ 5. NORMAL CONVERSATION LOOP                                      │

│    User speaks → STT transcribes → LLM responds → TTS speaks    │**Technology**: Vosk (offline speech recognition)

│    Agent State: LISTENING ⇄ PROCESSING ⇄ RESPONDING             │

│    Vision: Continues tracking locked face in background          │**Thread**: Dedicated audio capture thread

└────────────┬────────────────────────────────────────────────────┘

             │**Responsibilities**:

             ▼ Face lost for 1.5+ seconds- Continuous audio stream monitoring

┌─────────────────────────────────────────────────────────────────┐- Voice Activity Detection (VAD) using energy threshold

│ 6. FACE_LOST → IDLE                                              │- Speech segment extraction

│    Agent State: [any] → FACE_LOST → IDLE                        │- Vosk inference

│    Action: STT paused, conversation history cleared              │- Transcript queuing

│    Vision: Back to scanning mode                                 │

└────────────┬────────────────────────────────────────────────────┘**Key Parameters**:

             │- **Sample Rate**: 16kHz (Vosk requirement)

             └─────────────── Loop back to step 1- **Chunk Size**: 4096 samples (~256ms at 16kHz)

```- **Energy Threshold**: 300 (tunable for noise floor)

- **Silence Threshold**: 20 chunks (~5 seconds)

---

**Design Decision**: 

## 🧩 Component Deep DiveEnergy-based VAD is lightweight and sufficient for controlled environments. More sophisticated VAD (WebRTC VAD) could be added for noisy environments.



### 1. Vision Worker**Performance Considerations**:

- Model size: ~40MB (small model) for laptop testing

**Technology**: YuNet ONNX + Raspberry Pi camera (rpicam-vid)- Inference latency: 100-200ms typical

- Memory footprint: ~150MB

**Key Features**:

- Face detection using INT8 quantized model (2.5MB)---

- Face locking: Locks onto one person, ignores others

- Tracking: Follows face across frames (100px tolerance)### 3. LLM Worker (`src/workers/llm_worker.py`)

- Loss detection: 1.5s timeout before unlocking

**Technology**: Ollama + Qwen2.5 1.5B (4-bit quantized)

**Performance**: 60-120ms per frame, ~15-20% CPU, 100MB memory

**Thread**: Queue processing thread

### 2. Agent State Manager

**Responsibilities**:

**Purpose**: Explicit state machine for conversation control- Monitor STT→LLM queue

- Call Ollama API

**States**: `IDLE` → `FACE_DETECTED` → `LOCKED_IN` → `GREETING` → `LISTENING` → `PROCESSING` → `RESPONDING` → `FACE_LOST`- Manage conversation history

- Queue responses for TTS

### 3. STT Worker  

**Key Parameters**:

**Technology**: Whisper (tiny) + PyAudio- **Model**: `qwen2.5:0.5b-instruct-q4_k_M` (quantized for speed)

- **Temperature**: 0.7 (balanced creativity)

**Vision Integration**: Pause/resume based on face presence- **Max Tokens**: 100 (concise responses)

- **Timeout**: 30 seconds

**Performance**: 100-200ms latency, 150MB memory- **History**: Last 10 exchanges



### 4. LLM Worker**Design Decision**: 

Ollama provides clean API abstraction. 4-bit quantization reduces memory and increases speed while maintaining quality for conversational use.

**Technology**: Ollama + Qwen2.5:0.5b (q4_k_M)

**Performance Considerations**:

**Vision Integration**: Receives vision-triggered greetings- Model size: ~1GB on disk

- Inference latency: 500-1500ms (CPU-dependent)

**Performance**: 500-1500ms latency, 2GB memory (primary bottleneck)- Memory footprint: ~2GB during inference

- **Bottleneck candidate**: Likely slowest component on Raspberry Pi

### 5. TTS Worker

---

**Technology**: Piper (en_US-lessac-medium)

### 4. TTS Worker (`src/workers/tts_worker.py`)

**Performance**: 200-500ms latency, 200MB memory

**Technology**: Piper (neural TTS with ONNX runtime)

### 6. Orchestrator

**Thread**: Queue processing thread

**Responsibilities**:

- 4-worker coordination**Responsibilities**:

- Vision event monitoring- Monitor LLM→TTS queue

- Greeting injection- Synthesize speech with Piper

- State transitions- Play audio through PyAudio

- Clean up temporary files

---

**Key Parameters**:

## 📊 Performance (Raspberry Pi 4)- **Model**: `en_US-lessac-medium.onnx` (quality/speed balance)

- **Output**: 22kHz WAV

| Component | Latency | Memory | CPU Usage |- **Voice**: Default (configurable)

|-----------|---------|--------|-----------|

| Vision | 60-120ms | 100MB | 15-20% (continuous) |**Design Decision**: 

| STT | 100-200ms | 150MB | Burst only |Piper chosen for offline capability and natural voice quality. Medium model balances quality and speed.

| LLM | 500-1500ms | 2GB | 50-60% (burst) |

| TTS | 200-500ms | 200MB | Burst only |**Performance Considerations**:

| **Total** | 0.8-2.2s | ~2.5-3GB | 20% idle, 70-80% active |- Model size: ~60MB

- Synthesis latency: 200-500ms

---- Memory footprint: ~200MB

- Real-time factor: 0.2-0.5 (faster than real-time)

## 🎯 Reflex Agent Behavior

---

### Pattern 1: New Person

1. Face detected → lock (0.3s)### 5. Metrics Logger (`src/metrics_logger.py`)

2. Greet: "Hi there!"

3. Listen for response**Purpose**: Performance measurement and bottleneck identification

4. Conversation loop

**Tracked Metrics**:

### Pattern 2: Person Leaves- **STT Latency**: Time from audio end to transcript

1. Face lost for 1.5s- **LLM Latency**: Time from transcript to response

2. Stop listening- **TTS Latency**: Time from response to audio start

3. Reset to IDLE- **Total Latency**: Full conversation round-trip

- **Memory Usage**: RAM consumption (MB)

### Pattern 3: Multiple People- **Queue Depth**: Backpressure indicators

1. Locked to Person A- **Error Counts**: Component failures

2. Person B enters → ignored

3. Only unlocks if Person A leaves**Output Formats**:

1. **CSV**: Time-series data for analysis

---2. **JSON**: Structured export for processing

3. **Console**: Real-time feedback

## 🔧 Configuration Highlights4. **Summary**: Statistical analysis



- **Resolution**: 320x240 (speed/accuracy balance)**Design Decision**: 

- **FPS**: 5 effective (with frame skip=2)Multiple output formats support different analysis needs. CSV for time-series plotting, JSON for programmatic access, console for immediate feedback.

- **Lock confirmation**: 3 frames (0.3s)

- **Lost timeout**: 15 frames (1.5s)---

- **Greeting cooldown**: 10 seconds

### 6. Orchestrator (`src/orchestrator.py`)

---

**Purpose**: System coordination and lifecycle management

**For detailed vision setup**, see [VISION_SETUP.md](VISION_SETUP.md)

**Responsibilities**:

**For full original architecture details**, see `ARCHITECTURE.md.backup`- Worker initialization and startup

- Thread management
- Queue wiring
- Health monitoring
- Graceful shutdown
- Signal handling

**Monitoring Features**:
- Worker status checks
- Queue depth monitoring
- Memory tracking
- Conversation counting

**Design Decision**: 
Centralized orchestrator simplifies system control. Alternative would be distributed coordination, but adds complexity unnecessary for 3-component system.

---

## 🔌 Queue Architecture

### Queue 1: STT → LLM
**Purpose**: Deliver transcripts to language model

**Message Format**:
```python
{
    'type': 'transcript',
    'text': 'recognized speech text',
    'timestamp': 1234567890.123,
    'latency_ms': 150.0
}
```

**Size Limit**: 10 items (prevents memory buildup)

**Timeout**: 1 second for blocking operations

---

### Queue 2: LLM → TTS
**Purpose**: Deliver responses to speech synthesis

**Message Format**:
```python
{
    'type': 'response',
    'text': 'generated response text',
    'timestamp': 1234567890.456,
    'latency_ms': 850.0
}
```

**Size Limit**: 10 items

**Timeout**: 1 second

---

## 🎛️ Configuration Philosophy

### Why 16kHz Audio?
Vosk requires 16kHz sample rate. All audio pipelines configured to match.

### Why Queue Size = 10?
Prevents memory buildup while allowing some buffering. Chosen empirically.

### Why 4-bit Quantization?
Reduces LLM memory footprint by ~4x with minimal quality loss for conversational tasks.

### Why Medium TTS Model?
Balances naturalness and speed. Small models sound robotic, large models too slow for real-time.

---

## 🚦 Error Handling Strategy

### Worker-Level
- Each worker catches and logs its own exceptions
- Continues running despite individual failures
- Metrics track error frequency

### Queue-Level
- Timeout-based deadlock prevention
- Empty queue handling (non-blocking)
- Full queue detection (backpressure signal)

### System-Level
- Graceful shutdown on SIGINT/SIGTERM
- Resource cleanup (audio streams, files)
- Metrics export before exit

---

## 📊 Performance Baseline (Laptop)

**Expected Latencies**:
- STT: 100-200ms
- LLM: 500-1500ms ⚠️ *bottleneck*
- TTS: 200-500ms
- **Total**: 800-2200ms (0.8-2.2 seconds)

**Expected Memory**:
- STT: ~150MB
- LLM: ~2GB during inference
- TTS: ~200MB
- Orchestrator: ~50MB
- **Total**: ~2.5GB peak

**Target for Raspberry Pi 4** (4GB RAM):
- Need to optimize LLM inference
- Consider smaller model or quantization
- May need swap file for memory headroom

---

## 🔮 Future Architecture Considerations

### Scalability
- Add worker pools for parallel processing
- Implement priority queues for urgent requests
- Consider async/await for I/O operations

### Reliability
- Add worker health checks and auto-restart
- Implement circuit breakers for failing components
- Add request timeout and retry logic

### Features
- Wake word detection (Porcupine/Snowboy)
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
