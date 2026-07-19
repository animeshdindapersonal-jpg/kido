# KIDO Installation Guide

## Quick Start

### Option 1: Build from Source (Recommended)

#### Windows
1. Install Python 3.7+ from [python.org](https://python.org)
2. Open Command Prompt in the `kido_sdk` folder
3. Run: `build_windows.bat`
4. Extract `kido-windows.zip`
5. Add the extracted folder to your PATH
6. Open a new Command Prompt and run: `kido version`

#### macOS
1. Install Python 3.7+ (comes pre-installed on macOS)
2. Open Terminal in the `kido_sdk` folder
3. Run: `./build_unix.sh`
4. Extract `kido-macos.tar.gz`
5. Add to PATH: `export PATH=$PATH:/path/to/kido`
6. Run: `kido version`

#### Linux
1. Install Python 3.7+: `sudo apt install python3 python3-pip`
2. Open Terminal in the `kido_sdk` folder
3. Run: `./build_unix.sh`
4. Extract `kido-linux.tar.gz`
5. Add to PATH: `export PATH=$PATH:/path/to/kido`
6. Run: `kido version`

### Option 2: Run from Source (Development)

No build required - run directly from source:

```bash
cd kido_sdk
python3 -m kido_cli.cli version
```

Or create an alias:
```bash
alias kido='python3 /path/to/kido_sdk/kido_cli/cli.py'
```

### Option 3: Install as Python Package

```bash
cd kido_sdk
pip install -e .
```

Then run: `kido version`

## Detailed Instructions

### Windows Installation

1. **Install Python**
   - Download from [python.org/downloads](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify: Open Command Prompt and run `python --version`

2. **Build KIDO**
   ```cmd
   cd kido_sdk
   build_windows.bat
   ```

3. **Install**
   - Extract `kido-windows.zip` to `C:\kido`
   - Add to PATH:
     - Right-click "This PC" → Properties
     - Advanced system settings → Environment Variables
     - Edit PATH → Add `C:\kido`
   - Open new Command Prompt
   - Test: `kido version`

### macOS Installation

1. **Install Python** (if not already installed)
   ```bash
   brew install python3
   ```

2. **Build KIDO**
   ```bash
   cd kido_sdk
   ./build_unix.sh
   ```

3. **Install**
   ```bash
   # Extract
   tar -xzf kido-macos.tar.gz
   sudo mv dist /usr/local/kido
   
   # Add to PATH (add this line to ~/.bash_profile or ~/.zshrc)
   export PATH=$PATH:/usr/local/kido
   
   # Reload shell
   source ~/.bash_profile  # or ~/.zshrc
   
   # Test
   kido version
   ```

### Linux Installation

1. **Install Python**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip
   
   # Fedora
   sudo dnf install python3 python3-pip
   
   # Arch
   sudo pacman -S python python-pip
   ```

2. **Build KIDO**
   ```bash
   cd kido_sdk
   ./build_unix.sh
   ```

3. **Install**
   ```bash
   # Extract
   tar -xzf kido-linux.tar.gz
   sudo mv dist /opt/kido
   
   # Add to PATH (add this line to ~/.bashrc)
   export PATH=$PATH:/opt/kido
   
   # Reload shell
   source ~/.bashrc
   
   # Test
   kido version
   ```

## Verification

After installation, verify KIDO is working:

```bash
kido version
# Should output: 🧒 KIDO v1.0.0 — Ready to code!

kido help
# Should show available commands

# Run a test program
echo 'print "Hello, KIDO!"' > test.kd
kido run test.kd
# Should output: Hello, KIDO!
```

## Troubleshooting

### "kido: command not found"
- Make sure the KIDO directory is in your PATH
- Open a new terminal/command prompt after adding to PATH
- Check PATH: `echo $PATH` (Unix) or `echo %PATH%` (Windows)

### "Python not found"
- Install Python 3.7 or higher
- Make sure Python is in your PATH
- Try `python3` instead of `python` on macOS/Linux

### Build fails
- Make sure you have pip installed: `python -m pip --version`
- Update pip: `python -m pip install --upgrade pip`
- Install requirements manually: `pip install -r requirements.txt`

### Permission denied (Unix)
- Make scripts executable: `chmod +x build_unix.sh build.py`
- Use sudo for system-wide installation: `sudo mv dist /usr/local/kido`

## Uninstallation

### Windows
1. Delete the KIDO folder (e.g., `C:\kido`)
2. Remove from PATH (Environment Variables)

### macOS/Linux
```bash
sudo rm -rf /usr/local/kido  # or /opt/kido
# Remove PATH entry from ~/.bash_profile, ~/.zshrc, or ~/.bashrc
```

## Support

For issues and questions:
- Check the README.md for language documentation
- Review examples in the `examples/` folder
- Run `kido help` for command reference
