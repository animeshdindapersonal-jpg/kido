"""
KIDO CLI - Command line interface (production hardened)
"""

import sys
import os
import json
import traceback

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Package-relative import path for editable/dev installs
_SDK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SDK_ROOT not in sys.path:
    sys.path.insert(0, _SDK_ROOT)

from kido_core.lexer import tokenize
from kido_core.parser import parse
from kido_core.interpreter import Interpreter, run, run_file
from kido_core.errors import KidoError, SecurityError_
from kido_core.security import validate_project_name, check_source_size, check_file_size


VERSION = "1.1.0"

# Verbose internal errors only when explicitly enabled (teachers/devs)
_DEBUG = os.environ.get("KIDO_DEBUG", "").strip().lower() in ("1", "true", "yes", "on")


def print_banner():
    print(f"🧒 KIDO Programming Language v{VERSION}")
    print()


def _friendly_error(exc):
    """Return a kid-safe error string; never dump stack traces by default."""
    if isinstance(exc, KidoError):
        return str(exc)
    if _DEBUG:
        return f"🤔 Oops! Something went wrong: {exc}\n{traceback.format_exc()}"
    return "🤔 Oops! Something went wrong. Run with KIDO_DEBUG=1 for details."


def cmd_version():
    print(f"🧒 KIDO v{VERSION} — Ready to code!")


def cmd_help():
    print_banner()
    print("USAGE:")
    print("  kido <command> [options]")
    print()
    print("COMMANDS:")
    print("  run <file.kd>       Run a KIDO program")
    print("  check <file.kd>     Check for errors without running")
    print("  new <name>          Create a new KIDO project")
    print("  shell               Open interactive KIDO shell")
    print("  version             Show KIDO version")
    print("  help                Show this help message")
    print()
    print("EXAMPLES:")
    print("  kido run hello.kd")
    print("  kido new my_project")
    print("  kido shell")
    print()
    print("SECURITY:")
    print("  File I/O is sandboxed to the project folder.")
    print("  Set KIDO_SANDBOX=0 only if you fully trust the program.")
    print("  Set KIDO_DEBUG=1 to show detailed internal errors.")


def cmd_run(filepath):
    """Run a .kd file"""
    if not os.path.exists(filepath):
        print(f"🤔 Oops! File not found: {filepath}")
        sys.exit(1)

    if not str(filepath).lower().endswith('.kd'):
        print("🤔 Oops! File must have .kd extension")
        sys.exit(1)

    try:
        check_file_size(os.path.realpath(os.path.abspath(filepath)))
        run_file(filepath)
    except KidoError as e:
        print(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Program stopped by user")
        sys.exit(0)
    except Exception as e:
        print(_friendly_error(e))
        sys.exit(1)


def cmd_check(filepath):
    """Check a .kd file for errors"""
    if not os.path.exists(filepath):
        print(f"🤔 Oops! File not found: {filepath}")
        sys.exit(1)

    if not str(filepath).lower().endswith('.kd'):
        print("🤔 Oops! File must have .kd extension")
        sys.exit(1)

    try:
        abs_path = os.path.realpath(os.path.abspath(filepath))
        check_file_size(abs_path)
        with open(abs_path, 'r', encoding='utf-8') as f:
            source = f.read()
        check_source_size(source)

        tokens = tokenize(source, abs_path)
        parse(tokens, abs_path)

        print("✅ No problems found! Your code looks great!")
    except KidoError as e:
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print(_friendly_error(e))
        sys.exit(1)


def cmd_new(name):
    """Create a new KIDO project"""
    try:
        name = validate_project_name(name)
    except KidoError as e:
        print(str(e))
        sys.exit(1)

    # Always create under current working directory (never absolute path names)
    target = os.path.realpath(os.path.join(os.getcwd(), name))
    cwd = os.path.realpath(os.getcwd())
    if not target.startswith(cwd + os.sep) and target != cwd:
        print("🤔 Oops! Invalid project location.")
        sys.exit(1)

    if os.path.exists(target):
        print(f"🤔 Oops! Directory '{name}' already exists")
        sys.exit(1)

    # Create project structure
    os.makedirs(target)
    os.makedirs(os.path.join(target, 'assets'))
    os.makedirs(os.path.join(target, 'libs'))

    # Create main.kd
    main_kd = '''# My KIDO Program
print "Hello from KIDO!"
print ""

ask "What is your name?" name
print "Welcome to KIDO," name "!"
'''

    with open(os.path.join(target, 'main.kd'), 'w', encoding='utf-8') as f:
        f.write(main_kd)

    # Create .kdproj
    kdproj = {
        "name": name,
        "version": "1.0.0",
        "author": "",
        "main": "main.kd",
        "language": "en"
    }

    with open(os.path.join(target, f'{name}.kdproj'), 'w', encoding='utf-8') as f:
        json.dump(kdproj, f, indent=2)

    print(f"📁 Created project: {name}/")
    print(f"📝 Created: main.kd")
    print(f"⚙️  Created: {name}.kdproj")
    print()
    print(f"💡 Run it with: kido run {name}/main.kd")


def cmd_shell():
    """Interactive REPL"""
    print_banner()
    print("Type code and press Enter. Type 'quit' to exit.")
    print()

    env = Interpreter().global_env

    while True:
        try:
            line = input("> ")

            if line.strip().lower() in ('quit', 'exit', 'q'):
                print("Bye! 👋")
                break

            if not line.strip():
                continue

            try:
                check_source_size(line)
                tokens = tokenize(line, "<shell>")
                program = parse(tokens, "<shell>")
                interpreter = Interpreter()
                interpreter.global_env = env
                interpreter.execute(program)
            except KidoError as e:
                print(str(e))
            except Exception as e:
                print(_friendly_error(e))

        except KeyboardInterrupt:
            print("\nBye! 👋")
            break
        except EOFError:
            print("\nBye! 👋")
            break


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        cmd_help()
        sys.exit(0)

    command = sys.argv[1]

    if command == 'version' or command == '--version' or command == '-V':
        cmd_version()
    elif command == 'help' or command == '--help' or command == '-h':
        cmd_help()
    elif command == 'run':
        if len(sys.argv) < 3:
            print("🤔 Oops! Please specify a file to run")
            print("   Usage: kido run <file.kd>")
            sys.exit(1)
        cmd_run(sys.argv[2])
    elif command == 'check':
        if len(sys.argv) < 3:
            print("🤔 Oops! Please specify a file to check")
            print("   Usage: kido check <file.kd>")
            sys.exit(1)
        cmd_check(sys.argv[2])
    elif command == 'new':
        if len(sys.argv) < 3:
            print("🤔 Oops! Please specify a project name")
            print("   Usage: kido new <name>")
            sys.exit(1)
        cmd_new(sys.argv[2])
    elif command == 'shell':
        cmd_shell()
    else:
        print(f"🤔 Oops! Unknown command: {command}")
        print("   Run 'kido help' for available commands")
        sys.exit(1)


if __name__ == '__main__':
    main()
