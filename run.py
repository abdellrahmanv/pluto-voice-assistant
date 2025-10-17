"""
🪐 Project Pluto - Voice Assistant
Run the complete STT → LLM → TTS pipeline
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orchestrator import main

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                     🪐 PROJECT PLUTO 🪐                          ║
    ║         Vision-Driven Reflex Agent Voice Assistant               ║
    ║                                                                   ║
    ║  Pipeline: Vision → STT → LLM → TTS                              ║
    ║  Behavior: Detects faces, initiates conversation, stays focused  ║
    ║  Models: YuNet + Whisper + Qwen2.5 + Piper                       ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    main()
