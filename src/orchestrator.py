"""
🪐 Project Pluto - Orchestrator
Main coordinator for voice assistant pipeline
"""

import queue
import time
import signal
import sys
import threading
from typing import Optional

from config import QUEUE_CONFIG, ORCHESTRATOR_CONFIG, print_config_summary
from metrics_logger import get_logger, close_logger
from workers import STTWorker, LLMWorker, TTSWorker


class PlutoOrchestrator:
    """Main orchestrator coordinating STT → LLM → TTS pipeline"""
    
    def __init__(self):
        self.stt_to_llm_queue = queue.Queue(maxsize=QUEUE_CONFIG["max_size"])
        self.llm_to_tts_queue = queue.Queue(maxsize=QUEUE_CONFIG["max_size"])
        
        self.metrics = get_logger()
        
        self.stt_worker = STTWorker(self.stt_to_llm_queue, self.metrics)
        self.llm_worker = LLMWorker(self.stt_to_llm_queue, self.llm_to_tts_queue, self.metrics)
        self.tts_worker = TTSWorker(self.llm_to_tts_queue, self.metrics)
        
        self.workers = [self.stt_worker, self.llm_worker, self.tts_worker]
        
        self.running = False
        self.monitor_thread = None
        
        self.conversation_start_time = None
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("\n" + "="*70)
        print("🪐 PROJECT PLUTO - Voice Assistant Orchestrator")
        print("="*70 + "\n")
    
    def initialize(self):
        """Initialize all workers"""
        print("🚀 Initializing workers...")
        
        print_config_summary()
        print()
        
        all_ok = True
        
        if not self.stt_worker.start():
            print("❌ STT Worker failed to start")
            all_ok = False
        
        if not self.llm_worker.start():
            print("❌ LLM Worker failed to start")
            all_ok = False
        
        if not self.tts_worker.start():
            print("❌ TTS Worker failed to start")
            all_ok = False
        
        if all_ok:
            print("\n✅ All workers initialized successfully\n")
        else:
            print("\n❌ Some workers failed to initialize\n")
            return False
        
        self._setup_queue_monitoring()
        
        return True
    
    def _setup_queue_monitoring(self):
        """Monitor queue events for conversation flow tracking"""
        self.original_stt_put = self.stt_to_llm_queue.put
        self.stt_to_llm_queue.put = self._wrap_stt_put
        
        self.original_tts_get = self.llm_to_tts_queue.get
        self.llm_to_tts_queue.get = self._wrap_tts_get
    
    def _wrap_stt_put(self, item, **kwargs):
        """Track conversation start when STT produces transcript"""
        self.conversation_start_time = time.time()
        self.metrics.log_conversation_start()
        return self.original_stt_put(item, **kwargs)
    
    def _wrap_tts_get(self, **kwargs):
        """Track conversation end when TTS gets response"""
        item = self.original_tts_get(**kwargs)
        
        if self.conversation_start_time:
            total_latency = (time.time() - self.conversation_start_time) * 1000
            self.metrics.log_conversation_end(total_latency)
            self.conversation_start_time = None
        
        return item
    
    def start(self):
        """Start orchestrator"""
        if not self.initialize():
            print("❌ Orchestrator initialization failed")
            return False
        
        self.running = True
        
        if ORCHESTRATOR_CONFIG["health_monitoring"]:
            self.monitor_thread = threading.Thread(target=self._health_monitor, daemon=True)
            self.monitor_thread.start()
        
        print("="*70)
        print("🎙️  PLUTO IS READY - Start speaking!")
        print("   Press Ctrl+C to stop")
        print("="*70 + "\n")
        
        return True
    
    def _health_monitor(self):
        """Monitor worker health and queue states"""
        while self.running:
            time.sleep(ORCHESTRATOR_CONFIG["health_check_interval"])
            
            if ORCHESTRATOR_CONFIG["memory_monitoring"]:
                self.metrics.log_memory_usage()
            
            if ORCHESTRATOR_CONFIG["queue_monitoring"]:
                stt_depth = self.stt_to_llm_queue.qsize()
                llm_depth = self.llm_to_tts_queue.qsize()
                
                if stt_depth > 0 or llm_depth > 0:
                    self.metrics.log_metric('system', 'queue_depth', stt_depth + llm_depth, 'items')
    
    def get_status(self) -> dict:
        """Get orchestrator status"""
        return {
            'running': self.running,
            'workers': [w.get_status() for w in self.workers],
            'queues': {
                'stt_to_llm': self.stt_to_llm_queue.qsize(),
                'llm_to_tts': self.llm_to_tts_queue.qsize()
            },
            'conversations': self.metrics.conversation_count
        }
    
    def print_status(self):
        """Print current status"""
        status = self.get_status()
        
        print("\n" + "="*70)
        print("📊 PLUTO STATUS")
        print("="*70)
        
        for worker_status in status['workers']:
            icon = '✅' if worker_status['running'] else '❌'
            print(f"{icon} {worker_status['name']}: {worker_status}")
        
        print(f"\n📦 Queue Depths: STT→LLM={status['queues']['stt_to_llm']}, LLM→TTS={status['queues']['llm_to_tts']}")
        print(f"💬 Conversations: {status['conversations']}")
        print("="*70 + "\n")
    
    def run(self):
        """Main run loop"""
        if not self.start():
            return
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down...")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        print("\n🔄 Shutting down workers...")
        
        self.running = False
        
        for worker in self.workers:
            try:
                worker.stop()
            except Exception as e:
                print(f"⚠️  Error stopping {worker.__class__.__name__}: {e}")
        
        print("\n📊 Saving metrics...")
        close_logger()
        
        print("\n" + "="*70)
        print("🪐 PLUTO SHUTDOWN COMPLETE")
        print("="*70 + "\n")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n\n📡 Received signal {signum}")
        self.running = False


def main():
    """Entry point"""
    orchestrator = PlutoOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
