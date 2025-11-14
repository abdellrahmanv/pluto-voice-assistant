#!/usr/bin/env python3
"""
TTS Cache Manager
Pre-generate and cache common phrases for instant playback
"""

import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

CACHE_DIR = Path("cache/tts")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

COMMON_PHRASES = {
    "greeting": "Hi there! I'm Pluto, how can I help you today?",
    "error": "Sorry, I didn't catch that. Could you repeat that?",
    "goodbye": "Goodbye! Have a great day!",
    "thinking": "Let me think about that for a moment.",
    "busy": "I'm processing something right now. Please wait.",
}

def generate_cache():
    try:
        from config import PIPER_CONFIG
    except ImportError:
        print("Error: Could not import config. Make sure src/config.py exists.")
        return False
    
    print("TTS Cache Generation")
    print("=" * 60)
    
    for name, text in COMMON_PHRASES.items():
        output_file = CACHE_DIR / f"{name}.wav"
        
        cmd = [
            PIPER_CONFIG["piper_binary"],
            "--model", PIPER_CONFIG["model_path"],
            "--output_file", str(output_file)
        ]
        
        print(f"\nGenerating: {name}")
        print(f"  Text: {text}")
        
        try:
            result = subprocess.run(
                cmd, 
                input=text, 
                text=True, 
                capture_output=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                file_size = output_file.stat().st_size if output_file.exists() else 0
                print(f"  Status: OK ({file_size} bytes)")
            else:
                print(f"  Status: FAILED")
                print(f"  Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"  Status: TIMEOUT")
        except Exception as e:
            print(f"  Status: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print("Cache generation complete!")
    print(f"Cache location: {CACHE_DIR.absolute()}")
    
    # List generated files
    cache_files = list(CACHE_DIR.glob("*.wav"))
    if cache_files:
        print(f"\nGenerated {len(cache_files)} files:")
        for f in cache_files:
            size_kb = f.stat().st_size / 1024
            print(f"  - {f.name} ({size_kb:.1f} KB)")
    else:
        print("\nWarning: No cache files generated!")
    
    return True

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
