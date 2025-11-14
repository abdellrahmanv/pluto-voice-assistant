"""
🪐 Project Pluto - Orchestrator
Main coordinator for 3-worker voice assistant (STT, LLM, TTS)
"""

import queue
import time
import signal
import sys
import threading
import io
from typing import Optional
from datetime import datetime
from pathlib import Path

from config import QUEUE_CONFIG, ORCHESTRATOR_CONFIG, print_config_summary
from metrics_logger import get_logger, close_logger
from performance_reporter import get_reporter, close_reporter
from workers import STTWorker, LLMWorker, TTSWorker
from agent_state import AgentStateManager, AgentState


class PlutoOrchestrator:
    """Main orchestrator coordinating STT → LLM → TTS voice assistant"""
    
    def __init__(self):
        """
        Initialize orchestrator
        
        Args:        """
        # Session tracking
        self.session_start_time = datetime.now()
        
        # Performance reporter (NEW: Replaces log buffer approach)
        self.reporter = get_reporter()
        self.reporter.start_monitoring(interval=2.0)
        
        # Queues
        self.stt_to_llm_queue = queue.Queue(maxsize=QUEUE_CONFIG["max_size"])
        self.llm_to_tts_queue = queue.Queue(maxsize=QUEUE_CONFIG["max_size"])        
        # Metrics
        self.metrics = get_logger()
        
        # Agent state manager (NEW: Reflex agent behavior)
        self.agent_state = AgentStateManager()
        
        # Workers (pass reporter for latency tracking)
        self.stt_worker = STTWorker(self.stt_to_llm_queue, self.metrics, self.reporter)
        self.llm_worker = LLMWorker(self.stt_to_llm_queue, self.llm_to_tts_queue, self.metrics, self.reporter)
        self.tts_worker = TTSWorker(self.llm_to_tts_queue, self.metrics, self.reporter)
        self.workers = [self.stt_worker, self.llm_worker, self.tts_worker]
        
        # Control flags
        self.running = False
        self.monitor_thread = None        
        # Conversation tracking
        self.conversation_start_time = None
        self.last_greeting_time = 0
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("\n" + "="*70)
        print("🪐 PROJECT PLUTO - Voice Assistant")
        print("="*70 + "\n")

        # Start all workers
        all_ok = True
        for worker in self.workers:
            if not worker.start():
                print(f"✗ {worker.__class__.__name__} failed to start")
                all_ok = False

        if not all_ok:
            print("\n✗ Some workers failed to initialize\n")
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
        self.reporter.log_conversation_event('conversation_start', f"User spoke: {item.get('text', '')[:50]}")
        return self.original_stt_put(item, **kwargs)
    
    def _wrap_tts_get(self, **kwargs):
        """Track conversation end when TTS gets response"""
        item = self.original_tts_get(**kwargs)
        
        if self.conversation_start_time:
            total_latency = (time.time() - self.conversation_start_time) * 1000
            self.metrics.log_conversation_end(total_latency)
            self.reporter.log_latency('total', total_latency)
            self.reporter.log_conversation_event('conversation_end', f"Total latency: {total_latency:.0f}ms")
            self.conversation_start_time = None
        
        return item
    
    def start(self):
        """Start orchestrator"""
        if not self.initialize():
            print("❌ Orchestrator initialization failed")
            return False
        
        self.running = True
        
        # Start health monitor
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
    def _send_greeting(self):
        """
        Send greeting message to LLM to initiate conversation
        
        This bypasses STT and directly queues a greeting prompt
        """
        # Check cooldown to avoid repeated greetings
        current_time = time.time()
        if current_time - self.last_greeting_time < VISION_CONFIG['greeting_cooldown']:
            print("⏱️  Greeting on cooldown, skipping")
            return
        
        self.last_greeting_time = current_time
        
        # Transition to greeting state
        self.agent_state.transition(
            AgentState.GREETING,
            "Initiating conversation"
        )
        
        # Inject greeting into STT->LLM queue
        greeting_msg = {
            'type': 'transcript',
            'text': VISION_CONFIG['greeting_message'],
            'timestamp': current_time,
            'latency_ms': 0,
            'source': 'user'
        }
        
        try:
            self.stt_to_llm_queue.put_nowait(greeting_msg)
            print(f"💬 Greeting queued: \"{VISION_CONFIG['greeting_message']}\"")
            
            # Log greeting event
            self.reporter.log_conversation_event('greeting_sent', VISION_CONFIG['greeting_message'])
            
            # Transition to listening after greeting
            self.agent_state.transition(
                AgentState.LISTENING,
                "Waiting for user response"
            )
            
            # Resume STT to listen for response
            self.stt_worker.resume()
            
        except queue.Full:
            print("⚠️  Failed to queue greeting - queue full")
            self.reporter.log_warning("Failed to queue greeting - queue full")
    
    def get_status(self) -> dict:
        """Get orchestrator status"""
        status = {
            'running': self.running,
            'workers': [w.get_status() for w in self.workers],
            'queues': {
                'stt_to_llm': self.stt_to_llm_queue.qsize(),
                'llm_to_tts': self.llm_to_tts_queue.qsize()
            },
            'conversations': self.metrics.conversation_count,
            'agent_state': self.agent_state.get_state_info()
        }        
        return status
    
    def print_status(self):
        """Print current status"""
        status = self.get_status()
        
        print("\n" + "="*70)
        print("📊 PLUTO STATUS")
        print("="*70)
        
        # Agent state
        agent_info = status['agent_state']
        print(f"\n🤖 Agent State: {agent_info['state']}")
        print(f"   Locked: {agent_info['locked']}")
        if agent_info['locked']:
            print(f"   Face ID: {agent_info['locked_face_id']:.2f}")
        print(f"   Should Listen: {agent_info['should_listen']}")
        
        # Workers
        print("\n👷 Workers:")
        for worker_status in status['workers']:
            icon = '✅' if worker_status['running'] else '❌'
            print(f"  {icon} {worker_status['name']}: {worker_status}")
        
        # Queues
        queue_str = f"STT→LLM={status['queues']['stt_to_llm']}, LLM→TTS={status['queues']['llm_to_tts']}"
        print(f"\n📦 Queue Depths: {queue_str}")
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
                error_msg = f"Error stopping {worker.__class__.__name__}: {e}"
                print(f"⚠️  {error_msg}")
                self.reporter.log_error(error_msg)
        
        print("\n📊 Saving metrics...")
        close_logger()
        
        print("\n� Generating performance diagram report...")
        report_path = close_reporter()
        if report_path:
            print(f"✅ Performance report: {report_path}")
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

