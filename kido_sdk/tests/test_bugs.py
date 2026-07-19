#!/usr/bin/env python3
"""
KIDO Comprehensive Bug Hunt - A to Z
Tests every edge case, corner case, and potential bug
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kido_core.lexer import tokenize
from kido_core.parser import parse
from kido_core.interpreter import Interpreter, run
from kido_core.errors import *


class BugHunter:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.bugs = []
        self.current_category = ""

    def category(self, name):
        self.current_category = name
        print(f"\n{'=' * 60}")
        print(f"  {name}")
        print(f"{'=' * 60}")

    def test(self, name, code, expected_output=None, should_fail=False, check_fn=None):
        """Run a test and check for bugs"""
        try:
            interp = run(code)
            if should_fail:
                self.failed += 1
                self.bugs.append(
                    (self.current_category, name, "Should have failed but didn't", code)
                )
                print(f"  ❌ {name}: Should have failed but ran successfully")
                return

            if expected_output is not None:
                if interp.output == expected_output:
                    self.passed += 1
                    print(f"  ✅ {name}")
                else:
                    self.failed += 1
                    self.bugs.append(
                        (
                            self.current_category,
                            name,
                            f"Expected {expected_output}, got {interp.output}",
                            code,
                        )
                    )
                    print(
                        f"  ❌ {name}: Expected {expected_output}, got {interp.output}"
                    )
            elif check_fn is not None:
                if check_fn(interp):
                    self.passed += 1
                    print(f"  ✅ {name}")
                else:
                    self.failed += 1
                    self.bugs.append(
                        (self.current_category, name, "Check function failed", code)
                    )
                    print(f"  ❌ {name}: Check function failed")
            else:
                self.passed += 1
                print(f"  ✅ {name}")
        except Exception as e:
            if should_fail:
                self.passed += 1
                print(f"  ✅ {name} (correctly failed)")
            else:
                self.failed += 1
                self.bugs.append((self.current_category, name, str(e), code))
                print(f"  ❌ {name}: {e}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'=' * 60}")
        print(f"  BUG HUNT SUMMARY")
        print(f"{'=' * 60}")
        print(f"  Total tests: {total}")
        print(f"  Passed: {self.passed}")
        print(f"  Failed (bugs found): {self.failed}")
        print(f"{'=' * 60}")

        if self.bugs:
            print(f"\n  🐛 BUGS FOUND:")
            for cat, name, error, code in self.bugs:
                print(f"\n  [{cat}] {name}")
                print(f"    Error: {error}")
                print(f"    Code: {code[:80]}...")

        return self.failed == 0


hunter = BugHunter()

# ============================================================================
# A. ARITHMETIC EDGE CASES
# ============================================================================
hunter.category("A. Arithmetic Edge Cases")

hunter.test("A1: Zero division", "print 1 / 0", should_fail=True)
hunter.test("A2: Negative division", "print -10 / 2", ["-5.0"])
hunter.test("A3: Float division", "print 7 / 2", ["3.5"])
hunter.test("A4: Large numbers", "print 999999 * 999999", ["999998000001"])
hunter.test("A5: Zero multiplication", "print 0 * 999", ["0"])
hunter.test("A6: Negative power", "print 2 to the power 0", ["1"])
hunter.test("A7: Power of 1", "print 999 to the power 1", ["999"])
hunter.test("A8: Chained math", "print 1 + 2 * 3 - 4 / 2", ["5.0"])
hunter.test("A9: Negative modulo", "print abs -42", ["42"])
hunter.test("A10: Sqrt of 0", "print sqrt 0", ["0.0"])
hunter.test("A11: Sqrt of 1", "print sqrt 1", ["1.0"])
hunter.test("A12: Floor negative", "print floor -3.2", ["-4"])
hunter.test("A13: Ceil negative", "print ceil -3.2", ["-3"])
hunter.test("A14: Round .5", "print round 2.5", ["2"])  # Python rounds to even
hunter.test(
    "A15: Empty sum", "list x\nprint sum x", should_fail=True
)  # sum of empty list
hunter.test(
    "A16: Empty average", "list x\nprint average x", should_fail=True
)  # div by zero
hunter.test("A17: Min single", "print min 5", ["5"])
hunter.test("A18: Max single", "print max 5", ["5"])

# ============================================================================
# B. BOOLEAN LOGIC EDGE CASES
# ============================================================================
hunter.category("B. Boolean Logic Edge Cases")

hunter.test("B1: yes is yes", 'if yes is yes\n    print "ok"', ["ok"])
hunter.test("B2: no is no", 'if no is no\n    print "ok"', ["ok"])
hunter.test("B3: yes is not no", 'if not yes is no\n    print "ok"', ["ok"])
hunter.test("B4: not not yes", 'if not not yes\n    print "ok"', ["ok"])
hunter.test(
    "B5: and short circuit",
    """
remember x = no
if x and yes
    print "should not print"
""",
    [],
)
hunter.test(
    "B6: or short circuit",
    """
remember x = yes
if x or no
    print "ok"
""",
    ["ok"],
)
hunter.test(
    "B7: Truthy number",
    """
if 5
    print "truthy"
""",
    ["truthy"],
)
hunter.test(
    "B8: Falsy zero",
    """
if 0
    print "should not print"
""",
    [],
)
hunter.test(
    "B9: Truthy string",
    """
if "hello"
    print "truthy"
""",
    ["truthy"],
)
hunter.test(
    "B10: Falsy empty string",
    """
if ""
    print "should not print"
""",
    [],
)
hunter.test(
    "B11: Truthy list",
    """
list x = 1
if x
    print "truthy"
""",
    ["truthy"],
)
hunter.test(
    "B12: Falsy empty list",
    """
list x
if x
    print "should not print"
""",
    [],
)

# ============================================================================
# C. COMPARISON EDGE CASES
# ============================================================================
hunter.category("C. Comparison Edge Cases")

hunter.test("C1: String equals", 'if "abc" is "abc"\n    print "ok"', ["ok"])
hunter.test("C2: String not equals", 'if not "abc" is "def"\n    print "ok"', ["ok"])
hunter.test("C3: Number bigger", 'if 5 bigger 3\n    print "ok"', ["ok"])
hunter.test("C4: Number smaller", 'if 3 smaller 5\n    print "ok"', ["ok"])
hunter.test("C5: Equal numbers", 'if 5 bigger or same 5\n    print "ok"', ["ok"])
hunter.test("C6: Equal numbers 2", 'if 5 smaller or same 5\n    print "ok"', ["ok"])
hunter.test("C7: Nothing is nothing", 'if nothing is nothing\n    print "ok"', ["ok"])
hunter.test(
    "C8: List equality",
    """
list a = 1 2 3
list b = 1 2 3
if a is b
    print "equal"
""",
    ["equal"],
)
hunter.test(
    "C9: String bigger (lexicographic)", 'if "b" bigger "a"\n    print "ok"', ["ok"]
)
hunter.test(
    "C10: Bool comparison", 'if yes is not no\n    print "ok"', should_fail=True
)  # 'is not' issue

# ============================================================================
# D. DATA TYPE EDGE CASES
# ============================================================================
hunter.category("D. Data Type Edge Cases")

hunter.test("D1: Type of nothing", "print type nothing", ["nothing"])
hunter.test("D2: Type of yes", "remember x = yes\nprint type x", ["yesno"])
hunter.test("D3: Type of list", "list x\nprint type x", ["list"])
hunter.test("D4: Type of dict", "dict x\nprint type x", ["dict"])
hunter.test("D5: String + number", 'print "age:" 5', ["age: 5"])
hunter.test(
    "D6: Number + string coercion", 'print 5 + "3"', should_fail=True
)  # or should it concat?
hunter.test(
    "D7: Bool as number", "remember x = yes\nprint x + 1", should_fail=True
)  # bool + int
hunter.test("D8: Nothing in print", "print nothing", ["nothing"])
hunter.test(
    "D9: Nested list",
    """
list a = 1 2 3
list b
add b a
print b at 1
""",
    ["1 2 3"],
)
hunter.test(
    "D10: Dict with number key",
    """
dict d = {
    "1": "one"
}
print d at "1"
""",
    ["one"],
)

# ============================================================================
# E. ENVIRONMENT / SCOPE BUGS
# ============================================================================
hunter.category("E. Environment / Scope")

hunter.test(
    "E1: Variable shadowing",
    """
remember x = 10
fun test
    remember x = 20
    print x
test
print x
""",
    ["20", "10"],
)
hunter.test(
    "E2: Global access from function",
    """
remember x = 10
fun test
    print x
test
""",
    ["10"],
)
hunter.test("E3: Undefined variable", "print undefined_var", should_fail=True)
hunter.test(
    "E4: Similar name suggestion", "remember score = 5\nprint scor", should_fail=True
)
hunter.test(
    "E5: Constant reassignment", "const X = 5\nremember X = 10", should_fail=True
)
hunter.test(
    "E6: Function as variable",
    """
fun greet
    print "hi"
remember f = greet
""",
    None,
)  # Should work - store function reference
hunter.test(
    "E7: Multiple assignment unpack",
    """
fun get_pair
    return 1 2
remember a b = get_pair
print a b
""",
    ["1 2"],
)
hunter.test(
    "E8: Multiple assignment wrong count",
    """
fun get_triple
    return 1 2 3
remember a b = get_triple
""",
    should_fail=True,
)

# ============================================================================
# F. FUNCTION EDGE CASES
# ============================================================================
hunter.category("F. Function Edge Cases")

hunter.test(
    "F1: No return value",
    """
fun test
    print "hi"
remember x = test
print x
""",
    ["hi", "nothing"],
)
hunter.test(
    "F2: Deep recursion",
    """
fun count n
    if n is 0
        return 0
    remember prev = count(n - 1)
    return prev + 1
remember x = count(50)
print x
""",
    ["50"],
)
hunter.test(
    "F3: Wrong arg count",
    """
fun add a b
    return a + b
add 1
""",
    should_fail=True,
)
hunter.test(
    "F4: Extra args",
    """
fun add a b
    return a + b
add 1 2 3
""",
    should_fail=True,
)
hunter.test(
    "F5: Function with no args",
    """
fun hello
    return "world"
remember x = hello
print x
""",
    ["world"],
)
hunter.test(
    "F6: Nested function calls",
    """
fun double x
    return x * 2
fun quadruple x
    remember d = double x
    return double d
remember x = quadruple 5
print x
""",
    ["20"],
)
hunter.test(
    "F7: Function returning function result",
    """
fun add a b
    return a + b
print add 3 4
""",
    ["7"],
)
hunter.test(
    "F8: Recursive fibonacci",
    """
fun fib n
    if n smaller or same 1
        return n
    remember a = fib(n - 1)
    remember b = fib(n - 2)
    return a + b
remember x = fib(10)
print x
""",
    ["55"],
)

# ============================================================================
# G. GLOBAL / LOCAL SCOPE
# ============================================================================
hunter.category("G. Global / Local Scope")

hunter.test(
    "G1: Loop counter scope",
    """
repeat 3 times as i
    print i
""",
    ["1", "2", "3"],
)
hunter.test(
    "G2: Function local var not accessible outside",
    """
fun test
    remember local_var = 42
test
print local_var
""",
    should_fail=True,
)
hunter.test(
    "G3: Nested loops different counters",
    """
repeat 2 times as i
    repeat 2 times as j
        print i j
""",
    ["1 1", "1 2", "2 1", "2 2"],
)
hunter.test(
    "G4: Counter var after loop",
    """
repeat 3 times as i
    skip
print i
""",
    ["3"],
)

# ============================================================================
# H. HANDLING EDGE CASES (has, find, empty)
# ============================================================================
hunter.category("H. has/find/empty Edge Cases")

hunter.test(
    "H1: has on empty list",
    """
list x
if has x 1
    print "found"
""",
    [],
)
hunter.test("H2: has on string", 'if has "hello" "ell"\n    print "ok"', ["ok"])
hunter.test(
    "H3: find not found",
    """
list x = 1 2 3
remember pos = find x 99
print pos
""",
    ["0"],
)
hunter.test(
    "H4: find first element",
    """
list x = 10 20 30
remember pos = find x 10
print pos
""",
    ["1"],
)
hunter.test(
    "H5: empty on non-empty",
    """
list x = 1
if empty x
    print "empty"
""",
    [],
)
hunter.test(
    "H6: has on dict",
    """
dict d = {
    "key": "val"
}
if d has "key"
    print "ok"
""",
    ["ok"],
)
hunter.test(
    "H7: has missing key",
    """
dict d = {
    "key": "val"
}
if d has "missing"
    print "found"
""",
    [],
)

# ============================================================================
# I. INDENTATION EDGE CASES
# ============================================================================
hunter.category("I. Indentation Edge Cases")

hunter.test(
    "I1: Mixed spaces (should work)",
    """
if yes
    print "a"
    if yes
        print "b"
""",
    ["a", "b"],
)
hunter.test(
    "I2: Deep nesting",
    """
if yes
    if yes
        if yes
            if yes
                print "deep"
""",
    ["deep"],
)
hunter.test(
    "I3: Empty if block",
    """
if yes
    skip
print "after"
""",
    ["after"],
)

# ============================================================================
# J. JUST KEYWORDS AS VARIABLES
# ============================================================================
hunter.category("J. Keywords as Variables")

hunter.test("J1: Variable named 'sum'", "remember my_sum = 5\nprint my_sum", ["5"])
hunter.test("J2: Variable named 'max'", "remember my_max = 5\nprint my_max", ["5"])
hunter.test("J3: Variable named 'min'", "remember my_min = 5\nprint my_min", ["5"])
hunter.test(
    "J4: Variable named 'count'", "remember my_count = 5\nprint my_count", ["5"]
)
hunter.test("J5: Variable named 'result'", "remember result = 5\nprint result", ["5"])
hunter.test("J6: Variable named 'temp'", "remember temp = 5\nprint temp", ["5"])

# ============================================================================
# K. KEYWORD CONFLICTS
# ============================================================================
hunter.category("K. Keyword Conflicts")

hunter.test(
    "K1: print as variable name", "remember my_print = 5\nprint my_print", ["5"]
)
hunter.test("K2: list as variable name", "remember my_list = 5\nprint my_list", ["5"])
hunter.test(
    "K3: Using 'at' in expression",
    """
list x = 10 20 30
print x at 2
""",
    ["20"],
)
hunter.test(
    "K4: Using 'to' in write",
    """
write "hello" to "/tmp/kido_test_k4.txt"
remember content = read "/tmp/kido_test_k4.txt"
print content
""",
    ["hello"],
)
hunter.test(
    "K5: 'as' for type conversion",
    """
remember x = as string 42
print x
print type x
""",
    ["42", "string"],
)

# ============================================================================
# L. LIST EDGE CASES
# ============================================================================
hunter.category("L. List Edge Cases")

hunter.test(
    "L1: Access index 0 (invalid)",
    """
list x = 1 2 3
print x at 0
""",
    should_fail=True,
)
hunter.test(
    "L2: Access beyond length",
    """
list x = 1 2 3
print x at 10
""",
    should_fail=True,
)
hunter.test(
    "L3: Remove non-existent",
    """
list x = 1 2 3
remove x 99
print length x
""",
    ["3"],
)
hunter.test(
    "L4: Sort empty list",
    """
list x
sort x
print length x
""",
    ["0"],
)
hunter.test(
    "L5: Reverse empty list",
    """
list x
reverse x
print length x
""",
    ["0"],
)
hunter.test(
    "L6: Join empty list",
    """
list x
remember s = join x ","
print s
""",
    [""],
)
hunter.test(
    "L7: Split empty string",
    """
remember parts = split "" ","
print length parts
""",
    ["1"],
)
hunter.test(
    "L8: Combine lists",
    """
list a = 1 2
list b = 3 4
combine a b
print a
""",
    ["1 2 3 4"],
)
hunter.test(
    "L9: Copy list independence",
    """
list a = 1 2 3
list b = copy a
add b 4
print length a
print length b
""",
    ["3", "4"],
)
hunter.test(
    "L10: Replace at index",
    """
list x = 1 2 3
replace x at 2 with 99
print x
""",
    ["1 99 3"],
)
hunter.test(
    "L11: Remove at index",
    """
list x = 1 2 3
remove x at 2
print x
""",
    ["1 3"],
)
hunter.test(
    "L12: Add at position",
    """
list x = 1 3
add x 2 at 2
print x
""",
    ["1 2 3"],
)
hunter.test(
    "L13: Unique with duplicates",
    """
list x = 1 2 2 3 3 3
remember u = unique x
print u
""",
    ["1 2 3"],
)
hunter.test(
    "L14: Sort strings",
    """
list x = "banana" "apple" "cherry"
sort x
print x
""",
    ["apple banana cherry"],
)
hunter.test(
    "L15: Large list",
    """
list x
repeat 100 times as i
    add x i
print length x
print x at 1
print x at 100
""",
    ["100", "1", "100"],
)

# ============================================================================
# M. MATH FUNCTION EDGE CASES
# ============================================================================
hunter.category("M. Math Function Edge Cases")

hunter.test("M1: abs of 0", "print abs 0", ["0"])
hunter.test("M2: sqrt of negative", "print sqrt -1", should_fail=True)
hunter.test("M3: floor of integer", "print floor 5", ["5"])
hunter.test("M4: ceil of integer", "print ceil 5", ["5"])
hunter.test("M5: round of integer", "print round 5", ["5"])
hunter.test("M6: sum of negatives", "print sum -1 -2 -3", ["-6"])
hunter.test("M7: average of one", "print average 42", ["42.0"])
hunter.test("M8: min of negatives", "print min -5 -3 -10", ["-10"])
hunter.test("M9: max of negatives", "print max -5 -3 -10", ["-3"])
hunter.test(
    "M10: pi constant", "remember x = pi\nprint x", None
)  # Just check it doesn't crash
hunter.test("M11: e constant", "remember x = e\nprint x", None)

# ============================================================================
# N. NOTHING / NULL EDGE CASES
# ============================================================================
hunter.category("N. Nothing / Null Edge Cases")

hunter.test(
    "N1: Nothing in list",
    """
list x = 1 nothing 3
print length x
""",
    ["3"],
)
hunter.test(
    "N2: Nothing comparison",
    """
remember x = nothing
if x is nothing
    print "ok"
""",
    ["ok"],
)
hunter.test(
    "N3: Nothing + number",
    """
remember x = nothing
print x + 1
""",
    should_fail=True,
)
hunter.test(
    "N4: Nothing in condition",
    """
remember x = nothing
if x
    print "should not print"
""",
    [],
)

# ============================================================================
# O. OPERATOR PRECEDENCE
# ============================================================================
hunter.category("O. Operator Precedence")

hunter.test("O1: Mult before add", "print 2 + 3 * 4", ["14"])
hunter.test("O2: Div before sub", "print 10 - 6 / 2", ["7.0"])
hunter.test("O3: Power before mult", "print 2 * 3 to the power 2", ["18"])
hunter.test("O4: Unary minus", "print -5 + 3", ["-2"])
hunter.test("O5: Complex expression", "print 2 + 3 * 4 - 1", ["13"])
hunter.test("O6: String concat precedence", 'print "a" + "b" + "c"', ["abc"])

# ============================================================================
# P. PARSING EDGE CASES
# ============================================================================
hunter.category("P. Parsing Edge Cases")

hunter.test("P1: Empty program", "", [])
hunter.test("P2: Only comments", "# just a comment\n# another", [])
hunter.test("P3: Block comment", '/* comment */\nprint "ok"', ["ok"])
hunter.test("P4: Multiple blank lines", 'print "a"\n\n\n\nprint "b"', ["a", "b"])
hunter.test("P5: Trailing whitespace", 'print "ok"   ', ["ok"])
hunter.test("P6: Case insensitive keywords", 'PRINT "ok"', ["ok"])
hunter.test("P7: Case insensitive keywords 2", 'Print "ok"', ["ok"])
hunter.test("P8: String with spaces", 'print "hello world"', ["hello world"])
hunter.test("P9: Empty string", 'print ""', [""])
hunter.test("P10: String with numbers", 'print "abc123"', ["abc123"])
hunter.test("P11: Negative number literal", "print -42", ["-42"])
hunter.test("P12: Float literal", "print 3.14", ["3.14"])

# ============================================================================
# Q. QUEUE / STACK EDGE CASES
# ============================================================================
hunter.category("Q. Queue / Stack Patterns")

hunter.test(
    "Q1: Stack overflow prevention",
    """
list stack
repeat 100 times as i
    add stack i
print length stack
""",
    ["100"],
)
hunter.test(
    "Q2: Queue FIFO order",
    """
list q
add q "first"
add q "second"
add q "third"
remember f = q at 1
remove q at 1
print f
""",
    ["first"],
)

# ============================================================================
# R. RECURSION EDGE CASES
# ============================================================================
hunter.category("R. Recursion Edge Cases")

hunter.test(
    "R1: Base case only",
    """
fun test n
    if n is 0
        return "done"
    return test n - 1
remember x = test 0
print x
""",
    ["done"],
)
hunter.test(
    "R2: Mutual recursion",
    """
fun is_even n
    if n is 0
        return yes
    return is_odd(n - 1)

fun is_odd n
    if n is 0
        return no
    return is_even(n - 1)

remember x = is_even(4)
print x
""",
    ["yes"],
)
hunter.test(
    "R3: Tail recursion pattern",
    """
fun sum_to n acc
    if n is 0
        return acc
    return sum_to(n - 1, acc + n)
remember x = sum_to(10, 0)
print x
""",
    ["55"],
)

# ============================================================================
# S. STRING EDGE CASES
# ============================================================================
hunter.category("S. String Edge Cases")

hunter.test("S1: Length of empty string", 'print length ""', ["0"])
hunter.test("S2: Uppercase empty", 'print uppercase ""', [""])
hunter.test("S3: Lowercase empty", 'print lowercase ""', [""])
hunter.test("S4: Trim empty", 'print trim ""', [""])
hunter.test("S5: String at index 1", 'print "hello" at 1', ["h"])
hunter.test("S6: String at last index", 'print "hello" at 5', ["o"])
hunter.test("S7: String at index 0", 'print "hello" at 0', should_fail=True)
hunter.test("S8: String at beyond length", 'print "hello" at 10', should_fail=True)
hunter.test("S9: Find in string", 'print find "hello world" "world"', ["7"])
hunter.test("S10: Find not found", 'print find "hello" "xyz"', ["0"])
hunter.test("S11: Replace in string", 'print replace "hello" "l" "L"', ["heLLo"])
hunter.test(
    "S12: Split string",
    """
remember parts = split "a,b,c" ","
print parts
""",
    ["a b c"],
)
hunter.test(
    "S13: Join list",
    """
list x = "a" "b" "c"
print join x "-"
""",
    ["a-b-c"],
)
hunter.test("S14: Has substring", 'if has "hello" "ell"\n    print "ok"', ["ok"])
hunter.test("S15: Unicode characters", 'print "Hello 世界"', ["Hello 世界"])
hunter.test("S16: String from to", 'print "Hello World" from 1 to 5', ["Hello"])
hunter.test("S17: First N chars", 'print first "Hello" 3', ["Hel"])
hunter.test("S18: Last N chars", 'print last "Hello" 3', ["llo"])

# ============================================================================
# T. TRY/CATCH EDGE CASES
# ============================================================================
hunter.category("T. Try/Catch Edge Cases")

hunter.test(
    "T1: Catch division by zero",
    """
try
    print 1 / 0
catch err
    print "caught"
""",
    ["caught"],
)
hunter.test(
    "T2: Catch undefined var",
    """
try
    print undefined
catch err
    print "caught"
""",
    ["caught"],
)
hunter.test(
    "T3: No error in try",
    """
try
    print "ok"
catch err
    print "should not print"
""",
    ["ok"],
)
hunter.test(
    "T4: Throw custom error",
    """
try
    throw "my error"
catch err
    print err
""",
    None,
)  # Just check it doesn't crash
hunter.test(
    "T5: Nested try/catch",
    """
try
    try
        print 1 / 0
    catch err
        print "inner"
catch err
    print "outer"
""",
    ["inner"],
)

# ============================================================================
# U. UNARY OPERATORS
# ============================================================================
hunter.category("U. Unary Operators")

hunter.test("U1: Unary minus", "print -5", ["-5"])
hunter.test("U2: Double negative", "print - -5", ["5"])
hunter.test(
    "U3: Not yes",
    """
remember x = not yes
print x
""",
    ["no"],
)
hunter.test(
    "U4: Not no",
    """
remember x = not no
print x
""",
    ["yes"],
)
hunter.test(
    "U5: Not number",
    """
remember x = not 5
print x
""",
    ["no"],
)
hunter.test(
    "U6: Not zero",
    """
remember x = not 0
print x
""",
    ["yes"],
)

# ============================================================================
# V. VARIABLE EDGE CASES
# ============================================================================
hunter.category("V. Variable Edge Cases")

hunter.test(
    "V1: Long variable name",
    "remember this_is_a_very_long_variable_name = 42\nprint this_is_a_very_long_variable_name",
    ["42"],
)
hunter.test("V2: Variable with numbers", "remember var123 = 42\nprint var123", ["42"])
hunter.test(
    "V3: Variable starting with underscore",
    "remember _private = 42\nprint _private",
    ["42"],
)
hunter.test(
    "V4: Reassign different type",
    """
remember x = 5
remember x = "hello"
print x
""",
    ["hello"],
)
hunter.test(
    "V5: Self-reference",
    """
remember x = 5
remember x = x + 1
print x
""",
    ["6"],
)

# ============================================================================
# W. WRITE/READ EDGE CASES
# ============================================================================
hunter.category("W. Write/Read Edge Cases")

hunter.test(
    "W1: Write and read",
    """
write "test" to "/tmp/kido_w1.txt"
remember content = read "/tmp/kido_w1.txt"
print content
""",
    ["test"],
)
hunter.test(
    "W2: Append to file",
    """
write "hello" to "/tmp/kido_w2.txt"
append " world" to "/tmp/kido_w2.txt"
remember content = read "/tmp/kido_w2.txt"
print content
""",
    ["hello world"],
)
hunter.test(
    "W3: Read non-existent file",
    """
remember x = read "/tmp/kido_nonexistent_999.txt"
""",
    should_fail=True,
)
hunter.test(
    "W4: File exists check",
    """
write "test" to "/tmp/kido_w4.txt"
if file exists "/tmp/kido_w4.txt"
    print "exists"
""",
    ["exists"],
)
hunter.test(
    "W5: Delete file",
    """
write "test" to "/tmp/kido_w5.txt"
delete "/tmp/kido_w5.txt"
if file exists "/tmp/kido_w5.txt"
    print "exists"
""",
    [],
)

# ============================================================================
# X. EXTREME EDGE CASES
# ============================================================================
hunter.category("X. Extreme Edge Cases")

hunter.test(
    "X1: 100 nested ifs",
    """
if yes
    if yes
        if yes
            if yes
                if yes
                    if yes
                        if yes
                            if yes
                                if yes
                                    if yes
                                        print "deep"
""",
    ["deep"],
)
hunter.test(
    "X2: Long chain of additions", "print 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1", ["10"]
)
hunter.test(
    "X3: Many function args",
    """
fun sum5 a b c d e
    return a + b + c + d + e
remember x = sum5 1 2 3 4 5
print x
""",
    ["15"],
)
hunter.test("X4: Print nothing literal", "print nothing", ["nothing"])
hunter.test(
    "X5: Empty function body",
    """
fun empty_func
    skip
empty_func
print "after"
""",
    ["after"],
)

# ============================================================================
# Y. YES/NO EDGE CASES
# ============================================================================
hunter.category("Y. Yes/No Edge Cases")

hunter.test(
    "Y1: yes in list",
    """
list x = yes no yes
print x
""",
    ["yes no yes"],
)
hunter.test(
    "Y2: yes as return",
    """
fun test
    return yes
remember x = test
print x
""",
    ["yes"],
)
hunter.test(
    "Y3: no as return",
    """
fun test
    return no
remember x = test
print x
""",
    ["no"],
)
hunter.test(
    "Y4: yes in condition",
    """
if yes
    print "ok"
""",
    ["ok"],
)
hunter.test(
    "Y5: no in condition",
    """
if no
    print "should not print"
""",
    [],
)

# ============================================================================
# Z. ZERO / BOUNDARY EDGE CASES
# ============================================================================
hunter.category("Z. Zero / Boundary Edge Cases")

hunter.test(
    "Z1: Repeat 0 times",
    """
repeat 0 times
    print "should not print"
print "done"
""",
    ["done"],
)
hunter.test(
    "Z2: Repeat 1 time",
    """
repeat 1 times
    print "once"
""",
    ["once"],
)
hunter.test(
    "Z3: List with one element",
    """
list x = 42
print x at 1
""",
    ["42"],
)
hunter.test("Z4: String of length 1", 'print length "a"', ["1"])
hunter.test(
    "Z5: Zero in list",
    """
list x = 0
print x at 1
""",
    ["0"],
)
hunter.test(
    "Z6: Negative index",
    """
list x = 1 2 3
print x at -1
""",
    should_fail=True,
)
hunter.test(
    "Z7: Very large repeat",
    """
remember count = 0
repeat 1000 times
    remember count = count + 1
print count
""",
    ["1000"],
)
hunter.test(
    "Z8: Stop in first iteration",
    """
repeat 100 times as i
    if i is 1
        stop
    print i
""",
    [],
)
hunter.test(
    "Z9: Skip all iterations",
    """
repeat 5 times as i
    skip
    print "should not print"
print "done"
""",
    ["done"],
)
hunter.test(
    "Z10: For each empty list",
    """
list x
for each item in x
    print "should not print"
print "done"
""",
    ["done"],
)

# ============================================================================
# SUMMARY
# ============================================================================
hunter.summary()
