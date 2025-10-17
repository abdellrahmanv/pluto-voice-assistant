#!/usr/bin/env python3
"""
Pluto Log Visualizer - Run Wrapper
Captures all logs and generates a beautiful visualization report
"""

import subprocess
import sys
import time
import signal
from datetime import datetime
from pathlib import Path

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Generate log filenames with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
RAW_LOG = LOGS_DIR / f"pluto_run_{timestamp}.log"
REPORT_FILE = LOGS_DIR / f"pluto_report_{timestamp}.html"

print("=" * 70)
print("🪐 PLUTO - LOG VISUALIZER WRAPPER")
print("=" * 70)
print(f"\n📝 Logs will be saved to:")
print(f"   Raw log: {RAW_LOG}")
print(f"   Report:  {REPORT_FILE}")
print(f"\n▶️  Starting Pluto...")
print(f"⏹️  Press Ctrl+C to stop and generate report\n")
print("=" * 70 + "\n")

# Open log file
log_file = open(RAW_LOG, 'w', buffering=1)

# Start Pluto with output captured
process = subprocess.Popen(
    [sys.executable, "run.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True,
    bufsize=1
)

start_time = time.time()

def generate_log_lines(lines, css_class):
    """Generate HTML for log lines"""
    if not lines:
        return ''
    
    html = ''
    for line in lines:
        # Escape HTML
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        html += f'<div class="log-line {css_class}">{line}</div>\n'
    
    return html

def generate_report():
    """Generate HTML visualization report"""
    
    # Read log file
    with open(RAW_LOG, 'r') as f:
        log_lines = f.readlines()
    
    # Analyze log
    errors = []
    warnings = []
    success = []
    vision_events = []
    state_transitions = []
    performance = []
    
    for line in log_lines:
        line_lower = line.lower()
        
        if '❌' in line or 'error' in line_lower or 'failed' in line_lower:
            errors.append(line.strip())
        elif '⚠️' in line or 'warning' in line_lower:
            warnings.append(line.strip())
        elif '✅' in line or 'success' in line_lower or 'started' in line_lower:
            success.append(line.strip())
        elif 'face' in line_lower or 'locked' in line_lower or 'vision' in line_lower:
            vision_events.append(line.strip())
        elif 'state:' in line_lower or 'transition' in line_lower:
            state_transitions.append(line.strip())
        elif 'fps' in line_lower or 'latency' in line_lower or 'ms' in line_lower:
            performance.append(line.strip())
    
    # Calculate runtime
    runtime = time.time() - start_time
    runtime_str = f"{int(runtime // 60)}m {int(runtime % 60)}s"
    
    # Generate HTML report
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Pluto Run Report - {timestamp}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #764ba2;
            margin-top: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-card.success {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .stat-card.error {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        .stat-card.warning {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
        }}
        .stat-card.vision {{
            background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
            color: white;
        }}
        .stat-number {{
            font-size: 48px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .log-section {{
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .log-line {{
            font-family: 'Courier New', monospace;
            font-size: 13px;
            padding: 5px;
            border-bottom: 1px solid #e0e0e0;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .log-line:last-child {{
            border-bottom: none;
        }}
        .error-line {{
            background: #ffe6e6;
            color: #d32f2f;
        }}
        .warning-line {{
            background: #fff3e0;
            color: #f57c00;
        }}
        .success-line {{
            background: #e8f5e9;
            color: #388e3c;
        }}
        .vision-line {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        .empty {{
            color: #999;
            font-style: italic;
        }}
        .timestamp {{
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🪐 Pluto Voice Assistant - Run Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>Runtime: <strong>{runtime_str}</strong></p>
        
        <div class="stats">
            <div class="stat-card success">
                <div class="stat-label">✅ Success Events</div>
                <div class="stat-number">{len(success)}</div>
            </div>
            <div class="stat-card error">
                <div class="stat-label">❌ Errors</div>
                <div class="stat-number">{len(errors)}</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-label">⚠️ Warnings</div>
                <div class="stat-number">{len(warnings)}</div>
            </div>
            <div class="stat-card vision">
                <div class="stat-label">👁️ Vision Events</div>
                <div class="stat-number">{len(vision_events)}</div>
            </div>
        </div>
        
        <h2>❌ Errors ({len(errors)})</h2>
        <div class="log-section">
            {generate_log_lines(errors, 'error-line') if errors else '<p class="empty">No errors detected! 🎉</p>'}
        </div>
        
        <h2>⚠️ Warnings ({len(warnings)})</h2>
        <div class="log-section">
            {generate_log_lines(warnings, 'warning-line') if warnings else '<p class="empty">No warnings</p>'}
        </div>
        
        <h2>👁️ Vision System Events ({len(vision_events)})</h2>
        <div class="log-section">
            {generate_log_lines(vision_events[:20], 'vision-line') if vision_events else '<p class="empty">No vision events captured</p>'}
            {f'<p class="empty">... and {len(vision_events)-20} more</p>' if len(vision_events) > 20 else ''}
        </div>
        
        <h2>🔄 State Transitions ({len(state_transitions)})</h2>
        <div class="log-section">
            {generate_log_lines(state_transitions[:15], 'vision-line') if state_transitions else '<p class="empty">No state transitions captured</p>'}
            {f'<p class="empty">... and {len(state_transitions)-15} more</p>' if len(state_transitions) > 15 else ''}
        </div>
        
        <h2>⚡ Performance Metrics ({len(performance)})</h2>
        <div class="log-section">
            {generate_log_lines(performance[:15], 'success-line') if performance else '<p class="empty">No performance data captured</p>'}
            {f'<p class="empty">... and {len(performance)-15} more</p>' if len(performance) > 15 else ''}
        </div>
        
        <h2>✅ Success Events ({len(success)})</h2>
        <div class="log-section">
            {generate_log_lines(success[:10], 'success-line') if success else '<p class="empty">No success events</p>'}
            {f'<p class="empty">... and {len(success)-10} more</p>' if len(success) > 10 else ''}
        </div>
        
        <hr style="margin: 30px 0;">
        <p style="text-align: center; color: #999;">
            📝 Full raw log: <code>{RAW_LOG.name}</code><br>
            Generated by Pluto Log Visualizer
        </p>
    </div>
</body>
</html>
"""
    
    # Write report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

def cleanup(signum=None, frame=None):
    """Generate report and cleanup"""
    print("\n\n" + "=" * 70)
    print("⏹️  STOPPING AND GENERATING REPORT...")
    print("=" * 70)
    
    # Stop process
    process.terminate()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
    
    log_file.close()
    
    # Generate report
    generate_report()
    
    print("\n✅ Report generated!")
    print(f"📊 Open: {REPORT_FILE}")
    print(f"📝 Raw log: {RAW_LOG}\n")
    
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, cleanup)

# Stream output in real-time
try:
    for line in process.stdout:
        # Print to console
        print(line, end='')
        # Save to log file
        log_file.write(line)
        
    process.wait()
    cleanup()
    
except KeyboardInterrupt:
    cleanup()
