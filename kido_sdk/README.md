# 🧒 KIDO — A Real Programming Language for Kids

### *"Real code. Real syntax. Ridiculously easy."*

KIDO is a **real, text-based programming language** designed so that even a 6-year-old can learn to code. Kids type `.kd` files and run them from the terminal — just like real programmers.

---

## 🚀 Quick Start

```bash
# Install
chmod +x install.sh && sudo ./install.sh

# Create your first project
kido new my_project

# Run it
kido run my_project/main.kd
```

### Your First Program (`hello.kd`)

```
print "Hello World!"
ask "What is your name?" name
print "Hi" name "!"
```

```bash
$ kido run hello.kd
Hello World!
What is your name? Aarav
Hi Aarav !
```

---

## 📖 Language in 60 Seconds

| I want to... | KIDO Code |
|---|---|
| Show text | `print "Hello!"` |
| Store a value | `remember x = 5` |
| Ask user | `ask "Name?" name` |
| Repeat | `repeat 5 times` |
| Count | `repeat 5 times as i` |
| Decide | `if x bigger 5` |
| Make a function | `fun greet name` |
| Create a list | `list fruits = "apple" "banana"` |
| Add to list | `add fruits "mango"` |
| Get from list | `print fruits at 1` |

---

## 🎯 Key Design Principles

1. **Every keyword is a real English word** — `print`, `remember`, `if`, `repeat`
2. **Only 5 symbols** — `= + - * /` (no `{}`, `;`, `==`, `!=`)
3. **Case insensitive** — `PRINT`, `print`, `Print` all work
4. **Friendly errors** — Every error suggests a fix
5. **Lists start at 1** — Because kids count from 1

---

## 📚 Complete Language Reference

### Variables
```
remember name = "Aarav"       # Store a value
remember age = 7              # Numbers work too
const PI = 3.14159            # Constants can't change
```

### Input / Output
```
print "Hello!"                # Show text
print 2 + 3                   # Show math result
print "Hi" name               # Mix text and variables
ask "Your name?" name         # Get user input
```

### Math
```
print 5 + 3                   # 8
print 10 - 4                  # 6
print 3 * 5                   # 15
print 20 / 4                  # 5.0
print 2 to the power 10       # 1024
```

### Conditions
```
if age bigger 5
    print "Big kid!"
else if age is 5
    print "Exactly 5!"
else
    print "Little kid!"
```

**Comparison words:** `is`, `bigger`, `smaller`, `bigger or same`, `smaller or same`

**Logic:** `and`, `or`, `not`

### Loops
```
repeat 5 times
    print "Jump!"

repeat 5 times as i
    print "Number" i          # 1, 2, 3, 4, 5

repeat forever
    print "Loop!"
    wait 1                    # Pause 1 second

# Stop exits a loop, skip goes to next iteration
repeat 10 times as i
    if i is 5
        stop                  # Exit loop
    if i is 3
        skip                  # Skip to next
    print i
```

### Functions
```
fun greet name
    print "Hello" name

fun add a b
    return a + b

greet "Aarav"
remember result = add 3 4
print result                  # 7
```

### Lists (Arrays)
```
list fruits = "apple" "banana" "mango"

add fruits "grape"            # Add to end
remove fruits "banana"        # Remove by value
print fruits at 1             # apple (1-indexed!)
print length fruits           # How many items

if has fruits "apple"         # Check if contains
if empty fruits               # Check if empty

sort fruits                   # Sort A-Z
reverse fruits                # Reverse order
shuffle fruits                # Randomize

remember text = join fruits ", "   # Join to string
remember parts = split text ","    # Split to list
```

### Dictionaries
```
dict student = {
    "name": "Aarav",
    "age": 7
}

print student at "name"       # Aarav
set student "grade" "2nd"     # Add/change

if student has "name"         # Check key exists
remember all_keys = keys student
```

### Strings
```
remember msg = "Hello World"

print length msg              # 11
print uppercase msg           # HELLO WORLD
print lowercase msg           # hello world
print trim "  hi  "           # hi
print replace msg "World" "KIDO"  # Hello KIDO
print find msg "World"        # 7
```

### File I/O
```
write "Hello" to "file.txt"
append "More text" to "file.txt"
remember content = read "file.txt"

if file exists "file.txt"
    print "Found!"
```

### Error Handling
```
try
    remember result = 10 / 0
catch error
    print "Oops:" error
```

### Type Conversion
```
remember num = as number "42"    # String to number
remember text = as string 42     # Number to string
print type num                   # "number"
```

### Math Functions
```
print abs -5          # 5
print sqrt 16         # 4.0
print round 3.7       # 4
print min 5 3 8       # 3
print max 5 3 8       # 8
print sum 1 2 3       # 6
print average 1 2 3   # 2.0
```

### Random
```
remember num = random 1 10       # 1 to 10
remember item = random fruits    # Random from list
shuffle fruits                   # Randomize list
```

### Modules
```
# helpers.kd
fun greet name
    print "Hello" name

# main.kd
use "helpers.kd"
greet "Aarav"
```

### Comments
```
# This is a single-line comment

/*
This is a
multi-line comment
*/
```

---

## 🛠️ CLI Commands

```
kido run <file.kd>       Run a KIDO program
kido check <file.kd>     Check for errors
kido new <name>          Create a new project
kido shell               Interactive REPL
kido version             Show version
kido help                Show help
```

---

## 📁 Project Structure

```bash
$ kido new my_game
```

Creates:
```
my_game/
├── main.kd           ← Your main program
├── my_game.kdproj    ← Project config (JSON)
├── assets/           ← Images, sounds
└── libs/             ← Packages
```

---

## 🧪 Testing

```bash
cd kido_sdk
python3 tests/test_all.py
```

Expected output:
```
TESTS: 100 | PASSED: 100 | FAILED: 0
```

---

## 📝 Example Programs

### Number Guessing Game
```
remember secret = random 1 10
remember tries = 0

print "Guess a number between 1 and 10!"

repeat 5 times
    remember tries = tries + 1
    ask "Your guess:" guess
    remember guess = as number guess
    
    if guess is secret
        print "You got it in" tries "tries!"
        stop
    
    if guess smaller secret
        print "Too low!"
    
    if guess bigger secret
        print "Too high!"

print "The number was" secret
```

### Quiz Game
```
list questions = "5 + 3?" "Days in a week?" "10 * 2?"
list answers = "8" "7" "20"
remember score = 0

repeat length questions times as i
    print "Q:" questions at i
    ask "Answer:" guess
    
    if guess is answers at i
        print "Correct!"
        remember score = score + 1
    else
        print "Wrong! Answer:" answers at i

print "Score:" score "/" length questions
```

### Shopping List
```
list shopping

add shopping "milk"
add shopping "bread"
add shopping "eggs"

print "Shopping List:"
repeat length shopping times as i
    print i "." shopping at i

print "Total:" length shopping "items"
```

---

## 🏗️ Architecture

```
.kd file → Lexer → Tokens → Parser → AST → Interpreter → Output
```

- **Lexer** (`lexer.py`): Tokenizes source code
- **Parser** (`parser.py`): Builds Abstract Syntax Tree
- **Interpreter** (`interpreter.py`): Executes the AST
- **Environment** (`environment.py`): Variable scope management
- **Errors** (`errors.py`): Kid-friendly error messages

---

## 🛡️ Security

KIDO runs untrusted kid-written programs safely with a **defense-in-depth** sandbox.

### Path Sandbox (default: ON)

File I/O (`read`, `write`, `append`, `use`, `delete`) is locked to the project folder. Absolute paths and `..` traversal are blocked.

```bash
# Sandbox ON — safe default
kido run my_project/main.kd

# Disable only for fully trusted programs
KIDO_SANDBOX=0 kido run my_project/main.kd
```

### Resource Limits

| Limit | Env Variable | Default |
|---|---|---|
| Nested function calls | `KIDO_MAX_RECURSION` | 200 |
| Loop iterations | `KIDO_MAX_LOOP_ITERS` | 1,000,000 |
| `wait` seconds | `KIDO_MAX_WAIT_SECONDS` | 60 |
| `to the power` exponent | `KIDO_MAX_POWER_EXPONENT` | 10,000 |
| File read size (bytes) | `KIDO_MAX_FILE_BYTES` | 10 MB |
| Source size (bytes) | `KIDO_MAX_SOURCE_BYTES` | 2 MB |

### Error Safety

- No Python stack traces shown by default (set `KIDO_DEBUG=1` for dev)
- Infinite recursion caught via `RecursionGuard` + Python `RecursionError` handler
- All user-facing errors are kid-friendly with fix suggestions
- `try`/`catch` does **not** intercept security errors (sandbox bypass is never catchable)

### Threat Model

See [SECURITY.md](SECURITY.md) for the full 5-check audit covering secrets, PII, production hardening, deep code audit, and attacker-perspective analysis.

---

## 📄 License

MIT License — Free for everyone!

---

*🧒 KIDO: Real code. Real syntax. Ridiculously easy.*
