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
        
        # Recommendations (calculate from current data)
        avg_latencies = {}
        for component, samples in self.component_latencies.items():
            if samples:
                avg_latencies[component] = sum(lat for _, lat in samples) / len(samples)
        
        avg_cpu = sum(cpu for _, cpu in self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
        peak_temp = max((temp for _, temp in self.temp_samples), default=0) if self.temp_samples else 0
        
        lines.extend(self._generate_recommendations(avg_latencies, avg_cpu, peak_temp))
        
        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ Performance report generated: {output_path}")
        return output_path
    
    def _generate_summary_section(self) -> List[str]:
        """Generate executive summary section with performance scoring"""
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
        
        # Calculate performance scores
        scores = self._calculate_performance_scores(avg_latencies, avg_cpu, peak_temp)
        overall_score = scores['overall']
        
        # Overall grade with visual indicator
        lines.append(f"### Overall Performance: {scores['grade']} {scores['emoji']}\n\n")
        lines.append(f"**Score:** {overall_score}/100\n\n")
        
        # Visual performance gauge
        lines.append("```mermaid\n")
        lines.append("%%{init: {'theme':'base'}}%%\n")
        lines.append("graph LR\n")
        
        # Color-coded score boxes
        if overall_score >= 85:
            lines.append(f"    SCORE[\"⭐ {overall_score}/100<br/>EXCELLENT\"]:::excellent\n")
        elif overall_score >= 70:
            lines.append(f"    SCORE[\"✅ {overall_score}/100<br/>GOOD\"]:::good\n")
        elif overall_score >= 50:
            lines.append(f"    SCORE[\"⚠️ {overall_score}/100<br/>NEEDS IMPROVEMENT\"]:::warning\n")
        else:
            lines.append(f"    SCORE[\"❌ {overall_score}/100<br/>POOR\"]:::critical\n")
        
        lines.append("    classDef excellent fill:#22c55e,stroke:#16a34a,color:#fff\n")
        lines.append("    classDef good fill:#3b82f6,stroke:#2563eb,color:#fff\n")
        lines.append("    classDef warning fill:#f59e0b,stroke:#d97706,color:#fff\n")
        lines.append("    classDef critical fill:#ef4444,stroke:#dc2626,color:#fff\n")
        lines.append("```\n\n")
        
        # Key Metrics Table
        lines.append("### Key Metrics\n\n")
        lines.append(f"| Metric | Value | Status |\n")
        lines.append(f"|--------|-------|--------|\n")
        lines.append(f"| **Conversations** | {total_conversations} | {self._get_status_indicator(total_conversations > 0)} |\n")
        lines.append(f"| **Errors** | {total_errors} | {self._get_status_indicator(total_errors == 0)} |\n")
        lines.append(f"| **Warnings** | {total_warnings} | {self._get_status_indicator(total_warnings < 5)} |\n")
        
        if 'total' in avg_latencies:
            lines.append(f"| **End-to-End Latency** | {avg_latencies['total']:.0f}ms | {self._get_latency_status('total', avg_latencies['total'])} |\n")
        if 'stt' in avg_latencies:
            lines.append(f"| **STT Latency** | {avg_latencies['stt']:.0f}ms | {self._get_latency_status('stt', avg_latencies['stt'])} |\n")
        if 'llm' in avg_latencies:
            lines.append(f"| **LLM Latency** | {avg_latencies['llm']:.0f}ms | {self._get_latency_status('llm', avg_latencies['llm'])} |\n")
        if 'tts' in avg_latencies:
            lines.append(f"| **TTS Latency** | {avg_latencies['tts']:.0f}ms | {self._get_latency_status('tts', avg_latencies['tts'])} |\n")
        
        lines.append(f"| **CPU Usage** | {avg_cpu:.1f}% | {self._get_cpu_status(avg_cpu)} |\n")
        lines.append(f"| **Memory Usage** | {avg_mem:.0f}MB | {self._get_memory_status(avg_mem)} |\n")
        if peak_temp > 0:
            lines.append(f"| **Peak Temperature** | {peak_temp:.1f}°C | {self._get_temp_status(peak_temp)} |\n")
        
        lines.append("\n---\n\n")
        return lines
    
    def _calculate_performance_scores(self, latencies: Dict[str, float], cpu: float, temp: float) -> Dict[str, Any]:
        """Calculate overall performance score"""
        score = 100
        
        # Latency scoring (max -40 points)
        if 'total' in latencies:
            if latencies['total'] > 4000:
                score -= 40
            elif latencies['total'] > 3000:
                score -= 30
            elif latencies['total'] > 2500:
                score -= 20
            elif latencies['total'] > 2000:
                score -= 10
        
        if 'stt' in latencies:
            if latencies['stt'] > 500:
                score -= 10
            elif latencies['stt'] > 300:
                score -= 5
        
        if 'llm' in latencies:
            if latencies['llm'] > 3000:
                score -= 15
            elif latencies['llm'] > 2000:
                score -= 10
            elif latencies['llm'] > 1500:
                score -= 5
        
        # CPU scoring (max -20 points)
        if cpu > 90:
            score -= 20
        elif cpu > 80:
            score -= 15
        elif cpu > 70:
            score -= 10
        elif cpu > 60:
            score -= 5
        
        # Temperature scoring (max -20 points)
        if temp > 85:
            score -= 20
        elif temp > 80:
            score -= 15
        elif temp > 75:
            score -= 10
        elif temp > 70:
            score -= 5
        
        # Determine grade
        if score >= 90:
            grade = "EXCELLENT"
            emoji = "⭐"
        elif score >= 80:
            grade = "VERY GOOD"
            emoji = "🟢"
        elif score >= 70:
            grade = "GOOD"
            emoji = "✅"
        elif score >= 60:
            grade = "ACCEPTABLE"
            emoji = "🟡"
        elif score >= 50:
            grade = "NEEDS IMPROVEMENT"
            emoji = "⚠️"
        else:
            grade = "POOR"
            emoji = "❌"
        
        return {
            'overall': max(0, score),
            'grade': grade,
            'emoji': emoji
        }
    
    def _get_status_indicator(self, is_good: bool) -> str:
        """Get status indicator for boolean metrics"""
        return "✅ Good" if is_good else "❌ Bad"
    
    def _get_latency_status(self, component: str, latency: float) -> str:
        """Get status indicator for latency metrics"""
        thresholds = {
            'stt': (200, 300),      # Good < 200ms, OK < 300ms
            'llm': (1500, 2000),    # Good < 1500ms, OK < 2000ms
            'tts': (150, 250),      # Good < 150ms, OK < 250ms
            'total': (2000, 3000),  # Good < 2000ms, OK < 3000ms
        }
        
        if component not in thresholds:
            return "⚪ Unknown"
        
        good, acceptable = thresholds[component]
        
        if latency <= good:
            return "🟢 Excellent"
        elif latency <= acceptable:
            return "🟡 Acceptable"
        else:
            return "🔴 Too Slow"
    
    def _get_cpu_status(self, cpu: float) -> str:
        """Get status indicator for CPU usage"""
        if cpu <= 50:
            return "🟢 Low"
        elif cpu <= 70:
            return "🟡 Moderate"
        elif cpu <= 85:
            return "🟠 High"
        else:
            return "🔴 Critical"
    
    def _get_memory_status(self, memory_mb: float) -> str:
        """Get status indicator for memory usage"""
        if memory_mb <= 1500:
            return "🟢 Good"
        elif memory_mb <= 2500:
            return "🟡 Moderate"
        else:
            return "🔴 High"
    
    def _get_temp_status(self, temp: float) -> str:
        """Get status indicator for temperature"""
        if temp <= 65:
            return "🟢 Cool"
        elif temp <= 75:
            return "🟡 Warm"
        elif temp <= 85:
            return "🟠 Hot"
        else:
            return "🔴 Critical"
    
    def _generate_latency_diagrams(self) -> List[str]:
        """Generate latency performance diagrams"""
        lines = []
        lines.append("## ⏱️ Latency Performance Analysis\n\n")
        
        # Component latency comparison with color coding
        if self.component_latencies:
            lines.append("### Component Breakdown (Average)\n\n")
            lines.append("```mermaid\n")
            lines.append("%%{init: {'theme':'base'}}%%\n")
            lines.append("graph TD\n")
            
            # Calculate averages and determine status
            component_data = {}
            for component in ['stt', 'llm', 'tts', 'total']:
                if component in self.component_latencies:
                    samples = self.component_latencies[component]
                    avg = sum(lat for _, lat in samples) / len(samples)
                    component_data[component] = avg
                    
                    # Determine status and color
                    status = self._get_latency_status(component, avg)
                    
                    if '🟢' in status:
                        style = ":::excellent"
                    elif '🟡' in status:
                        style = ":::warning"
                    else:
                        style = ":::critical"
                    
                    icon = {'stt': '🎤', 'llm': '🧠', 'tts': '🔊', 'total': '⏱️'}.get(component, '')
                    lines.append(f"    {component.upper()}[\"{icon} {component.upper()}<br/>{avg:.0f}ms<br/>{status}\"]{style}\n")
            
            lines.append("    classDef excellent fill:#22c55e,stroke:#16a34a,color:#fff\n")
            lines.append("    classDef warning fill:#f59e0b,stroke:#d97706,color:#fff\n")
            lines.append("    classDef critical fill:#ef4444,stroke:#dc2626,color:#fff\n")
            lines.append("```\n\n")
            
            # Target vs Actual comparison
            lines.append("### Performance vs Targets\n\n")
            lines.append("```mermaid\n")
            lines.append("%%{init: {'theme':'base'}}%%\n")
            lines.append("xychart-beta\n")
            lines.append("    title \"Latency: Target vs Actual\"\n")
            lines.append("    x-axis [STT, LLM, TTS, Total]\n")
            lines.append("    y-axis \"Latency (ms)\" 0 --> " + str(int(max(component_data.values()) * 1.3)) + "\n")
            
            # Target values
            targets = [200, 1500, 150, 2000]
            target_str = ", ".join(str(t) for t in targets)
            
            # Actual values (in order: STT, LLM, TTS, Total)
            actuals = [
                component_data.get('stt', 0),
                component_data.get('llm', 0),
                component_data.get('tts', 0),
                component_data.get('total', 0)
            ]
            actual_str = ", ".join(f"{a:.0f}" for a in actuals)
            
            lines.append(f"    bar \"Target\" [{target_str}]\n")
            lines.append(f"    bar \"Actual\" [{actual_str}]\n")
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
        lines.append("## 💻 System Resource Analysis\n\n")
        
        # System health summary
        avg_cpu = sum(cpu for _, cpu in self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
        avg_mem = sum(mem for _, mem in self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0
        avg_temp = sum(temp for _, temp in self.temp_samples) / len(self.temp_samples) if self.temp_samples else 0
        
        lines.append("### System Health Overview\n\n")
        lines.append("```mermaid\n")
        lines.append("%%{init: {'theme':'base'}}%%\n")
        lines.append("graph TD\n")
        
        # CPU status
        cpu_status = self._get_cpu_status(avg_cpu)
        if '🟢' in cpu_status:
            cpu_style = ":::excellent"
        elif '🟡' in cpu_status:
            cpu_style = ":::warning"
        else:
            cpu_style = ":::critical"
        lines.append(f"    CPU[\"💻 CPU<br/>{avg_cpu:.1f}%<br/>{cpu_status}\"]{cpu_style}\n")
        
        # Memory status
        mem_status = self._get_memory_status(avg_mem)
        if '🟢' in mem_status:
            mem_style = ":::excellent"
        elif '🟡' in mem_status:
            mem_style = ":::warning"
        else:
            mem_style = ":::critical"
        lines.append(f"    MEM[\"🧠 Memory<br/>{avg_mem:.0f}MB<br/>{mem_status}\"]{mem_style}\n")
        
        # Temperature status (if available)
        if self.temp_samples and avg_temp > 0:
            temp_status = self._get_temp_status(avg_temp)
            if '🟢' in temp_status:
                temp_style = ":::excellent"
            elif '🟡' in temp_status or '🟠' in temp_status:
                temp_style = ":::warning"
            else:
                temp_style = ":::critical"
            lines.append(f"    TEMP[\"🌡️ Temperature<br/>{avg_temp:.1f}°C<br/>{temp_status}\"]{temp_style}\n")
        
        lines.append("    classDef excellent fill:#22c55e,stroke:#16a34a,color:#fff\n")
        lines.append("    classDef warning fill:#f59e0b,stroke:#d97706,color:#fff\n")
        lines.append("    classDef critical fill:#ef4444,stroke:#dc2626,color:#fff\n")
        lines.append("```\n\n")
        
        # CPU Usage Chart
        if self.cpu_samples:
            lines.append("### CPU Usage Over Time\n\n")
            
            # Calculate thresholds
            max_cpu = max(cpu for _, cpu in self.cpu_samples)
            lines.append(f"**Peak:** {max_cpu:.1f}% | **Average:** {avg_cpu:.1f}%\n\n")
            
            lines.append("```mermaid\n")
            lines.append("%%{init: {'theme':'base'}}%%\n")
            lines.append("xychart-beta\n")
            lines.append("    title \"CPU Usage (Target: <50% Good, <70% OK)\"\n")
            
            # Take samples every N to fit in chart (max 30 points)
            step = max(1, len(self.cpu_samples) // 30)
            sampled_cpu = self.cpu_samples[::step]
            
            lines.append("    x-axis [" + ", ".join(f"\"{i+1}\"" for i in range(len(sampled_cpu))) + "]\n")
            lines.append("    y-axis \"CPU %\" 0 --> 100\n")
            lines.append("    line [" + ", ".join(f"{cpu:.1f}" for _, cpu in sampled_cpu) + "]\n")
            lines.append("```\n\n")
        
        # Memory Usage Chart
        if self.memory_samples:
            lines.append("### Memory Usage Over Time\n\n")
            
            max_mem = max(mem for _, mem in self.memory_samples)
            lines.append(f"**Peak:** {max_mem:.0f}MB | **Average:** {avg_mem:.0f}MB\n\n")
            
            lines.append("```mermaid\n")
            lines.append("%%{init: {'theme':'base'}}%%\n")
            lines.append("xychart-beta\n")
            lines.append("    title \"Memory Usage (Target: <1500MB Good, <2500MB OK)\"\n")
            
            step = max(1, len(self.memory_samples) // 30)
            sampled_mem = self.memory_samples[::step]
            
            lines.append("    x-axis [" + ", ".join(f"\"{i+1}\"" for i in range(len(sampled_mem))) + "]\n")
            lines.append(f"    y-axis \"Memory (MB)\" 0 --> {int(max_mem * 1.2)}\n")
            lines.append("    line [" + ", ".join(f"{mem:.0f}" for _, mem in sampled_mem) + "]\n")
            lines.append("```\n\n")
        
        # Temperature Chart (Raspberry Pi)
        if self.temp_samples:
            lines.append("### CPU Temperature Over Time\n\n")
            
            max_temp = max(temp for _, temp in self.temp_samples)
            lines.append(f"**Peak:** {max_temp:.1f}°C | **Average:** {avg_temp:.1f}°C\n\n")
            
            lines.append("```mermaid\n")
            lines.append("%%{init: {'theme':'base'}}%%\n")
            lines.append("xychart-beta\n")
            lines.append("    title \"CPU Temperature (Target: <65°C Cool, <75°C OK)\"\n")
            
            step = max(1, len(self.temp_samples) // 30)
            sampled_temp = self.temp_samples[::step]
            
            lines.append("    x-axis [" + ", ".join(f"\"{i+1}\"" for i in range(len(sampled_temp))) + "]\n")
            lines.append("    y-axis \"Temperature (°C)\" 0 --> 100\n")
            lines.append("    line [" + ", ".join(f"{temp:.1f}" for _, temp in sampled_temp) + "]\n")
            lines.append("```\n\n")
            
            # Temperature warning with recommendations
            if max_temp > 85:
                lines.append("> 🔴 **CRITICAL:** Peak temperature {:.1f}°C is DANGEROUS!\n".format(max_temp))
                lines.append("> **Actions Required:**\n")
                lines.append("> - Add heatsink or cooling fan immediately\n")
                lines.append("> - Reduce CPU frequency (add `arm_freq=1200` to config.txt)\n")
                lines.append("> - Check ambient temperature and airflow\n\n")
            elif max_temp > 80:
                lines.append("> 🟠 **WARNING:** Peak temperature {:.1f}°C is too high!\n".format(max_temp))
                lines.append("> **Recommendations:**\n")
                lines.append("> - Add cooling solution (heatsink recommended)\n")
                lines.append("> - Improve ventilation around device\n")
                lines.append("> - May cause thermal throttling and performance degradation\n\n")
            elif max_temp > 75:
                lines.append("> 🟡 **NOTICE:** Temperature {:.1f}°C is elevated\n".format(max_temp))
                lines.append("> - Consider adding heatsink for better performance\n")
                lines.append("> - Monitor during longer sessions\n\n")
            elif max_temp > 70:
                lines.append("> 🟢 **INFO:** Temperature {:.1f}°C is within acceptable range\n".format(max_temp))
                lines.append("> - Normal operation, but cooling could improve longevity\n\n")
            else:
                lines.append("> ✅ **EXCELLENT:** Temperature {:.1f}°C is optimal!\n\n".format(max_temp))
        
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
    
    def _generate_recommendations(self, avg_latencies: Dict[str, float], avg_cpu: float, peak_temp: float) -> List[str]:
        """Generate actionable recommendations based on performance"""
        lines = []
        lines.append("## 💡 Recommendations\n\n")
        
        recommendations = []
        
        # Latency recommendations
        if 'total' in avg_latencies:
            if avg_latencies['total'] > 3000:
                recommendations.append("🔴 **CRITICAL:** Total latency is very high (>{:.0f}ms)".format(avg_latencies['total']))
                recommendations.append("   - Consider using a more powerful model (e.g., upgrade to RPi 5)")
                recommendations.append("   - Check if Ollama is using proper CPU optimization")
                recommendations.append("   - Reduce LLM model size or use quantized version")
            elif avg_latencies['total'] > 2500:
                recommendations.append("🟡 **Latency:** Total response time could be improved (>{:.0f}ms)".format(avg_latencies['total']))
                recommendations.append("   - LLM is the bottleneck - consider model optimization")
                recommendations.append("   - Check system load during conversations")
        
        if 'stt' in avg_latencies and avg_latencies['stt'] > 300:
            recommendations.append("🟡 **STT Performance:** Speech recognition is slow (>{:.0f}ms)".format(avg_latencies['stt']))
            recommendations.append("   - Whisper Tiny should be <250ms on RPi 4")
            recommendations.append("   - Check CPU availability during STT processing")
        
        if 'llm' in avg_latencies and avg_latencies['llm'] > 2000:
            recommendations.append("🟠 **LLM Performance:** Language model inference is slow (>{:.0f}ms)".format(avg_latencies['llm']))
            recommendations.append("   - This is expected on RPi 4 with Qwen2.5:0.5B")
            recommendations.append("   - Consider: RPi 5, or cloud-based LLM (OpenAI API)")
        
        # CPU recommendations
        if avg_cpu > 80:
            recommendations.append("🔴 **CPU Overload:** Average CPU usage is very high ({:.1f}%)".format(avg_cpu))
            recommendations.append("   - System is running at capacity")
            recommendations.append("   - Consider disabling vision worker if not needed")
            recommendations.append("   - Check for background processes consuming resources")
        elif avg_cpu > 70:
            recommendations.append("🟡 **CPU Usage:** CPU usage is high ({:.1f}%)".format(avg_cpu))
            recommendations.append("   - Normal for active conversations, but monitor stability")
        
        # Temperature recommendations
        if peak_temp > 80:
            recommendations.append("🔴 **THERMAL:** Temperature is critical ({:.1f}°C)".format(peak_temp))
            recommendations.append("   - **URGENT:** Add cooling solution (heatsink + fan)")
            recommendations.append("   - Thermal throttling is likely reducing performance")
            recommendations.append("   - Long-term high temps reduce hardware lifespan")
        elif peak_temp > 75:
            recommendations.append("🟠 **Cooling:** Temperature is elevated ({:.1f}°C)".format(peak_temp))
            recommendations.append("   - Add heatsink to improve thermal performance")
            recommendations.append("   - Improve airflow around device")
        
        # Positive feedback
        if not recommendations:
            lines.append("### ✅ System Performance is Excellent!\n\n")
            lines.append("Your system is running optimally:\n\n")
            lines.append("- ✅ Latency is within acceptable ranges\n")
            lines.append("- ✅ CPU usage is healthy\n")
            if peak_temp > 0:
                lines.append("- ✅ Thermal performance is good\n")
            lines.append("\n**Keep it up!** Your Pluto assistant is performing at peak efficiency.\n\n")
        else:
            lines.append("### Performance Improvements\n\n")
            for rec in recommendations:
                lines.append(f"{rec}\n")
            lines.append("\n")
        
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
