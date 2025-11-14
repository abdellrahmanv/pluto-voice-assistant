#!/usr/bin/env python3
"""
Disable Vision/Face Detection in Pluto
Removes camera and face detection features
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
CONFIG_FILE = PROJECT_ROOT / "src" / "config.py"

print("Disabling vision/face detection in Pluto...")

# Read config.py
with open(CONFIG_FILE, 'r') as f:
    config = f.read()

# Find and modify VISION_CONFIG
if "VISION_CONFIG" in config:
    # Add enable_vision: False
    config = re.sub(
        r'VISION_CONFIG\s*=\s*\{',
        'VISION_CONFIG = {\n    "enable_vision": False,',
        config
    )
    
    print("✓ Added enable_vision: False to VISION_CONFIG")

# Save modified config
with open(CONFIG_FILE, 'w') as f:
    f.write(config)

print("✓ Vision features disabled!")
print("\nNow run: python3 src/orchestrator.py")
