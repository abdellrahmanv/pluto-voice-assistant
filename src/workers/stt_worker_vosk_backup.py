"""
🪐 Project Pluto - STT Worker
Speech-to-Text using Vosk offline recognition
"""

import os
import queue
import threading
import time
import pyaudio
import json
from pathlib import Path
from typing import Optional

from vosk import Model, KaldiRecognizer

from config import AUDIO_CONFIG, VOSK_CONFIG, WORKER_CONFIG, QUEUE_CONFIG


class STTWorker:
    """Speech-to-Text worker using Vosk"""
    
    def __init__(self, output_queue: queue.Queue, metrics_logger=None):
        self.output_queue = output_queue
        self.metrics = metrics_logger
        self.running = False
        self.thread = None
        
        self.audio = None
        self.stream = None
        self.model = None
        self.recognizer = None
        
        self.warmup_complete = False
        self.processing_count = 0
        
        print("🎤 STT Worker initializing...")
    
    def initialize(self):
        """Load Vosk model and initialize audio"""
        try:
            model_path = VOSK_CONFIG["model_path"]
            
            if not Path(model_path).exists():
                print(f"⚠️  Vosk model not found at: {model_path}")
                print(f"   Download model from: https://alphacephei.com/vosk/models")
                print(f"   Extract to: {model_path}")
                raise FileNotFoundError(f"Vosk model not found: {model_path}")
            
            print(f"   Loading Vosk model from: {model_path}")
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, VOSK_CONFIG["sample_rate"])
            
            self.audio = pyaudio.PyAudio()
            
            print(f"   Opening audio input: {AUDIO_CONFIG['sample_rate']}Hz")
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=AUDIO_CONFIG["channels"],
                rate=AUDIO_CONFIG["sample_rate"],
                input=True,
                frames_per_buffer=AUDIO_CONFIG["chunk_size"]
            )
            
            print("✅ STT Worker initialized")
            return True
            
        except Exception as e:
            print(f"❌ STT initialization failed: {e}")
            return False
    
    def warmup(self):
        """Warmup recognition engine"""
        if not WORKER_CONFIG["warmup_enabled"]:
            self.warmup_complete = True
            return
        
        print("   STT warmup: Processing silent audio...")
        start = time.time()
        
        silent_audio = b'\x00\x00' * AUDIO_CONFIG["chunk_size"]
        
        for _ in range(10):
            self.recognizer.AcceptWaveform(silent_audio)
        
        elapsed = (time.time() - start) * 1000
        print(f"   STT warmup complete: {elapsed:.0f}ms")
        self.warmup_complete = True
    
    def start(self):
        """Start STT processing thread"""
        if not self.initialize():
            return False
        
        self.warmup()
        
        self.running = True
        self.thread = threading.Thread(target=self._process_audio, daemon=True)
        self.thread.start()
        print("🎤 STT Worker started")
        return True
    
    def stop(self):
        """Stop STT processing"""
        print("🎤 STT Worker stopping...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2)
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        print("✅ STT Worker stopped")
    
    def _process_audio(self):
        """Main audio processing loop"""
        print("🎤 Listening for speech...")
        
        silence_chunks = 0
        speech_started = False
        audio_buffer = []
        
        while self.running:
            try:
                data = self.stream.read(AUDIO_CONFIG["chunk_size"], exception_on_overflow=False)
                
                is_speech = self._detect_speech(data)
                
                if is_speech:
                    silence_chunks = 0
                    if not speech_started:
                        speech_started = True
                        print("🎙️  Speech detected...")
                    audio_buffer.append(data)
                else:
                    if speech_started:
                        silence_chunks += 1
                        audio_buffer.append(data)
                        
                        if silence_chunks >= AUDIO_CONFIG["silence_chunks_threshold"]:
                            self._process_speech(audio_buffer)
                            audio_buffer = []
                            speech_started = False
                            silence_chunks = 0
                
            except Exception as e:
                if self.running:
                    print(f"❌ STT processing error: {e}")
                    if self.metrics:
                        self.metrics.log_error('stt', 'processing_error', str(e))
    
    def _detect_speech(self, audio_data: bytes) -> bool:
        """Simple voice activity detection based on energy"""
        import audioop
        energy = audioop.rms(audio_data, 2)
        return energy > AUDIO_CONFIG["energy_threshold"]
    
    def _process_speech(self, audio_buffer: list):
        """Process captured speech"""
        start_time = time.time()
        
        try:
            for chunk in audio_buffer:
                self.recognizer.AcceptWaveform(chunk)
            
            result = self.recognizer.FinalResult()
            result_dict = json.loads(result)
            text = result_dict.get('text', '').strip()
            
            if text:
                latency = (time.time() - start_time) * 1000
                
                print(f"   📝 Recognized: \"{text}\"")
                
                if self.metrics:
                    self.metrics.log_metric('stt', 'latency', latency, 'ms')
                
                self.output_queue.put({
                    'type': 'transcript',
                    'text': text,
                    'timestamp': time.time(),
                    'latency_ms': latency
                })
                
                self.processing_count += 1
            
            self.recognizer.Reset()
            
        except Exception as e:
            print(f"❌ Speech processing error: {e}")
            if self.metrics:
                self.metrics.log_error('stt', 'recognition_error', str(e))
    
    def get_status(self) -> dict:
        """Get worker status"""
        return {
            'name': 'STT',
            'running': self.running,
            'warmup_complete': self.warmup_complete,
            'processed': self.processing_count,
            'model_loaded': self.model is not None,
            'stream_active': self.stream is not None and self.stream.is_active()
        }
