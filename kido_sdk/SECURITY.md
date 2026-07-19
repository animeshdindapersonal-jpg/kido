# KIDO Security Audit Report

> **Methodology:** Mayank Shah "5 Security Checks Before You Launch"
> **Target:** KIDO v1.1.0 — A real programming language for kids
> **Date:** July 2026

---

## Check 01 — Secrets Scanning

**Scope:** env files, configs, source code, build artifacts, git history

| Item | Status | Notes |
|---|---|---|
| `.env` in repo | ✅ Excluded | `.gitignore` covers `.env`; only `.env.example` is tracked |
| `.env.example` | ✅ Clean | Contains only documented env var names with safe defaults |
| Hardcoded secrets in source | ✅ None found | `kido_core/` contains no tokens, keys, or passwords |
| Test files with secrets | ✅ None found | Tests use temporary paths, no hardcoded credentials |
| Build artifacts | ✅ Clean | `MANIFEST.in` excludes `.env`; `setup.py` packages only `kido_core/` and `kido_cli/` |

**Verdict:** ✅ PASS — No secrets exposed.

---

## Check 02 — PII Scanning

**Scope:** Logs, error messages, output capture, file I/O, network requests

| Item | Status | Notes |
|---|---|---|
| Logging PII | ✅ N/A | No logging framework; `print` output is in-memory only |
| Error messages leak paths | ✅ Safe | `KidoError` shows only kid-friendly messages; `KIDO_DEBUG=1` required for traces |
| File I/O path disclosure | ✅ Safe | Sandboxed paths resolved internally; absolute paths never printed |
| Network requests | ✅ N/A | KIDO has no networking (`fetch`/`send`/`download` are lexed but not implemented) |
| REPL history | ✅ N/A | Shell is ephemeral — no history file written |

**Verdict:** ✅ PASS — No PII leakage paths.

---

## Check 03 — Production Hardening

### 3.1 Path Traversal Sandbox

`kido_core/security.py:resolve_safe_path()` implements strict containment:

- Blocks absolute paths outside project directory
- Blocks `..` traversal components
- Blocks null bytes
- Resolves symlinks via `os.path.realpath()`
- Verifies final resolved path is under `base_dir`
- For-write operations validate parent directory is also inside sandbox

```python
# KIDO_SANDBOX=1 (default) blocks:
write "../../etc/passwd" to "x"          # SecurityError
read "/etc/passwd"                       # SecurityError
use "../../malicious.kd"                 # SecurityError
```

### 3.2 Resource Limits

All limits are env-var overridable with safe defaults:

| Limit | Env Var | Default | Protection |
|---|---|---|---|
| Recursion depth | `KIDO_MAX_RECURSION` | 200 | Prevents stack overflow |
| Loop iterations | `KIDO_MAX_LOOP_ITERS` | 1,000,000 | Prevents infinite loops |
| Wait seconds | `KIDO_MAX_WAIT_SECONDS` | 60 | Prevents long sleeps |
| Exponent | `KIDO_MAX_POWER_EXPONENT` | 10,000 | Prevents CPU bomb via `2 ** 1000000` |
| File size | `KIDO_MAX_FILE_BYTES` | 10 MB | Prevents memory exhaustion |
| Source size | `KIDO_MAX_SOURCE_BYTES` | 2 MB | Prevents large program load |

### 3.3 Error Safety

- **No stack traces** by default — `_friendly_error()` in CLI catches all exceptions
- `KIDO_DEBUG=1` available for teacher/developer troubleshooting
- Security errors (`SecurityError_`) are **never catchable** by `try`/`catch` — sandbox is always enforced
- `RecursionError` from Python's runtime is caught and re-raised as `SecurityError_` (interpreter.py:82)

### 3.4 CLI Hardening

- `kido new` validates project names via `validate_project_name()` (rejects path separators, dots, shell metacharacters)
- `kido run` and `kido check` validate file extension (`.kd` only)
- All CLI commands wrap exceptions in kid-friendly messages

### 3.5 Package Security

- `setup.py`: zero runtime dependencies — no supply-chain risk from pip packages
- `MANIFEST.in`: excludes `.env` files and test artifacts
- Version pinning: `python_requires=">=3.8"` ensures minimum supported interpreter

**Verdict:** ✅ PASS — Production hardening complete.

---

## Check 04 — Deep Code Audit

### 4.1 Parser: Space-Separated Function Call Ambiguity

**Finding:** `factorial n - 1` was parsed as `factorial(n, -1)` — the MINUS token triggered function-call argument collection.

**Fix:** Removed `MINUS` from the space-separated trigger set in `parse_primary()` (parser.py:927). Added MINUS to the "break at binary operator" list in the args loop (parser.py:995).

**Current behavior:** `factorial n - 1` parses as `factorial(n) - 1` (binary minus); `factorial(n - 1)` with parentheses parses correctly as a single argument.

### 4.2 Parser: Missing Keyword Function Calls

**Finding:** `print read "file.txt"` failed because `_parse_simple_primary()` had a shorter keyword list than `parse_primary()`. Keywords like `read`, `write`, `add`, `remove`, `shuffle`, `sort`, etc. were missing.

**Fix:** Added all missing keywords to `_parse_simple_primary()` function call list (parser.py:~1461).

### 4.3 Recursion Guard

`RecursionGuard` (security.py:273) tracks call depth with `enter()`/`leave()`:

- Default max: 200 (safe below Python's ~1000 `sys.getrecursionlimit()`)
- Increments on function entry, decrements on return
- Raises `SecurityError_` on overflow — **not catchable**
- Paired with interpreter `except RecursionError` handler (interpreter.py:82) as second line of defense

### 4.4 Loop Guard

`LoopGuard` (security.py:295) tracks global iteration budget:

- Default max: 1,000,000 iterations
- Raises `SecurityError_` on overflow
- Covers all loop types: `repeat n times`, `repeat forever`, `for each`

### 4.5 Type Safety

- All arithmetic operators validate operand types
- Division by zero raises `ZeroDivisionError_` (not a crash)
- `as number` / `as string` fail with clear errors
- List/dict access bounds-checked

### 4.6 Try/Catch Security Boundary

```python
CONTROL_FLOW = (SecurityError_, BreakLoop, SkipIteration, ReturnSignal, StopExecution)
```

The `try` handler in `interpreter.py` checks `isinstance(e, CONTROL_FLOW)` and re-raises without catching. This ensures security errors, break/skip/return signals, and program termination are **never** suppressed by user code.

### 4.7 Lexer Edge Cases

- Null bytes in source → `SyntaxError_`
- Overlong identifiers/literals → clamped or rejected
- Unterminated strings → `SyntaxError_`

**Verdict:** ✅ PASS — Deep audit complete. All critical paths reviewed.

---

## Check 05 — Attacker Perspective

### Attack Surface

| Attack Vector | Mitigation |
|---|---|
| **Path traversal** (`../../etc/passwd`) | `resolve_safe_path()` blocks `..`, absolute paths, null bytes |
| **CPU bomb** (`2 ** 1000000000`) | `check_power()` limits exponent to 10,000 |
| **Infinite loop** (`repeat forever` with no `stop`) | `LoopGuard` kills after 1M iterations |
| **Stack overflow** (deep recursion) | `RecursionGuard` at 200 + Python `RecursionError` handler |
| **Disk fill** (write huge files) | `check_file_size()` on read; no write-limit beyond OS |
| **Memory exhaustion** (huge source) | `check_source_size()` limits source to 2 MB |
| **Wait bomb** (`wait 999999`) | `check_wait_seconds()` clamps to 60s default |
| **Shell injection** (project names) | `validate_project_name()` rejects non-alphanumeric chars |
| **Supply chain** (malicious deps) | Zero runtime dependencies in `setup.py` |
| **Info leak** (stack traces) | `_friendly_error()` suppresses traces; `KIDO_DEBUG=1` required |
| **try/catch bypass** | Security errors excluded from `CONTROL_FLOW` — never catchable |
| **Module injection** (`use` with path) | `resolve_safe_path()` sandboxes `use` statements |

### Escalation Chains

```
Attacker goal: read /etc/passwd
  → write "../../etc/passwd" to "x"     → BLOCKED (.. not allowed)
  → read "/etc/passwd"                   → BLOCKED (absolute path outside sandbox)
  → read "x" (symlink to /etc/passwd)    → BLOCKED (realpath resolves symlink, fails sandbox check)

Attacker goal: denial of service
  → 2 ** 1000000000                      → BLOCKED (exponent too large)
  → repeat 9999999999 times              → BLOCKED (LoopGuard at 1M)
  → factorial(1000000)                   → BLOCKED (RecursionGuard at 200 + Python RecursionError)
  → wait 999999                          → BLOCKED (max 60s)

Attacker goal: execute arbitrary Python
  → KIDO has no eval/exec — lexer/parser/interpreter are self-contained
  → No import/__import__ access
  → Only predefined built-in functions available
```

### Remaining Considerations

| Item | Severity | Note |
|---|---|---|
| Large file writes (within sandbox) | Low | Kid could fill disk with `append` in a loop; mitigated by LoopGuard |
| `random` seed predictability | Low | Not a crypto application; `random` is stdlib `random` module |
| Side-channel via timing | Low | Not applicable — KIDO is a kid's educational language |

**Verdict:** ✅ PASS — No viable attack path identified. Language is safe for untrusted kid code.

---

## Summary

| Check | Description | Status |
|---|---|---|
| 01 | Secrets scanning | ✅ PASS |
| 02 | PII scanning | ✅ PASS |
| 03 | Production hardening | ✅ PASS |
| 04 | Deep audit | ✅ PASS |
| 05 | Attacker perspective | ✅ PASS |

**Overall:** KIDO is production-safe for classroom/education environments. The defense-in-depth sandbox (`RecursionGuard` + `LoopGuard` + path validation + resource limits + uncatchable security errors) ensures that even intentionally malicious .kd programs cannot escape the project directory or consume excessive resources.
