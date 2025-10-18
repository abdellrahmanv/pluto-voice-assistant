# 📊 Performance Reporting System

## Overview

Pluto now generates **visual performance diagrams** in Markdown format for every run. These reports replace the old text-based logging approach with interactive charts and comprehensive system metrics.

## What Gets Tracked

### 🎯 Response Time Metrics
- **STT (Speech-to-Text)** - Whisper transcription latency
- **LLM (Language Model)** - Qwen2.5 inference latency  
- **TTS (Text-to-Speech)** - Piper synthesis latency
- **End-to-End** - Total conversation response time

### 💻 System Resources
- **CPU Usage** - Percentage utilization over time
- **Memory Usage** - RAM consumption in MB
- **CPU Temperature** - Thermal monitoring (Raspberry Pi)

### 📅 Conversation Events
- Face detection and tracking
- Greeting triggers
- Conversation starts/ends
- Agent state transitions

## Report Format

Every run generates a file: `logs/performance_report_YYYYMMDD_HHMMSS.md`

### Report Sections

1. **Executive Summary** - Quick overview table with key metrics
2. **Latency Performance** - Visual charts showing response times
3. **System Resources** - CPU, Memory, Temperature graphs
4. **Conversation Timeline** - Gantt chart of conversation flow
5. **Detailed Statistics** - Tables with min/max/mean/median/P95
6. **Errors & Warnings** - Issues encountered during session

## Visual Diagrams

Reports use **Mermaid** syntax for diagrams. GitHub and many Markdown viewers render these automatically.

### Example: Latency Chart
```mermaid
xychart-beta
    title "STT Response Time"
    x-axis [1, 2, 3, 4, 5]
    y-axis "Latency (ms)" 0 --> 500
    line [245, 189, 234, 210, 198]
```

### Example: CPU Usage
```mermaid
xychart-beta
    title "CPU Usage"
    x-axis [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y-axis "CPU %" 0 --> 100
    line [45.2, 52.1, 48.9, 55.3, 60.1, 58.4, 51.2, 49.8, 47.5, 50.0]
```

## How It Works

### Background Monitoring
The `PerformanceReporter` runs a background thread that:
- Samples system metrics every 2 seconds
- Captures CPU, memory, temperature
- Timestamps all events

### Automatic Generation
On shutdown (`Ctrl+C`):
1. Stop background monitoring
2. Generate comprehensive Markdown report
3. Save to `logs/` directory
4. Print report location

## Viewing Reports

### On Raspberry Pi
```bash
# View report in terminal
cat logs/performance_report_20251018_143022.md

# Or copy to your PC and open in:
# - GitHub (upload to repo)
# - VS Code (with Markdown preview)
# - Any Markdown viewer with Mermaid support
```

### On Windows/Mac
- Use VS Code with Markdown Preview
- Upload to GitHub for automatic rendering
- Use online Mermaid editor: https://mermaid.live/

## Temperature Warnings

Reports include automatic thermal analysis:

- 🟢 **< 70°C** - Normal operation
- 🟡 **70-80°C** - Monitor thermal performance
- 🔴 **> 80°C** - Consider cooling improvements

## Statistics Explained

### Latency Metrics
- **Min** - Fastest response time
- **Max** - Slowest response time  
- **Mean** - Average (sum / count)
- **Median** - Middle value (50th percentile)
- **P95** - 95th percentile (worst 5% excluded)

### Why P95?
P95 is industry standard for latency SLAs. It shows typical "worst case" while ignoring outliers from garbage collection, thermal throttling, etc.

## Integration with Existing Metrics

The performance reporter works **alongside** the existing `metrics_logger.py`:

- **metrics_logger.py** - Saves CSV/JSON raw data for analysis
- **performance_reporter.py** - Generates visual reports for humans

Both run simultaneously and complement each other.

## Example Report Output

```markdown
# 🪐 Pluto Performance Report

**Session ID:** `20251018_143022`
**Duration:** 5m 42s

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Conversations** | 12 |
| **Errors** | 0 |
| **Avg End-to-End Latency** | 2,340ms |
| **Avg STT Latency** | 245ms |
| **Avg LLM Latency** | 1,890ms |
| **Avg TTS Latency** | 205ms |
| **Avg CPU Usage** | 52.3% |
| **Avg Memory Usage** | 1,245MB |
| **Peak Temperature** | 64.5°C |

## ⏱️ Latency Performance
[Charts showing response times over time]

## 💻 System Resources  
[Charts showing CPU, Memory, Temperature]

## 📅 Conversation Timeline
[Gantt chart of conversations]

## 📈 Detailed Statistics
[Tables with min/max/mean/median/P95]

## ✅ No Issues Detected
Session completed without errors or warnings.
```

## Customization

### Change Monitoring Interval
In `orchestrator.py`:
```python
self.reporter.start_monitoring(interval=5.0)  # Sample every 5 seconds
```

### Disable Temperature Monitoring
Temperature tracking is optional and automatically disabled on non-Raspberry Pi systems.

### Custom Output Path
```python
report_path = self.reporter.generate_report(
    output_path=Path("/custom/path/my_report.md")
)
```

## Troubleshooting

### "Charts not rendering"
- Ensure your Markdown viewer supports Mermaid
- GitHub renders Mermaid automatically
- VS Code requires Markdown Preview Mermaid extension

### "Temperature always 0"
- Temperature monitoring only works on Raspberry Pi
- Requires `/sys/class/thermal/thermal_zone0/temp` access

### "Report not generated"
- Check `logs/` directory permissions
- Ensure disk space available
- Check console for error messages

## Benefits Over Old Logging

✅ **Visual** - Charts instead of text walls  
✅ **Comprehensive** - System metrics + latency + events  
✅ **Portable** - View on any Markdown viewer  
✅ **Automatic** - No manual analysis needed  
✅ **Shareable** - Easy to upload to GitHub/docs  

## Next Steps

1. Run Pluto normally
2. Stop with `Ctrl+C`  
3. Check `logs/` for your report
4. Open in VS Code or GitHub
5. Analyze performance visually

Enjoy your new performance insights! 🚀
