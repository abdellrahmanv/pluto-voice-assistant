#!/usr/bin/env python3
"""
Completely remove vision/camera functionality from Pluto
Makes it a pure voice assistant
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

def remove_vision_from_orchestrator():
    """Remove all vision code from orchestrator.py"""
    file_path = PROJECT_ROOT / "src" / "orchestrator.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove vision import
    content = re.sub(r'from workers\.vision_worker import VisionWorker\n', '', content)
    content = re.sub(r'from config import.*VISION_CONFIG.*\n', 
                    'from config import QUEUE_CONFIG, ORCHESTRATOR_CONFIG, print_config_summary\n', content)
    
    # Change docstring
    content = content.replace('Main coordinator for 4-worker reflex agent (STT, LLM, TTS, Vision)', 
                            'Main coordinator for 3-worker voice assistant (STT, LLM, TTS)')
    content = content.replace('Main orchestrator coordinating STT → LLM → TTS + Vision reflex agent',
                            'Main orchestrator coordinating STT → LLM → TTS voice assistant')
    
    # Remove enable_vision parameter and all vision initialization
    content = re.sub(r'def __init__\(self, enable_vision=True\):', 'def __init__(self):', content)
    content = re.sub(r'\s+enable_vision: Enable vision worker.*\n', '', content)
    content = re.sub(r'\s+self\.vision_to_orchestrator_queue = .*\n', '', content)
    content = re.sub(r'\s+# Vision worker.*\n', '', content)
    content = re.sub(r'\s+self\.enable_vision = .*\n', '', content)
    content = re.sub(r'\s+self\.vision_worker = .*\n', '', content)
    
    # Remove vision worker initialization block
    vision_init_pattern = r'\s+if self\.enable_vision:.*?else:\s+self\.workers = \[self\.stt_worker, self\.llm_worker, self\.tts_worker\]'
    content = re.sub(vision_init_pattern, '\n        self.workers = [self.stt_worker, self.llm_worker, self.tts_worker]', 
                    content, flags=re.DOTALL)
    
    # Remove vision monitor thread
    content = re.sub(r'\s+self\.vision_monitor_thread = None\n', '', content)
    
    # Remove vision startup code
    content = re.sub(r'\s+# Start vision worker.*?\n.*?all_ok = False\n', '', content, flags=re.DOTALL)
    content = re.sub(r'\s+# Start vision event monitor.*?\n.*?self\.vision_monitor_thread\.start\(\)\n', '', content, flags=re.DOTALL)
    
    # Remove vision ready message
    content = re.sub(r'\s+if self\.enable_vision:\s+print.*?\n.*?else:\s+print', '        print', content, flags=re.DOTALL)
    content = content.replace('👁️  PLUTO IS READY - Looking for people to talk to!', '🎤 PLUTO IS READY - Voice assistant active!')
    content = content.replace('With Vision-Driven Interaction', 'Pure Voice Assistant')
    
    # Remove entire vision event monitor method
    content = re.sub(r'\s+def _vision_event_monitor\(self\):.*?time\.sleep\(0\.1\)\n', '', content, flags=re.DOTALL)
    
    # Remove handle vision event method
    content = re.sub(r'\s+def _handle_vision_event\(self, event: dict\):.*?self\.agent_state\.transition_to\(AgentState\.LISTENING\)\n', '', content, flags=re.DOTALL)
    
    # Remove vision queue from status
    content = re.sub(r"\s+if self\.enable_vision:.*?self\.vision_to_orchestrator_queue\.qsize\(\)\n", '', content, flags=re.DOTALL)
    content = re.sub(r"\s+if 'vision_to_orchestrator' in status.*?\n", '', content)
    content = re.sub(r", Vision→Orch=\{status\['queues'\]\['vision_to_orchestrator'\]\}", '', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Removed vision from orchestrator.py")

def remove_vision_from_config():
    """Remove vision config and checks"""
    file_path = PROJECT_ROOT / "src" / "config.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove VISION_CONFIG entirely
    content = re.sub(r'# Vision/Face Detection.*?}\n', '', content, flags=re.DOTALL)
    
    # Remove vision from CONFIG dict
    content = re.sub(r'\s+"vision": VISION_CONFIG,\n', '', content)
    
    # Remove vision model check
    content = re.sub(r'\s+# Vision model check.*?\n.*?\n.*?\n', '', content, flags=re.DOTALL)
    
    # Remove YuNet print statement
    content = re.sub(r'\s+print\(f"  YuNet:.*?\n', '', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Removed vision from config.py")

def delete_vision_worker():
    """Delete vision_worker.py entirely"""
    file_path = PROJECT_ROOT / "src" / "workers" / "vision_worker.py"
    
    if file_path.exists():
        file_path.unlink()
        print("✓ Deleted vision_worker.py")
    else:
        print("  vision_worker.py already deleted")

def update_readme():
    """Update README to reflect voice-only assistant"""
    file_path = PROJECT_ROOT / "README.md"
    
    if not file_path.exists():
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('face detection', 'voice interaction')
    content = content.replace('vision', 'voice')
    content = content.replace('Vision', 'Voice')
    content = content.replace('camera', 'microphone')
    content = content.replace('Camera', 'Microphone')
    content = re.sub(r'YuNet.*?\n', '', content)
    content = re.sub(r'face_detection.*?\n', '', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Updated README.md")

def main():
    print("\n" + "="*60)
    print("Removing ALL vision/camera functionality from Pluto")
    print("Making it a pure voice assistant")
    print("="*60 + "\n")
    
    remove_vision_from_orchestrator()
    remove_vision_from_config()
    delete_vision_worker()
    update_readme()
    
    print("\n" + "="*60)
    print("✓ Vision removal complete!")
    print("="*60)
    print("\nPluto is now a VOICE-ONLY assistant:")
    print("  - No camera required")
    print("  - No face detection")
    print("  - Pure STT → LLM → TTS pipeline")
    print("\nCommit and push these changes to GitHub.")

if __name__ == "__main__":
    main()
