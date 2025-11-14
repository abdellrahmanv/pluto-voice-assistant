# 🚀 Pluto Optimization Guide for Raspberry Pi 4B

**Target**: Reduce response time from **2340ms to ~1400ms** (40% faster)

---

## 📊 Current Performance Baseline

From `logs/example_performance_report.md`:

| Component | Current | Target | Status |
|-----------|---------|--------|--------|
| **STT** | 245ms | <200ms | 🟡 Acceptable |
| **LLM** | 1890ms | <1500ms | 🟡 Acceptable (Bottleneck) |
| **TTS** | 205ms | <150ms | 🟡 Acceptable |
| **Total** | **2340ms** | <2000ms | 🟡 Acceptable |

**System Resources**:
- CPU: 52.3% average (60% peak)
- Memory: 1245 MB
- Temperature: 64.5°C

---

## 🎯 Optimization Strategy

### Phase 1: Quick Wins (Hardware + Dependencies)
**Time**: ~15 minutes  
**Expected**: 2340ms → ~1600ms (-740ms)

1. ✅ Switch to faster-whisper (4x faster STT)
2. ✅ Use Qwen2.5 q2_K quantization (40% faster LLM)
3. ✅ Enable CPU performance governor
4. ✅ Reduce max tokens (150 → 60)
5. ✅ Speed up Piper TTS (20%)
6. ✅ Setup TTS caching

### Phase 2: Code Optimizations
**Time**: ~20 minutes  
**Expected**: 1600ms → ~1400ms (-200ms)

1. ✅ Update STT worker to use faster-whisper
2. ✅ Add TTS caching to worker
3. ✅ Optimize LLM worker (retry logic, trimming)
4. ✅ Reduce conversation history (5 → 2 turns)
5. ✅ Improve error handling

---

## 🚀 Quick Start

### Prerequisites

1. **Raspberry Pi 4B** with 4GB RAM
2. **Raspberry Pi OS** (64-bit recommended)
3. **Ollama** installed and running (`ollama serve`)
4. **Python 3.11+**
5. **Git** (to clone/update)

### Step-by-Step Instructions

#### 1. Backup Your System (Important!)

```bash
# Create full backup
cd ~/pluto
tar -czf pluto_backup_$(date +%Y%m%d).tar.gz .
```

#### 2. Run Phase 1 Optimization

```bash
cd ~/pluto
python3 optimize_phase1.py
```

**What it does**:
- Updates `requirements.txt` (openai-whisper → faster-whisper)
- Installs dependencies
- Pulls Ollama q2_K model
- Sets CPU to performance mode (requires sudo)
- Updates configuration files
- Creates TTS cache directory

**Expected output**:
```
🚀 Pluto Phase 1 Optimization - Quick Wins
Target: Raspberry Pi 4B
Goal: 2340ms → ~1600ms response time

✅ Updated requirements.txt
✅ Installed faster-whisper successfully
✅ Model qwen2.5:0.5b-instruct-q2_k ready
✅ CPU governor set to 'performance'
✅ Configuration updated

🎉 Phase 1 Complete!
Expected: 2340ms → ~1510ms (-830ms / 35% faster)
```

#### 3. Generate TTS Cache

```bash
python3 generate_tts_cache.py
```

**What it does**:
- Pre-generates common phrases (greeting, error, goodbye)
- Saves WAV files to `cache/tts/`
- Eliminates synthesis latency for cached phrases

#### 4. Run Phase 2 Optimization

```bash
python3 optimize_phase2.py
```

**What it does**:
- Updates STT worker to use faster-whisper API
- Adds caching logic to TTS worker
- Optimizes LLM worker (retries, trimming)
- Updates configuration thresholds
- Creates performance test script

**Expected output**:
```
🚀 Pluto Phase 2 Optimization - Code Improvements
Target: Raspberry Pi 4B
Goal: 1600ms → ~1400ms

✅ STT worker updated to faster-whisper
✅ TTS worker updated with caching
✅ LLM worker optimized
✅ Configuration updated
✅ Test script created

🎉 Phase 2 Complete!
Total: 2340ms → 1380ms (-960ms / 41% faster!)
```

#### 5. Test the Optimizations

```bash
python3 test_performance.py
```

**What it tests**:
- Import checks (faster-whisper, Ollama)
- STT performance (should be <200ms)
- LLM performance (should be <1500ms)
- Configuration validation

**Expected output**:
```
🚀 Pluto Performance Test

✅ PASS  Imports
✅ PASS  faster-whisper (60ms)
✅ PASS  Ollama (1200ms)

🎉 All tests passed! System is optimized and ready.
```

#### 6. Start Pluto

```bash
# Make sure Ollama is running
ollama serve &

# Start Pluto
python3 src/orchestrator.py
```

---

## 📊 Expected Results

### Before Optimization

```
🎤 STT:   245ms  ████████████
🧠 LLM:   1890ms █████████████████████████████████████████████
🔊 TTS:   205ms  ██████████
─────────────────────────────────────────────────────
⏱️  TOTAL: 2340ms
```

### After Optimization (Phase 1 + 2)

```
🎤 STT:   60ms   ███
🧠 LLM:   1200ms ██████████████████████████████
🔊 TTS:   120ms  ██████
─────────────────────────────────────────────────────
⏱️  TOTAL: 1380ms  (-960ms / 41% faster!)
```

---

## 🛠️ Troubleshooting

### Issue: faster-whisper import error

```bash
pip3 install faster-whisper --upgrade
pip3 install onnxruntime --upgrade
```

### Issue: Ollama model not found

```bash
# Check available models
ollama list

# Pull the optimized model
ollama pull qwen2.5:0.5b-instruct-q2_k

# Test it
ollama run qwen2.5:0.5b-instruct-q2_k
```

### Issue: CPU governor not set

```bash
# Check current governor
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# Set manually (requires sudo)
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Make permanent (add to /etc/rc.local)
sudo nano /etc/rc.local
# Add before 'exit 0':
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### Issue: System slower than expected

**Check CPU throttling**:
```bash
# Monitor CPU frequency
watch -n 1 cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
# Should show 1500000 (1.5GHz)
```

**Check temperature**:
```bash
vcgencmd measure_temp
# Should be <75°C. If higher, add cooling.
```

**Check Ollama**:
```bash
# Ensure Ollama is running
systemctl status ollama
# Or start manually
ollama serve
```

### Issue: TTS cache not working

```bash
# Regenerate cache
python3 generate_tts_cache.py

# Check cache files
ls -lh cache/tts/
# Should show: greeting.wav, error.wav, goodbye.wav
```

---

## 🔄 Rollback Instructions

### Restore from automatic backups:

```bash
# List available backups
ls -lh backups/

# Restore Phase 1
cp -r backups/backup_[timestamp]/* ./

# Restore Phase 2
cp -r backups/phase2_backup_[timestamp]/* ./

# Reinstall old dependencies
pip3 install openai-whisper
```

### Restore from manual backup:

```bash
# Extract backup
tar -xzf pluto_backup_[date].tar.gz -C pluto_restored/
cd pluto_restored/
```

---

## 📈 Monitoring Performance

### Real-time monitoring during operation:

```bash
# Terminal 1: System resources
htop

# Terminal 2: CPU temperature
watch -n 2 vcgencmd measure_temp

# Terminal 3: Pluto logs
tail -f logs/pluto.log
```

### After conversations:

```bash
# View latest performance report
cat logs/example_performance_report.md

# Or open with markdown viewer
markdown-viewer logs/example_performance_report.md
```

---

## 🎯 Advanced Optimizations (Optional)

### 1. Increase GPU Memory (Helps OpenCV)

```bash
sudo raspi-config
# Advanced Options → Memory Split → Set to 256MB
sudo reboot
```

### 2. Disable Unused Services

```bash
sudo systemctl disable bluetooth
sudo systemctl disable hciuart
sudo reboot
```

### 3. Use Vosk instead of Whisper (Even faster, lower accuracy)

```bash
# Install Vosk
pip3 install vosk

# Download Vosk model
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models/

# Update config.py to use Vosk (manual change)
```

### 4. Add Active Cooling

- **Passive**: Heatsink (keeps temp <65°C)
- **Active**: 5V fan (keeps temp <50°C)
- Mount fan on GPIO pins 4 (5V) and 6 (GND)

---

## 📋 Optimization Checklist

- [ ] Phase 1 completed
- [ ] TTS cache generated
- [ ] Phase 2 completed
- [ ] Performance test passed
- [ ] Ollama q2_K model installed
- [ ] CPU governor set to performance
- [ ] System tested and working
- [ ] Performance report reviewed

---

## 🆘 Support

### If optimizations fail:

1. **Check logs**: `logs/pluto.log`
2. **Run diagnostics**: `python3 test_performance.py`
3. **Restore backup**: `cp -r backups/backup_*/* ./`
4. **Verify dependencies**: `pip3 list | grep -E "whisper|ollama|piper"`

### Common Issues:

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: faster_whisper` | `pip3 install faster-whisper` |
| `Ollama not responding` | `ollama serve` in separate terminal |
| `Permission denied (CPU governor)` | Run with `sudo` or skip this step |
| `Model not found` | `ollama pull qwen2.5:0.5b-instruct-q2_k` |

---

## 📚 Additional Resources

- [faster-whisper docs](https://github.com/guillaumekln/faster-whisper)
- [Ollama models](https://ollama.ai/library/qwen2.5)
- [Piper TTS](https://github.com/rhasspy/piper)
- [RPi CPU governor](https://www.raspberrypi.org/documentation/configuration/config-txt/overclocking.md)

---

**Last Updated**: November 14, 2025  
**Version**: 1.0  
**Target Hardware**: Raspberry Pi 4B (4GB RAM)
