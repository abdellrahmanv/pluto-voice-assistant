# 🏗️ Project Pluto - Architecture Documentation

## 🎯 Design Philosophy

Project Pluto is built on three core principles:

### 1. **Modularity**
Each component (STT, LLM, TTS) is an independent worker with clear responsibilities and interfaces.

### 2. **Queue-Based Communication**
Workers communicate through thread-safe queues, enabling:
- Asynchronous processing
- Natural backpressure handling
- Easy debugging and monitoring
- Clean separation of concerns

### 3. **Comprehensive Metrics**
Every operation is measured to identify bottlenecks before deploying to resource-constrained hardware (Raspberry Pi 4).

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      🪐 PLUTO ORCHESTRATOR                      │
│                  (Thread Management & Coordination)              │
└─────────────────────────────────────────────────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
    ┌────▼────┐          ┌─────▼─────┐         ┌─────▼─────┐
    │   STT   │──Queue──▶│    LLM    │──Queue──▶│    TTS    │
    │  Vosk   │          │  Qwen2.5  │          │   Piper   │
    └─────────┘          └───────────┘          └───────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
                         ┌──────▼──────┐
                         │   METRICS   │
                         │   LOGGER    │
                         └─────────────┘
```

---

## 🔄 Data Flow

### Stage 1: Speech Input (STT Worker)
```
User speaks ──▶ PyAudio captures audio ──▶ VAD detects speech
    ──▶ Vosk recognizes text ──▶ Queue: {"type": "transcript", "text": "..."}
```

### Stage 2: Language Processing (LLM Worker)
```
Queue receives transcript ──▶ Ollama API call ──▶ Qwen2.5 generates response
    ──▶ Queue: {"type": "response", "text": "..."}
```

### Stage 3: Speech Output (TTS Worker)
```
Queue receives response ──▶ Piper synthesizes WAV ──▶ PyAudio plays audio
    ──▶ User hears response
```

---

## 🧩 Component Deep Dive

### 1. Configuration System (`src/config.py`)

**Purpose**: Centralized configuration management

**Key Features**:
- Model paths and parameters
- Audio settings (16kHz for Vosk compatibility)
- Queue configurations
- Worker warmup settings
- Metrics thresholds

**Design Decision**: 
Single source of truth prevents configuration drift. All workers import settings from here.

---

### 2. STT Worker (`src/workers/stt_worker.py`)

**Technology**: Vosk (offline speech recognition)

**Thread**: Dedicated audio capture thread

**Responsibilities**:
- Continuous audio stream monitoring
- Voice Activity Detection (VAD) using energy threshold
- Speech segment extraction
- Vosk inference
- Transcript queuing

**Key Parameters**:
- **Sample Rate**: 16kHz (Vosk requirement)
- **Chunk Size**: 4096 samples (~256ms at 16kHz)
- **Energy Threshold**: 300 (tunable for noise floor)
- **Silence Threshold**: 20 chunks (~5 seconds)

**Design Decision**: 
Energy-based VAD is lightweight and sufficient for controlled environments. More sophisticated VAD (WebRTC VAD) could be added for noisy environments.

**Performance Considerations**:
- Model size: ~40MB (small model) for laptop testing
- Inference latency: 100-200ms typical
- Memory footprint: ~150MB

---

### 3. LLM Worker (`src/workers/llm_worker.py`)

**Technology**: Ollama + Qwen2.5 1.5B (4-bit quantized)

**Thread**: Queue processing thread

**Responsibilities**:
- Monitor STT→LLM queue
- Call Ollama API
- Manage conversation history
- Queue responses for TTS

**Key Parameters**:
- **Model**: `qwen2.5:1.5b-instruct-q4_K_M` (quantized for speed)
- **Temperature**: 0.7 (balanced creativity)
- **Max Tokens**: 100 (concise responses)
- **Timeout**: 30 seconds
- **History**: Last 10 exchanges

**Design Decision**: 
Ollama provides clean API abstraction. 4-bit quantization reduces memory and increases speed while maintaining quality for conversational use.

**Performance Considerations**:
- Model size: ~1GB on disk
- Inference latency: 500-1500ms (CPU-dependent)
- Memory footprint: ~2GB during inference
- **Bottleneck candidate**: Likely slowest component on Raspberry Pi

---

### 4. TTS Worker (`src/workers/tts_worker.py`)

**Technology**: Piper (neural TTS with ONNX runtime)

**Thread**: Queue processing thread

**Responsibilities**:
- Monitor LLM→TTS queue
- Synthesize speech with Piper
- Play audio through PyAudio
- Clean up temporary files

**Key Parameters**:
- **Model**: `en_US-lessac-medium.onnx` (quality/speed balance)
- **Output**: 22kHz WAV
- **Voice**: Default (configurable)

**Design Decision**: 
Piper chosen for offline capability and natural voice quality. Medium model balances quality and speed.

**Performance Considerations**:
- Model size: ~60MB
- Synthesis latency: 200-500ms
- Memory footprint: ~200MB
- Real-time factor: 0.2-0.5 (faster than real-time)

---

### 5. Metrics Logger (`src/metrics_logger.py`)

**Purpose**: Performance measurement and bottleneck identification

**Tracked Metrics**:
- **STT Latency**: Time from audio end to transcript
- **LLM Latency**: Time from transcript to response
- **TTS Latency**: Time from response to audio start
- **Total Latency**: Full conversation round-trip
- **Memory Usage**: RAM consumption (MB)
- **Queue Depth**: Backpressure indicators
- **Error Counts**: Component failures

**Output Formats**:
1. **CSV**: Time-series data for analysis
2. **JSON**: Structured export for processing
3. **Console**: Real-time feedback
4. **Summary**: Statistical analysis

**Design Decision**: 
Multiple output formats support different analysis needs. CSV for time-series plotting, JSON for programmatic access, console for immediate feedback.

---

### 6. Orchestrator (`src/orchestrator.py`)

**Purpose**: System coordination and lifecycle management

**Responsibilities**:
- Worker initialization and startup
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
