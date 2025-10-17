#!/bin/bash

# Pluto Voice Assistant - Raspberry Pi Setup Script
# This script automates the installation of Pluto and its dependencies on a Raspberry Pi.

echo "Starting Pluto setup for Raspberry Pi..."

# --- 1. System Update and Dependency Installation ---
echo "Updating package list and installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    git \
    python3-pip \
    python3-venv \
    python3-dev \
    portaudio19-dev \
    libportaudio2 \
    espeak-ng \
    libespeak-ng1 \
    curl \
    build-essential

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "Failed to install system dependencies. Please check your internet connection and try again."
    exit 1
fi

echo "System dependencies installed successfully."

# --- 2. Create Python Virtual Environment ---
echo "Creating Python virtual environment in '.venv'..."
python3 -m venv .venv

# Check if venv was created
if [ ! -d ".venv" ]; then
    echo "Failed to create Python virtual environment."
    exit 1
fi

# --- 3. Activate Virtual Environment and Install Python Packages ---
echo "Activating virtual environment and installing Python packages from requirements.txt..."
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install packages
pip install -r requirements.txt

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "Failed to install Python packages from requirements.txt. Please check the file and your internet connection."
    deactivate
    exit 1
fi

echo "Python packages installed successfully."

# --- 4. Install Piper TTS (ARM64 Version) ---
echo "Running the Piper TTS installation script..."
chmod +x install_piper_pi.sh
./install_piper_pi.sh

# Check if Piper was installed
if [ ! -f "./piper/piper" ]; then
    echo "Piper TTS installation failed. Please check the output of install_piper_pi.sh."
    deactivate
    exit 1
fi

echo "Piper TTS installed successfully."

# --- 5. Check for Ollama ---
echo ""
echo "Checking for Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    # Check if the model is installed
    if ollama list | grep -q "qwen2.5:0.5b"; then
        echo "✅ Qwen model is installed"
    else
        echo "⚠️  Qwen model not found"
        echo "   Install it with: ollama pull qwen2.5:0.5b-instruct-q4_k_M"
    fi
else
    echo "⚠️  Ollama is NOT installed"
    echo ""
    echo "   To install Ollama, run:"
    echo "   curl -fsSL https://ollama.com/install.sh | sh"
    echo "   ollama pull qwen2.5:0.5b-instruct-q4_k_M"
    echo ""
fi

# --- 6. Final Steps ---
deactivate
echo ""
echo "================================================================="
echo "✅ PLUTO VOICE ASSISTANT SETUP COMPLETE!"
echo "================================================================="
echo ""
echo "📋 What was installed:"
echo "   ✅ System dependencies (Python, PortAudio, espeak-ng)"
echo "   ✅ Python virtual environment (.venv)"
echo "   ✅ Python packages (Whisper, PyAudio, etc.)"
echo "   ✅ Piper TTS (ARM64 version)"
echo "   ✅ Voice model (en_US-lessac-medium)"
echo ""
echo "🚀 To run Pluto:"
echo "   1. Make sure Ollama is running (in another terminal):"
echo "      ollama serve"
echo ""
echo "   2. Activate the virtual environment:"
echo "      source .venv/bin/activate"
echo ""
echo "   3. Start Pluto:"
echo "      python run.py"
echo ""
echo "================================================================="
echo ""

