# 📝 Pluto Simple Logs

## Log File
- **File**: `pluto_run.log`
- **Location**: Same directory as `simple_agent_working.py`

## What Gets Logged
✅ All console output (print statements)  
✅ All errors and exceptions  
✅ Timestamps for each run  
✅ Full error tracebacks  
✅ Microphone detection info  
✅ Speech recognition results  
✅ TTS command results  

## How to Use

### Run with logging:
```bash
python3 simple_agent_working.py
```

The log file `pluto_run.log` will be created automatically!

### View the log:
```bash
cat pluto_run.log
```

### View last 50 lines:
```bash
tail -50 pluto_run.log
```

### Clear the log:
```bash
rm pluto_run.log
```

## Sharing Errors

When you get an error:
1. Run the program: `python3 simple_agent_working.py`
2. Let the error happen
3. Open `pluto_run.log`
4. Copy the last section (from `NEW RUN` to the end)
5. Share it with me!

## Example Log Entry
```
============================================================
🪐 NEW RUN: 2025-11-15 14:30:22
============================================================
📝 Logging to: pluto_run.log
   You can share this file to debug errors!

🪐 Pluto Simple - Starting up...
✅ Found Piper at: ../models/en_US-lessac-medium.onnx
🎤 Initializing USB card 3 for microphone...
✅ Microphone locked to USB card 3
✅ Pluto is ready!
```

## Log File Size
The log file keeps growing with each run. Clear it occasionally:
```bash
# Keep only last 100 lines
tail -100 pluto_run.log > temp.log && mv temp.log pluto_run.log
```
