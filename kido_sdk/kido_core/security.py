"""
KIDO Security Hardening
-----------------------
Sandboxing, path validation, and resource limits for production-safe
execution of untrusted .kd programs (classroom / kids environments).

Environment overrides (all optional):
  KIDO_MAX_RECURSION      default 500
  KIDO_MAX_LOOP_ITERS     default 1_000_000
  KIDO_MAX_WAIT_SECONDS   default 60
  KIDO_MAX_POWER_EXPONENT default 10_000
  KIDO_MAX_FILE_BYTES     default 10_485_760 (10 MB)
  KIDO_MAX_SOURCE_BYTES   default 2_097_152 (2 MB)
  KIDO_SANDBOX            "1" (default) | "0" to disable path sandbox
"""

from __future__ import annotations

import os
import re
from typing import Optional

from .errors import RuntimeError_, ValueError_, SecurityError_


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_bool(name: str, default: bool = True) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() not in ("0", "false", "no", "off")


# Resource limits (overridable via env for advanced installs)
# Keep default low enough that logical depth * Python frames stays under
# sys.getrecursionlimit() (~1000). ~3–5 frames per call → 200 is safe.
MAX_RECURSION = _env_int("KIDO_MAX_RECURSION", 200)
MAX_LOOP_ITERATIONS = _env_int("KIDO_MAX_LOOP_ITERS", 1_000_000)
MAX_WAIT_SECONDS = _env_int("KIDO_MAX_WAIT_SECONDS", 60)
MAX_POWER_EXPONENT = _env_int("KIDO_MAX_POWER_EXPONENT", 10_000)
MAX_FILE_BYTES = _env_int("KIDO_MAX_FILE_BYTES", 10 * 1024 * 1024)
MAX_SOURCE_BYTES = _env_int("KIDO_MAX_SOURCE_BYTES", 2 * 1024 * 1024)
SANDBOX_ENABLED = _env_bool("KIDO_SANDBOX", True)

# Project names: letters, numbers, underscore, hyphen only; no path separators
_SAFE_PROJECT_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")


def validate_project_name(name: str) -> str:
    """Validate CLI project name — reject path traversal and injection."""
    if not name or not isinstance(name, str):
        raise ValueError_("Project name cannot be empty")
    name = name.strip()
    if name in (".", "..") or "/" in name or "\\" in name:
        raise SecurityError_(
            "Project name cannot contain path separators.",
            suggestion="Use a simple name like 'my_game' or 'hello_world'."
        )
    if ".." in name or name.startswith("."):
        raise SecurityError_(
            "Project name cannot start with a dot or contain '..'.",
            suggestion="Use a simple name like 'my_game'."
        )
    if not _SAFE_PROJECT_NAME.match(name):
        raise SecurityError_(
            f"Invalid project name '{name}'.",
            suggestion="Use letters, numbers, underscore, or hyphen. Start with a letter."
        )
    return name


def resolve_safe_path(
    base_dir: str,
    user_path: str,
    *,
    line: Optional[int] = None,
    must_exist: bool = False,
    for_write: bool = False,
) -> str:
    """
    Resolve user-supplied path strictly under base_dir.

    Blocks:
      - Absolute paths outside the sandbox
      - Path traversal (../)
      - Null bytes
      - Symlink escapes (when target exists)
    """
    if not SANDBOX_ENABLED:
        # Advanced mode: still join but resolve absolute
        if os.path.isabs(user_path):
            return os.path.normpath(user_path)
        return os.path.normpath(os.path.join(base_dir, user_path))

    if user_path is None:
        raise SecurityError_("Missing file path", line)

    path_str = str(user_path)
    if "\x00" in path_str:
        raise SecurityError_("Invalid file path (null byte)", line)

    # Normalize base to absolute real path
    base = os.path.realpath(os.path.abspath(base_dir))
    if not os.path.isdir(base):
        # Allow base_dir that will be created only for parent of write? No —
        # base must exist as the program's project directory.
        try:
            os.makedirs(base, exist_ok=True)
        except OSError:
            raise SecurityError_(f"Invalid working directory: {base_dir}", line)

    # Reject absolute paths that escape (Windows drive letters, /etc, etc.)
    candidate = path_str.replace("\\", "/")
    # Strip leading ./ only
    while candidate.startswith("./"):
        candidate = candidate[2:]

    # If absolute, only allow if it is already under base
    if os.path.isabs(path_str):
        target = os.path.realpath(os.path.abspath(path_str))
    else:
        # Reject components that are empty or pure traversal before join
        parts = []
        for part in candidate.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                raise SecurityError_(
                    "Path not allowed: cannot use '..' to leave the project folder.",
                    line,
                    "Keep files inside your project folder."
                )
            parts.append(part)
        relative = os.path.join(*parts) if parts else ""
        target = os.path.realpath(os.path.join(base, relative))

    # Ensure target is inside base (prefix check with separator)
    base_prefix = base if base.endswith(os.sep) else base + os.sep
    if target != base and not target.startswith(base_prefix):
        raise SecurityError_(
            "Path not allowed: file must stay inside the project folder.",
            line,
            "Use a relative path like 'data.txt' or 'libs/helper.kd'."
        )

    if must_exist and not os.path.exists(target):
        from .errors import FileNotFoundError_
        raise FileNotFoundError_(f"File not found: {user_path}", line)

    if for_write:
        # Parent directory must be inside sandbox
        parent = os.path.dirname(target)
        parent_real = os.path.realpath(parent) if os.path.isdir(parent) else os.path.realpath(
            os.path.dirname(target) if parent else base
        )
        # If parent doesn't exist yet, walk up until we find an existing ancestor under base
        check = target
        while not os.path.exists(check):
            parent = os.path.dirname(check)
            if parent == check:
                break
            check = parent
        check_real = os.path.realpath(check) if os.path.exists(check) else base
        if check_real != base and not (check_real + os.sep).startswith(base_prefix) and check_real != base:
            if not str(check_real).startswith(base_prefix) and check_real != base:
                raise SecurityError_(
                    "Path not allowed: cannot write outside the project folder.",
                    line
                )

    return target


def check_file_size(filepath: str, line: Optional[int] = None) -> None:
    """Reject oversized files before reading into memory."""
    try:
        size = os.path.getsize(filepath)
    except OSError:
        return
    if size > MAX_FILE_BYTES:
        raise SecurityError_(
            f"File is too large ({size} bytes). Max is {MAX_FILE_BYTES} bytes.",
            line,
            "Use a smaller file or ask a teacher to raise KIDO_MAX_FILE_BYTES."
        )


def check_source_size(source: str, line: Optional[int] = None) -> None:
    """Reject oversized source programs."""
    size = len(source.encode("utf-8", errors="replace"))
    if size > MAX_SOURCE_BYTES:
        raise SecurityError_(
            f"Program is too large ({size} bytes). Max is {MAX_SOURCE_BYTES} bytes.",
            line
        )


def check_wait_seconds(seconds, line: Optional[int] = None) -> float:
    """Clamp / validate wait duration."""
    if not isinstance(seconds, (int, float)):
        from .errors import TypeError_
        raise TypeError_("wait requires a number", line)
    if seconds < 0:
        raise ValueError_("wait cannot be negative", line)
    if seconds > MAX_WAIT_SECONDS:
        raise SecurityError_(
            f"wait is too long (max {MAX_WAIT_SECONDS} seconds).",
            line,
            "Use a shorter wait, or set KIDO_MAX_WAIT_SECONDS for longer pauses."
        )
    return float(seconds)


def check_power(base, exp, line: Optional[int] = None):
    """Prevent CPU / memory bombs via huge exponents."""
    if not isinstance(base, (int, float)) or not isinstance(exp, (int, float)):
        from .errors import TypeError_
        raise TypeError_("Power requires numbers", line)
    # bool is subclass of int — treat as number OK
    if isinstance(exp, float) and not exp.is_integer():
        # allow fractional powers for positive bases only via **
        if base < 0:
            raise ValueError_("Cannot raise a negative number to a fractional power", line)
        if abs(exp) > 1000:
            raise SecurityError_(f"Exponent too large (max 1000 for fractional).", line)
        return base ** exp
    exp_i = int(exp)
    if abs(exp_i) > MAX_POWER_EXPONENT:
        raise SecurityError_(
            f"Exponent too large (max {MAX_POWER_EXPONENT}).",
            line,
            "Use a smaller number."
        )
    # Guard absurd intermediate size: |base|**exp roughly
    if abs(base) > 1 and abs(exp_i) > 100_000:
        raise SecurityError_("Power result would be too large.", line)
    try:
        result = base ** exp
    except OverflowError:
        raise SecurityError_("Power result is too large to compute.", line)
    return result


def check_loop_count(count, line: Optional[int] = None) -> int:
    """Validate repeat count against resource limits."""
    if not isinstance(count, (int, float)):
        from .errors import TypeError_
        raise TypeError_(
            f"repeat count must be a number, got {type(count).__name__}",
            line
        )
    n = int(count)
    if n < 0:
        raise ValueError_("repeat count cannot be negative", line)
    if n > MAX_LOOP_ITERATIONS:
        raise SecurityError_(
            f"repeat count too large (max {MAX_LOOP_ITERATIONS}).",
            line,
            "Use a smaller number so the program stays responsive."
        )
    return n


class RecursionGuard:
    """Tracks call depth for user-defined functions."""

    def __init__(self, max_depth: int = MAX_RECURSION):
        self.max_depth = max_depth
        self.depth = 0

    def enter(self, line: Optional[int] = None) -> None:
        self.depth += 1
        if self.depth > self.max_depth:
            self.depth -= 1
            raise SecurityError_(
                f"Too many nested function calls (max {self.max_depth}).",
                line,
                "Check for infinite recursion, or set KIDO_MAX_RECURSION."
            )

    def leave(self) -> None:
        if self.depth > 0:
            self.depth -= 1


class LoopGuard:
    """Global iteration budget across forever-loops and nested repeats."""

    def __init__(self, max_iters: int = MAX_LOOP_ITERATIONS):
        self.max_iters = max_iters
        self.count = 0

    def tick(self, line: Optional[int] = None) -> None:
        self.count += 1
        if self.count > self.max_iters:
            raise SecurityError_(
                f"Program ran too many loop iterations (max {self.max_iters}).",
                line,
                "Add a 'stop' condition, or raise KIDO_MAX_LOOP_ITERS carefully."
            )
