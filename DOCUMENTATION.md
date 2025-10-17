# 📚 Project Pluto - Complete Technical Documentation

**Version**: 0.1.0  
**Architecture**: Offline Voice Assistant (STT → LLM → TTS)  
**Purpose**: Laptop validation before Raspberry Pi 4 deployment

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Installation](#installation)
3. [Configuration Reference](#configuration-reference)
4. [Component Documentation](#component-documentation)
5. [API Reference](#api-reference)
6. [Metrics & Monitoring](#metrics--monitoring)
7. [Performance Tuning](#performance-tuning)
8. [Troubleshooting](#troubleshooting)
9. [Development Guide](#development-guide)

---

## 🎯 System Overview

### Purpose
Project Pluto validates the complete voice assistant pipeline on a laptop before deploying to Raspberry Pi 4. The system measures:
- Component latencies (STT, LLM, TTS)
- Memory consumption
- Queue depths and backpressure
- Total conversation latency

### Architecture
```
User Speech → Vosk (STT) → Qwen2.5 (LLM) → Piper (TTS) → Audio Output
                ↓              ↓               ↓
              Queue 1       Queue 2      Metrics Logger
```

### Components
- **STT Worker**: Vosk offline speech recognition (16kHz)
- **LLM Worker**: Ollama + Qwen2.5 1.5B (4-bit quantized)
- **TTS Worker**: Piper neural TTS (ONNX runtime)
- **Orchestrator**: Thread coordination and lifecycle
- **Metrics Logger**: Performance tracking and export

---

## 🔧 Installation

### Prerequisites
```powershell
# 1. Python 3.8+ (64-bit recommended)
python --version  # Should be 3.8+

# 2. Ollama installed and running
ollama --version

# 3. Piper binary available
piper --version
```

### Step 1: Clone/Download Project
```powershell
cd C:\Users\Asus\Desktop
git clone <your-repo-url> pluto
cd pluto
```

### Step 2: Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Verify activation
python -c "import sys; print(sys.prefix)"
# Should show path to pluto\venv
```

### Step 3: Install Python Dependencies
```powershell
pip install -r requirements.txt

# If PyAudio fails on Windows:
pip install pipwin
pipwin install pyaudio
```

### Step 4: Download Models

#### Vosk STT Model (~40MB)
```powershell
# Download from: https://alphacephei.com/vosk/models
# Recommended: vosk-model-small-en-us-0.15

# Create models directory
mkdir models

# Extract downloaded zip to models/
# Result: models/vosk-model-small-en-us-0.15/
```

#### Piper TTS Model (~60MB)
```powershell
# Download from: https://github.com/rhasspy/piper/releases
# Navigate to latest release → Assets
# Download: en_US-lessac-medium.onnx (and .json config)

# Place in models/
# Result: models/en_US-lessac-medium.onnx
```

#### Qwen2.5 LLM Model (~1GB)
```powershell
# Start Ollama server first
ollama serve

# In new terminal, pull model
ollama pull qwen2.5:0.5b-instruct-q4_K_M

# Verify
ollama list
# Should show: qwen2.5:0.5b-instruct-q4_K_M
```

### Step 5: Verify Installation
```powershell
# Run tests
pytest tests/test_integration.py -v

# Start application
python run.py
```

---

## ⚙️ Configuration Reference

### File: `src/config.py`

All system configuration in one place. Edit this file to customize behavior.

#### Audio Configuration

```python
AUDIO_CONFIG = {
    "sample_rate": 16000,      # Hz - MUST match Vosk requirement
    "channels": 1,             # Mono audio
    "chunk_size": 4096,        # Samples per read (~256ms at 16kHz)
    "energy_threshold": 300,   # VAD threshold (adjust for noise)
    "silence_chunks_threshold": 20,  # Chunks of silence to end (20 * 256ms = 5s)
}
```

**Tuning Tips**:
- **energy_threshold**: Increase in noisy environments (400-500), decrease for quiet (200-250)
- **chunk_size**: Larger = less CPU, more latency. 4096 is optimal.
- **silence_chunks_threshold**: Decrease for faster cutoff (15 = 3.8s), increase for patience (25 = 6.4s)

#### Vosk STT Configuration

```python
VOSK_CONFIG = {
    "model_path": "./models/vosk-model-small-en-us-0.15",
    "sample_rate": 16000,      # MUST match AUDIO_CONFIG
}
```

**Model Options**:
- **Small** (~40MB): Fast, good for testing. Accuracy ~85%
- **Large** (~1.8GB): Better accuracy (~95%), slower inference
- For Raspberry Pi: Use Small model

#### Ollama LLM Configuration

```python
OLLAMA_CONFIG = {
    "host": "http://localhost:11434",
    "model": "qwen2.5:0.5b-instruct-q4_K_M",
    "temperature": 0.7,         # 0=deterministic, 1=creative
    "max_tokens": 100,          # Response length (shorter=faster)
    "timeout": 30,              # Seconds before giving up
    "system_prompt": "You are a helpful voice assistant...",
    "max_history": 10,          # Conversation turns to remember
}
```

**Model Options**:
- **qwen2.5:0.5b-q4**: Faster, less capable
- **qwen2.5:1.5b-q4**: **Recommended** - balance of speed/quality
- **qwen2.5:3b-q4**: Better quality, slower (may not run on Pi)

**Tuning Tips**:
- **max_tokens**: 50 for speed, 150 for detailed answers
- **temperature**: 0.5 for factual, 0.9 for creative
- **max_history**: Increase for context-aware conversations (uses more memory)

#### Piper TTS Configuration

```python
PIPER_CONFIG = {
    "piper_binary": "piper",   # Or full path: "C:/path/to/piper.exe"
    "model_path": "./models/en_US-lessac-medium.onnx",
    "voice": None,             # Or specific speaker ID if multi-speaker model
}
```

**Model Options**:
- **low quality**: Fastest, robotic (~20MB)
- **medium quality**: **Recommended** - natural, fast (~60MB)
- **high quality**: Most natural, slower (~150MB)

#### Queue Configuration

```python
QUEUE_CONFIG = {
    "max_size": 10,            # Items per queue before blocking
    "get_timeout": 1,          # Seconds to wait for queue item
}
```

**Tuning Tips**:
- **max_size**: Increase to 20 for burst handling, decrease to 5 for strict real-time
- **get_timeout**: Decrease to 0.5 for faster shutdown response

#### Worker Configuration

```python
WORKER_CONFIG = {
    "warmup_enabled": True,    # Run warmup inference on startup
}
```

Set to `False` to skip warmup and start faster (cold start latency will be higher).

#### Metrics Configuration

```python
METRICS_CONFIG = {
    "csv_enabled": True,        # Export to CSV
    "json_enabled": True,       # Export to JSON
    "console_enabled": True,    # Print to console
    
    # Latency thresholds (warnings printed if exceeded)
    "max_stt_latency": 500,     # ms
    "max_llm_latency": 3000,    # ms
    "max_tts_latency": 1000,    # ms
    "max_total_latency": 5000,  # ms
}
```

#### Orchestrator Configuration

```python
ORCHESTRATOR_CONFIG = {
    "health_monitoring": True,        # Enable health checks
    "health_check_interval": 5,       # Seconds between checks
    "memory_monitoring": True,        # Track RAM usage
    "queue_monitoring": True,         # Track queue depths
}
```

Set all to `False` for minimal overhead (not recommended for testing).

---

## 🔨 Component Documentation

### 1. STT Worker (`src/workers/stt_worker.py`)

#### Purpose
Capture audio from microphone, detect speech, and transcribe to text using Vosk.

#### Class: `STTWorker`

**Constructor**:
```python
STTWorker(output_queue: queue.Queue, metrics_logger=None)
```

**Methods**:

##### `initialize() -> bool`
Load Vosk model and initialize PyAudio stream.

Returns:
- `True` if successful
- `False` if model not found or audio error

##### `warmup()`
Process silent audio to warm up recognition engine. Reduces cold start latency.

##### `start() -> bool`
Start audio capture thread. Returns `True` if successful.

##### `stop()`
Gracefully stop audio capture and close resources.

##### `get_status() -> dict`
Returns worker status:
```python
{
    'name': 'STT',
    'running': bool,
    'warmup_complete': bool,
    'processed': int,  # Number of transcripts produced
    'model_loaded': bool,
    'stream_active': bool
}
```

#### Internal Methods

##### `_process_audio()`
Main thread loop:
1. Read audio chunks from microphone
2. Detect speech using energy threshold
3. Buffer speech segments
4. Recognize with Vosk when silence detected
5. Put transcript on output queue

##### `_detect_speech(audio_data: bytes) -> bool`
Simple Voice Activity Detection using RMS energy.

Returns:
- `True` if audio energy > threshold (speech detected)
- `False` otherwise (silence)

##### `_process_speech(audio_buffer: list)`
Process captured speech:
1. Feed all chunks to Vosk recognizer
2. Get final result
3. Extract text
4. Put on queue with metadata

#### Queue Output Format

```python
{
    'type': 'transcript',
    'text': 'recognized text here',
    'timestamp': 1234567890.123,
    'latency_ms': 150.0
}
```

#### Performance Characteristics
- **Model Load Time**: 2-5 seconds (one-time)
- **Warmup Time**: 100-200ms
- **Per-Inference Latency**: 100-200ms
- **Memory Footprint**: ~150MB
- **CPU Usage**: 10-20% (single core)

---

### 2. LLM Worker (`src/workers/llm_worker.py`)

#### Purpose
Process transcripts and generate conversational responses using Ollama + Qwen2.5.

#### Class: `LLMWorker`

**Constructor**:
```python
LLMWorker(
    input_queue: queue.Queue,
    output_queue: queue.Queue,
    metrics_logger=None
)
```

**Methods**:

##### `initialize() -> bool`
Check Ollama server connectivity and model availability.

Returns:
- `True` if server reachable and model found
- `False` if connection error or model missing

##### `warmup()`
Run test inference with short prompt to load model into memory.

##### `start() -> bool`
Start queue processing thread. Returns `True` if successful.

##### `stop()`
Gracefully stop queue processing.

##### `clear_history()`
Clear conversation history (useful for new sessions).

##### `get_status() -> dict`
Returns worker status:
```python
{
    'name': 'LLM',
    'running': bool,
    'warmup_complete': bool,
    'processed': int,  # Number of responses generated
    'history_length': int,  # Conversation turns
    'server_reachable': bool
}
```

#### Internal Methods

##### `_process_queue()`
Main thread loop:
1. Get transcript from input queue (timeout 1s)
2. Generate response via Ollama API
3. Put response on output queue
4. Update conversation history

##### `_generate(prompt: str, max_tokens: Optional[int]) -> str`
Call Ollama API to generate response.

Parameters:
- `prompt`: User's text input
- `max_tokens`: Optional override for response length

Returns:
- Generated response text

Handles:
- Timeouts (returns error message)
- API errors (returns error message)
- Network failures (returns error message)

##### `_check_server() -> bool`
Quick health check for Ollama server availability.

#### Queue Input Format

```python
{
    'type': 'transcript',
    'text': 'user query text',
    'timestamp': float,
    'latency_ms': float
}
```

#### Queue Output Format

```python
{
    'type': 'response',
    'text': 'assistant response text',
    'timestamp': float,
    'latency_ms': float
}
```

#### Performance Characteristics
- **Server Start Time**: 5-10 seconds (one-time)
- **Model Pull Time**: 30-60 seconds (one-time download)
- **Warmup Time**: 500-1000ms
- **Per-Inference Latency**: 500-1500ms ⚠️ **BOTTLENECK**
- **Memory Footprint**: ~2GB during inference
- **CPU Usage**: 50-80% (all cores)

---

### 3. TTS Worker (`src/workers/tts_worker.py`)

#### Purpose
Synthesize speech from text using Piper and play audio through speakers.

#### Class: `TTSWorker`

**Constructor**:
```python
TTSWorker(input_queue: queue.Queue, metrics_logger=None)
```

**Methods**:

##### `initialize() -> bool`
Check Piper binary and model availability, initialize PyAudio.

Returns:
- `True` if Piper working and model found
- `False` if binary missing or model not found

##### `warmup()`
Synthesize short test phrase to load model into memory.

##### `start() -> bool`
Start queue processing thread. Returns `True` if successful.

##### `stop()`
Gracefully stop processing and clean up temporary files.

##### `get_status() -> dict`
Returns worker status:
```python
{
    'name': 'TTS',
    'running': bool,
    'warmup_complete': bool,
    'processed': int,  # Number of audio outputs
    'model_exists': bool,
    'piper_available': bool
}
```

#### Internal Methods

##### `_process_queue()`
Main thread loop:
1. Get response from input queue (timeout 1s)
2. Synthesize speech with Piper
3. Play audio through PyAudio
4. Log metrics

##### `_synthesize(text: str, play: bool) -> bool`
Call Piper to synthesize speech.

Parameters:
- `text`: Response text to synthesize
- `play`: Whether to play audio (False for warmup)

Returns:
- `True` if synthesis successful
- `False` on error

Process:
1. Call Piper subprocess with text input
2. Piper writes WAV to temp file
3. Return success status

##### `_play_wav(wav_path: Path)`
Play WAV file through PyAudio.

Process:
1. Open WAV file
2. Create PyAudio stream with matching parameters
3. Read and write chunks until complete
4. Close stream

##### `_check_piper() -> bool`
Quick availability check for Piper binary.

#### Queue Input Format

```python
{
    'type': 'response',
    'text': 'text to synthesize',
    'timestamp': float,
    'latency_ms': float
}
```

#### Performance Characteristics
- **Model Load Time**: 1-2 seconds (one-time)
- **Warmup Time**: 200-400ms
- **Per-Synthesis Latency**: 200-500ms
- **Real-Time Factor**: 0.2-0.5 (faster than real-time)
- **Memory Footprint**: ~200MB
- **CPU Usage**: 20-30% (single core)

---

### 4. Orchestrator (`src/orchestrator.py`)

#### Purpose
Coordinate all workers, manage lifecycle, monitor health, handle shutdown.

#### Class: `PlutoOrchestrator`

**Constructor**:
```python
PlutoOrchestrator()
```

Automatically creates:
- Two queues (STT→LLM, LLM→TTS)
- Metrics logger
- Three workers (STT, LLM, TTS)
- Signal handlers (SIGINT, SIGTERM)

**Methods**:

##### `initialize() -> bool`
Initialize all workers in sequence.

Returns:
- `True` if all workers start successfully
- `False` if any worker fails

Process:
1. Print configuration summary
2. Start STT worker
3. Start LLM worker
4. Start TTS worker
5. Setup queue monitoring hooks

##### `start() -> bool`
Start orchestrator and health monitoring.

Returns:
- `True` if initialization successful
- `False` on failure

##### `run()`
Main run loop. Blocks until shutdown signal received.

##### `shutdown()`
Graceful shutdown sequence:
1. Stop all workers
2. Export metrics
3. Print summary

##### `get_status() -> dict`
Returns complete system status:
```python
{
    'running': bool,
    'workers': [  # List of worker statuses
        {'name': 'STT', ...},
        {'name': 'LLM', ...},
        {'name': 'TTS', ...}
    ],
    'queues': {
        'stt_to_llm': int,  # Current depth
        'llm_to_tts': int
    },
    'conversations': int  # Total count
}
```

##### `print_status()`
Print formatted status to console.

#### Internal Methods

##### `_setup_queue_monitoring()`
Wrap queue put/get methods to track conversation flow.

##### `_wrap_stt_put(item, **kwargs)`
Hook when STT puts transcript. Marks conversation start.

##### `_wrap_tts_get(**kwargs)`
Hook when TTS gets response. Marks conversation end, calculates total latency.

##### `_health_monitor()`
Background thread that periodically:
- Logs memory usage
- Logs queue depths
- Runs every `health_check_interval` seconds

##### `_signal_handler(signum, frame)`
Handle SIGINT (Ctrl+C) and SIGTERM gracefully.

---

### 5. Metrics Logger (`src/metrics_logger.py`)

#### Purpose
Collect, store, and export performance metrics for analysis.

#### Class: `MetricsLogger`

**Constructor**:
```python
MetricsLogger(session_id: Optional[str] = None)
```

If `session_id` not provided, uses timestamp: `YYYYMMDD_HHMMSS`

**Methods**:

##### `log_metric(component, metric_type, value, unit, metadata=None)`
Log a single performance metric.

Parameters:
- `component`: 'stt', 'llm', 'tts', 'system', 'total'
- `metric_type`: 'latency', 'memory', 'queue_depth', 'error'
- `value`: Numeric measurement
- `unit`: 'ms', 'MB', 'items', 'count'
- `metadata`: Optional dict with extra info

Actions:
- Appends to in-memory list
- Updates statistics
- Writes to CSV (if enabled)
- Prints to console (if enabled)
- Checks against thresholds

##### `log_conversation_start()`
Mark start of new conversation cycle.

##### `log_conversation_end(total_latency: float)`
Mark end of conversation, log total latency.

##### `log_memory_usage() -> float`
Measure and log current process memory usage.

Returns:
- Memory in MB

##### `log_error(component, error_type, details)`
Log error occurrence.

##### `get_statistics() -> dict`
Calculate statistics for all logged metrics.

Returns:
```python
{
    'stt': {
        'latency': {
            'count': int,
            'min': float,
            'max': float,
            'mean': float,
            'median': float
        }
    },
    'llm': { ... },
    'tts': { ... },
    ...
}
```

##### `print_summary()`
Print formatted summary to console with statistics.

##### `export_json()`
Export all metrics and statistics to JSON file.

##### `close()`
Finalize logging:
- Export JSON
- Print summary
- Close files

#### Data Class: `PerformanceMetric`

```python
@dataclass
class PerformanceMetric:
    timestamp: float
    component: str
    metric_type: str
    value: float
    unit: str
    metadata: Dict[str, Any] = None
```

#### Output Files

**CSV** (`logs/metrics_SESSIONID.csv`):
```csv
timestamp,timestamp_readable,component,metric_type,value,unit,metadata
1234567890.123,2024-01-01T12:00:00,stt,latency,150.0,ms,{}
```

**JSON** (`logs/metrics_SESSIONID.json`):
```json
{
  "session_id": "20240101_120000",
  "session_start": 1234567890.0,
  "conversation_count": 5,
  "metrics": [ ... ],
  "statistics": { ... }
}
```

**Summary** (`logs/summary_SESSIONID.txt`):
```
🪐 PROJECT PLUTO - SESSION SUMMARY
Session ID: 20240101_120000
Runtime: 120.5s
Conversations: 5

STATISTICS:
{ JSON statistics dump }
```

---

## 📊 Metrics & Monitoring

### Tracked Metrics

| Metric | Component | Unit | Typical Value | Threshold |
|--------|-----------|------|---------------|-----------|
| STT Latency | stt | ms | 100-200 | 500 |
| LLM Latency | llm | ms | 500-1500 | 3000 |
| TTS Latency | tts | ms | 200-500 | 1000 |
| Total Latency | total | ms | 800-2200 | 5000 |
| Memory Usage | system | MB | 2500 peak | N/A |
| Queue Depth | system | items | 0-2 | N/A |
| Errors | all | count | 0 | N/A |

### Real-Time Console Output

```
🎙️  Speech detected...
   📝 Recognized: "Hello Pluto"
  🎤 STT: 150ms
   🤔 Thinking about: "Hello Pluto"
   💭 Response: "Hi there! How can I help you?"
  🧠 LLM: 850ms
   🗣️  Speaking: "Hi there! How can I help you!"
  🔊 TTS: 300ms
  ⏱️  total: 1300ms
```

### CSV Analysis

Import CSV into Excel/pandas for time-series analysis:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('logs/metrics_20240101_120000.csv')

# Plot latencies over time
stt = df[df['metric_type'] == 'latency'][df['component'] == 'stt']
plt.plot(stt['timestamp'], stt['value'])
plt.title('STT Latency Over Time')
plt.ylabel('Latency (ms)')
plt.show()
```

### JSON Programmatic Access

```python
import json

with open('logs/metrics_20240101_120000.json') as f:
    data = json.load(f)

print(f"Total conversations: {data['conversation_count']}")
print(f"Mean LLM latency: {data['statistics']['llm']['latency']['mean']}")
```

---

## ⚡ Performance Tuning

### Laptop Baseline (Expected)

**Hardware**: Modern laptop (8GB+ RAM, 4+ core CPU)

| Component | Latency | Memory | Notes |
|-----------|---------|--------|-------|
| STT | 100-200ms | ~150MB | Optimal |
| LLM | 500-1500ms | ~2GB | **Bottleneck** |
| TTS | 200-500ms | ~200MB | Good |
| **Total** | **800-2200ms** | **~2.5GB** | Acceptable |

### Raspberry Pi 4 Projections

**Hardware**: Pi 4 (4GB RAM, ARM Cortex-A72)

| Component | Expected Latency | Expected Memory | Notes |
|-----------|------------------|-----------------|-------|
| STT | 200-400ms | ~150MB | Slight slowdown |
| LLM | **2000-5000ms** | ~2GB | **Major bottleneck** |
| TTS | 400-800ms | ~200MB | Manageable |
| **Total** | **2600-6200ms** | **~2.5GB** | May need optimization |

### Optimization Strategies

#### 1. LLM Optimization (Priority #1)

**Option A**: Use smaller model
```python
OLLAMA_CONFIG = {
    "model": "qwen2.5:0.5b-instruct-q4_K_M",  # Faster, less capable
    ...
}
```
Expected: 300-800ms latency, ~1GB memory

**Option B**: Reduce max_tokens
```python
OLLAMA_CONFIG = {
    "max_tokens": 50,  # Shorter responses = faster
    ...
}
```
Expected: 30-40% latency reduction

**Option C**: Enable GPU acceleration (if available)
- Pi 4 has VideoCore VI GPU (limited ML support)
- Consider Coral USB Accelerator for Edge TPU

#### 2. STT Optimization

**Use lightweight model**:
```python
VOSK_CONFIG = {
    "model_path": "./models/vosk-model-small-en-us-0.15",  # Already optimal
}
```

**Reduce chunk size for faster VAD** (increases CPU):
```python
AUDIO_CONFIG = {
    "chunk_size": 2048,  # Half size = twice as many reads
}
```

#### 3. TTS Optimization

**Use low-quality model**:
```python
PIPER_CONFIG = {
    "model_path": "./models/en_US-lessac-low.onnx",  # Faster, less natural
}
```
Expected: 100-250ms latency, ~80MB memory

#### 4. System-Wide Optimizations

**Disable health monitoring** (save ~2-3% CPU):
```python
ORCHESTRATOR_CONFIG = {
    "health_monitoring": False,
    "memory_monitoring": False,
    "queue_monitoring": False,
}
```

**Disable warmup** (faster startup):
```python
WORKER_CONFIG = {
    "warmup_enabled": False,
}
```
Warning: First inference will be slower

**Reduce queue size** (save memory):
```python
QUEUE_CONFIG = {
    "max_size": 5,  # Half the default
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### "Vosk model not found"

**Symptoms**:
```
⚠️  Vosk model not found at: ./models/vosk-model-small-en-us-0.15
```

**Solution**:
1. Download model: https://alphacephei.com/vosk/models
2. Extract to `models/` directory
3. Verify path in `src/config.py`:
   ```python
   VOSK_CONFIG = {
       "model_path": "./models/vosk-model-small-en-us-0.15",
   }
   ```

---

#### "Cannot connect to Ollama"

**Symptoms**:
```
❌ Cannot connect to Ollama at http://localhost:11434
```

**Solution**:
1. Start Ollama server:
   ```powershell
   ollama serve
   ```
2. Verify server running:
   ```powershell
   curl http://localhost:11434/api/tags
   ```
3. Check firewall not blocking port 11434

---

#### "Model qwen2.5:0.5b-instruct-q4_K_M not found"

**Symptoms**:
```
⚠️  Model 'qwen2.5:0.5b-instruct-q4_K_M' not found
```

**Solution**:
```powershell
ollama pull qwen2.5:0.5b-instruct-q4_K_M

# Verify
ollama list
```

---

#### "Piper binary not found"

**Symptoms**:
```
❌ Piper binary not found: piper
```

**Solution**:
1. Download Piper: https://github.com/rhasspy/piper/releases
2. Extract `piper.exe` to accessible location
3. Either:
   - Add to system PATH
   - Or set full path in config:
     ```python
     PIPER_CONFIG = {
         "piper_binary": "C:/path/to/piper.exe",
         ...
     }
     ```

---

#### "PyAudio could not find microphone"

**Symptoms**:
```
❌ Error opening audio stream
```

**Solution**:
1. Check microphone connected and recognized (Windows Sound Settings)
2. Test microphone in another app
3. Verify PyAudio installation:
   ```powershell
   python -c "import pyaudio; p = pyaudio.PyAudio(); print(p.get_device_count())"
   ```
4. If shows 0 devices, reinstall PyAudio:
   ```powershell
   pip uninstall pyaudio
   pip install pipwin
   pipwin install pyaudio
   ```

---

#### LLM responses are slow

**Symptoms**:
```
⚠️  WARNING: LLM latency (3200ms) exceeds threshold (3000ms)
```

**Solutions**:
1. **Use smaller model**:
   ```powershell
   ollama pull qwen2.5:0.5b-instruct-q4_K_M
   ```
   Update `src/config.py`:
   ```python
   OLLAMA_CONFIG = {
       "model": "qwen2.5:0.5b-instruct-q4_K_M",
       ...
   }
   ```

2. **Reduce max_tokens**:
   ```python
   OLLAMA_CONFIG = {
       "max_tokens": 50,  # Shorter responses
       ...
   }
   ```

3. **Lower temperature** (slightly faster):
   ```python
   OLLAMA_CONFIG = {
       "temperature": 0.5,
       ...
   }
   ```

---

#### VAD not detecting speech

**Symptoms**:
- Speaks but nothing happens
- "Listening..." but never "Speech detected"

**Solutions**:
1. **Lower energy threshold**:
   ```python
   AUDIO_CONFIG = {
       "energy_threshold": 200,  # From 300
       ...
   }
   ```

2. **Test microphone level**:
   ```powershell
   python -c "
   import pyaudio, audioop
   p = pyaudio.PyAudio()
   stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True)
   while True:
       data = stream.read(4096)
       print(audioop.rms(data, 2))
   "
   ```
   Speak and note peak values. Set `energy_threshold` to 70% of peak.

---

#### VAD too sensitive (triggers on background noise)

**Symptoms**:
- Random "Speech detected" when quiet
- False transcripts

**Solutions**:
1. **Raise energy threshold**:
   ```python
   AUDIO_CONFIG = {
       "energy_threshold": 400,  # From 300
       ...
   }
   ```

2. **Increase silence threshold**:
   ```python
   AUDIO_CONFIG = {
       "silence_chunks_threshold": 25,  # From 20 (longer patience)
       ...
   }
   ```

---

## 👨‍💻 Development Guide

### Running Tests

```powershell
# All tests
pytest tests/test_integration.py -v

# Specific test
pytest tests/test_integration.py::TestMetricsLogger::test_metric_logging -v

# With coverage
pytest tests/test_integration.py --cov=src --cov-report=html
```

### Adding New Metrics

1. **Choose metric type**: latency, memory, custom
2. **Log in appropriate worker**:
   ```python
   self.metrics.log_metric('component', 'type', value, 'unit')
   ```
3. **Update threshold** (optional) in `src/config.py`:
   ```python
   METRICS_CONFIG = {
       "max_your_metric": 1000,
       ...
   }
   ```
4. **Add threshold check** in `metrics_logger.py`:
   ```python
   def _check_thresholds(self, metric):
       if metric.metric_type == 'your_type':
           threshold = METRICS_CONFIG['max_your_metric']
           if metric.value > threshold:
               print(f"⚠️  WARNING: ...")
   ```

### Adding New Worker

1. **Create file**: `src/workers/new_worker.py`
2. **Implement class**:
   ```python
   class NewWorker:
       def __init__(self, input_queue, output_queue, metrics_logger=None):
           ...
       
       def initialize(self) -> bool:
           ...
       
       def warmup(self):
           ...
       
       def start(self) -> bool:
           self.thread = threading.Thread(target=self._process, daemon=True)
           self.thread.start()
           ...
       
       def stop(self):
           ...
       
       def get_status(self) -> dict:
           ...
       
       def _process(self):
           while self.running:
               ...
   ```
3. **Export in** `src/workers/__init__.py`:
   ```python
   from .new_worker import NewWorker
   ```
4. **Wire in orchestrator** `src/orchestrator.py`:
   ```python
   self.new_worker = NewWorker(queue_in, queue_out, self.metrics)
   ```

### Code Style

- **Docstrings**: All public methods
- **Type hints**: Function parameters and returns
- **Comments**: Complex logic only
- **Formatting**: Follow existing patterns
- **Emojis**: Use in print statements for UX

### Git Workflow

```powershell
# Create feature branch
git checkout -b feature/new-feature

# Make changes
git add .
git commit -m "Add new feature: description"

# Push
git push origin feature/new-feature

# Create pull request on GitHub
```

---

## 📞 Support & Resources

### Documentation
- **QUICKSTART.md**: Fast setup guide
- **ARCHITECTURE.md**: Design philosophy
- **DIAGRAMS.md**: Visual references
- **FILE_INDEX.md**: File navigation

### External Resources
- **Vosk**: https://alphacephei.com/vosk/
- **Ollama**: https://ollama.ai/
- **Piper**: https://github.com/rhasspy/piper
- **Qwen2.5**: https://github.com/QwenLM/Qwen2.5

### Project Info
- **Version**: 0.1.0
- **License**: MIT
- **Python**: 3.8+
- **Platform**: Windows 10/11, Linux (untested on macOS)

---

**End of Documentation**

For complete project overview, return to [README.md](README.md)
