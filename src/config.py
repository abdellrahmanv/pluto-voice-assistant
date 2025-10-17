"""
🪐 Project Pluto - Configuration Management
Centralized settings for voice assistant test architecture
"""

import os
from pathlib import Path
from typing import Dict, Any
import json

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Base project directory
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# AUDIO CONFIGURATION
# ============================================================================

AUDIO_CONFIG = {
    # Recording settings
    "sample_rate": 16000,  # Hz - Vosk requires 16kHz
    "channels": 1,  # Mono audio
    "chunk_size": 4096,  # Samples per buffer
    "format": "int16",  # 16-bit PCM
    
    # Device settings
    "input_device_index": None,  # None = default microphone
    "output_device_index": None,  # None = default speaker
    
    # Voice activity detection (adjusted for better sensitivity)
    "energy_threshold": 300,  # Lowered from 500 - more sensitive
    "silence_threshold": 300,  # Lowered from 500 - detects quieter speech
    "silence_chunks_threshold": 20,  # Reduced from 30 - faster detection
    "silence_duration": 1.0,  # Reduced from 1.5 - faster cutoff
    "min_phrase_duration": 0.3,  # Reduced from 0.5 - capture shorter phrases
    "max_phrase_duration": 20.0,  # Increased from 15 - allow longer sentences
}

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Whisper STT Model (replaced Vosk for better accuracy)
WHISPER_CONFIG = {
    "model_size": "tiny",  # tiny, base, small, medium, large
    "device": "cpu",  # cpu or cuda
    "language": "en",  # Language code (None for auto-detect)
    "task": "transcribe",  # transcribe or translate
    "fp16": False,  # Use FP16 (only works on GPU)
    
    # Decoding options
    "temperature": 0.0,  # Sampling temperature (0 = deterministic)
    "best_of": 5,  # Number of candidates when sampling
    "beam_size": 5,  # Beam size for beam search
    
    # Model info
    "model_info": {
        "tiny": "39M params, ~1GB RAM, ~1s latency, good accuracy",
        "base": "74M params, ~1.5GB RAM, ~1.5s latency, better accuracy",
        "small": "244M params, ~2GB RAM, ~3s latency, best accuracy"
    }
}

# Ollama/Qwen2.5 LLM
OLLAMA_CONFIG = {
    "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
    "model": os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b-instruct-q4_K_M"),
    "timeout": 30.0,  # seconds
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 150,
    "max_history": 5,  # Number of conversation turns to remember
    "stream": False,
    
    "system_prompt": (
        "You are a helpful voice assistant. Give concise, natural responses "
        "suitable for speech output. Keep answers brief (1-3 sentences) unless "
        "specifically asked for more detail."
    ),
}

# Piper TTS Model
PIPER_CONFIG = {
    "piper_binary": str(PROJECT_ROOT / "piper" / "piper"),
    "model_path": str(MODELS_DIR / "en_US-lessac-medium.onnx"),
    "config_path": str(MODELS_DIR / "en_US-lessac-medium.onnx.json"),
    "voice": None,  # Speaker ID (None = default voice)
    "speaker_id": 0,
    "length_scale": 1.0,
    "noise_scale": 0.667,
    "noise_w": 0.8,
    "sample_rate": 22050,
}

# ============================================================================
# QUEUE CONFIGURATION
# ============================================================================

QUEUE_CONFIG = {
    "max_size": 10,
    "timeout": 5.0,
    "get_timeout": 1.0,  # Timeout for queue.get() operations
    "block_on_full": False,
}

# ============================================================================
# WORKER CONFIGURATION
# ============================================================================

WORKER_CONFIG = {
    "startup_timeout": 30.0,
    "shutdown_timeout": 10.0,
    "heartbeat_interval": 5.0,
    
    "max_retries": 3,
    "retry_delay": 1.0,
    "error_recovery_enabled": True,
    
    "warmup_enabled": True,  # Fixed: renamed from enable_warmup
    "warmup_iterations": 3,
    "batch_processing": False,
}

# ============================================================================
# METRICS & LOGGING
# ============================================================================

METRICS_CONFIG = {
    "log_interval": 5.0,
    "csv_flush_interval": 10.0,
    
    "track_latency": True,
    "track_memory": True,
    "track_queue_depth": True,
    "track_error_rate": True,
    
    "max_stt_latency": 1000,  # ms
    "max_llm_latency": 3000,
    "max_tts_latency": 1500,
    "max_total_latency": 5000,
    "max_memory_mb": 4096,
    
    "csv_enabled": True,
    "json_enabled": True,
    "console_enabled": True,
}

LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    
    "file_enabled": True,
    "file_path": str(LOGS_DIR / "pluto.log"),
    "max_bytes": 10 * 1024 * 1024,
    "backup_count": 5,
    
    "console_enabled": True,
    "console_colors": True,
}

# ============================================================================
# ORCHESTRATOR CONFIGURATION
# ============================================================================

ORCHESTRATOR_CONFIG = {
    "conversation_timeout": 60.0,
    "max_concurrent_conversations": 1,
    
    "health_monitoring": True,  # Enable health monitoring
    "memory_monitoring": True,  # Enable memory monitoring
    "queue_monitoring": True,  # Enable queue depth monitoring
    "health_check_enabled": True,
    "health_check_interval": 10.0,
    "worker_timeout": 30.0,
    
    "shutdown_grace_period": 5.0,
    "force_kill_timeout": 10.0,
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_config(section: str) -> Dict[str, Any]:
    """Get configuration section by name"""
    config_map = {
        "audio": AUDIO_CONFIG,
        "whisper": WHISPER_CONFIG,
        "ollama": OLLAMA_CONFIG,
        "piper": PIPER_CONFIG,
        "queue": QUEUE_CONFIG,
        "worker": WORKER_CONFIG,
        "metrics": METRICS_CONFIG,
        "logging": LOGGING_CONFIG,
        "orchestrator": ORCHESTRATOR_CONFIG,
    }
    return config_map.get(section.lower(), {})


def validate_config() -> bool:
    """Validate configuration settings"""
    errors = []
    
    # Whisper model will be downloaded automatically on first use
    # No need to check for model path
    
    if not Path(PIPER_CONFIG["model_path"]).exists():
        errors.append(f"Piper model not found: {PIPER_CONFIG['model_path']}")
    
    # Whisper works with 16kHz audio (same as Vosk)
    if AUDIO_CONFIG["sample_rate"] != 16000:
        errors.append("Audio sample rate must be 16000 Hz for Whisper")
    
    if errors:
        print("⚠️  Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True


def print_config_summary():
    """Print configuration summary"""
    print("\n" + "="*70)
    print("🪐 PROJECT PLUTO - Configuration Summary")
    print("="*70)
    
    print(f"\n📁 Paths:")
    print(f"  Project Root: {PROJECT_ROOT}")
    print(f"  Models Dir:   {MODELS_DIR}")
    print(f"  Logs Dir:     {LOGS_DIR}")
    
    print(f"\n🎤 Audio:")
    print(f"  Sample Rate:  {AUDIO_CONFIG['sample_rate']} Hz")
    print(f"  Channels:     {AUDIO_CONFIG['channels']}")
    
    print(f"\n🤖 Models:")
    print(f"  Whisper: {WHISPER_CONFIG['model_size']} ({WHISPER_CONFIG['model_info'][WHISPER_CONFIG['model_size']]})")
    print(f"  Ollama: {OLLAMA_CONFIG['model']}")
    print(f"  Piper:  {PIPER_CONFIG['model_path']}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    print_config_summary()
    if validate_config():
        print("✅ Configuration valid")
    else:
        print("❌ Configuration has errors")
