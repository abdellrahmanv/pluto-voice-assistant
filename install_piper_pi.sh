#!/bin/bash
# Raspberry Pi Installation Script for Project Pluto
# Installs Piper TTS for ARM64 architecture

set -e

MODEL_NAME="en_US-lessac-medium"
PIPER_VERSION="2023.11.14-2"

echo ""
echo "================================================================="
echo "        PIPER TTS - RASPBERRY PI INSTALLATION                   "
echo "================================================================="
echo ""

# Paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="$PROJECT_ROOT/models"
PIPER_DIR="$PROJECT_ROOT/piper"
TEMP_DIR="$PROJECT_ROOT/temp_downloads"

# Create directories
echo "[*] Creating directories..."
mkdir -p "$MODELS_DIR"
mkdir -p "$PIPER_DIR"
mkdir -p "$TEMP_DIR"
echo "[+] Directories created"

# Detect architecture
ARCH=$(uname -m)
echo ""
echo "[*] Detected architecture: $ARCH"

if [[ "$ARCH" == "aarch64" ]] || [[ "$ARCH" == "arm64" ]]; then
    PIPER_ARCH="aarch64"
elif [[ "$ARCH" == "armv7l" ]]; then
    PIPER_ARCH="armv7l"
else
    echo "[-] Unsupported architecture: $ARCH"
    echo "    Raspberry Pi should be aarch64 or armv7l"
    exit 1
fi

echo "[*] Using Piper build for: linux_$PIPER_ARCH"

# URLs
PIPER_URL="https://github.com/rhasspy/piper/releases/download/$PIPER_VERSION/piper_linux_$PIPER_ARCH.tar.gz"
VOICE_URL_BASE="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"
VOICE_ONNX_URL="$VOICE_URL_BASE/en/en_US/lessac/medium/$MODEL_NAME.onnx"
VOICE_JSON_URL="$VOICE_URL_BASE/en/en_US/lessac/medium/$MODEL_NAME.onnx.json"

# Download Piper binary
echo ""
echo "[*] Downloading Piper binary for Linux $PIPER_ARCH..."
PIPER_TAR="$TEMP_DIR/piper.tar.gz"

if curl -L "$PIPER_URL" -o "$PIPER_TAR"; then
    SIZE=$(du -h "$PIPER_TAR" | cut -f1)
    echo "[+] Piper binary downloaded ($SIZE)"
else
    echo "[-] Failed to download Piper binary"
    echo "    Manual download: $PIPER_URL"
    exit 1
fi

# Extract Piper
echo ""
echo "[*] Extracting Piper..."
tar -xzf "$PIPER_TAR" -C "$TEMP_DIR"

# Find and copy piper directory
if [ -d "$TEMP_DIR/piper" ]; then
    cp -r "$TEMP_DIR/piper/"* "$PIPER_DIR/"
    chmod +x "$PIPER_DIR/piper"
    echo "[+] Piper extracted to: piper/"
    echo "    (includes binary, libs, and espeak-ng-data)"
else
    echo "[-] piper directory not found in archive"
    exit 1
fi

# Download voice model (.onnx)
echo ""
echo "[*] Downloading voice model ($MODEL_NAME.onnx)..."
VOICE_ONNX_PATH="$MODELS_DIR/$MODEL_NAME.onnx"

if curl -L "$VOICE_ONNX_URL" -o "$VOICE_ONNX_PATH"; then
    SIZE=$(du -h "$VOICE_ONNX_PATH" | cut -f1)
    echo "[+] Voice model downloaded ($SIZE)"
else
    echo "[-] Failed to download voice model"
    echo "    Manual download: $VOICE_ONNX_URL"
    exit 1
fi

# Download voice config (.json)
echo ""
echo "[*] Downloading voice config ($MODEL_NAME.onnx.json)..."
VOICE_JSON_PATH="$MODELS_DIR/$MODEL_NAME.onnx.json"

if curl -L "$VOICE_JSON_URL" -o "$VOICE_JSON_PATH"; then
    echo "[+] Voice config downloaded"
else
    echo "[-] Failed to download voice config"
    echo "    Manual download: $VOICE_JSON_URL"
    exit 1
fi

# Cleanup
echo ""
echo "[*] Cleaning up temporary files..."
rm -rf "$TEMP_DIR"
echo "[+] Cleanup complete"

# Test Piper
echo ""
echo "[*] Testing Piper installation..."
if "$PIPER_DIR/piper" --version > /dev/null 2>&1; then
    echo "[+] Piper is working!"
else
    echo "[!] Piper test had issues (may need dependencies)"
    echo "    Install: sudo apt-get install libespeak-ng1"
fi

echo ""
echo "================================================================="
echo ""
echo "[SUCCESS] PIPER TTS INSTALLATION COMPLETE!"
echo ""
echo "Files installed:"
echo "   +- piper/piper              (Piper binary)"
echo "   +- models/$MODEL_NAME.onnx      (Voice model)"
echo "   +- models/$MODEL_NAME.onnx.json (Voice config)"
echo ""
echo "Next steps:"
echo "   1. Run setup script: ./setup_pi.sh"
echo "   2. Or manually install Python packages:"
echo "      python3 -m venv venv"
echo "      source venv/bin/activate"
echo "      pip install -r requirements.txt"
echo ""
echo "================================================================="
echo ""
