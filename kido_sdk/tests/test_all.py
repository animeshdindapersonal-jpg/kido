#!/usr/bin/env python3
"""
KIDO Comprehensive Test Suite
Tests all language features end-to-end
"""

import sys
import os
import subprocess
import tempfile

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kido_core.lexer import tokenize
from kido_core.parser import parse
from kido_core.interpreter import Interpreter, run
from kido_core.errors import *


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test(self, name, func):
        """Run a single test"""
        try:
            func()
            self.passed += 1
            print(f"  ✅ {name}")
        except Exception as e:
            self.failed += 1
            self.errors.append((name, str(e)))
            print(f"  ❌ {name}: {e}")

    def summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print()
        print("=" * 60)
        print(f"TESTS: {total} | PASSED: {self.passed} | FAILED: {self.failed}")
        print("=" * 60)

        if self.errors:
            print()
            print("FAILURES:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")

        return self.failed == 0


def run_kido(source):
    """Run KIDO code and capture output"""
    interp = run(source)
    return interp.output


# ============================================================================
# TEST SUITE
# ============================================================================

runner = TestRunner()

print("🧒 KIDO Test Suite v1.0")
print("=" * 60)
print()

# ----------------------------------------------------------------------------
print("📝 LEXER TESTS")
# ----------------------------------------------------------------------------


def test_lexer_basic():
    tokens = tokenize('print "Hello"')
    assert tokens[0].type == "KEYWORD"
    assert tokens[0].value == "print"
    assert tokens[1].type == "STRING"
    assert tokens[1].value == "Hello"


def test_lexer_numbers():
    tokens = tokenize("remember x = 42")
    assert tokens[3].type == "NUMBER"
    assert tokens[3].value == 42


def test_lexer_float():
    tokens = tokenize("remember pi = 3.14")
    assert tokens[3].value == 3.14


def test_lexer_keywords_case():
    tokens = tokenize('PRINT "hi"')
    assert tokens[0].type == "KEYWORD"
    assert tokens[0].value == "print"


def test_lexer_comments():
    tokens = tokenize('# this is a comment\nprint "hi"')
    # Comment should be skipped
    assert tokens[0].type == "KEYWORD"
    assert tokens[0].value == "print"


def test_lexer_block_comment():
    tokens = tokenize('/* comment */\nprint "hi"')
    # Find the first non-newline, non-indent/dedent token
    meaningful = [t for t in tokens if t.type not in ("NEWLINE", "INDENT", "DEDENT")]
    assert meaningful[0].type == "KEYWORD"
    assert meaningful[0].value == "print"


def test_lexer_operators():
    tokens = tokenize("5 + 3 * 2")
    assert tokens[1].type == "PLUS"
    assert tokens[3].type == "STAR"


def test_lexer_negative():
    tokens = tokenize("remember x = -5")
    assert tokens[3].type == "NUMBER"
    assert tokens[3].value == -5


runner.test("Basic tokenization", test_lexer_basic)
runner.test("Number tokens", test_lexer_numbers)
runner.test("Float tokens", test_lexer_float)
runner.test("Case-insensitive keywords", test_lexer_keywords_case)
runner.test("Line comments", test_lexer_comments)
runner.test("Block comments", test_lexer_block_comment)
runner.test("Operators", test_lexer_operators)
runner.test("Negative numbers", test_lexer_negative)

# ----------------------------------------------------------------------------
print()
print("🌳 PARSER TESTS")
# ----------------------------------------------------------------------------


def test_parser_print():
    tokens = tokenize('print "Hello"')
    ast = parse(tokens)
    assert len(ast.statements) == 1


def test_parser_remember():
    tokens = tokenize("remember x = 5")
    ast = parse(tokens)
    assert ast.statements[0].name == "x"


def test_parser_if():
    source = """if x bigger 5
    print "big"
"""
    tokens = tokenize(source)
    ast = parse(tokens)
    assert len(ast.statements) == 1


def test_parser_repeat():
    source = """repeat 3 times
    print "hi"
"""
    tokens = tokenize(source)
    ast = parse(tokens)
    assert len(ast.statements) == 1


def test_parser_fun():
    source = """fun greet name
    print "Hi" name
"""
    tokens = tokenize(source)
    ast = parse(tokens)
    assert ast.statements[0].name == "greet"


def test_parser_list():
    source = 'list fruits = "apple" "banana"'
    tokens = tokenize(source)
    ast = parse(tokens)
    assert len(ast.statements) == 1


def test_parser_dict():
    source = """dict d = {
    "name": "test"
}"""
    tokens = tokenize(source)
    ast = parse(tokens)
    assert len(ast.statements) == 1


runner.test("Print statement", test_parser_print)
runner.test("Remember statement", test_parser_remember)
runner.test("If statement", test_parser_if)
runner.test("Repeat statement", test_parser_repeat)
runner.test("Function definition", test_parser_fun)
runner.test("List creation", test_parser_list)
runner.test("Dict creation", test_parser_dict)

# ----------------------------------------------------------------------------
print()
print("🖨️  PRINT TESTS")
# ----------------------------------------------------------------------------


def test_print_string():
    out = run_kido('print "Hello"')
    assert out == ["Hello"]


def test_print_number():
    out = run_kido("print 42")
    assert out == ["42"]


def test_print_expression():
    out = run_kido("print 2 + 3")
    assert out == ["5"]


def test_print_multiple():
    out = run_kido('print "Hi" "World"')
    assert out == ["Hi World"]


def test_print_variable():
    out = run_kido("remember x = 10\nprint x")
    assert out == ["10"]


def test_print_boolean():
    out = run_kido("print yes\nprint no")
    assert out == ["yes", "no"]


def test_print_nothing():
    out = run_kido("print nothing")
    assert out == ["nothing"]


runner.test("Print string", test_print_string)
runner.test("Print number", test_print_number)
runner.test("Print expression", test_print_expression)
runner.test("Print multiple values", test_print_multiple)
runner.test("Print variable", test_print_variable)
runner.test("Print boolean", test_print_boolean)
runner.test("Print nothing", test_print_nothing)

# ----------------------------------------------------------------------------
print()
print("📦 VARIABLE TESTS")
# ----------------------------------------------------------------------------


def test_var_assign():
    out = run_kido("remember x = 5\nprint x")
    assert out == ["5"]


def test_var_string():
    out = run_kido('remember name = "Tom"\nprint name')
    assert out == ["Tom"]


def test_var_update():
    out = run_kido("remember x = 5\nremember x = 10\nprint x")
    assert out == ["10"]


def test_const():
    out = run_kido("const MY_CONST = 42\nprint MY_CONST")
    assert out == ["42"]


def test_const_error():
    try:
        run_kido("const X = 5\nremember X = 10")
        assert False, "Should have raised error"
    except RuntimeError_:
        pass


runner.test("Variable assignment", test_var_assign)
runner.test("String variable", test_var_string)
runner.test("Variable update", test_var_update)
runner.test("Constant", test_const)
runner.test("Constant immutability", test_const_error)

# ----------------------------------------------------------------------------
print()
print("🔢 MATH TESTS")
# ----------------------------------------------------------------------------


def test_add():
    out = run_kido("print 5 + 3")
    assert out == ["8"]


def test_subtract():
    out = run_kido("print 10 - 4")
    assert out == ["6"]


def test_multiply():
    out = run_kido("print 6 * 7")
    assert out == ["42"]


def test_divide():
    out = run_kido("print 20 / 4")
    assert out == ["5.0"]


def test_power():
    out = run_kido("print 2 to the power 10")
    assert out == ["1024"]


def test_divide_zero():
    try:
        run_kido("print 5 / 0")
        assert False, "Should raise ZeroDivisionError"
    except ZeroDivisionError_:
        pass


def test_negative():
    out = run_kido("print -5 + 3")
    assert out == ["-2"]


def test_precedence():
    out = run_kido("print 2 + 3 * 4")
    assert out == ["14"]


runner.test("Addition", test_add)
runner.test("Subtraction", test_subtract)
runner.test("Multiplication", test_multiply)
runner.test("Division", test_divide)
runner.test("Power", test_power)
runner.test("Division by zero", test_divide_zero)
runner.test("Negative numbers", test_negative)
runner.test("Operator precedence", test_precedence)

# ----------------------------------------------------------------------------
print()
print("🔀 CONDITIONAL TESTS")
# ----------------------------------------------------------------------------


def test_if_true():
    out = run_kido('if 5 bigger 3\n    print "yes"')
    assert out == ["yes"]


def test_if_false():
    out = run_kido('if 3 bigger 5\n    print "yes"')
    assert out == []


def test_if_else():
    out = run_kido("""if 3 bigger 5
    print "big"
else
    print "small"
""")
    assert out == ["small"]


def test_if_equals():
    out = run_kido("""remember x = 5
if x is 5
    print "match"
""")
    assert out == ["match"]


def test_if_and():
    out = run_kido("""remember x = 7
if x bigger 5 and x smaller 10
    print "in range"
""")
    assert out == ["in range"]


def test_if_or():
    out = run_kido("""remember x = 3
if x is 3 or x is 5
    print "match"
""")
    assert out == ["match"]


def test_if_not():
    out = run_kido("""if not no
    print "yes"
""")
    assert out == ["yes"]


runner.test("If true", test_if_true)
runner.test("If false", test_if_false)
runner.test("If else", test_if_else)
runner.test("If equals (is)", test_if_equals)
runner.test("If with and", test_if_and)
runner.test("If with or", test_if_or)
runner.test("If with not", test_if_not)

# ----------------------------------------------------------------------------
print()
print("🔁 LOOP TESTS")
# ----------------------------------------------------------------------------


def test_repeat_times():
    out = run_kido("""repeat 3 times
    print "hi"
""")
    assert out == ["hi", "hi", "hi"]


def test_repeat_counter():
    out = run_kido("""repeat 3 times as i
    print i
""")
    assert out == ["1", "2", "3"]


def test_repeat_stop():
    out = run_kido("""repeat 10 times as i
    if i is 3
        stop
    print i
""")
    assert out == ["1", "2"]


def test_repeat_skip():
    out = run_kido("""repeat 5 times as i
    if i is 3
        skip
    print i
""")
    assert out == ["1", "2", "4", "5"]


def test_nested_loops():
    out = run_kido("""remember total = 0
repeat 3 times
    repeat 2 times
        remember total = total + 1
print total
""")
    assert out == ["6"]


runner.test("Repeat N times", test_repeat_times)
runner.test("Repeat with counter", test_repeat_counter)
runner.test("Stop in loop", test_repeat_stop)
runner.test("Skip in loop", test_repeat_skip)
runner.test("Nested loops", test_nested_loops)

# ----------------------------------------------------------------------------
print()
print("🎯 FUNCTION TESTS")
# ----------------------------------------------------------------------------


def test_fun_basic():
    out = run_kido("""fun greet
    print "Hello!"

greet
""")
    assert out == ["Hello!"]


def test_fun_params():
    out = run_kido("""fun greet name
    print "Hi" name
greet "Tom"
""")
    assert out == ["Hi Tom"]


def test_fun_return():
    out = run_kido("""fun add a b
    return a + b
remember result = add 3 4
print result
""")
    assert out == ["7"]


def test_fun_multiple_returns():
    out = run_kido("""fun get_pair
    return 1 2

remember a b = get_pair
print a b
""")
    assert out == ["1 2"]


def test_fun_recursive():
    out = run_kido("""fun factorial n
    if n smaller or same 1
        return 1
    return n * factorial(n - 1)

remember result = factorial(5)
print result
""")
    assert out == ["120"]


runner.test("Basic function", test_fun_basic)
runner.test("Function with params", test_fun_params)
runner.test("Function return", test_fun_return)
runner.test("Multiple return values", test_fun_multiple_returns)
runner.test("Recursive function", test_fun_recursive)

# ----------------------------------------------------------------------------
print()
print("📚 LIST TESTS")
# ----------------------------------------------------------------------------


def test_list_create():
    out = run_kido("""list fruits = "apple" "banana" "mango"
print length fruits
""")
    assert out == ["3"]


def test_list_access():
    out = run_kido("""list fruits = "apple" "banana" "mango"
print fruits at 1
print fruits at 2
""")
    assert out == ["apple", "banana"]


def test_list_add():
    out = run_kido("""list fruits = "apple"
add fruits "banana"
print length fruits
""")
    assert out == ["2"]


def test_list_remove():
    out = run_kido("""list fruits = "apple" "banana"
remove fruits "apple"
print length fruits
""")
    assert out == ["1"]


def test_list_has():
    out = run_kido("""list fruits = "apple" "banana"
if has fruits "apple"
    print "found"
""")
    assert out == ["found"]


def test_list_sort():
    out = run_kido("""list nums = 3 1 2
sort nums
print nums
""")
    assert out == ["1 2 3"]


def test_list_reverse():
    out = run_kido("""list nums = 1 2 3
reverse nums
print nums
""")
    assert out == ["3 2 1"]


def test_list_empty():
    out = run_kido("""list empty_list
if empty empty_list
    print "empty"
""")
    assert out == ["empty"]


def test_list_join():
    out = run_kido("""list fruits = "a" "b" "c"
print join fruits ", "
""")
    assert out == ["a, b, c"]


def test_list_find():
    out = run_kido("""list fruits = "apple" "banana" "mango"
print find fruits "banana"
""")
    assert out == ["2"]


runner.test("List creation", test_list_create)
runner.test("List access", test_list_access)
runner.test("List add", test_list_add)
runner.test("List remove", test_list_remove)
runner.test("List has", test_list_has)
runner.test("List sort", test_list_sort)
runner.test("List reverse", test_list_reverse)
runner.test("List empty", test_list_empty)
runner.test("List join", test_list_join)
runner.test("List find", test_list_find)

# ----------------------------------------------------------------------------
print()
print("📖 DICTIONARY TESTS")
# ----------------------------------------------------------------------------


def test_dict_create():
    out = run_kido("""dict d = {
    "name": "Tom"
}
print d at "name"
""")
    assert out == ["Tom"]


def test_dict_keys():
    out = run_kido("""dict d = {
    "a": 1,
    "b": 2
}
remember k = keys d
print length k
""")
    assert out == ["2"]


def test_dict_has():
    out = run_kido("""dict d = {
    "name": "Tom"
}
if d has "name"
    print "yes"
""")
    assert out == ["yes"]


runner.test("Dict creation", test_dict_create)
runner.test("Dict keys", test_dict_keys)
runner.test("Dict has", test_dict_has)

# ----------------------------------------------------------------------------
print()
print("📝 STRING TESTS")
# ----------------------------------------------------------------------------


def test_string_length():
    out = run_kido('print length "Hello"')
    assert out == ["5"]


def test_string_uppercase():
    out = run_kido('print uppercase "hello"')
    assert out == ["HELLO"]


def test_string_lowercase():
    out = run_kido('print lowercase "HELLO"')
    assert out == ["hello"]


def test_string_trim():
    out = run_kido('print trim "  hi  "')
    assert out == ["hi"]


def test_string_replace():
    out = run_kido('print replace "Hello World" "World" "KIDO"')
    assert out == ["Hello KIDO"]


def test_string_split():
    out = run_kido("""remember parts = split "a,b,c" ","
print length parts
""")
    assert out == ["3"]


def test_string_concat():
    out = run_kido('print "Hello" + " " + "World"')
    assert out == ["Hello World"]


runner.test("String length", test_string_length)
runner.test("String uppercase", test_string_uppercase)
runner.test("String lowercase", test_string_lowercase)
runner.test("String trim", test_string_trim)
runner.test("String replace", test_string_replace)
runner.test("String split", test_string_split)
runner.test("String concatenation", test_string_concat)

# ----------------------------------------------------------------------------
print()
print("🔧 TYPE TESTS")
# ----------------------------------------------------------------------------


def test_type_number():
    out = run_kido("print type 42")
    assert out == ["number"]


def test_type_string():
    out = run_kido('print type "hi"')
    assert out == ["string"]


def test_type_yesno():
    out = run_kido("""remember flag = yes
print type flag
""")
    assert out == ["yesno"]


def test_type_list():
    out = run_kido("""list x = 1 2 3
print type x
""")
    assert out == ["list"]


def test_as_number():
    out = run_kido("""remember x = as number "42"
print x
""")
    assert out == ["42"]


def test_as_string():
    out = run_kido("""remember x = as string 42
print x
""")
    assert out == ["42"]


runner.test("Type number", test_type_number)
runner.test("Type string", test_type_string)
runner.test("Type yesno", test_type_yesno)
runner.test("Type list", test_type_list)
runner.test("As number", test_as_number)
runner.test("As string", test_as_string)

# ----------------------------------------------------------------------------
print()
print("🎲 RANDOM TESTS")
# ----------------------------------------------------------------------------


def test_random_range():
    out = run_kido("""remember x = random 1 10
if x bigger or same 1
    if x smaller or same 10
        print "ok"
""")
    assert out == ["ok"]


def test_random_list():
    out = run_kido("""list items = "a" "b" "c"
remember x = random items
if has items x
    print "ok"
""")
    assert out == ["ok"]


runner.test("Random in range", test_random_range)
runner.test("Random from list", test_random_list)

# ----------------------------------------------------------------------------
print()
print("📐 MATH FUNCTION TESTS")
# ----------------------------------------------------------------------------


def test_abs():
    out = run_kido("print abs -5")
    assert out == ["5"]


def test_sqrt():
    out = run_kido("print sqrt 16")
    assert out == ["4.0"]


def test_min():
    out = run_kido("print min 5 3 8")
    assert out == ["3"]


def test_max():
    out = run_kido("print max 5 3 8")
    assert out == ["8"]


def test_sum():
    out = run_kido("print sum 1 2 3 4 5")
    assert out == ["15"]


runner.test("abs()", test_abs)
runner.test("sqrt()", test_sqrt)
runner.test("min()", test_min)
runner.test("max()", test_max)
runner.test("sum()", test_sum)

# ----------------------------------------------------------------------------
print()
print("🛡️  ERROR HANDLING TESTS")
# ----------------------------------------------------------------------------


def test_try_catch():
    out = run_kido("""try
    remember x = 5 / 0
catch error
    print "caught"
""")
    assert out == ["caught"]


def test_throw():
    out = run_kido("""try
    throw "custom error"
catch error
    print error
""")
    assert "custom error" in out[0]


runner.test("Try/catch", test_try_catch)
runner.test("Throw", test_throw)

# ----------------------------------------------------------------------------
print()
print("📁 FILE I/O TESTS")
# ----------------------------------------------------------------------------


def test_file_write_read():
    with tempfile.TemporaryDirectory() as tmpdir:
        source = """write "Hello KIDO" to "test.txt"
remember content = read "test.txt"
print content
"""
        interp = run(source, base_dir=tmpdir)
        assert interp.output == ["Hello KIDO"]


def test_file_append():
    with tempfile.TemporaryDirectory() as tmpdir:
        source = """write "Line 1" to "test.txt"
append " Line 2" to "test.txt"
remember content = read "test.txt"
print content
"""
        interp = run(source, base_dir=tmpdir)
        assert "Line 1 Line 2" in interp.output[0]


runner.test("File write/read", test_file_write_read)
runner.test("File append", test_file_append)

# ----------------------------------------------------------------------------
print()
print("🏗️  COMPLEX PROGRAM TESTS")
# ----------------------------------------------------------------------------


def test_fibonacci():
    out = run_kido("""fun fib n
    if n smaller or same 1
        return n
    remember a = fib(n - 1)
    remember b = fib(n - 2)
    return a + b

repeat 7 times as i
    remember val = fib(i - 1)
    print val
""")
    assert out == ["0", "1", "1", "2", "3", "5", "8"]


def test_bubble_sort():
    out = run_kido("""list nums = 5 3 8 1 2

# KIDO has a built-in sort
sort nums
print nums
""")
    assert out == ["1 2 3 5 8"]


def test_string_reverse():
    out = run_kido("""remember s = "Hello"
remember result = ""
remember len = length s
repeat len times as i
    remember idx = len - i + 1
    remember ch = s at idx
    remember result = result + ch
print result
""")
    assert out == ["olleH"]


runner.test("Fibonacci sequence", test_fibonacci)
runner.test("Bubble sort", test_bubble_sort)
runner.test("String reverse function", test_string_reverse)

# ----------------------------------------------------------------------------
print()
print("📂 EXAMPLE FILE TESTS")
# ----------------------------------------------------------------------------

examples_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples"
)

example_files = [
    "hello.kd",
    "shopping_list.kd",
    "grades.kd",
    "functions.kd",
    "dictionaries.kd",
    "rps.kd",
    "math_demo.kd",
    "strings.kd",
]

for example_file in example_files:
    filepath = os.path.join(examples_dir, example_file)
    if os.path.exists(filepath):

        def test_example(fp=filepath):
            with open(fp, "r", encoding="utf-8") as f:
                source = f.read()
            interp = run(source, fp, os.path.dirname(fp))
            assert len(interp.output) > 0, "No output produced"

        runner.test(f"Example: {example_file}", test_example)
    else:
        print(f"  ⏭️  Example: {example_file} (not found)")

# ============================================================================
# SUMMARY
# ============================================================================

success = runner.summary()
sys.exit(0 if success else 1)
