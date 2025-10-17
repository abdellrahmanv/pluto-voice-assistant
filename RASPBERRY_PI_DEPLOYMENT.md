# Project Pluto - Raspberry Pi Deployment Guide

## What Changes for Raspberry Pi

### 1. **Operating System Differences**
- **Windows** → **Linux (Raspberry Pi OS)**
- PowerShell scripts (`.ps1`) → Bash scripts (`.sh`)
- Windows paths → Linux paths

### 2. **Architecture Differences**
- **x86_64** (Intel/AMD) → **ARM64** (Raspberry Pi 4/5)
- Need ARM-compatible binaries for Piper

### 3. **What Stays The Same**
- ✅ All Python source code (100% compatible)
- ✅ Whisper model (platform-independent)
- ✅ Qwen2.5 model (works with Ollama on ARM)
- ✅ Piper voice models (.onnx files - same)
- ✅ Python packages (same versions)

---

## Quick Deployment Steps

### **On Your Windows PC (Preparation):**

1. **Copy these folders to Raspberry Pi:**
   ```
   pluto/
   ├── src/              ← All Python code
   ├── requirements.txt  ← Python packages
   ├── run.py           ← Entry point
   └── models/          ← Copy your Whisper & Piper models
       └── en_US-lessac-medium.onnx
   ```

2. **Use SCP or USB drive to transfer:**
   ```powershell
   # Option A: SCP (if Pi has SSH enabled)
   scp -r C:\Users\Asus\Desktop\pluto pi@raspberrypi.local:~/

   # Option B: Copy to USB drive, then plug into Pi
   ```

---

### **On Raspberry Pi:**

1. **Install system dependencies:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-venv portaudio19-dev
   ```

2. **Install Ollama (ARM64):**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull qwen2.5:0.5b-instruct-q4_K_M
   ```

3. **Install Piper (ARM64):**
   ```bash
   cd ~/pluto
   ./install_piper_pi.sh
   ```

4. **Setup Python environment:**
   ```bash
   cd ~/pluto
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Run Pluto:**
   ```bash
   # Terminal 1: Start Ollama
   ollama serve

   # Terminal 2: Run Pluto
   source venv/bin/activate
   python run.py
   ```

---

## Performance Expectations

### **Raspberry Pi 4 (4GB+ RAM):**
- Whisper Tiny: ~2-3 seconds (acceptable)
- Qwen2.5: ~3-5 seconds (workable)
- Piper TTS: ~1-2 seconds (good)
- **Total latency: ~6-10 seconds** (usable for testing)

### **Raspberry Pi 5 (8GB RAM):**
- Whisper Tiny: ~1-2 seconds (good)
- Qwen2.5: ~2-3 seconds (good)
- Piper TTS: ~1 second (excellent)
- **Total latency: ~4-6 seconds** (production-ready)

---

## Files I'll Create for You

1. `install_piper_pi.sh` - Automated Piper installation for ARM64
2. `setup_pi.sh` - Complete Raspberry Pi setup automation
3. `config_pi.py` - Linux path configurations
4. `systemd service file` - Auto-start Pluto on boot
5. `RASPBERRY_PI_GUIDE.md` - Complete deployment instructions

---

## What Won't Work on Pi

- ❌ PowerShell scripts (`.ps1`) - replaced with Bash
- ❌ Windows-specific paths - already using Path() objects (compatible!)
- ❌ That's it! Everything else works!

---

## Optimization Tips for Pi

1. **Use Whisper Tiny** (already configured) - larger models too slow
2. **Keep Qwen2.5 1.5B** - perfect size for Pi
3. **Disable unnecessary logging** for speed
4. **Use USB microphone** for better audio quality
5. **Overclock Pi 4** to 2.0 GHz for better performance

---

Ready to create all the Raspberry Pi deployment files?
