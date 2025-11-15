# 🪐 Pluto Simple - Scenario-Based Voice Agent

A lightweight voice assistant with **no LLM** - just STT → Scenarios → TTS

## Features
- ✅ **Simple pattern matching** - no complex AI
- ✅ **Voice commands** - speak naturally
- ✅ **Predefined scenarios** - fast responses
- ✅ **Lightweight** - runs on any PC/Raspberry Pi
- ✅ **Raspberry Pi ready** - automatic setup script included

## Quick Start

### For Raspberry Pi (Automated Setup)
```bash
chmod +x setup_pi.sh
sudo ./setup_pi.sh
python3 simple_agent.py
```

**Want natural human voice OFFLINE? (Uses Piper from main Pluto)**
```bash
cd pluto-simple
python3 simple_agent_piper.py  # Natural voice, no internet needed! ⭐
```

**Or use Google TTS (needs internet but very natural)**
```bash
chmod +x install_better_voice.sh
./install_better_voice.sh
python3 simple_agent_gtts.py
```

See [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md) for details.

### For PC/Manual Install

#### 1. Install Dependencies
```bash
pip install SpeechRecognition pyttsx3 pyaudio
```

#### 2. Run
```bash
python simple_agent.py
```

#### 3. Talk to Pluto!
Say: **"Hey Pluto"** to wake up, then try:
- "Introduce yourself"
- "What's your name?"
- "What time is it?"
- "Tell me a joke"
- "Help"
- "Goodbye"

## Available Scenarios

| Voice Command | Response |
|--------------|----------|
| Hey Pluto | Wakes up and greets you |
| Introduce yourself | Tells you about itself |
| What's your name? | Says "Pluto" |
| What time is it? | Current time |
| What's the date? | Current date |
| How are you? | Friendly response |
| Tell me a joke | Tells a joke |
| What's the weather? | Mock weather response |
| Help | Lists available commands |
| Thank you | You're welcome |
| Goodbye / Exit | Shuts down |

## How It Works

```
┌─────────────┐
│ Microphone  │ ──→ Speech Recognition (Google)
└─────────────┘
       │
       ↓
┌─────────────┐
│ STT (Text)  │ ──→ "Hey Pluto"
└─────────────┘
       │
       ↓
┌─────────────┐
│  Scenarios  │ ──→ Pattern Matching (if/elif)
└─────────────┘
       │
       ↓
┌─────────────┐
│ TTS Engine  │ ──→ pyttsx3 (Local)
└─────────────┘
       │
       ↓
┌─────────────┐
│   Speaker   │
└─────────────┘
```

## Add Your Own Scenarios

Edit `simple_agent.py` and add to `handle_scenario()`:

```python
elif "your command" in user_input:
    self.speak("Your response here!")
```

## No Internet Required
- TTS: Uses local pyttsx3 (offline)
- STT: Uses Google Speech Recognition (requires internet)

## vs Full Pluto
| Feature | Pluto Simple | Full Pluto |
|---------|-------------|-----------|
| LLM | ❌ No | ✅ Qwen2.5 |
| Vision | ❌ No | ✅ Face detection |
| Responses | Predefined | Generated |
| Resource Usage | Very Low | Medium |
| Setup | 2 minutes | 15 minutes |

---

**Perfect for:** Learning, testing, embedded devices, or when you don't need AI complexity!
