"""
Speech-to-Text Worker using OpenAI Whisper
Replaces Vosk with much more accurate Whisper Tiny model
"""

import time
import queue
import threading
import pyaudio
import numpy as np
import wave
import whisper
from pathlib import Path
from typing import Optional

from config import (
    AUDIO_CONFIG,
    WHISPER_CONFIG,
    WORKER_CONFIG,
    QUEUE_CONFIG,
)


class STTWorker:
    """Speech-to-text worker using Whisper"""
    
    def __init__(self, output_queue: queue.Queue, metrics=None):
        self.output_queue = output_queue
        self.metrics = metrics
        
        self.running = False
        self.thread = None
        self.warmup_complete = False
        
        # Audio components
        self.audio = None
        self.stream = None
        self.model = None
        
        # Temp file for audio processing
        self.temp_audio_path = Path("temp_recording.wav")
        
        # Stats
        self.processing_count = 0
    
    def initialize(self) -> bool:
        """Initialize Whisper model and audio"""
        try:
            print(f"   Loading Whisper model: {WHISPER_CONFIG['model_size']}")
            
            # Load Whisper model
            self.model = whisper.load_model(
                WHISPER_CONFIG['model_size'],
                device=WHISPER_CONFIG['device']
            )
            
            print(f"   Whisper model loaded on: {WHISPER_CONFIG['device']}")
            
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            
            # Open audio stream
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=AUDIO_CONFIG['channels'],
                rate=AUDIO_CONFIG['sample_rate'],
                input=True,
                input_device_index=AUDIO_CONFIG['input_device_index'],
                frames_per_buffer=AUDIO_CONFIG['chunk_size']
            )
            
            print(f"   Opening audio input: {AUDIO_CONFIG['sample_rate']}Hz")
            print("✅ STT Worker initialized")
            return True
            
        except Exception as e:
            print(f"❌ STT initialization failed: {e}")
            return False
    
    def warmup(self):
        """Warmup Whisper model"""
        if not WORKER_CONFIG["warmup_enabled"]:
            self.warmup_complete = True
            return
        
        print("   STT warmup: Testing Whisper model...")
        start_time = time.time()
        
        try:
            # Create 1 second of silent audio for warmup
            silent_audio = np.zeros(AUDIO_CONFIG['sample_rate'], dtype=np.float32)
            
            # Run inference
            result = self.model.transcribe(
                silent_audio,
                language=WHISPER_CONFIG['language'],
                task=WHISPER_CONFIG['task'],
                fp16=WHISPER_CONFIG['fp16']
            )
            
            warmup_time = (time.time() - start_time) * 1000
            print(f"   STT warmup complete: {warmup_time:.0f}ms")
            self.warmup_complete = True
            
        except Exception as e:
            print(f"⚠️  STT warmup failed: {e}")
            self.warmup_complete = True  # Continue anyway
    
    def start(self) -> bool:
        """Start the STT worker thread"""
        if not self.initialize():
            return False
        
        self.warmup()
        
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        
        print("🎤 Listening for speech...")
        print("🎤 STT Worker started")
        return True
    
    def stop(self):
        """Stop the STT worker"""
        print("🎤 STT Worker stopping...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=5.0)
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        if self.temp_audio_path.exists():
            self.temp_audio_path.unlink()
        
        print("✅ STT Worker stopped")
    
    def _listen_loop(self):
        """Main listening loop"""
        while self.running:
            try:
                # Detect speech and record
                audio_data = self._record_speech()
                
                if audio_data is not None and audio_data.size > 0:
                    # Transcribe
                    start_time = time.time()
                    text = self._transcribe(audio_data)
                    latency = (time.time() - start_time) * 1000
                    
                    if text and text.strip():
                        print(f"   📝 Recognized: \"{text}\"")
                        print(f"  🎤 STT: {latency:.0f}ms")
                        
                        # Send to LLM queue
                        self.output_queue.put({
                            'type': 'transcript',  # Fixed: changed from 'transcription' to 'transcript'
                            'text': text,
                            'timestamp': time.time()
                        })
                        
                        if self.metrics:
                            self.metrics.log_metric('stt', 'latency', latency, 'ms')
                        
                        self.processing_count += 1
            
            except Exception as e:
                if self.running:
                    print(f"❌ STT processing error: {e}")
                    if self.metrics:
                        self.metrics.log_error('stt', 'processing_error', str(e))
    
    def _record_speech(self) -> Optional[np.ndarray]:
        """Record audio until silence detected"""
        try:
            frames = []
            silent_chunks = 0
            speech_started = False
            total_chunks = 0
            max_chunks = int(AUDIO_CONFIG['max_phrase_duration'] * 
                           AUDIO_CONFIG['sample_rate'] / AUDIO_CONFIG['chunk_size'])
            
            while self.running and total_chunks < max_chunks:
                # Read audio chunk
                data = self.stream.read(AUDIO_CONFIG['chunk_size'], exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                
                # Calculate energy
                energy = np.abs(audio_chunk).mean()
                
                # Check for speech
                if energy > AUDIO_CONFIG['energy_threshold']:
                    if not speech_started:
                        print("🎙️  Speech detected...")
                        speech_started = True
                    
                    frames.append(audio_chunk)
                    silent_chunks = 0
                else:
                    if speech_started:
                        frames.append(audio_chunk)
                        silent_chunks += 1
                        
                        # Check if silence duration exceeded
                        if silent_chunks >= AUDIO_CONFIG['silence_chunks_threshold']:
                            break
                
                total_chunks += 1
            
            if not frames:
                return None
            
            # Combine frames
            audio_data = np.concatenate(frames)
            
            # Check minimum duration
            duration = len(audio_data) / AUDIO_CONFIG['sample_rate']
            if duration < AUDIO_CONFIG['min_phrase_duration']:
                return None
            
            return audio_data
            
        except Exception as e:
            if self.running:
                print(f"❌ Recording error: {e}")
            return None
    
    def _transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio using Whisper"""
        try:
            # Convert int16 to float32 [-1.0, 1.0]
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_float,
                language=WHISPER_CONFIG['language'],
                task=WHISPER_CONFIG['task'],
                fp16=WHISPER_CONFIG['fp16'],
                temperature=WHISPER_CONFIG['temperature'],
                best_of=WHISPER_CONFIG['best_of'],
                beam_size=WHISPER_CONFIG['beam_size']
            )
            
            return result['text'].strip()
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            if self.metrics:
                self.metrics.log_error('stt', 'transcription_error', str(e))
            return ""
