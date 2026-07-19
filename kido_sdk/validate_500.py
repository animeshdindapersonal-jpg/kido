#!/usr/bin/env python3
"""
Validate all 500 KIDO programs by parsing and running each one.
"""

import sys
import os
import io
from unittest.mock import patch

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kido_core.lexer import tokenize
from kido_core.parser import parse
from kido_core.interpreter import Interpreter, run
from kido_core.errors import *

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples/500-problems")

passed = 0
failed = 0
errors = []

categories = [
    "01-math-numbers",
    "02-word-strings",
    "03-lists-data",
    "04-quiz-trivia",
    "05-story-madlibs",
    "06-logic-decision",
    "07-pattern-sequence",
    "08-simulation-games",
    "09-functions",
    "10-dictionary",
    "11-file-io",
    "12-drawing-music",
    "13-calendar-time",
    "14-geometry",
    "15-crypto",
    "16-probability-stats",
    "17-education-school",
    "18-life-skills",
    "19-recursion",
    "20-science-nature",
]

total_files = 0
for cat in categories:
    catdir = os.path.join(BASE, cat)
    if not os.path.isdir(catdir):
        continue
    files = sorted([f for f in os.listdir(catdir) if f.endswith(".kd")])
    for fname in files:
        fpath = os.path.join(catdir, fname)
        total_files += 1
        source = open(fpath, encoding="utf-8").read()

        try:
            tokens = tokenize(source)
            ast = parse(tokens)
        except Exception as e:
            failed += 1
            errors.append(f"PARSE [{cat}/{fname}]: {e}")
            print(f"  FAIL [{cat}/{fname}] PARSE ERROR: {e}")
            continue

        try:
            with patch("builtins.input", return_value="test"):
                interp = run(source, fpath, os.path.dirname(fpath))
            passed += 1
            if passed % 50 == 0:
                print(f"  ... {passed} passed so far ...")
        except Exception as e:
            failed += 1
            errors.append(f"RUN [{cat}/{fname}]: {e}")
            print(f"  FAIL [{cat}/{fname}] RUNTIME ERROR: {e}")

print()
print("=" * 60)
print(f"VALIDATION: {total_files} files")
print(f"PASSED: {passed} | FAILED: {failed}")
print("=" * 60)

if errors:
    print(f"\nERRORS ({len(errors)}):")
    for err in errors:
        print(f"  {err}")

sys.exit(0 if failed == 0 else 1)
