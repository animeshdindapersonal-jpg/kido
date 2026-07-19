"""
Fix remaining issues in KIDO programs:
1. call keyword removal (any position in line)
2. elif -> else + nested if
3. Trailing extra " on print statements
4. rem -> full modulo expression (n - floor(n / d) * d)
5. Broken \n in strings
"""

import re, os
from pathlib import Path

BASE = Path("examples/500-problems")


def fix_line(line, in_elif_block=None):
    stripped = line.strip()
    indent = line[: len(line) - len(line.lstrip())]

    # 1. Fix call keyword - replace "call funcname args" with "funcname args"
    # Handle: "remember x = call funcname args"
    # Handle: "call funcname args"
    line = re.sub(r"\bcall\s+(\w+)", r"\1", line)

    return line, in_elif_block


def fix_program(text, fpath):
    lines = text.split("\n")
    fixed = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        indent = line[: len(line) - len(line.lstrip())]

        # 1. Fix elif -> else + if with proper indentation
        if stripped.startswith("elif "):
            condition = stripped[5:]
            # If body is on same line: elif cond body
            # Split into else + if cond + body
            body = ""
            for kw in [" print ", " remember ", " call "]:
                if kw in condition:
                    parts = condition.split(kw, 1)
                    cond_part = parts[0]
                    body_part = kw.strip() + " " + parts[1]
                    condition = cond_part
                    body = body_part
                    break
            fixed.append(indent + "else")
            fixed.append(indent + "    if " + condition)
            if body:
                # Body is on same line as elif
                fixed.append(indent + "        " + body)
            else:
                # Body is on next line with indentation
                pass  # Will be handled by collecting next lines
            i += 1
            continue

        # 2. Fix trailing extra quote on print lines
        # Pattern: print "..." var"  ->  print "..." var
        # The issue is when a line ends with " but it's not closing a string
        if '"' in stripped:
            fixed_line = _fix_trailing_quote(line)
        else:
            fixed_line = line

        # 3. Fix call keyword
        fixed_line = re.sub(r"\bcall\s+(\w+)", r"\1", fixed_line)

        # 4. Fix rem keyword (modulo)
        fixed_line = re.sub(
            r"(\w+)\s+rem\s+(\w+)", r"(\1 - floor(\1 / \2) * \2)", fixed_line
        )
        fixed_line = re.sub(
            r"(\w+)\s+rem\s+(\d+)", r"(\1 - floor(\1 / \2) * \2)", fixed_line
        )
        fixed_line = re.sub(
            r"\((\s*\w+\s*-\s*floor\s*\(\s*\w+\s*/\s*\w+\s*\)\s*\*\s*\w+\s*)\)",
            r"\1",
            fixed_line,
        )

        fixed.append(fixed_line)
        i += 1

    return "\n".join(fixed) + "\n"


def _fix_trailing_quote(line):
    """Remove trailing extra quote from print statements like: print "Tails:" tails" """
    stripped = line.rstrip()
    if not stripped.endswith('"'):
        return line
    # Remove the trailing quote
    # But only if it's an extra quote (odd number of quotes in line)
    quote_count = stripped.count('"')
    if quote_count % 2 == 0:
        return line  # Balanced, leave alone
    # This line has an odd number of quotes - remove the trailing one
    # First, check if it's actually a string ending
    # Pattern: ... var" where var is not quoted
    before_quote = stripped[:-1].rstrip()
    # Check if the character before the trailing quote area is a word char
    # e.g. tails" -> before_quote ends with tails
    if before_quote and before_quote[-1].isalpha():
        line = before_quote
    return line


def fix_io014(text):
    """Fix the broken \n in io014.kd"""
    return text.replace('split data "\n"', 'split data "\\\\n"')


def main():
    cats = sorted(BASE.iterdir())
    total_fixed = 0
    total_files = 0

    for catdir in cats:
        if not catdir.is_dir():
            continue
        for fpath in sorted(catdir.glob("*.kd")):
            total_files += 1
            original = fpath.read_text(encoding="utf-8")
            fixed = fix_program(original, fpath)
            fixed = fix_io014(fixed)

            if fixed != original:
                fpath.write_text(fixed, encoding="utf-8")
                total_fixed += 1
                print(f"FIXED {fpath.relative_to(BASE)}")

    print(f"\nFixed {total_fixed} of {total_files} files")


if __name__ == "__main__":
    main()
