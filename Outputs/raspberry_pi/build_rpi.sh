#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "Building Accent Classifier Standalone for Raspberry Pi OS"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Install required system audio libraries for PortAudio and Tkinter
echo "[*] Checking and installing system dependencies (PortAudio, Tkinter)..."
sudo apt-get update
sudo apt-get install -y libportaudio2 libasound2-dev libsndfile1 python3-tk python3-venv

# 2. Set up virtual environment
if [ ! -d ".build_env" ]; then
    echo "[*] Creating build virtual environment..."
    python3 -m venv .build_env
fi

echo "[*] Activating build virtual environment..."
source .build_env/bin/activate

echo "[*] Installing Python packages and PyInstaller..."
pip install --upgrade pip
pip install -r ../../requirements.txt pyinstaller

# 3. Compile standalone Linux ARM binary
echo "[*] Compiling standalone executable with PyInstaller..."
export PYINSTALLER_CONFIG_DIR="$SCRIPT_DIR/.pyinstaller"
pyinstaller --noconfirm --clean main_rpi.spec

if [ -f "dist/AccentClassifier" ]; then
    chmod +x dist/AccentClassifier
    echo "=========================================================="
    echo "[SUCCESS] Raspberry Pi binary built successfully!"
    echo "Executable location: $SCRIPT_DIR/dist/AccentClassifier"
    echo "To launch: ./dist/AccentClassifier"
    echo "=========================================================="
else
    echo "[ERROR] Build failed. Check the output above."
    exit 1
fi
