"""
🪐 Project Pluto - Metrics Logger
Performance tracking and measurement system
"""

import time
import csv
import json
import psutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

from config import LOGS_DIR, METRICS_CONFIG


@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    timestamp: float
    component: str
    metric_type: str
    value: float
    unit: str
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp_readable'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return data


class MetricsLogger:
    """Centralized metrics collection and reporting system"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.metrics: List[PerformanceMetric] = []
        self.lock = threading.Lock()
        
        self.csv_path = LOGS_DIR / f"metrics_{self.session_id}.csv"
        self.json_path = LOGS_DIR / f"metrics_{self.session_id}.json"
        self.summary_path = LOGS_DIR / f"summary_{self.session_id}.txt"
        
        self.stats = defaultdict(lambda: defaultdict(list))
        self.session_start = time.time()
        self.conversation_count = 0
        
        if METRICS_CONFIG["csv_enabled"]:
            self._init_csv()
        
        print(f"📊 Metrics Logger initialized - Session: {self.session_id}")
    
    def _init_csv(self):
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'timestamp_readable', 'component', 'metric_type', 'value', 'unit', 'metadata'])
    
    def log_metric(self, component: str, metric_type: str, value: float, unit: str, metadata: Optional[Dict] = None):
        metric = PerformanceMetric(
            timestamp=time.time(),
            component=component,
            metric_type=metric_type,
            value=value,
            unit=unit,
            metadata=metadata or {}
        )
        
        with self.lock:
            self.metrics.append(metric)
            self.stats[component][metric_type].append(value)
            
            if METRICS_CONFIG["csv_enabled"]:
                self._append_to_csv(metric)
            
            if METRICS_CONFIG["console_enabled"]:
                self._console_output(metric)
            
            self._check_thresholds(metric)
    
    def _append_to_csv(self, metric: PerformanceMetric):
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                metric.timestamp,
                datetime.fromtimestamp(metric.timestamp).isoformat(),
                metric.component,
                metric.metric_type,
                metric.value,
                metric.unit,
                json.dumps(metric.metadata)
            ])
    
    def _console_output(self, metric: PerformanceMetric):
        icon_map = {'stt': '🎤', 'llm': '🧠', 'tts': '🔊', 'vision': '👁️', 'system': '💻', 'total': '⏱️'}
        icon = icon_map.get(metric.component, '📊')
        
        if metric.metric_type == 'latency':
            print(f"  {icon} {metric.component.upper()}: {metric.value:.0f}{metric.unit}")
    
    def _check_thresholds(self, metric: PerformanceMetric):
        if metric.metric_type != 'latency':
            return
        
        thresholds = {
            'stt': METRICS_CONFIG['max_stt_latency'],
            'llm': METRICS_CONFIG['max_llm_latency'],
            'tts': METRICS_CONFIG['max_tts_latency'],
            'total': METRICS_CONFIG['max_total_latency']
        }
        
        threshold = thresholds.get(metric.component)
        if threshold and metric.value > threshold:
            print(f"⚠️  WARNING: {metric.component.upper()} latency ({metric.value:.0f}ms) exceeds threshold ({threshold}ms)")
    
    def log_conversation_start(self):
        self.conversation_count += 1
        self.log_metric('system', 'conversation_start', time.time(), 'timestamp', {'conversation_id': self.conversation_count})
    
    def log_conversation_end(self, total_latency: float):
        self.log_metric('total', 'latency', total_latency, 'ms', {'conversation_id': self.conversation_count})
    
    def log_memory_usage(self):
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.log_metric('system', 'memory', memory_mb, 'MB')
        return memory_mb
    
    def log_error(self, component: str, error_type: str, details: str):
        self.log_metric(component, 'error', 1, 'count', {'error_type': error_type, 'details': details})
    
    def log_vision_detection(self, fps: float, faces_detected: int, face_locked: bool):
        """Log vision detection metrics"""
        self.log_metric('vision', 'fps', fps, 'fps')
        self.log_metric('vision', 'faces_detected', faces_detected, 'count')
        self.log_metric('vision', 'face_locked', 1 if face_locked else 0, 'bool')
    
    def log_vision_event(self, event_type: str, face_id: Optional[float] = None):
        """Log vision events (face_locked, face_lost, etc)"""
        metadata = {}
        if face_id is not None:
            metadata['face_id'] = face_id
        self.log_metric('vision', f'event_{event_type}', 1, 'event', metadata=metadata)
    
    def get_statistics(self) -> Dict[str, Any]:
        stats_summary = {}
        
        for component, metrics in self.stats.items():
            stats_summary[component] = {}
            
            for metric_type, values in metrics.items():
                if not values:
                    continue
                
                stats_summary[component][metric_type] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'mean': sum(values) / len(values),
                    'median': sorted(values)[len(values) // 2],
                }
        
        return stats_summary
    
    def print_summary(self):
        runtime = time.time() - self.session_start
        stats = self.get_statistics()
        
        print("\n" + "="*70)
        print("📊 PLUTO SESSION SUMMARY")
        print("="*70)
        
        print(f"\n⏱️  Runtime: {runtime:.1f}s")
        print(f"💬 Conversations: {self.conversation_count}")
        
        for comp in ['stt', 'llm', 'tts', 'total']:
            if comp in stats and 'latency' in stats[comp]:
                s = stats[comp]['latency']
                icon = {'stt': '🎤', 'llm': '🧠', 'tts': '🔊', 'total': '⏱️'}[comp]
                print(f"\n{icon} {comp.upper()} Latency:")
                print(f"   Mean: {s['mean']:.0f}ms | Min: {s['min']:.0f}ms | Max: {s['max']:.0f}ms")
        
        if 'vision' in stats and 'fps' in stats['vision']:
            fps_s = stats['vision']['fps']
            print(f"\n👁️  Vision FPS: Mean: {fps_s['mean']:.1f} | Min: {fps_s['min']:.1f} | Max: {fps_s['max']:.1f}")
        
        if 'system' in stats and 'memory' in stats['system']:
            mem = stats['system']['memory']
            print(f"\n💾 Memory: Mean: {mem['mean']:.0f}MB | Peak: {mem['max']:.0f}MB")
        
        print("\n" + "="*70)
        
        self._save_summary(runtime, stats)
    
    def _save_summary(self, runtime: float, stats: Dict):
        with open(self.summary_path, 'w') as f:
            f.write(f"🪐 PROJECT PLUTO - SESSION SUMMARY\n")
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Runtime: {runtime:.1f}s\n")
            f.write(f"Conversations: {self.conversation_count}\n\n")
            f.write("STATISTICS:\n")
            f.write(json.dumps(stats, indent=2))
    
    def export_json(self):
        if not METRICS_CONFIG["json_enabled"]:
            return
        
        export_data = {
            'session_id': self.session_id,
            'session_start': self.session_start,
            'conversation_count': self.conversation_count,
            'metrics': [m.to_dict() for m in self.metrics],
            'statistics': self.get_statistics()
        }
        
        with open(self.json_path, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def close(self):
        self.export_json()
        self.print_summary()
        print(f"\n✅ Metrics saved to: {LOGS_DIR}")


_global_logger: Optional[MetricsLogger] = None


def get_logger(session_id: Optional[str] = None) -> MetricsLogger:
    global _global_logger
    if _global_logger is None:
        _global_logger = MetricsLogger(session_id)
    return _global_logger


def close_logger():
    global _global_logger
    if _global_logger:
        _global_logger.close()
        _global_logger = None
