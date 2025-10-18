"""
🪐 Project Pluto - Performance Diagram Reporter
Generates visual Markdown reports with Mermaid diagrams for system performance
"""

import psutil
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict


class PerformanceReporter:
    """
    Generate comprehensive performance reports with diagrams
    Tracks: latency, CPU, memory, temperature over time
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start = time.time()
        
        # Time-series data storage
        self.snapshots: List[Dict[str, Any]] = []
        self.component_latencies = defaultdict(list)  # {component: [(timestamp, latency), ...]}
        self.conversation_events = []  # [(timestamp, event_type, details), ...]
        self.errors = []
        self.warnings = []
        
        # System monitoring
        self.cpu_samples = []  # [(timestamp, cpu_percent), ...]
        self.memory_samples = []  # [(timestamp, memory_mb), ...]
        self.temp_samples = []  # [(timestamp, temp_celsius), ...]
        
        # Monitoring thread
        self.monitoring_active = False
        
        print(f"📊 Performance Reporter initialized - Session: {self.session_id}")
    
    def start_monitoring(self, interval: float = 2.0):
        """Start background system monitoring"""
        import threading
        
        self.monitoring_active = True
        
        def monitor_loop():
            while self.monitoring_active:
                self.capture_system_snapshot()
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        print(f"🔍 System monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop background system monitoring"""
        self.monitoring_active = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        print("🛑 System monitoring stopped")
    
    def capture_system_snapshot(self):
        """Capture current system metrics"""
        timestamp = time.time()
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_samples.append((timestamp, cpu_percent))
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_mb = memory.used / 1024 / 1024
        self.memory_samples.append((timestamp, memory_mb))
        
        # Temperature (Raspberry Pi specific)
        try:
            temp = self._get_temperature()
            if temp is not None:
                self.temp_samples.append((timestamp, temp))
        except Exception:
            pass  # Temperature monitoring optional
    
    def _get_temperature(self) -> Optional[float]:
        """Get CPU temperature (Raspberry Pi)"""
        try:
            # Try Raspberry Pi thermal zone
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
                return temp
        except FileNotFoundError:
            return None
        except Exception:
            return None
    
    def log_latency(self, component: str, latency_ms: float):
        """Log component latency"""
        timestamp = time.time()
        self.component_latencies[component].append((timestamp, latency_ms))
    
    def log_conversation_event(self, event_type: str, details: str = ""):
        """Log conversation events (start, end, greeting, etc)"""
        timestamp = time.time()
        self.conversation_events.append((timestamp, event_type, details))
    
    def log_error(self, message: str):
        """Log error"""
        timestamp = time.time()
        self.errors.append((timestamp, message))
    
    def log_warning(self, message: str):
        """Log warning"""
        timestamp = time.time()
        self.warnings.append((timestamp, message))
    
    def generate_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Generate comprehensive Markdown report with Mermaid diagrams
        
        Returns:
            Path to generated report file
        """
        if output_path is None:
            logs_dir = Path(__file__).parent.parent / "logs"
            logs_dir.mkdir(exist_ok=True)
            output_path = logs_dir / f"performance_report_{self.session_id}.md"
        
        # Calculate session duration
        duration = time.time() - self.session_start
        duration_str = self._format_duration(duration)
        
        # Build report
        lines = []
        lines.append("# 🪐 Pluto Performance Report\n\n")
        lines.append(f"**Session ID:** `{self.session_id}`\n\n")
        lines.append(f"**Start Time:** {datetime.fromtimestamp(self.session_start).strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        lines.append(f"**Duration:** {duration_str}\n\n")
        lines.append("---\n\n")
        
        # Executive Summary
        lines.extend(self._generate_summary_section())
        
        # Latency Performance Diagrams
        lines.extend(self._generate_latency_diagrams())
        
        # System Resource Diagrams
        lines.extend(self._generate_system_diagrams())
        
        # Conversation Timeline
        lines.extend(self._generate_timeline_section())
        
        # Detailed Statistics Tables
        lines.extend(self._generate_statistics_tables())
        
        # Errors and Warnings
        lines.extend(self._generate_issues_section())
        
        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ Performance report generated: {output_path}")
        return output_path
    
    def _generate_summary_section(self) -> List[str]:
        """Generate executive summary section"""
        lines = []
        lines.append("## 📊 Executive Summary\n\n")
        
        # Count statistics
        total_conversations = sum(1 for _, evt, _ in self.conversation_events if evt == 'conversation_start')
        total_errors = len(self.errors)
        total_warnings = len(self.warnings)
        
        # Latency statistics
        avg_latencies = {}
        for component, samples in self.component_latencies.items():
            if samples:
                avg = sum(lat for _, lat in samples) / len(samples)
                avg_latencies[component] = avg
        
        # System statistics
        avg_cpu = sum(cpu for _, cpu in self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
        avg_mem = sum(mem for _, mem in self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0
        peak_temp = max((temp for _, temp in self.temp_samples), default=0) if self.temp_samples else 0
        
        lines.append(f"| Metric | Value |\n")
        lines.append(f"|--------|-------|\n")
        lines.append(f"| **Conversations** | {total_conversations} |\n")
        lines.append(f"| **Errors** | {total_errors} |\n")
        lines.append(f"| **Warnings** | {total_warnings} |\n")
        
        if 'total' in avg_latencies:
            lines.append(f"| **Avg End-to-End Latency** | {avg_latencies['total']:.0f}ms |\n")
        if 'stt' in avg_latencies:
            lines.append(f"| **Avg STT Latency** | {avg_latencies['stt']:.0f}ms |\n")
        if 'llm' in avg_latencies:
            lines.append(f"| **Avg LLM Latency** | {avg_latencies['llm']:.0f}ms |\n")
        if 'tts' in avg_latencies:
            lines.append(f"| **Avg TTS Latency** | {avg_latencies['tts']:.0f}ms |\n")
        
        lines.append(f"| **Avg CPU Usage** | {avg_cpu:.1f}% |\n")
        lines.append(f"| **Avg Memory Usage** | {avg_mem:.0f}MB |\n")
        if peak_temp > 0:
            lines.append(f"| **Peak Temperature** | {peak_temp:.1f}°C |\n")
        
        lines.append("\n---\n\n")
        return lines
    
    def _generate_latency_diagrams(self) -> List[str]:
        """Generate latency performance diagrams"""
        lines = []
        lines.append("## ⏱️ Latency Performance\n\n")
        
        # Component latency comparison (bar chart)
        if self.component_latencies:
            lines.append("### Component Latency Comparison\n\n")
            lines.append("```mermaid\n")
            lines.append("%%{init: {'theme':'base'}}%%\n")
            lines.append("graph LR\n")
            
            for component in ['stt', 'llm', 'tts', 'total']:
                if component in self.component_latencies:
                    samples = self.component_latencies[component]
                    avg = sum(lat for _, lat in samples) / len(samples)
                    lines.append(f"    {component.upper()}[\"{component.upper()}<br/>{avg:.0f}ms\"]\n")
            
            lines.append("```\n\n")
        
        # Latency over time (line chart data)
        lines.append("### Latency Over Time\n\n")
        
        for component in ['stt', 'llm', 'tts', 'total']:
            if component not in self.component_latencies:
                continue
            
            samples = self.component_latencies[component]
            if not samples:
                continue
            
            lines.append(f"#### {component.upper()} Latency Timeline\n\n")
            lines.append("```mermaid\n")
            lines.append("%%{init: {'theme':'base', 'themeVariables': {'xyChart': {'backgroundColor': 'transparent'}}}}%%\n")
            lines.append("xychart-beta\n")
            lines.append(f"    title \"{component.upper()} Response Time\"\n")
            lines.append("    x-axis [" + ", ".join(f"{i+1}" for i in range(min(20, len(samples)))) + "]\n")
            
            # Take last 20 samples
            recent_samples = samples[-20:]
            latencies = [f"{lat:.0f}" for _, lat in recent_samples]
            lines.append("    y-axis \"Latency (ms)\" 0 --> " + str(int(max(lat for _, lat in recent_samples) * 1.2)) + "\n")
            lines.append("    line [" + ", ".join(latencies) + "]\n")
            lines.append("```\n\n")
        
        lines.append("---\n\n")
        return lines
    
    def _generate_system_diagrams(self) -> List[str]:
        """Generate system resource usage diagrams"""
        lines = []
        lines.append("## 💻 System Resources\n\n")
        
        # CPU Usage Chart
        if self.cpu_samples:
            lines.append("### CPU Usage Over Time\n\n")
            lines.append("```mermaid\n")
            lines.append("%%{init: {'theme':'base'}}%%\n")
            lines.append("xychart-beta\n")
            lines.append("    title \"CPU Usage\"\n")
            
            # Take samples every N to fit in chart (max 30 points)
            step = max(1, len(self.cpu_samples) // 30)
            sampled_cpu = self.cpu_samples[::step]
            
            lines.append("    x-axis [" + ", ".join(f"{i+1}" for i in range(len(sampled_cpu))) + "]\n")
            lines.append("    y-axis \"CPU %\" 0 --> 100\n")
            lines.append("    line [" + ", ".join(f"{cpu:.1f}" for _, cpu in sampled_cpu) + "]\n")
            lines.append("```\n\n")
        
        # Memory Usage Chart
        if self.memory_samples:
            lines.append("### Memory Usage Over Time\n\n")
            lines.append("```mermaid\n")
            lines.append("%%{init: {'theme':'base'}}%%\n")
            lines.append("xychart-beta\n")
            lines.append("    title \"Memory Usage\"\n")
            
            step = max(1, len(self.memory_samples) // 30)
            sampled_mem = self.memory_samples[::step]
            
            max_mem = max(mem for _, mem in sampled_mem)
            lines.append("    x-axis [" + ", ".join(f"{i+1}" for i in range(len(sampled_mem))) + "]\n")
            lines.append(f"    y-axis \"Memory (MB)\" 0 --> {int(max_mem * 1.2)}\n")
            lines.append("    line [" + ", ".join(f"{mem:.0f}" for _, mem in sampled_mem) + "]\n")
            lines.append("```\n\n")
        
        # Temperature Chart (Raspberry Pi)
        if self.temp_samples:
            lines.append("### CPU Temperature Over Time\n\n")
            lines.append("```mermaid\n")
            lines.append("%%{init: {'theme':'base'}}%%\n")
            lines.append("xychart-beta\n")
            lines.append("    title \"CPU Temperature\"\n")
            
            step = max(1, len(self.temp_samples) // 30)
            sampled_temp = self.temp_samples[::step]
            
            lines.append("    x-axis [" + ", ".join(f"{i+1}" for i in range(len(sampled_temp))) + "]\n")
            lines.append("    y-axis \"Temperature (°C)\" 0 --> 100\n")
            lines.append("    line [" + ", ".join(f"{temp:.1f}" for _, temp in sampled_temp) + "]\n")
            lines.append("```\n\n")
            
            # Temperature warning
            max_temp = max(temp for _, temp in self.temp_samples)
            if max_temp > 80:
                lines.append("> ⚠️ **WARNING:** Peak temperature exceeded 80°C - consider cooling improvements\n\n")
            elif max_temp > 70:
                lines.append("> ⚠️ **NOTICE:** Peak temperature exceeded 70°C - monitor thermal performance\n\n")
        
        lines.append("---\n\n")
        return lines
    
    def _generate_timeline_section(self) -> List[str]:
        """Generate conversation timeline"""
        lines = []
        lines.append("## 📅 Conversation Timeline\n\n")
        
        if not self.conversation_events:
            lines.append("*No conversation events recorded*\n\n")
            lines.append("---\n\n")
            return lines
        
        # Gantt-style timeline
        lines.append("```mermaid\n")
        lines.append("%%{init: {'theme':'base'}}%%\n")
        lines.append("gantt\n")
        lines.append("    title Conversation Flow\n")
        lines.append("    dateFormat X\n")
        lines.append("    axisFormat %M:%S\n")
        
        # Group by conversation
        conversation_starts = [(ts, det) for ts, evt, det in self.conversation_events if evt == 'conversation_start']
        
        for i, (start_ts, details) in enumerate(conversation_starts[:10], 1):  # Max 10 conversations
            start_ms = int((start_ts - self.session_start) * 1000)
            
            # Find corresponding end
            end_ts = start_ts + 5  # Default 5 second duration
            for ts, evt, _ in self.conversation_events:
                if evt == 'conversation_end' and ts > start_ts:
                    end_ts = ts
                    break
            
            end_ms = int((end_ts - self.session_start) * 1000)
            
            lines.append(f"    Conversation {i} :conv{i}, {start_ms}, {end_ms}\n")
        
        lines.append("```\n\n")
        lines.append("---\n\n")
        return lines
    
    def _generate_statistics_tables(self) -> List[str]:
        """Generate detailed statistics tables"""
        lines = []
        lines.append("## 📈 Detailed Statistics\n\n")
        
        # Latency breakdown table
        if self.component_latencies:
            lines.append("### Latency Breakdown\n\n")
            lines.append("| Component | Count | Min | Max | Mean | Median | P95 |\n")
            lines.append("|-----------|-------|-----|-----|------|--------|-----|\n")
            
            for component in ['stt', 'llm', 'tts', 'vision', 'total']:
                if component not in self.component_latencies:
                    continue
                
                samples = [lat for _, lat in self.component_latencies[component]]
                if not samples:
                    continue
                
                sorted_samples = sorted(samples)
                count = len(samples)
                min_lat = min(samples)
                max_lat = max(samples)
                mean_lat = sum(samples) / count
                median_lat = sorted_samples[count // 2]
                p95_lat = sorted_samples[int(count * 0.95)] if count > 1 else max_lat
                
                lines.append(f"| **{component.upper()}** | {count} | {min_lat:.0f}ms | {max_lat:.0f}ms | {mean_lat:.0f}ms | {median_lat:.0f}ms | {p95_lat:.0f}ms |\n")
            
            lines.append("\n")
        
        # System resource stats
        if self.cpu_samples or self.memory_samples or self.temp_samples:
            lines.append("### System Resource Statistics\n\n")
            lines.append("| Resource | Min | Max | Mean |\n")
            lines.append("|----------|-----|-----|------|\n")
            
            if self.cpu_samples:
                cpu_vals = [cpu for _, cpu in self.cpu_samples]
                lines.append(f"| **CPU Usage** | {min(cpu_vals):.1f}% | {max(cpu_vals):.1f}% | {sum(cpu_vals)/len(cpu_vals):.1f}% |\n")
            
            if self.memory_samples:
                mem_vals = [mem for _, mem in self.memory_samples]
                lines.append(f"| **Memory Usage** | {min(mem_vals):.0f}MB | {max(mem_vals):.0f}MB | {sum(mem_vals)/len(mem_vals):.0f}MB |\n")
            
            if self.temp_samples:
                temp_vals = [temp for _, temp in self.temp_samples]
                lines.append(f"| **CPU Temperature** | {min(temp_vals):.1f}°C | {max(temp_vals):.1f}°C | {sum(temp_vals)/len(temp_vals):.1f}°C |\n")
            
            lines.append("\n")
        
        lines.append("---\n\n")
        return lines
    
    def _generate_issues_section(self) -> List[str]:
        """Generate errors and warnings section"""
        lines = []
        
        if self.errors:
            lines.append("## ❌ Errors\n\n")
            for ts, msg in self.errors[:20]:  # Max 20 errors
                time_str = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                lines.append(f"- **[{time_str}]** {msg}\n")
            
            if len(self.errors) > 20:
                lines.append(f"\n*...and {len(self.errors) - 20} more errors*\n")
            lines.append("\n---\n\n")
        
        if self.warnings:
            lines.append("## ⚠️ Warnings\n\n")
            for ts, msg in self.warnings[:20]:  # Max 20 warnings
                time_str = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                lines.append(f"- **[{time_str}]** {msg}\n")
            
            if len(self.warnings) > 20:
                lines.append(f"\n*...and {len(self.warnings) - 20} more warnings*\n")
            lines.append("\n---\n\n")
        
        if not self.errors and not self.warnings:
            lines.append("## ✅ No Issues Detected\n\n")
            lines.append("Session completed without errors or warnings.\n\n")
            lines.append("---\n\n")
        
        return lines
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


# Singleton instance
_performance_reporter: Optional[PerformanceReporter] = None


def get_reporter(session_id: Optional[str] = None) -> PerformanceReporter:
    """Get global performance reporter instance"""
    global _performance_reporter
    if _performance_reporter is None:
        _performance_reporter = PerformanceReporter(session_id)
    return _performance_reporter


def close_reporter() -> Optional[Path]:
    """Close reporter and generate final report"""
    global _performance_reporter
    if _performance_reporter:
        _performance_reporter.stop_monitoring()
        report_path = _performance_reporter.generate_report()
        _performance_reporter = None
        return report_path
    return None
