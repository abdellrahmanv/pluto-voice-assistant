#!/usr/bin/env python3
"""
Clean up Pluto project - Remove unnecessary files
Keep only essential files for deployment
"""

import os
from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).parent

# Files to DELETE (debugging, testing, obsolete)
FILES_TO_DELETE = [
    "debug_vision_worker.py",
    "diagnose_camera_hardware.sh",
    "diagnose_vision_system.py",
    "test_camera_cleanup.py",
    "test_vision_startup.py",
    "test_vnc_window.py",
    "fix_vision_startup.py",
    "do_cleanup.py",
    "download_yunet_model.py",
    "reset_camera.sh",
    "add_gui_preview_instructions.txt",
    "VISION_SETUP.md",
]

# Duplicate/redundant docs to DELETE
DOCS_TO_DELETE = [
    "HOW_TO_RUN.md",  # Redundant with QUICKSTART.md
    "QUICK_START_PI.md",  # Redundant with RASPBERRY_PI_SETUP.md
    "RASPBERRY_PI_DEPLOYMENT.md",  # Redundant with RASPBERRY_PI_SETUP.md
    "SIMPLE_ARCHITECTURE_DIAGRAM.md",  # Redundant with AGENT_ARCHITECTURE.md
]

# KEEP these essential files
ESSENTIAL_FILES = [
    # Core scripts
    "run.py",
    "run_nocam.py",
    "setup.py",
    "setup_pi.sh",
    "install_piper_pi.sh",
    "update.sh",
    "verify_install.py",
    
    # Optimization scripts
    "preflight_check.py",
    "optimize_phase1.py",
    "optimize_phase2.py",
    "generate_tts_cache.py",
    "disable_vision.py",
    "test_performance.py",
    
    # Documentation
    "README.md",
    "QUICKSTART.md",
    "DOCUMENTATION.md",
    "AGENT_ARCHITECTURE.md",
    "RASPBERRY_PI_SETUP.md",
    "OPTIMIZATION_GUIDE.md",
    "OPTIMIZATION_SUMMARY.md",
    "README_OPTIMIZATION.md",
    "OPTIMIZATION_COMPLETE.txt",
    
    # Config
    "requirements.txt",
]

def cleanup():
    print("Pluto Project Cleanup")
    print("=" * 60)
    
    deleted = []
    kept = []
    
    # Delete unnecessary files
    all_to_delete = FILES_TO_DELETE + DOCS_TO_DELETE
    
    for filename in all_to_delete:
        filepath = PROJECT_ROOT / filename
        if filepath.exists():
            try:
                if filepath.is_file():
                    filepath.unlink()
                elif filepath.is_dir():
                    shutil.rmtree(filepath)
                deleted.append(filename)
                print(f"✓ Deleted: {filename}")
            except Exception as e:
                print(f"✗ Failed to delete {filename}: {e}")
        else:
            print(f"  Skipped: {filename} (not found)")
    
    # List kept files
    print("\n" + "=" * 60)
    print("KEPT FILES:")
    print("=" * 60)
    
    for filename in ESSENTIAL_FILES:
        filepath = PROJECT_ROOT / filename
        if filepath.exists():
            size = filepath.stat().st_size / 1024
            kept.append((filename, size))
    
    kept.sort()
    for name, size in kept:
        print(f"  {name:40s} ({size:6.1f} KB)")
    
    print("\n" + "=" * 60)
    print(f"Deleted: {len(deleted)} files")
    print(f"Kept: {len(kept)} files")
    print("=" * 60)
    
    print("\nProject structure cleaned!")
    print("Core files: src/, models/, piper/, cache/")
    print("Documentation: README.md, QUICKSTART.md, RASPBERRY_PI_SETUP.md")
    print("Optimization: preflight_check.py → optimize_phase1.py → optimize_phase2.py")

if __name__ == "__main__":
    cleanup()
