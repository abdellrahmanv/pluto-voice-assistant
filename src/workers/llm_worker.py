"""
🪐 Project Pluto - LLM Worker
Language Model inference using Ollama + Qwen2.5
"""

import queue
import threading
import time
import requests
from typing import Optional, List, Dict

from config import OLLAMA_CONFIG, WORKER_CONFIG, QUEUE_CONFIG


class LLMWorker:
    """Language Model worker using Ollama"""
    
    def __init__(self, input_queue: queue.Queue, output_queue: queue.Queue, metrics_logger=None, reporter=None):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.metrics = metrics_logger
        self.reporter = reporter
        self.running = False
        self.thread = None
        
        self.conversation_history: List[Dict[str, str]] = []
        self.warmup_complete = False
        self.processing_count = 0
        
        self.api_url = f"{OLLAMA_CONFIG['host']}/api/generate"
        
        print("🧠 LLM Worker initializing...")
    
    def initialize(self):
        """Check Ollama server and model availability"""
        try:
            print(f"   Checking Ollama server at: {OLLAMA_CONFIG['host']}")
            
            response = requests.get(f"{OLLAMA_CONFIG['host']}/api/tags", timeout=5)
            
            if response.status_code != 200:
                print(f"⚠️  Ollama server not responding properly")
                return False
            
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            if OLLAMA_CONFIG['model'] not in model_names:
                print(f"⚠️  Model '{OLLAMA_CONFIG['model']}' not found")
                print(f"   Available models: {model_names}")
                print(f"   Run: ollama pull {OLLAMA_CONFIG['model']}")
                return False
            
            print(f"   Model '{OLLAMA_CONFIG['model']}' ready")
            print("✅ LLM Worker initialized")
            return True
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to Ollama at {OLLAMA_CONFIG['host']}")
            print(f"   Start server with: ollama serve")
            return False
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}")
            return False
    
    def warmup(self):
        """Warmup model with test inference"""
        if not WORKER_CONFIG["warmup_enabled"]:
            self.warmup_complete = True
            return
        
        print("   LLM warmup: Running test inference...")
        start = time.time()
        
        try:
            response = self._generate("Hello", max_tokens=10)
            elapsed = (time.time() - start) * 1000
            print(f"   LLM warmup complete: {elapsed:.0f}ms")
        except Exception as e:
            print(f"⚠️  LLM warmup failed: {e}")
        
        self.warmup_complete = True
    
    def start(self):
        """Start LLM processing thread"""
        if not self.initialize():
            return False
        
        self.warmup()
        
        self.running = True
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()
        print("🧠 LLM Worker started")
        return True
    
    def stop(self):
        """Stop LLM processing"""
        print("🧠 LLM Worker stopping...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=5)
        
        print("✅ LLM Worker stopped")
    
    def _process_queue(self):
        """Main queue processing loop
        
        Processes transcripts from STT worker or vision-triggered greetings.
        Vision-triggered messages have 'source': 'vision_trigger' in metadata.
        """
        while self.running:
            try:
                task = self.input_queue.get(timeout=QUEUE_CONFIG["get_timeout"])
                
                if task['type'] == 'transcript':
                    user_text = task['text']
                    source = task.get('source', 'stt')
                    
                    if source == 'vision_trigger':
                        print(f"   👁️ Vision-triggered greeting: \"{user_text}\"")
                    else:
                        print(f"   🤔 Thinking about: \"{user_text}\"")
                    
                    start_time = time.time()
                    response_text = self._generate(user_text)
                    latency = (time.time() - start_time) * 1000
                    
                    print(f"   💭 Response: \"{response_text}\"")
                    
                    if self.metrics:
                        self.metrics.log_metric('llm', 'latency', latency, 'ms')
                    
                    if self.reporter:
                        self.reporter.log_latency('llm', latency)
                    
                    self.output_queue.put({
                        'type': 'response',
                        'text': response_text,
                        'timestamp': time.time(),
                        'latency_ms': latency
                    })
                    
                    self.conversation_history.append({'role': 'user', 'content': user_text})
                    self.conversation_history.append({'role': 'assistant', 'content': response_text})
                    
                    if len(self.conversation_history) > OLLAMA_CONFIG["max_history"] * 2:
                        self.conversation_history = self.conversation_history[-OLLAMA_CONFIG["max_history"] * 2:]
                    
                    self.processing_count += 1
                
                self.input_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                if self.running:
                    print(f"❌ LLM processing error: {e}")
                    if self.metrics:
                        self.metrics.log_error('llm', 'processing_error', str(e))
    
    def _generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate response from Ollama"""
        try:
            payload = {
                'model': OLLAMA_CONFIG['model'],
                'prompt': prompt,
                'system': OLLAMA_CONFIG['system_prompt'],
                'stream': False,
                'options': {
                    'temperature': OLLAMA_CONFIG['temperature'],
                    'num_predict': max_tokens or OLLAMA_CONFIG['max_tokens']
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=OLLAMA_CONFIG['timeout'])
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.exceptions.Timeout:
            return "I'm thinking too slowly. Please try again."
        except requests.exceptions.RequestException as e:
            print(f"❌ Ollama request failed: {e}")
            return "I encountered an error. Please try again."
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            return "Something went wrong."
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🗑️  Conversation history cleared")
    
    def get_status(self) -> dict:
        """Get worker status"""
        return {
            'name': 'LLM',
            'running': self.running,
            'warmup_complete': self.warmup_complete,
            'processed': self.processing_count,
            'history_length': len(self.conversation_history) // 2,
            'server_reachable': self._check_server()
        }
    
    def _check_server(self) -> bool:
        """Quick server health check"""
        try:
            response = requests.get(f"{OLLAMA_CONFIG['host']}/api/tags", timeout=1)
            return response.status_code == 200
        except:
            return False
