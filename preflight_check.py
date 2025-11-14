#!/usr/bin/env python3
"""
Pre-Flight Check - Verify system ready for optimization
Run this BEFORE optimize_phase1.py
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def check_item(name, passed, details=""):
    """Print check result"""
    icon = f"{Colors.GREEN}✅" if passed else f"{Colors.RED}❌"
    print(f"{icon} {name}{Colors.ENDC}")
    if details:
        print(f"   {Colors.BLUE}{details}{Colors.ENDC}")
    return passed

def check_python():
    """Check Python version"""
    version = sys.version_info
    passed = version.major == 3 and version.minor >= 11
    details = f"Found: Python {version.major}.{version.minor}.{version.micro}"
    if not passed:
        details += f" (Need: Python 3.11+)"
    return check_item("Python 3.11+", passed, details)

def check_pip():
    """Check pip installation"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True, text=True, check=True
        )
        return check_item("pip", True, result.stdout.strip())
    except:
        return check_item("pip", False, "pip not found or not working")

def check_git():
    """Check git installation"""
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True, text=True, check=True
        )
        return check_item("git", True, result.stdout.strip())
    except:
        return check_item("git", False, "git not installed (optional)")

def check_ollama():
    """Check Ollama installation"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, check=False
        )
        
        if result.returncode == 0:
            models = result.stdout.strip()
            has_qwen = "qwen2.5" in models.lower()
            details = "Ollama running"
            if has_qwen:
                details += " | qwen2.5 found"
            else:
                details += " | Will download qwen2.5"
            return check_item("Ollama", True, details)
        else:
            return check_item("Ollama", False, "Run: ollama serve")
    except FileNotFoundError:
        return check_item("Ollama", False, "Not installed - visit ollama.ai")

def check_disk_space():
    """Check available disk space"""
    try:
        stat = shutil.disk_usage(".")
        free_gb = stat.free / (1024**3)
        passed = free_gb >= 2.0
        details = f"Free space: {free_gb:.1f} GB"
        if not passed:
            details += " (Need: 2GB+)"
        return check_item("Disk space", passed, details)
    except:
        return check_item("Disk space", False, "Could not check")

def check_files():
    """Check required project files"""
    files = [
        "requirements.txt",
        "src/config.py",
        "src/workers/stt_worker.py",
        "src/workers/llm_worker.py",
        "src/workers/tts_worker.py"
    ]
    
    missing = [f for f in files if not Path(f).exists()]
    
    if missing:
        details = f"Missing: {', '.join(missing)}"
        return check_item("Project files", False, details)
    else:
        return check_item("Project files", True, "All required files present")

def check_platform():
    """Check platform (Linux/RPi preferred)"""
    platform = sys.platform
    
    if platform == "linux":
        # Try to detect Raspberry Pi
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()
                if "BCM" in cpuinfo or "Raspberry" in cpuinfo:
                    return check_item("Platform", True, "Raspberry Pi detected")
        except:
            pass
        return check_item("Platform", True, "Linux (CPU governor available)")
    elif platform == "darwin":
        return check_item("Platform", True, "macOS (CPU governor skipped)")
    elif platform == "win32":
        return check_item("Platform", True, "Windows (CPU governor skipped)")
    else:
        return check_item("Platform", False, f"Unknown platform: {platform}")

def check_internet():
    """Check internet connectivity"""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return check_item("Internet", True, "Connected")
    except:
        return check_item("Internet", False, "No connection (needed for downloads)")

def check_dependencies():
    """Check if current dependencies installed"""
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
        
        # Check for key packages
        has_pyaudio = "pyaudio" in requirements
        has_opencv = "opencv" in requirements
        has_whisper = "whisper" in requirements
        
        details = "requirements.txt found"
        if not all([has_pyaudio, has_opencv, has_whisper]):
            details += " (Some packages missing)"
        
        return check_item("Dependencies file", True, details)
    except:
        return check_item("Dependencies file", False, "requirements.txt not found")

def main():
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}🔍 Pluto Pre-Flight Check{Colors.ENDC}")
    print(f"{Colors.BOLD}   Verify system ready for optimization{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    checks = [
        ("System", [
            check_platform,
            check_python,
            check_pip,
            check_git,
        ]),
        ("Services", [
            check_ollama,
        ]),
        ("Resources", [
            check_disk_space,
            check_internet,
        ]),
        ("Project", [
            check_files,
            check_dependencies,
        ])
    ]
    
    all_passed = True
    
    for section, funcs in checks:
        print(f"\n{Colors.BOLD}{section}:{Colors.ENDC}")
        for func in funcs:
            result = func()
            if not result:
                all_passed = False
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ All checks passed! Ready to optimize.{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Next steps:{Colors.ENDC}")
        print(f"  1. python3 optimize_phase1.py")
        print(f"  2. python3 optimize_phase2.py")
        print(f"  3. python3 test_performance.py\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some checks failed!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Action required:{Colors.ENDC}")
        print(f"  • Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print(f"  • Start Ollama: ollama serve")
        print(f"  • Install Python deps: pip3 install -r requirements.txt")
        print(f"\nThen run this check again.\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Cancelled{Colors.ENDC}\n")
        sys.exit(1)
