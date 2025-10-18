# PLUTO - Simple Architecture Diagram

## 🤖 Agent Type: State-Based Reflex Agent

```
┌─────────────────────────────────────────────────────────────┐
│                    PLUTO VOICE ASSISTANT                    │
│                   (Reflex Agent - FSM)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🧠 AI Models

```
╔════════════════════════════════════════════════════════════╗
║                        AI MODELS                           ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  ┌──────────────────────────────────────────────────┐    ║
║  │ 🎤 Speech-to-Text (STT)                          │    ║
║  │ Model: whisper-tiny                              │    ║
║  │ Target: < 200ms                                  │    ║
║  └──────────────────────────────────────────────────┘    ║
║                          ↓                                 ║
║  ┌──────────────────────────────────────────────────┐    ║
║  │ 🧠 Language Model (LLM)                          │    ║
║  │ Model: qwen2.5:0.5b-instruct-q4_k_M              │    ║
║  │ Target: < 1500ms                                 │    ║
║  └──────────────────────────────────────────────────┘    ║
║                          ↓                                 ║
║  ┌──────────────────────────────────────────────────┐    ║
║  │ 🔊 Text-to-Speech (TTS)                          │    ║
║  │ Model: piper en_US-lessac-medium                 │    ║
║  │ Target: < 150ms                                  │    ║
║  └──────────────────────────────────────────────────┘    ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

## 🔄 State Machine (8 States)

```
      ┌──────────────────────────────────────────────────┐
      │                  STATE FLOW                      │
      └──────────────────────────────────────────────────┘

            ┌──────────┐
            │   IDLE   │ (Waiting for someone)
            └─────┬────┘
                  │
                  ↓
         ┌────────────────┐
         │ FACE_DETECTED  │ (Sees a face)
         └────────┬───────┘
                  │
                  ↓
          ┌──────────────┐
          │  LOCKED_IN   │ (Focused on person)
          └──────┬───────┘
                  │
                  ↓
           ┌──────────┐
           │ GREETING │ (Says hello)
           └─────┬────┘
                  │
                  ↓
          ┌───────────┐
          │ LISTENING │ (Recording speech)
          └─────┬─────┘
                  │
                  ↓
         ┌────────────┐
         │ PROCESSING │ (LLM thinking)
         └─────┬──────┘
                  │
                  ↓
         ┌────────────┐
         │ RESPONDING │ (Speaking back)
         └─────┬──────┘
                  │
                  └──────┐
                         ↓
                  ┌──────────────┐
                  │  FACE_LOST   │
                  └──────┬───────┘
                         │
                         ↓ (Back to IDLE)
```

## 🏗️ System Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║                      SYSTEM COMPONENTS                           ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ┌────────────┐           ┌──────────────────┐                  ║
║  │   Camera   │──────────→│  Vision Worker   │                  ║
║  └────────────┘           │    (OpenCV)      │                  ║
║                           └────────┬─────────┘                  ║
║                                    │                             ║
║  ┌────────────┐                    ↓                             ║
║  │ Microphone │           ┌───────────────────┐                 ║
║  └──────┬─────┘           │  ORCHESTRATOR     │                 ║
║         │                 │  (Coordinator)    │                 ║
║         ↓                 └─────────┬─────────┘                 ║
║  ┌──────────────┐                  │                             ║
║  │  STT Worker  │←─────────────────┘                             ║
║  │  (Whisper)   │                                                ║
║  └──────┬───────┘                  ┌─────────────────┐          ║
║         │                          │ AgentStateManager│          ║
║         ↓                          │   (FSM Control)  │          ║
║  ┌──────────────┐                  └─────────────────┘          ║
║  │  LLM Worker  │                                                ║
║  │  (Qwen2.5)   │                  ┌──────────────────┐         ║
║  └──────┬───────┘                  │ Performance      │         ║
║         │                          │ Reporter         │         ║
║         ↓                          └──────────────────┘         ║
║  ┌──────────────┐                                                ║
║  │  TTS Worker  │                                                ║
║  │   (Piper)    │                                                ║
║  └──────┬───────┘                                                ║
║         │                                                         ║
║         ↓                                                         ║
║  ┌────────────┐                                                  ║
║  │  Speaker   │                                                  ║
║  └────────────┘                                                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 📊 Data Flow with Queues

```
     SENSORS              WORKERS                ACTUATORS
        │                    │                       │
        │                    │                       │
┌───────▼────────┐    ┌──────▼────────┐     ┌──────▼────────┐
│     Camera     │    │               │     │               │
│  (Face Input)  │───→│    Vision     │────→│  Orchestrator │
└────────────────┘    │    Worker     │     └───────┬───────┘
                      └───────────────┘             │
                                                    │
┌────────────────┐    ┌───────────────┐            │
│   Microphone   │    │               │     [Queue 1: Vision→Orch]
│ (Audio Input)  │───→│  STT Worker   │            │
└────────────────┘    │  (Whisper)    │            │
                      └───────┬───────┘            │
                              │                     │
                      [Queue 2: STT→LLM]           │
                              │                     │
                              ↓                     │
                      ┌───────────────┐            │
                      │  LLM Worker   │←───────────┘
                      │  (Qwen2.5)    │
                      └───────┬───────┘
                              │
                      [Queue 3: LLM→TTS]
                              │
                              ↓
                      ┌───────────────┐
                      │  TTS Worker   │
                      │   (Piper)     │
                      └───────┬───────┘
                              │
                              ↓
                      ┌───────────────┐
                      │    Speaker    │
                      │ (Audio Output)│
                      └───────────────┘
```

## ⚡ Performance Target

```
┌─────────────────────────────────────────────────────┐
│  TOTAL RESPONSE TIME TARGET: < 2000ms (2 seconds)  │
└─────────────────────────────────────────────────────┘

    STT        LLM         TTS
  <200ms    <1500ms     <150ms
  ▓▓▓▓      ▓▓▓▓▓▓▓▓▓▓▓  ▓▓
  ├─────────┼───────────┼──────┤
  0        200        1700   1850ms
```

## 🖥️ Deployment

```
╔════════════════════════════════════╗
║      RASPBERRY PI 4 SETUP          ║
╠════════════════════════════════════╣
║  • Hardware: Raspberry Pi 4        ║
║  • RAM: 4GB                        ║
║  • OS: Linux                       ║
║  • LLM Server: Ollama (local)      ║
║  • Models: All running locally     ║
║  • Interface: Terminal/SSH         ║
║  • Reports: ASCII graphs in logs/  ║
╚════════════════════════════════════╝
```

---

**Summary**: Pluto is a reflex agent that responds to faces and voices using 3 AI models (Whisper → Qwen2.5 → Piper) with 8 states, 4 workers, and 3 message queues.
