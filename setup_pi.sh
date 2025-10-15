#!/bin/bash

# Pluto Voice Assistant - Raspberry Pi Setup Script
# This script automates the installation of Pluto and its dependencies on a Raspberry Pi.

echo "Starting Pluto setup for Raspberry Pi..."

# --- 1. System Update and Dependency Installation ---
echo "Updating package list and installing system dependencies..."
sudo apt-get update
sudo apt-get install -y git python3-pip python3-venv portaudio19-dev espeak-ng

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "Failed to install system dependencies. Please check your internet connection and try again."
    exit 1
fi

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

# --- 5. Final Steps ---
deactivate
echo "-------------------------------------------------"
echo "✅ Pluto setup complete!"
echo "-------------------------------------------------"
echo "To run the assistant, follow these steps:"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Run the main application: python run.py"
echo "-------------------------------------------------"

