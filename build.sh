#!/bin/bash
# --------------------------------------------------------------
# Build ChatBot.app for macOS
# Usage:  ./build.sh
# --------------------------------------------------------------
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building ChatBot for macOS..."
echo "---------------------------------"

# Activate venv
source venv/bin/activate

# Clean previous builds
rm -rf build dist

# Build with PyInstaller
echo "Running PyInstaller..."
pyinstaller build_macos.spec --noconfirm

# Copy config.json next to the .app (user-editable)
cp config.json dist/ChatBot.app/../config.json 2>/dev/null || true

echo ""
echo "---------------------------------"
echo "Build complete!"
echo ""
echo "App location:"
echo "   $SCRIPT_DIR/dist/ChatBot.app"
echo ""
echo "To run:"
echo "   open dist/ChatBot.app"
echo ""
echo "To install:"
echo "   1. Copy dist/ChatBot.app to /Applications/"
echo "   2. Or drag ChatBot.app into the Applications folder"
echo ""
echo "First launch: macOS may block it."
echo "   Go to System Settings -> Privacy & Security -> Open Anyway"
echo "---------------------------------"
