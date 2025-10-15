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
    ║            Offline Voice Assistant Test Architecture             ║
    ║                                                                   ║
    ║  Pipeline: Vosk (STT) → Qwen2.5 (LLM) → Piper (TTS)             ║
    ║  Purpose: Validate integration logic and measure performance     ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    main()
