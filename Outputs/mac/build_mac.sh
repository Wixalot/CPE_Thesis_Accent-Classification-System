#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "Building Accent Classifier Standalone for macOS (.app)"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Set local cache directory to prevent permission errors
export PYINSTALLER_CONFIG_DIR="$SCRIPT_DIR/.pyinstaller"

# 2. Use virtualenv python if present, or system python
if [ -f "../../.myenv/bin/pyinstaller" ]; then
    PYI="../../.myenv/bin/pyinstaller"
else
    PYI="pyinstaller"
fi

echo "[*] Compiling macOS Application Bundle..."
$PYI --noconfirm --clean main.spec

if [ -d "dist/main.app" ]; then
    echo "=========================================================="
    echo "[SUCCESS] macOS app built successfully!"
    echo "App bundle: $SCRIPT_DIR/dist/main.app"
    echo "=========================================================="
else
    echo "[ERROR] Build failed."
    exit 1
fi
