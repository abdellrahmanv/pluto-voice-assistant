"""
🪐 Project Pluto - Voice-Only Assistant (No Camera)
Run STT → LLM → TTS pipeline without vision

This mode runs Pluto as a pure voice assistant:
- No camera/face detection
- Always listening for voice commands
- Same conversational AI capabilities
- Lower resource usage
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orchestrator import PlutoOrchestrator

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                  🎙️  PLUTO VOICE-ONLY MODE 🎙️                ║
    ║        Voice Assistant Without Camera (STT→LLM→TTS)          ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  Pipeline: Microphone → STT → LLM → TTS → Speaker            ║
    ║  Mode: Always listening (no face detection required)          ║
    ║  Models: Whisper + Qwen2.5 + Piper                           ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize orchestrator with vision disabled
    orchestrator = PlutoOrchestrator(enable_vision=False)
    
    try:
        print("\n🎙️  Voice-only mode starting...")
        print("   Just start talking - I'm always listening!\n")
        
        if orchestrator.start():
            # Keep running until interrupted
            import time
            while orchestrator.running:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏸️  Shutting down voice assistant...")
    finally:
        orchestrator.stop()
        print("✅ Voice assistant stopped. Goodbye!\n")
