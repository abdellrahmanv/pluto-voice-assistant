"""
🪐 Project Pluto - TTS Worker
Text-to-Speech using Piper neural synthesis
"""

import os
import queue
import threading
import time
import wave
import subprocess
import pyaudio
from pathlib import Path
from typing import Optional

from config import AUDIO_CONFIG, PIPER_CONFIG, WORKER_CONFIG, QUEUE_CONFIG


class TTSWorker:
    """Text-to-Speech worker using Piper"""
    
    def __init__(self, input_queue: queue.Queue, metrics_logger=None):
        self.input_queue = input_queue
        self.metrics = metrics_logger
        self.running = False
        self.thread = None
        
        self.audio = None
        self.warmup_complete = False
        self.processing_count = 0
        
        self.temp_wav_path = Path("temp_tts.wav")
        
        print("🔊 TTS Worker initializing...")
    
    def initialize(self):
        """Check Piper installation and model"""
        try:
            model_path = Path(PIPER_CONFIG["model_path"])
            
            if not model_path.exists():
                print(f"⚠️  Piper model not found at: {model_path}")
                print(f"   Download model from: https://github.com/rhasspy/piper/releases")
                print(f"   Example: en_US-lessac-medium.onnx")
                raise FileNotFoundError(f"Piper model not found: {model_path}")
            
            print(f"   Piper model found: {model_path}")
            print(f"   Piper binary: {PIPER_CONFIG['piper_binary']}")
            
            # Verify Piper binary exists
            if not Path(PIPER_CONFIG["piper_binary"]).exists():
                print(f"⚠️  Piper binary not found")
                print(f"   Install from: https://github.com/rhasspy/piper")
                return False
            
            print(f"   Piper binary ready")
            
            self.audio = pyaudio.PyAudio()
            
            print("✅ TTS Worker initialized")
            return True
            
        except FileNotFoundError:
            print(f"❌ Piper binary not found: {PIPER_CONFIG['piper_binary']}")
            print(f"   Install Piper and set correct path in config")
            return False
        except Exception as e:
            print(f"❌ TTS initialization failed: {e}")
            return False
    
    def warmup(self):
        """Warmup TTS engine"""
        if not WORKER_CONFIG["warmup_enabled"]:
            self.warmup_complete = True
            return
        
        print("   TTS warmup: Synthesizing test audio...")
        start = time.time()
        
        try:
            self._synthesize("Warmup test.", play=False)
            elapsed = (time.time() - start) * 1000
            print(f"   TTS warmup complete: {elapsed:.0f}ms")
        except Exception as e:
            print(f"⚠️  TTS warmup failed: {e}")
        
        if self.temp_wav_path.exists():
            self.temp_wav_path.unlink()
        
        self.warmup_complete = True
    
    def start(self):
        """Start TTS processing thread"""
        if not self.initialize():
            return False
        
        self.warmup()
        
        self.running = True
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()
        print("🔊 TTS Worker started")
        return True
    
    def stop(self):
        """Stop TTS processing"""
        print("🔊 TTS Worker stopping...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2)
        
        if self.audio:
            self.audio.terminate()
        
        if self.temp_wav_path.exists():
            self.temp_wav_path.unlink()
        
        print("✅ TTS Worker stopped")
    
    def _process_queue(self):
        """Main queue processing loop"""
        while self.running:
            try:
                task = self.input_queue.get(timeout=QUEUE_CONFIG["get_timeout"])
                
                if task['type'] == 'response':
                    response_text = task['text']
                    print(f"   🗣️  Speaking: \"{response_text}\"")
                    
                    start_time = time.time()
                    success = self._synthesize(response_text, play=True)
                    
                    if success:
                        latency = (time.time() - start_time) * 1000
                        
                        if self.metrics:
                            self.metrics.log_metric('tts', 'latency', latency, 'ms')
                        
                        self.processing_count += 1
                
                self.input_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                if self.running:
                    print(f"❌ TTS processing error: {e}")
                    if self.metrics:
                        self.metrics.log_error('tts', 'processing_error', str(e))
    
    def _synthesize(self, text: str, play: bool = True) -> bool:
        """Synthesize speech using Piper"""
        try:
            cmd = [
                PIPER_CONFIG["piper_binary"],
                "--model", PIPER_CONFIG["model_path"],
                "--output_file", str(self.temp_wav_path)
            ]
            
            if PIPER_CONFIG["voice"]:
                cmd.extend(["--speaker", str(PIPER_CONFIG["voice"])])
            
            result = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"❌ Piper synthesis failed:")
                print(f"   Return code: {result.returncode}")
                print(f"   STDERR: {result.stderr}")
                print(f"   STDOUT: {result.stdout}")
                print(f"   Command: {' '.join(cmd)}")
                return False
            
            if play and self.temp_wav_path.exists():
                self._play_wav(self.temp_wav_path)
            
            return True
            
        except subprocess.TimeoutExpired:
            print(f"❌ TTS synthesis timeout")
            return False
        except Exception as e:
            print(f"❌ Synthesis error: {e}")
            if self.metrics:
                self.metrics.log_error('tts', 'synthesis_error', str(e))
            return False
    
    def _play_wav(self, wav_path: Path):
        """Play WAV file through PyAudio"""
        try:
            wf = wave.open(str(wav_path), 'rb')
            
            stream = self.audio.open(
                format=self.audio.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )
            
            chunk_size = 1024
            data = wf.readframes(chunk_size)
            
            while data and self.running:
                stream.write(data)
                data = wf.readframes(chunk_size)
            
            stream.stop_stream()
            stream.close()
            wf.close()
            
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            if self.metrics:
                self.metrics.log_error('tts', 'playback_error', str(e))
    
    def get_status(self) -> dict:
        """Get worker status"""
        return {
            'name': 'TTS',
            'running': self.running,
            'warmup_complete': self.warmup_complete,
            'processed': self.processing_count,
            'model_exists': Path(PIPER_CONFIG["model_path"]).exists(),
            'piper_available': self._check_piper()
        }
    
    def _check_piper(self) -> bool:
        """Quick Piper availability check"""
        try:
            result = subprocess.run(
                [PIPER_CONFIG["piper_binary"], "--version"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
