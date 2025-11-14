#!/usr/bin/env python3
"""
TTS Cache Manager for Pluto Voice Assistant
Pre-generate and cache common phrases for instant playback
Repository: github.com/abdellrahmanv/pluto-voice-assistant
Raspberry Pi 4B optimized
"""

import subprocess
import sys
from pathlib import Path

# Detect if we're in the pluto-voice-assistant directory
PROJECT_ROOT = Path(__file__).parent
if not (PROJECT_ROOT / "src").exists():
    print("Error: Must run from pluto-voice-assistant directory")
    print(f"Current directory: {PROJECT_ROOT}")
    sys.exit(1)

# Add src to path
sys.path.insert(0, str(PROJECT_ROOT / "src"))

CACHE_DIR = PROJECT_ROOT / "cache" / "tts"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

COMMON_PHRASES = {
    "greeting": "Hi there! I'm Pluto, your voice assistant. How can I help you today?",
    "error": "Sorry, I didn't catch that. Could you repeat that?",
    "goodbye": "Goodbye! Have a great day!",
    "thinking": "Let me think about that for a moment.",
    "busy": "I'm processing something right now. Please wait.",
    "no_face": "I can't see you, but I'm all ears! How can I help?",
    "ready": "Pluto voice assistant is ready!",
}

def generate_cache():
    """Generate TTS cache for Pluto voice assistant on Raspberry Pi"""
    try:
        from config import PIPER_CONFIG
    except ImportError:
        print("Error: Could not import config. Make sure src/config.py exists.")
        print("Run from: ~/pluto-voice-assistant/")
        return False
    
    print("\nPluto Voice Assistant - TTS Cache Generation")
    print("Repository: github.com/abdellrahmanv/pluto-voice-assistant")
    print("=" * 60)
    print(f"Cache location: cache/tts/")
    print("=" * 60)
    
    for name, text in COMMON_PHRASES.items():
        output_file = CACHE_DIR / f"{name}.wav"
        
        piper_bin = Path(PIPER_CONFIG["piper_binary"])
        
        # Ensure piper binary is executable
        if not piper_bin.exists():
            print(f"\nError: Piper binary not found at {piper_bin}")
            continue
        
        cmd = [
            str(piper_bin.absolute()),
            "--model", PIPER_CONFIG["model_path"],
            "--output_file", str(output_file)
        ]
        
        print(f"\nGenerating: {name}")
        print(f"  Text: {text}")
        
        try:
            # Use shell execution for better compatibility
            shell_cmd = f'echo "{text}" | {str(piper_bin.absolute())} --model {PIPER_CONFIG["model_path"]} --output_file {str(output_file)}'
            
            result = subprocess.run(
                shell_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(piper_bin.parent)
            )
            
            if result.returncode == 0 and output_file.exists():
                file_size = output_file.stat().st_size
                print(f"  Status: OK ({file_size} bytes)")
            else:
                print(f"  Status: FAILED")
                if result.stderr:
                    print(f"  Error: {result.stderr}")
                if result.stdout:
                    print(f"  Output: {result.stdout}")
        except subprocess.TimeoutExpired:
            print(f"  Status: TIMEOUT")
        except Exception as e:
            print(f"  Status: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print("Cache generation complete!")
    print(f"Cache location: cache/tts/")
    
    # List generated files
    cache_files = sorted(CACHE_DIR.glob("*.wav"))
    if cache_files:
        print(f"\nGenerated {len(cache_files)} cached phrases:")
        total_size = 0
        for f in cache_files:
            size_kb = f.stat().st_size / 1024
            total_size += size_kb
            print(f"  - {f.name:20s} ({size_kb:6.1f} KB)")
        print(f"\nTotal cache size: {total_size:.1f} KB")
        print("\nThese phrases will now play instantly (0ms) instead of ~200ms!")
        print("Run Pluto to test: python3 src/orchestrator.py")
    else:
        print("\nWarning: No cache files generated!")
        print("Check that Piper is installed and configured correctly.")
    
    return len(cache_files) > 0

if __name__ == "__main__":
    try:
        success = generate_cache()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
