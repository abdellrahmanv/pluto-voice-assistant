# 🪐 Pluto Simple - Raspberry Pi Installation Guide

## Quick Setup (One Command)

```bash
chmod +x setup_pi.sh
sudo ./setup_pi.sh
```

That's it! The script installs everything automatically.

---

## What Gets Installed

### System Packages:
- `python3` - Python 3
- `python3-pip` - Package manager
- `portaudio19-dev` - Audio libraries
- `espeak` - Text-to-speech engine
- `flac` - Audio codec

### Python Packages:
- `SpeechRecognition` - Speech-to-text
- `pyttsx3` - Text-to-speech
- `pyaudio` - Audio input/output

---

## Hardware Requirements

### Minimum:
- **Raspberry Pi 3B+** or newer
- **1GB RAM** (2GB+ recommended)
- **Microphone** (USB or built-in)
- **Speaker** (3.5mm jack, HDMI, or USB)
- **Internet connection** (for speech recognition)

### Recommended:
- **Raspberry Pi 4** (2GB+ RAM)
- **USB Microphone** (better quality)
- **Powered speakers** or headphones

---

## Manual Installation (if needed)

### Step 1: Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Install Dependencies
```bash
sudo apt-get install -y python3 python3-pip python3-dev
sudo apt-get install -y portaudio19-dev espeak flac
```

### Step 3: Install Python Packages
```bash
pip3 install SpeechRecognition pyttsx3 pyaudio
```

### Step 4: Test Audio
```bash
# Test microphone
arecord -l

# Test speaker
espeak "Hello from Pluto"

# Record and play test
arecord -d 3 test.wav
aplay test.wav
```

---

## Running Pluto Simple

```bash
python3 simple_agent.py
```

### Expected Output:
```
🪐 Pluto Simple Agent Initialized
╔═════════════════════════════════════════════╗
║   🪐 PLUTO SIMPLE AGENT                     ║
║   Scenario-Based Assistant                  ║
╚═════════════════════════════════════════════╝

🎙️ Listening...
```

---

## Troubleshooting

### ❌ No microphone detected
```bash
# List audio devices
arecord -l

# If USB mic not detected, reconnect and check again
lsusb
```

### ❌ Speech recognition not working
- Make sure you have internet connection (uses Google Speech API)
- Test microphone: `arecord -d 5 test.wav && aplay test.wav`
- Speak clearly and close to microphone

### ❌ TTS (pyttsx3) not speaking
```bash
# Test espeak directly
espeak "test"

# If no sound, check volume
alsamixer

# Or try
sudo apt-get install --reinstall espeak
```

### ❌ "ALSA lib" errors (can be ignored)
These are warnings from audio library, usually safe to ignore.

### ❌ Permission denied on audio device
```bash
sudo usermod -a -G audio $USER
# Logout and login again
```

---

## Auto-Start on Boot (Optional)

### Method 1: systemd service
Create `/etc/systemd/system/pluto.service`:
```ini
[Unit]
Description=Pluto Simple Voice Agent
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pluto-simple
ExecStart=/usr/bin/python3 /home/pi/pluto-simple/simple_agent.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable pluto.service
sudo systemctl start pluto.service
```

### Method 2: crontab
```bash
crontab -e
# Add this line:
@reboot sleep 30 && cd /home/pi/pluto-simple && python3 simple_agent.py
```

---

## Performance Tips

### For Raspberry Pi 3:
- Close unnecessary programs
- Use wired internet (faster than WiFi for speech recognition)
- Consider USB microphone (better quality than built-in)

### For Raspberry Pi 4:
- Should run smoothly with default settings
- Can handle multiple voice commands quickly

---

## Testing Checklist

- [ ] Internet connection working
- [ ] Microphone detected: `arecord -l`
- [ ] Speaker working: `espeak "test"`
- [ ] Python installed: `python3 --version`
- [ ] Packages installed: `pip3 list | grep Speech`
- [ ] Script runs: `python3 simple_agent.py`
- [ ] Voice recognized: Say "Hey Pluto"

---

## Next Steps

1. ✅ Run setup script
2. ✅ Test microphone and speaker
3. ✅ Run `python3 simple_agent.py`
4. ✅ Say "Hey Pluto"
5. 🎉 Start talking!

**Need help?** Check SCENARIOS.md for available commands.
