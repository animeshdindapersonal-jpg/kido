# 🚀 KIDO Quick Start Guide

## What You Have

The `kido_sdk` folder contains:
- ✅ **Complete KIDO language implementation** (100% working, 100/100 tests passing)
- ✅ **Pre-built executable** (`dist/kido` or `dist/kido.exe`)
- ✅ **50 example programs** demonstrating all features
- ✅ **Build system** to create standalone executables
- ✅ **Installers** for Windows, macOS, and Linux

## Quick Test (No Installation)

Test the pre-built executable immediately:

```bash
cd kido_sdk

# Check version
./dist/kido version

# Run an example
./dist/kido run examples/hello.kd

# Create a new project
./dist/kido new myproject
cd myproject
# Edit main.kd with your code
../dist/kido run main.kd
```

## Installation Options

### Option 1: Quick Install (Linux/macOS)

```bash
cd kido_sdk
chmod +x install.sh
sudo ./install.sh
```

Then open a new terminal and run: `kido version`

### Option 2: Quick Install (Windows)

```cmd
cd kido_sdk
install.bat
```

Follow the prompts, then open a new Command Prompt and run: `kido version`

### Option 3: Manual Install (Any Platform)

1. Copy `dist/kido` (or `dist/kido.exe`) to a folder in your PATH
2. Open a new terminal/command prompt
3. Run: `kido version`

### Option 4: Build from Source

If you want to rebuild the executable:

**Linux/macOS:**
```bash
cd kido_sdk
chmod +x build_unix.sh
./build_unix.sh
```

**Windows:**
```cmd
cd kido_sdk
build_windows.bat
```

## File Structure

```
kido_sdk/
├── dist/                      # Pre-built executables
│   ├── kido                   # Linux/macOS executable
│   ├── kido.exe              # Windows executable (after building)
│   └── examples/             # Example programs
├── kido_core/                # Language implementation
│   ├── lexer.py              # Tokenizer
│   ├── parser.py             # Parser
│   ├── interpreter.py        # Executor
│   ├── environment.py        # Variable scope
│   └── errors.py             # Error handling
├── kido_cli/                 # Command-line interface
│   └── cli.py                # CLI commands
├── examples/                 # 50 example programs
│   ├── hello.kd              # Hello World
│   ├── calculator.kd         # Calculator
│   ├── report_card.kd        # Student report card
│   └── ... (47 more)
├── stress_tests/             # 50 stress test programs
├── tests/                    # Test suite (100 tests)
├── build.py                  # Build script
├── build_unix.sh            # Unix build script
├── build_windows.bat        # Windows build script
├── install.sh               # Unix installer
├── install.bat              # Windows installer
├── INSTALL.md               # Detailed installation guide
├── README.md                # Language documentation
└── requirements.txt         # Python dependencies
```

## Your First KIDO Program

1. **Create a new file:** `hello.kd`

```kido
print "Hello, World!"
ask "What is your name?" name
print "Welcome to KIDO," name "!"
```

2. **Run it:**

```bash
kido run hello.kd
```

3. **Output:**

```
Hello, World!
What is your name? Alice
Welcome to KIDO, Alice!
```

## Available Commands

```bash
kido version              # Show version
kido help                 # Show help
kido run <file.kd>        # Run a program
kido check <file.kd>      # Check for errors
kido new <project>        # Create new project
kido shell                # Interactive REPL
```

## Language Features

KIDO supports:
- ✅ Variables and constants
- ✅ Functions (with recursion)
- ✅ Lists and dictionaries
- ✅ Loops (repeat, for each)
- ✅ Conditionals (if/else)
- ✅ String operations
- ✅ File I/O
- ✅ Error handling (try/catch)
- ✅ Math functions
- ✅ And much more!

See `README.md` for complete language documentation.

## Example Programs

Try these examples:

```bash
# Hello World
kido run examples/hello.kd

# Calculator
kido run examples/calculator.kd

# Student Report Card
kido run examples/report_card.kd

# Number Guessing Game
kido run examples/guessing_game.kd

# Shopping List
kido run examples/shopping_list.kd
```

## Troubleshooting

### "kido: command not found"
- Make sure the KIDO folder is in your PATH
- Open a new terminal/command prompt after installation
- Or use the full path: `./dist/kido run file.kd`

### "Permission denied" (Linux/macOS)
```bash
chmod +x dist/kido
chmod +x install.sh
```

### Build fails
```bash
# Install dependencies
pip install -r requirements.txt

# Try building again
python3 build.py
```

## Next Steps

1. **Read the documentation:** `README.md`
2. **Try the examples:** `examples/` folder
3. **Write your own programs:** Start with simple scripts
4. **Learn the language:** Experiment with different features
5. **Build something cool:** Games, utilities, tools!

## Support

- **Documentation:** README.md, INSTALL.md
- **Examples:** examples/ folder (50 programs)
- **Tests:** tests/ folder (100 tests)
- **Help command:** `kido help`

---

**🧒 KIDO: Real code. Real syntax. Ridiculously easy.**

Happy coding!
