"""
Quick verification that all Python packages are installed correctly
"""

print("🔍 Checking Python dependencies for Project Pluto...\n")

required_packages = {
    'vosk': 'Vosk (STT)',
    'pyaudio': 'PyAudio (Audio I/O)',
    'requests': 'Requests (HTTP client)',
    'psutil': 'psutil (System monitoring)',
    'numpy': 'NumPy (Numerical operations)',
    'scipy': 'SciPy (Audio processing)',
    'pytest': 'pytest (Testing)',
}

all_installed = True

for package, description in required_packages.items():
    try:
        __import__(package)
        print(f"✅ {description:30} - OK")
    except ImportError:
        print(f"❌ {description:30} - NOT INSTALLED")
        all_installed = False

print()

if all_installed:
    print("🎉 All required packages are installed!")
    print("\nNext steps:")
    print("1. Download models (Vosk, Piper, Qwen2.5)")
    print("2. Start Ollama server: ollama serve")
    print("3. Run Pluto: python run.py")
else:
    print("⚠️  Some packages are missing. Install with:")
    print("   pip install -r requirements.txt")

print()
