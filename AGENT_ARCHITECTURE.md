# 🪐 Pluto Agent Architecture

**Project Pluto - Vision-Driven Reflex Agent Voice Assistant**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Type](#architecture-type)
3. [System Components](#system-components)
4. [Agent States](#agent-states)
5. [Data Flow](#data-flow)
6. [Worker Threads](#worker-threads)
7. [Queue System](#queue-system)
8. [Reflex Agent Behavior](#reflex-agent-behavior)
9. [Fallback Mechanisms](#fallback-mechanisms)

---

## 🎯 Overview

**Pluto** is a **Reflex Agent** with the following characteristics:

- **Event-Driven**: Reacts to external stimuli (face detection, voice input)
- **State-Based**: Maintains internal state to manage conversations
- **Multi-Modal**: Combines vision (camera) and voice (microphone/speaker)
- **Real-Time**: Processes inputs and generates responses with minimal latency
- **Fault-Tolerant**: Falls back gracefully when components fail

**Core Philosophy**: "See a person → Greet them → Listen → Respond → Repeat"

---

## 🏗️ Architecture Type

### **Reflex Agent with State**

```
┌─────────────────────────────────────────────────────────────┐
│                      ENVIRONMENT                            │
│  👤 Person in front of camera                              │
│  🗣️ Person speaking                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                        SENSORS                              │
│  📷 Vision Sensor (YuNet face detection)                   │
│  🎤 Audio Sensor (Microphone)                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENT (Orchestrator)                     │
│  🧠 State Manager (AgentStateManager)                      │
│  🔄 State Machine (8 states)                               │
│  📊 Performance Monitoring                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI MODELS (Workers)                      │
│  🎤 STT Worker (Whisper)                                   │
│  🧠 LLM Worker (Qwen2.5 via Ollama)                        │
│  🔊 TTS Worker (Piper)                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       ACTUATORS                             │
│  🔊 Speaker (Audio output)                                  │
│  📝 Performance Reports (Markdown files)                    │
└─────────────────────────────────────────────────────────────┘
```

**Key Characteristics:**

1. **Condition-Action Rules**:
   - `IF face_detected THEN lock_face AND greet`
   - `IF speech_detected THEN process_with_llm`
   - `IF response_ready THEN speak`

2. **Internal State**:
   - Tracks which face is locked
   - Remembers conversation context (5 turns)
   - Monitors system resources

3. **No Planning**:
   - Reacts immediately to stimuli
   - No future prediction
   - Simple, fast, deterministic

---

## 🧩 System Components

### **1. Orchestrator** (`src/orchestrator.py`)
**Role**: Central coordinator and agent brain

**Responsibilities**:
- Initialize all workers
- Manage agent state machine
- Monitor vision events
- Coordinate conversation flow
- Handle graceful shutdown
- Monitor system health

**Key Features**:
- Vision timeout fallback (10 seconds)
- Queue monitoring
- Performance tracking
- Signal handling (Ctrl+C)

---

### **2. Agent State Manager** (`src/agent_state.py`)
**Role**: Finite State Machine for conversation management

**States** (8 total):

```
┌──────────┐
│   IDLE   │ ← No face detected, waiting
└─────┬────┘
      │ 👤 Face appears
      ▼
┌──────────────┐
│FACE_DETECTED │ ← Counting frames to confirm
└──────┬───────┘
       │ ✅ Lock confirmed
       ▼
┌─────────────┐
│  LOCKED_IN  │ ← Ready to greet
└──────┬──────┘
       │ 👋 Send greeting
       ▼
┌──────────────┐
│   GREETING   │ ← Playing greeting TTS
└──────┬───────┘
       │ ✅ Greeting done
       ▼
┌──────────────┐
│  LISTENING   │ ← STT active, waiting for speech
└──────┬───────┘
       │ 🗣️ Speech detected
       ▼
┌──────────────┐
│ PROCESSING   │ ← LLM generating response
└──────┬───────┘
       │ 💬 Response ready
       ▼
┌──────────────┐
│ RESPONDING   │ ← TTS playing response
└──────┬───────┘
       │ ✅ Response done
       ▼
┌──────────────┐ (loops back to LISTENING)
│  FACE_LOST   │ ← Face disappeared, cleanup
└──────┬───────┘
       │ ⏱️ Timeout
       ▼
    (IDLE)
```

**Valid Transitions**:
- IDLE → FACE_DETECTED
- FACE_DETECTED → LOCKED_IN or IDLE
- LOCKED_IN → GREETING
- GREETING → LISTENING
- LISTENING → PROCESSING
- PROCESSING → RESPONDING
- RESPONDING → LISTENING (loop)
- Any state → FACE_LOST (person leaves)
- FACE_LOST → IDLE (reset)

**State Methods**:
- `transition(new_state, reason)` - Change state with validation
- `lock_face(face_id)` - Lock onto detected face
- `is_locked()` - Check if face is locked
- `should_listen()` - Should STT be active?
- `should_greet()` - Should send greeting?
- `reset()` - Return to IDLE

---

### **3. Vision Worker** (`src/workers/vision_worker.py`)
**Role**: Computer vision sensor

**Technology**: YuNet face detection (OpenCV DNN)

**Responsibilities**:
- Capture frames from camera (10 FPS)
- Detect faces in frame
- Track faces across frames
- Lock onto stable faces (5+ frames)
- Report face events to orchestrator

**Events**:
- `idle` - No faces
- `face_detected` - New face(s) seen
- `face_locked` - Face stable for 5+ frames
- `locked_tracking` - Tracking locked face
- `face_lost` - Locked face disappeared

**Performance**:
- ~100ms per frame (Raspberry Pi 5)
- 10 FPS target
- Face confidence threshold: 0.6

---

### **4. STT Worker** (`src/workers/stt_worker.py`)
**Role**: Speech-to-Text conversion

**Technology**: OpenAI Whisper (tiny model)

**Responsibilities**:
- Capture audio from microphone
- Detect voice activity (VAD)
- Transcribe speech to text
- Send transcripts to LLM

**Configuration**:
- Model: `whisper-tiny` (39M params)
- Device: CPU
- Language: English
- Beam size: 5
- Temperature: 0.0 (deterministic)

**Performance**:
- ~150-200ms latency (target: <200ms)
- ~1GB RAM
- Good accuracy for conversational speech

**States**:
- Paused: When no face locked (vision mode)
- Active: When face locked or voice-only mode

---

### **5. LLM Worker** (`src/workers/llm_worker.py`)
**Role**: Natural language understanding and generation

**Technology**: Qwen2.5:0.5b (via Ollama)

**Responsibilities**:
- Receive transcribed text
- Generate contextual responses
- Maintain conversation history (5 turns)
- Send responses to TTS

**Configuration**:
- Model: `qwen2.5:0.5b-instruct-q4_k_M`
- Host: `http://localhost:11434`
- Temperature: 0.7
- Top-p: 0.9
- Max tokens: 150
- History: 5 turns

**System Prompt**:
> "You are a helpful voice assistant. Give concise, natural responses suitable for speech output. Keep answers brief (1-3 sentences) unless specifically asked for more detail."

**Performance**:
- ~800-1200ms latency (target: <1500ms)
- 0.5B parameters (quantized)
- Optimized for edge devices

---

### **6. TTS Worker** (`src/workers/tts_worker.py`)
**Role**: Text-to-Speech synthesis

**Technology**: Piper neural TTS

**Responsibilities**:
- Receive text responses
- Synthesize natural speech
- Play audio through speaker

**Configuration**:
- Model: `en_US-lessac-medium.onnx`
- Sample rate: 22050 Hz
- Speaker ID: 0
- Length scale: 1.0
- Noise: 0.667

**Performance**:
- ~100-150ms latency (target: <150ms)
- Natural-sounding voice
- Low resource usage

---

### **7. Performance Reporter** (`src/performance_reporter.py`)
**Role**: System monitoring and reporting

**Responsibilities**:
- Track latency for each component
- Monitor CPU, memory, temperature
- Generate ASCII/Unicode performance reports
- Log conversation events
- Track model configurations

**Report Sections**:
1. **Summary**: Overall score, key metrics
2. **Model Performance**: Per-model analysis
3. **Latency Analysis**: STT, LLM, TTS, total
4. **System Resources**: CPU, memory, temperature
5. **Statistics**: Min/avg/max for all metrics
6. **Recommendations**: Optimization suggestions

**Visualization**: ASCII/Unicode graphs (terminal-friendly)

---

## 🔄 Data Flow

### **Complete Conversation Flow**

```
1. 👁️ VISION DETECTION
   Camera → Vision Worker → Orchestrator
   Face detected → Lock face → Transition to LOCKED_IN

2. 👋 GREETING
   Orchestrator → LLM Queue → TTS Worker → Speaker
   "Hi there! I'm Pluto, how can I help you today?"

3. 🎤 LISTENING
   Microphone → STT Worker → Transcript
   User: "What's the weather today?"

4. 🧠 LLM PROCESSING
   Transcript → LLM Worker → Ollama API → Response
   "I'm a voice assistant without internet access..."

5. 🔊 RESPONSE
   Response → TTS Worker → Speaker
   Agent speaks response

6. 🔁 LOOP
   Back to LISTENING state
   Wait for next user input

7. 👋 EXIT
   Face lost → FACE_LOST state → Reset to IDLE
```

---

## 🔀 Queue System

### **Three Main Queues**:

1. **STT → LLM Queue** (`stt_to_llm_queue`)
   - Type: `queue.Queue`
   - Max size: 10
   - Content: `{'text': 'transcribed speech'}`
   - Flow: Speech transcripts from STT to LLM

2. **LLM → TTS Queue** (`llm_to_tts_queue`)
   - Type: `queue.Queue`
   - Max size: 10
   - Content: `{'text': 'response', 'priority': 'normal'}`
   - Flow: Generated responses from LLM to TTS

3. **Vision → Orchestrator Queue** (`vision_to_orchestrator_queue`)
   - Type: `queue.Queue`
   - Max size: 5
   - Content: `{'state': 'face_locked', 'locked_face': {...}}`
   - Flow: Face detection events from Vision to Orchestrator

### **Queue Monitoring**:
- Health monitor checks queue depth every 5 seconds
- Warns if queues are backing up
- Tracks queue depth in performance reports

---

## 🤖 Reflex Agent Behavior

### **Perception-Action Cycle**:

```python
while running:
    # 1. PERCEIVE
    event = vision_queue.get()  # or speech detected
    
    # 2. INTERPRET
    current_state = agent_state.current_state
    
    # 3. DECIDE (condition-action rules)
    if current_state == IDLE and event == 'face_detected':
        action = 'lock_face_and_greet'
    elif current_state == LISTENING and event == 'speech_detected':
        action = 'process_with_llm'
    elif current_state == PROCESSING and event == 'response_ready':
        action = 'speak_response'
    
    # 4. ACT
    execute(action)
    
    # 5. UPDATE STATE
    agent_state.transition(next_state)
```

### **Key Behaviors**:

1. **Opportunistic Greeting**:
   - Sees face → Immediately greets
   - No delay, no waiting
   - Proactive engagement

2. **Contextual Listening**:
   - Only listens when face locked
   - Pauses STT when idle
   - Saves processing power

3. **Conversational Loop**:
   - Listen → Process → Respond → Listen (repeat)
   - Maintains conversation until face lost
   - Tracks conversation turns

4. **Graceful Reset**:
   - Face lost → Wait 2 seconds
   - Clear conversation history
   - Return to IDLE
   - Ready for next person

---

## 🛡️ Fallback Mechanisms

### **1. Vision Timeout Fallback** (NEW)

**Problem**: Camera might not work on Raspberry Pi

**Solution**: 10-second grace period

```
START
  ↓
Wait 10 seconds
  ↓
Camera working? ──YES──→ Continue vision mode
  ↓ NO
Announce: "I can't see you, but I'm all ears!"
  ↓
Enable STT (voice-only mode)
  ↓
Continue as voice assistant
```

**User Experience**:
- System doesn't hang or crash
- Clear audio announcement
- Voice still works perfectly
- Logged in performance report

---

### **2. Worker Failure Handling**

**Each worker has**:
- Initialization checks
- Graceful error handling
- Fallback defaults
- Status reporting

**Example**:
```python
if not stt_worker.start():
    print("❌ STT Worker failed")
    return False  # Don't start system
```

---

### **3. Model Fallback**

**LLM Connection Lost**:
- Retry connection
- Log warning
- Queue responses for retry
- Clear error message to user

**STT Recognition Fails**:
- "Sorry, I didn't catch that"
- Wait for next input
- No crash

---

## 📊 Performance Characteristics

### **Latency Targets**:
- **STT**: <200ms (typically 150-200ms)
- **LLM**: <1500ms (typically 800-1200ms)
- **TTS**: <150ms (typically 100-150ms)
- **Total**: <2000ms (typically 1200-1500ms)

### **Resource Usage** (Raspberry Pi 5):
- **CPU**: 40-60% during conversation
- **Memory**: 1.2-1.5 GB RAM
- **Temperature**: 55-65°C (with heatsink)

### **Throughput**:
- **Conversations/hour**: 100+ possible
- **Face detection**: 10 FPS
- **Response time**: ~1.5s average

---

## 🎯 Design Decisions

### **Why Reflex Agent?**
1. ✅ **Fast**: Immediate reactions
2. ✅ **Simple**: Easy to understand and debug
3. ✅ **Reliable**: Predictable behavior
4. ✅ **Edge-Friendly**: Low computational overhead
5. ✅ **Deterministic**: Same input → same output

### **Why State Machine?**
1. ✅ **Clear states**: Know exactly where agent is
2. ✅ **Validated transitions**: Prevents impossible states
3. ✅ **Debuggable**: State history for troubleshooting
4. ✅ **Maintainable**: Easy to add new states/transitions

### **Why Multi-Threading?**
1. ✅ **Parallel processing**: Vision + Audio simultaneously
2. ✅ **Non-blocking**: No one worker blocks others
3. ✅ **Responsive**: Fast reaction to events
4. ✅ **Scalable**: Easy to add new workers

### **Why Queues?**
1. ✅ **Decoupling**: Workers don't depend on each other
2. ✅ **Buffering**: Handle bursts of activity
3. ✅ **Thread-safe**: Built-in synchronization
4. ✅ **Monitoring**: Easy to track data flow

---

## 🚀 Deployment Architecture

### **Raspberry Pi 5 Setup**:

```
┌─────────────────────────────────────────────────────────┐
│              Raspberry Pi 5 (8GB RAM)                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🐧 Raspberry Pi OS (64-bit)                           │
│  🐍 Python 3.11                                        │
│  🦙 Ollama (local LLM server)                          │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │           Pluto Voice Assistant                 │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  📷 Camera → Vision Worker (YuNet)             │   │
│  │  🎤 Mic → STT Worker (Whisper)                 │   │
│  │  🧠 LLM Worker ← → Ollama (Qwen2.5)            │   │
│  │  🔊 TTS Worker (Piper) → Speaker               │   │
│  │  🎯 Orchestrator (State Machine)               │   │
│  │  📊 Performance Reporter                        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  📁 /home/pi/pluto/                                    │
│     ├── src/          (Python code)                    │
│     ├── models/       (Whisper, Piper, YuNet)         │
│     ├── logs/         (Performance reports)            │
│     └── config/       (Configuration files)            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Summary

**Pluto is a Reflex Agent that**:

1. ✅ **Sees people** with computer vision
2. ✅ **Greets proactively** when faces detected
3. ✅ **Listens** with speech recognition
4. ✅ **Thinks** with local LLM
5. ✅ **Responds** with natural TTS
6. ✅ **Tracks** all performance metrics
7. ✅ **Falls back** when components fail
8. ✅ **Runs efficiently** on edge devices

**Architecture Type**: State-Based Reflex Agent with Multi-Modal Input

**Best For**: Interactive kiosks, home assistants, robots, edge devices

**Not For**: Complex planning tasks, multi-step reasoning, strategic games

---

**Created**: October 18, 2025  
**Version**: 2.0  
**Author**: Pluto Development Team
