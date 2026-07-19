#!/bin/bash

echo "============================================================"
echo "KIDO SDK Builder for macOS/Linux"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.7 or higher."
    exit 1
fi

echo "Installing build dependencies..."
python3 -m pip install --upgrade pip > /dev/null 2>&1
python3 -m pip install -r requirements.txt > /dev/null 2>&1

echo ""
echo "Building KIDO executable..."
python3 build.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed!"
    exit 1
fi

echo ""
echo "============================================================"
echo "Build complete!"
echo "============================================================"
echo ""
echo "To install KIDO:"
echo "  1. Extract the archive (kido-macos.tar.gz or kido-linux.tar.gz)"
echo "  2. Add the folder to your PATH:"
echo "     export PATH=\$PATH:/path/to/kido"
echo "  3. Run: kido version"
echo ""
