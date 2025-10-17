"""
🪐 Project Pluto - Orchestrator
Main coordinator for 4-worker reflex agent (STT, LLM, TTS, Vision)
"""

import queue
import time
import signal
import sys
import threading
from typing import Optional

from config import QUEUE_CONFIG, ORCHESTRATOR_CONFIG, VISION_CONFIG, print_config_summary
from metrics_logger import get_logger, close_logger
from workers import STTWorker, LLMWorker, TTSWorker
from workers.vision_worker import VisionWorker
from agent_state import AgentStateManager, AgentState


class PlutoOrchestrator:
    """Main orchestrator coordinating STT → LLM → TTS + Vision reflex agent"""
    
    def __init__(self, enable_vision=True):
        """
        Initialize orchestrator
        
        Args:
            enable_vision: Enable vision worker (default: True)
        """
        # Queues
        self.stt_to_llm_queue = queue.Queue(maxsize=QUEUE_CONFIG["max_size"])
        self.llm_to_tts_queue = queue.Queue(maxsize=QUEUE_CONFIG["max_size"])
        self.vision_to_orchestrator_queue = queue.Queue(maxsize=QUEUE_CONFIG["max_size"])
        
        # Metrics
        self.metrics = get_logger()
        
        # Agent state manager (NEW: Reflex agent behavior)
        self.agent_state = AgentStateManager()
        
        # Workers
        self.stt_worker = STTWorker(self.stt_to_llm_queue, self.metrics)
        self.llm_worker = LLMWorker(self.stt_to_llm_queue, self.llm_to_tts_queue, self.metrics)
        self.tts_worker = TTSWorker(self.llm_to_tts_queue, self.metrics)
        
        # Vision worker (optional)
        self.enable_vision = enable_vision
        self.vision_worker = None
        if self.enable_vision:
            try:
                self.vision_worker = VisionWorker(self.vision_to_orchestrator_queue)
                self.workers = [self.stt_worker, self.llm_worker, self.tts_worker, self.vision_worker]
            except Exception as e:
                print(f"⚠️  Vision worker initialization failed: {e}")
                print(f"   Running without vision capabilities")
                self.enable_vision = False
                self.workers = [self.stt_worker, self.llm_worker, self.tts_worker]
        else:
            self.workers = [self.stt_worker, self.llm_worker, self.tts_worker]
        
        # Control flags
        self.running = False
        self.monitor_thread = None
        self.vision_monitor_thread = None
        
        # Conversation tracking
        self.conversation_start_time = None
        self.last_greeting_time = 0
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("\n" + "="*70)
        print("🪐 PROJECT PLUTO - Reflex Agent Voice Assistant")
        if self.enable_vision:
            print("   With Vision-Driven Interaction")
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
        
        # Start health monitor
        if ORCHESTRATOR_CONFIG["health_monitoring"]:
            self.monitor_thread = threading.Thread(target=self._health_monitor, daemon=True)
            self.monitor_thread.start()
        
        # Start vision event monitor (NEW: Reflex agent behavior)
        if self.enable_vision:
            self.vision_monitor_thread = threading.Thread(target=self._vision_event_monitor, daemon=True)
            self.vision_monitor_thread.start()
        
        print("="*70)
        if self.enable_vision:
            print("👁️  PLUTO IS READY - Looking for people to talk to!")
        else:
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
    
    def _vision_event_monitor(self):
        """
        Monitor vision events and drive reflex agent behavior
        
        This is the core of the reflex agent:
        - Detects new faces
        - Locks onto a person
        - Initiates greeting
        - Manages conversation state
        """
        print("👁️  Vision event monitor started")
        
        while self.running:
            try:
                # Get vision event (non-blocking with timeout)
                try:
                    event = self.vision_to_orchestrator_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                # Handle vision events based on current state
                self._handle_vision_event(event)
                
            except Exception as e:
                print(f"⚠️  Vision monitor error: {e}")
                time.sleep(0.1)
    
    def _handle_vision_event(self, event: dict):
        """
        Handle vision events and update agent state
        
        Args:
            event: Vision event dict with state and face info
        """
        vision_state = event.get('state', 'idle')
        
        # State: IDLE - waiting for a face
        if self.agent_state.current_state == AgentState.IDLE:
            if vision_state in ['face_locked', 'locked_tracking']:
                # New face detected and locked!
                locked_face = event.get('locked_face')
                if locked_face:
                    print(f"\n👤 New person detected!")
                    
                    # Transition to FACE_DETECTED
                    self.agent_state.transition(
                        AgentState.FACE_DETECTED,
                        f"Face locked at {locked_face['center']}"
                    )
                    
                    # Then immediately to LOCKED_IN (ready to greet)
                    self.agent_state.lock_face(locked_face['id'])
                    self.agent_state.transition(
                        AgentState.LOCKED_IN,
                        "Ready to initiate conversation"
                    )
                    
                    # Trigger greeting
                    self._send_greeting()
        
        # State: LOCKED_IN or later - person is engaged
        elif self.agent_state.is_locked():
            if vision_state == 'face_lost':
                # Person left!
                print(f"\n👋 Person left the conversation")
                
                # Transition to FACE_LOST
                self.agent_state.transition(
                    AgentState.FACE_LOST,
                    "Face no longer detected"
                )
                
                # Stop listening
                self.stt_worker.pause()
                
                # Reset after timeout
                time.sleep(2.0)
                self.agent_state.reset()
                print("🔄 Ready for next person\n")
            
            elif vision_state in ['face_locked', 'locked_tracking']:
                # Person still here, continue normal operation
                pass
    
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
            'source': 'vision_trigger'  # Mark as vision-initiated
        }
        
        try:
            self.stt_to_llm_queue.put_nowait(greeting_msg)
            print(f"💬 Greeting queued: \"{VISION_CONFIG['greeting_message']}\"")
            
            # Transition to listening after greeting
            self.agent_state.transition(
                AgentState.LISTENING,
                "Waiting for user response"
            )
            
            # Resume STT to listen for response
            self.stt_worker.resume()
            
        except queue.Full:
            print("⚠️  Failed to queue greeting - queue full")
    
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
        
        if self.enable_vision:
            status['queues']['vision_to_orchestrator'] = self.vision_to_orchestrator_queue.qsize()
        
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
        if 'vision_to_orchestrator' in status['queues']:
            queue_str += f", Vision→Orch={status['queues']['vision_to_orchestrator']}"
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
