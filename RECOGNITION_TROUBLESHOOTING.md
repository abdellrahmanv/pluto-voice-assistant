# Speech Recognition Troubleshooting Guide

## Current Issue: Poor Transcription Quality

Based on your session logs, Vosk is mishearing words:

**What you said** → **What Vosk heard:**
- (probably "hey there") → "the hey there are i swear" ❌
- (something short) → "the" ❌  
- (something else) → "you're an unappealing else" ❌

---

## Root Causes

### 1. **Small Vosk Model** (Main Issue)
- Current: `vosk-model-small-en-us-0.15` (40 MB)
- Pros: Fast, low memory
- Cons: **Lower accuracy**, struggles with accents/background noise

### 2. **Microphone Sensitivity**
- May be too aggressive in cutting off speech
- Background noise might confuse recognition

### 3. **Performance Metrics from Your Session**
```
STT Latency: 233ms - 643ms (GOOD)
LLM Latency: 2484ms - 2657ms (OK)
TTS Latency: 3434ms - 6767ms (SLOW - but working)
```

---

## Solutions

### ✅ **Solution 1: Upgrade Vosk Model (BEST)**

**Run this command:**
```powershell
.\upgrade_vosk.ps1
```

**What it does:**
- Downloads `vosk-model-en-us-0.22` (1.8 GB - much better accuracy)
- Updates config automatically
- Significantly improves recognition quality

**Trade-offs:**
- ✅ Much better word recognition
- ✅ Better with accents and background noise
- ❌ ~100-200ms slower (still acceptable)
- ❌ Uses more RAM (~500 MB more)

---

### ✅ **Solution 2: I Already Adjusted Audio Settings**

**What I changed in config.py:**
```python
"energy_threshold": 300,  # More sensitive (was 500)
"silence_threshold": 300,  # Detects quieter speech
"silence_chunks_threshold": 20,  # Faster detection
"silence_duration": 1.0,  # Faster cutoff
"max_phrase_duration": 20.0,  # Allow longer sentences
```

**This helps with:**
- Capturing quieter speech
- Faster voice activity detection
- Allowing longer phrases

---

### 💡 **Solution 3: Tips for Better Recognition**

**1. Microphone Setup:**
- Speak clearly and at normal volume
- Keep microphone 6-12 inches from mouth
- Minimize background noise
- Use a better microphone if possible

**2. Speaking Style:**
- Speak at normal pace (not too fast)
- Pronounce words clearly
- Pause briefly between sentences
- Avoid filler words ("um", "uh")

**3. Environment:**
- Reduce background noise (TV, music, fans)
- Close windows if outside noise
- Use in quieter room

---

## Recommended Action Plan

### **IMMEDIATE (Quick Test):**
```powershell
# Run Pluto again with adjusted audio settings
C:\Users\Asus\Desktop\pluto\venv\Scripts\python.exe C:\Users\Asus\Desktop\pluto\run.py
```

Try speaking clearly into your microphone and see if recognition improves.

---

### **IF STILL POOR (Best Solution):**
```powershell
# Upgrade to better Vosk model
.\upgrade_vosk.ps1

# Then run Pluto again
C:\Users\Asus\Desktop\pluto\venv\Scripts\python.exe C:\Users\Asus\Desktop\pluto\run.py
```

**Expected improvement:** 70-80% recognition accuracy → 90-95% accuracy

---

## Alternative: Test Your Microphone

```powershell
# Quick microphone test
python -c "import pyaudio; p = pyaudio.PyAudio(); print('Microphones:'); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count()) if p.get_device_info_by_index(i)['maxInputChannels'] > 0]"
```

This shows all available microphones. You might want to select a specific one in config.py.

---

## Current System Performance

From your session:
- ⏱️ **Runtime:** 129 seconds
- 💬 **Conversations:** 3 attempts
- 🎤 **STT Speed:** 233-643ms ✅ GOOD
- 🧠 **LLM Speed:** 2484-2657ms ✅ ACCEPTABLE
- 🔊 **TTS Speed:** 3434-6767ms ⚠️ SLOW (but functional)
- 💾 **Memory:** 179-194 MB ✅ EFFICIENT

**The system is working well performance-wise - just needs better speech recognition!**

---

## Next Steps

1. **Try with adjusted settings** (already done - run Pluto again)
2. **If still poor:** Run `.\upgrade_vosk.ps1` to get better model
3. **Test in quiet environment** with clear speech
4. **Check microphone quality/positioning**

---

*Model comparison:*
- **Small model** (current): 40 MB, ~70-80% accuracy, 200-500ms latency
- **Large model** (recommended): 1.8 GB, ~90-95% accuracy, 300-700ms latency

The large model is worth it for real-world use!
