#!/bin/bash

echo "============================================================"
echo "🧒 KIDO Installer for Linux/macOS"
echo "============================================================"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "This installer needs root privileges to install system-wide."
    echo "Please run with sudo: sudo ./install.sh"
    echo ""
    echo "Or install for current user only (no sudo needed):"
    echo "  ./install.sh --user"
    exit 1
fi

# Check for --user flag
USER_INSTALL=false
if [ "$1" = "--user" ]; then
    USER_INSTALL=true
    echo "Installing for current user only..."
else
    echo "Installing system-wide..."
fi

# Check if build exists
if [ ! -f "dist/kido" ]; then
    echo "ERROR: KIDO executable not found in dist/"
    echo "Please run build_unix.sh first to build KIDO."
    exit 1
fi

# Determine installation directory
if [ "$USER_INSTALL" = true ]; then
    INSTALL_DIR="$HOME/.local/bin/kido"
    mkdir -p "$HOME/.local/bin"
else
    INSTALL_DIR="/usr/local/bin/kido"
fi

echo ""
echo "Installing KIDO to: $INSTALL_DIR"

# Create installation directory
if [ "$USER_INSTALL" = true ]; then
    mkdir -p "$INSTALL_DIR"
else
    mkdir -p "$INSTALL_DIR"
fi

# Copy executable
cp dist/kido "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/kido"

# Copy examples
if [ -d "examples" ]; then
    cp -r examples "$INSTALL_DIR/"
    echo "✅ Examples installed to $INSTALL_DIR/examples"
fi

# Copy README
if [ -f "README.md" ]; then
    cp README.md "$INSTALL_DIR/"
fi

echo "✅ KIDO executable installed"

# Add to PATH if not already there
if [ "$USER_INSTALL" = true ]; then
    SHELL_RC="$HOME/.bashrc"
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    
    if ! grep -q "$HOME/.local/bin" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# KIDO Programming Language" >> "$SHELL_RC"
        echo "export PATH=\$PATH:$HOME/.local/bin/kido" >> "$SHELL_RC"
        echo "✅ Added to PATH in $SHELL_RC"
        echo ""
        echo "Please run: source $SHELL_RC"
    fi
fi

echo ""
echo "============================================================"
echo "✅ Installation complete!"
echo "============================================================"
echo ""
echo "To use KIDO:"
echo "  kido version     - Check version"
echo "  kido help        - Show help"
echo "  kido run file.kd - Run a KIDO program"
echo ""
echo "Try it now:"
echo "  kido version"
echo ""
