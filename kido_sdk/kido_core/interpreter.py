"""
KIDO Interpreter - Executes AST nodes
"""

import os
import sys
import time
import json
import random
import math
from datetime import datetime

from .parser import (
    Program, PrintStatement, RememberStatement, MultiRememberStatement,
    ConstStatement, AskStatement, IfStatement, RepeatTimesStatement,
    RepeatForeverStatement, ForEachStatement, FunDefStatement, ReturnStatement,
    StopStatement, SkipStatement, ThrowStatement, TryCatchStatement,
    WaitStatement, ListStatement, DictStatement, UseStatement,
    ExpressionStatement, NumberLiteral, StringLiteral, BooleanLiteral,
    NothingLiteral, Identifier, BinaryOp, UnaryOp, FunctionCall,
    ListAccess, DictAccess, ListLiteral, DictLiteral
)
from .environment import Environment
from .errors import (
    KidoError, NameError_, TypeError_, ValueError_, IndexError_,
    KeyError_, ZeroDivisionError_, FileNotFoundError_, RuntimeError_,
    SecurityError_, StopExecution, BreakLoop, SkipIteration, ReturnSignal,
    CONTROL_FLOW,
)
from .security import (
    resolve_safe_path, check_file_size, check_source_size,
    check_wait_seconds, check_power, check_loop_count,
    RecursionGuard, LoopGuard, MAX_FILE_BYTES,
)


class Function:
    """Represents a user-defined function"""
    def __init__(self, name, params, block, closure):
        self.name = name
        self.params = params
        self.block = block
        self.closure = closure


class Interpreter:
    def __init__(self, filename="<input>", base_dir=None):
        self.filename = filename
        self.base_dir = os.path.realpath(os.path.abspath(base_dir or os.getcwd()))
        self.global_env = Environment()
        self.output = []  # Capture output for testing
        self._recursion = RecursionGuard()
        self._loop_guard = LoopGuard()
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Setup built-in constants"""
        self.global_env.set('pi', math.pi, is_const=True)
        self.global_env.set('e', math.e, is_const=True)

    def _safe_path(self, user_path, line=None, must_exist=False, for_write=False):
        """Resolve a user path inside the project sandbox."""
        return resolve_safe_path(
            self.base_dir, user_path,
            line=line, must_exist=must_exist, for_write=for_write,
        )
    
    def execute(self, program):
        """Execute a program (AST)"""
        if not isinstance(program, Program):
            raise RuntimeError_("Expected Program node")
        
        try:
            for stmt in program.statements:
                self.execute_statement(stmt, self.global_env)
        except StopExecution:
            pass  # Normal program termination
        except BreakLoop:
            raise RuntimeError_("'stop' used outside of a loop")
        except SkipIteration:
            raise RuntimeError_("'skip' used outside of a loop")
        except RecursionError:
            raise SecurityError_(
                "Too many nested function calls.",
                suggestion="Check for infinite recursion. Prefer fun(n - 1) with parentheses."
            )
    
    def execute_statement(self, stmt, env):
        """Execute a single statement"""
        if isinstance(stmt, PrintStatement):
            self.execute_print(stmt, env)
        elif isinstance(stmt, RememberStatement):
            self.execute_remember(stmt, env)
        elif isinstance(stmt, MultiRememberStatement):
            self.execute_multi_remember(stmt, env)
        elif isinstance(stmt, ConstStatement):
            self.execute_const(stmt, env)
        elif isinstance(stmt, AskStatement):
            self.execute_ask(stmt, env)
        elif isinstance(stmt, IfStatement):
            self.execute_if(stmt, env)
        elif isinstance(stmt, RepeatTimesStatement):
            self.execute_repeat_times(stmt, env)
        elif isinstance(stmt, RepeatForeverStatement):
            self.execute_repeat_forever(stmt, env)
        elif isinstance(stmt, ForEachStatement):
            self.execute_for_each(stmt, env)
        elif isinstance(stmt, FunDefStatement):
            self.execute_fun_def(stmt, env)
        elif isinstance(stmt, ReturnStatement):
            self.execute_return(stmt, env)
        elif isinstance(stmt, StopStatement):
            raise BreakLoop()
        elif isinstance(stmt, SkipStatement):
            raise SkipIteration()
        elif isinstance(stmt, ThrowStatement):
            self.execute_throw(stmt, env)
        elif isinstance(stmt, TryCatchStatement):
            self.execute_try_catch(stmt, env)
        elif isinstance(stmt, WaitStatement):
            self.execute_wait(stmt, env)
        elif isinstance(stmt, ListStatement):
            self.execute_list(stmt, env)
        elif isinstance(stmt, DictStatement):
            self.execute_dict(stmt, env)
        elif isinstance(stmt, UseStatement):
            self.execute_use(stmt, env)
        elif isinstance(stmt, ExpressionStatement):
            result = self.evaluate(stmt.expression, env)
            # If the expression evaluates to a Function, auto-call it
            if isinstance(result, Function) and result.name:
                self.call_function(result, [], env, stmt.line)
        else:
            raise RuntimeError_(f"Unknown statement type: {type(stmt).__name__}")
    
    def execute_print(self, stmt, env):
        values = []
        for i, expr in enumerate(stmt.expressions):
            val = self.evaluate(expr, env)
            # If first value is a Function, call it with remaining values as args
            if i == 0 and isinstance(val, Function) and len(stmt.expressions) > 1:
                # Collect remaining expressions as arguments
                arg_values = []
                for j in range(1, len(stmt.expressions)):
                    arg_val = self.evaluate(stmt.expressions[j], env)
                    arg_values.append(arg_val)
                # Call the function with these arguments
                if len(arg_values) != len(val.params):
                    raise RuntimeError_(
                        f"Function '{val.name}' expects {len(val.params)} arguments, got {len(arg_values)}",
                        expr.line
                    )
                # Create function scope and execute
                func_env = val.closure.child_scope()
                for param, arg in zip(val.params, arg_values):
                    func_env.set(param, arg)
                try:
                    for s in val.block:
                        self.execute_statement(s, func_env)
                    val = None
                except ReturnSignal as ret:
                    val = ret.value
                # Don't process remaining expressions
                values.append(val)
                break
            # Auto-call if value is a Function with no params
            elif isinstance(val, Function) and len(val.params) == 0:
                val = self.call_function(val, [], env, expr.line)
            values.append(val)
        output = ' '.join(self._to_string(v) for v in values)
        print(output)
        self.output.append(output)
    
    def execute_remember(self, stmt, env):
        # Check if trying to reassign a constant
        if env.is_constant(stmt.name):
            raise RuntimeError_(f"Cannot reassign constant '{stmt.name}'", stmt.line)
        
        value = self.evaluate(stmt.value, env)
        # Auto-call if value is a Function with no params
        if isinstance(value, Function) and len(value.params) == 0:
            value = self.call_function(value, [], env, stmt.line)
        # Always set in current scope (proper lexical scoping)
        env.set(stmt.name, value)
    
    def execute_multi_remember(self, stmt, env):
        value = self.evaluate(stmt.value, env)
        
        # If value is a function, call it first
        if isinstance(value, Function):
            try:
                value = self.call_function(value, [], env, stmt.line)
            except ReturnSignal:
                pass
        
        if isinstance(value, (list, tuple)):
            if len(value) != len(stmt.names):
                raise RuntimeError_(
                    f"Expected {len(stmt.names)} values, got {len(value)}",
                    stmt.line
                )
            for name, val in zip(stmt.names, value):
                env.set(name, val)
        else:
            # Single value - assign to first, rest get nothing
            env.set(stmt.names[0], value)
            for name in stmt.names[1:]:
                env.set(name, None)
    
    def execute_const(self, stmt, env):
        value = self.evaluate(stmt.value, env)
        env.set(stmt.name, value, is_const=True)
    
    def execute_ask(self, stmt, env):
        prompt = self._to_string(self.evaluate(stmt.prompt, env))
        value = input(prompt + " ")
        # Try to convert to number if possible
        try:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass  # Keep as string
        env.set(stmt.variable, value)
    
    def execute_if(self, stmt, env):
        condition = self.evaluate(stmt.condition, env)
        if self._is_truthy(condition):
            for s in stmt.then_block:
                self.execute_statement(s, env)
        elif stmt.else_block:
            for s in stmt.else_block:
                self.execute_statement(s, env)
    
    def execute_repeat_times(self, stmt, env):
        count = check_loop_count(self.evaluate(stmt.count, env), stmt.line)
        for i in range(1, count + 1):
            self._loop_guard.tick(stmt.line)
            try:
                if stmt.counter_var:
                    env.set(stmt.counter_var, i)
                for s in stmt.block:
                    self.execute_statement(s, env)
            except SkipIteration:
                continue
            except BreakLoop:
                break
            except StopExecution:
                raise
    
    def execute_repeat_forever(self, stmt, env):
        while True:
            self._loop_guard.tick(stmt.line)
            try:
                for s in stmt.block:
                    self.execute_statement(s, env)
            except SkipIteration:
                continue
            except BreakLoop:
                break
            except StopExecution:
                raise
    
    def execute_for_each(self, stmt, env):
        iterable = self.evaluate(stmt.iterable, env)
        if not isinstance(iterable, list):
            raise TypeError_(
                f"for each requires a list, got {type(iterable).__name__}",
                stmt.line
            )
        
        for item in iterable:
            self._loop_guard.tick(stmt.line)
            try:
                env.set(stmt.variable, item)
                for s in stmt.block:
                    self.execute_statement(s, env)
            except SkipIteration:
                continue
            except BreakLoop:
                break
            except StopExecution:
                raise
    
    def execute_fun_def(self, stmt, env):
        func = Function(stmt.name, stmt.params, stmt.block, env)
        env.set(stmt.name, func)
    
    def execute_return(self, stmt, env):
        values = [self.evaluate(v, env) for v in stmt.values]
        if len(values) == 0:
            raise ReturnSignal(None)
        elif len(values) == 1:
            raise ReturnSignal(values[0])
        else:
            raise ReturnSignal(values)
    
    def execute_throw(self, stmt, env):
        message = self.evaluate(stmt.message, env)
        raise RuntimeError_(self._to_string(message), stmt.line)
    
    def execute_try_catch(self, stmt, env):
        try:
            for s in stmt.try_block:
                self.execute_statement(s, env)
        except CONTROL_FLOW:
            # stop / skip / return / break must never be swallowed by catch
            raise
        except SecurityError_:
            # Security violations are not catchable (sandbox integrity)
            raise
        except KidoError as e:
            env.set(stmt.catch_var, e.message)
            for s in stmt.catch_block:
                self.execute_statement(s, env)
        except Exception as e:
            # Hide internal Python details from kid-facing catch variable
            env.set(stmt.catch_var, "Something unexpected went wrong.")
            for s in stmt.catch_block:
                self.execute_statement(s, env)
    
    def execute_wait(self, stmt, env):
        seconds = check_wait_seconds(self.evaluate(stmt.seconds, env), stmt.line)
        time.sleep(seconds)
    
    def execute_list(self, stmt, env):
        items = [self.evaluate(item, env) for item in stmt.items]
        # If there's exactly one item and it's a list, use it directly
        # This allows: list b = copy a  (instead of wrapping in another list)
        if len(items) == 1 and isinstance(items[0], list):
            env.set(stmt.name, items[0])
        else:
            env.set(stmt.name, items)
    
    def execute_dict(self, stmt, env):
        pairs = {}
        for key, value in stmt.pairs.items():
            pairs[key] = self.evaluate(value, env)
        env.set(stmt.name, pairs)
    
    def execute_use(self, stmt, env):
        filepath = self._safe_path(stmt.filename, stmt.line, must_exist=True)
        if not filepath.endswith('.kd'):
            raise SecurityError_(
                "Modules must be .kd files.",
                stmt.line,
                "Use a file like 'helpers.kd'."
            )
        check_file_size(filepath, stmt.line)

        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        check_source_size(source, stmt.line)
        
        from .lexer import tokenize
        from .parser import parse
        
        tokens = tokenize(source, filepath)
        program = parse(tokens, filepath)
        
        # Execute the module (keep sandbox root; do not widen base_dir)
        old_base_dir = self.base_dir
        module_dir = os.path.dirname(filepath)
        # Module dir must still be under original sandbox — already enforced
        self.base_dir = module_dir
        
        try:
            for s in program.statements:
                self.execute_statement(s, env)
        finally:
            self.base_dir = old_base_dir
    
    def evaluate(self, expr, env):
        """Evaluate an expression"""
        if isinstance(expr, NumberLiteral):
            return expr.value
        elif isinstance(expr, StringLiteral):
            return expr.value
        elif isinstance(expr, BooleanLiteral):
            return expr.value
        elif isinstance(expr, NothingLiteral):
            return None
        elif isinstance(expr, Identifier):
            return env.get(expr.name, expr.line)
        elif isinstance(expr, BinaryOp):
            return self.evaluate_binary_op(expr, env)
        elif isinstance(expr, UnaryOp):
            return self.evaluate_unary_op(expr, env)
        elif isinstance(expr, FunctionCall):
            return self.evaluate_function_call(expr, env)
        elif isinstance(expr, ListAccess):
            return self.evaluate_list_access(expr, env)
        elif isinstance(expr, DictAccess):
            return self.evaluate_dict_access(expr, env)
        elif isinstance(expr, ListLiteral):
            return [self.evaluate(item, env) for item in expr.items]
        elif isinstance(expr, DictLiteral):
            return {k: self.evaluate(v, env) for k, v in expr.pairs.items()}
        else:
            raise RuntimeError_(f"Unknown expression type: {type(expr).__name__}")
    
    def evaluate_binary_op(self, expr, env):
        left = self.evaluate(expr.left, env)
        
        # Short-circuit for logical operators
        if expr.op == 'and':
            if not self._is_truthy(left):
                return left
            return self.evaluate(expr.right, env)
        elif expr.op == 'or':
            if self._is_truthy(left):
                return left
            return self.evaluate(expr.right, env)
        
        right = self.evaluate(expr.right, env)
        
        # Arithmetic
        if expr.op == '+':
            # Check for type mismatches
            if isinstance(left, str) and isinstance(right, (int, float)):
                raise TypeError_("Cannot add string and number. Use 'as string' to convert.", expr.line)
            if isinstance(right, str) and isinstance(left, (int, float)):
                raise TypeError_("Cannot add number and string. Use 'as string' to convert.", expr.line)
            if isinstance(left, bool) or isinstance(right, bool):
                if isinstance(left, (int, float)) and not isinstance(left, bool):
                    raise TypeError_("Cannot add number and yes/no", expr.line)
                if isinstance(right, (int, float)) and not isinstance(right, bool):
                    raise TypeError_("Cannot add yes/no and number", expr.line)
            
            if isinstance(left, str) or isinstance(right, str):
                return self._to_string(left) + self._to_string(right)
            return left + right
        elif expr.op == '-':
            return left - right
        elif expr.op == '*':
            return left * right
        elif expr.op == '/':
            if right == 0:
                raise ZeroDivisionError_(expr.line)
            return left / right
        elif expr.op == '**':
            return check_power(left, right, expr.line)
        
        # Comparison
        elif expr.op == 'is':
            return left == right
        elif expr.op == '>':
            return left > right
        elif expr.op == '<':
            return left < right
        elif expr.op == '>=':
            return left >= right
        elif expr.op == '<=':
            return left <= right
        elif expr.op == 'has':
            if isinstance(left, (list, str)):
                return right in left
            elif isinstance(left, dict):
                return right in left
            return False
        elif expr.op == 'starts_with':
            return str(left).startswith(str(right))
        elif expr.op == 'ends_with':
            return str(left).endswith(str(right))
        
        raise RuntimeError_(f"Unknown operator: {expr.op}")
    
    def evaluate_unary_op(self, expr, env):
        operand = self.evaluate(expr.operand, env)
        
        if expr.op == '-':
            return -operand
        elif expr.op == 'not':
            return not self._is_truthy(operand)
        
        raise RuntimeError_(f"Unknown unary operator: {expr.op}")
    
    def evaluate_function_call(self, expr, env):
        # Check if it's a user-defined function
        if env.has(expr.name):
            func = env.get(expr.name)
            if isinstance(func, Function):
                return self.call_function(func, expr.args, env, expr.line)
        
        # Built-in function
        return self.call_builtin(expr.name, expr.args, env, expr.line)
    
    def call_function(self, func, arg_nodes, caller_env, line):
        # Evaluate args before entering recursion frame
        args = [self.evaluate(arg, caller_env) for arg in arg_nodes]
        
        if len(args) != len(func.params):
            raise RuntimeError_(
                f"Function '{func.name}' expects {len(func.params)} arguments, got {len(args)}",
                line
            )
        
        self._recursion.enter(line)
        try:
            # Create new scope
            func_env = func.closure.child_scope()
            for param, arg in zip(func.params, args):
                func_env.set(param, arg)
            
            # Execute function body
            try:
                for stmt in func.block:
                    self.execute_statement(stmt, func_env)
                return None
            except ReturnSignal as ret:
                return ret.value
            except RecursionError:
                # Python stack exhausted before our logical guard (deep call chains)
                raise SecurityError_(
                    f"Too many nested function calls (max {self._recursion.max_depth}).",
                    line,
                    "Check for infinite recursion. Use parentheses: fun(n - 1)."
                )
        finally:
            self._recursion.leave()
    
    def call_builtin(self, name, arg_nodes, env, line):
        args = [self.evaluate(arg, env) for arg in arg_nodes]
        
        # List operations
        if name == 'add':
            if len(args) < 2:
                raise RuntimeError_("add requires a list and a value", line)
            lst, value = args[0], args[1]
            if not isinstance(lst, list):
                raise TypeError_("add requires a list", line)
            # Check if third arg is 'at' keyword (add at position)
            if len(args) >= 4 and args[2] == 'at':
                idx = int(args[3]) - 1  # 1-indexed to 0-indexed
                if idx < 0:
                    idx = 0
                if idx > len(lst):
                    idx = len(lst)
                lst.insert(idx, value)
                return None
            lst.append(value)
            return None
        
        elif name == 'remove':
            if len(args) < 2:
                raise RuntimeError_("remove requires a list and a value", line)
            lst = args[0]
            if not isinstance(lst, list):
                raise TypeError_("remove requires a list", line)
            # Check if second arg is 'at' keyword (remove by position)
            if len(args) >= 3 and args[1] == 'at':
                idx = int(args[2]) - 1  # 1-indexed to 0-indexed
                if 0 <= idx < len(lst):
                    lst.pop(idx)
                return None
            # Remove by value
            value = args[1]
            if value in lst:
                lst.remove(value)
            return None
        
        elif name == 'length':
            if len(args) != 1:
                raise RuntimeError_("length requires 1 argument", line)
            return len(args[0])
        
        elif name == 'has':
            if len(args) != 2:
                raise RuntimeError_("has requires 2 arguments", line)
            container, item = args
            if isinstance(container, list):
                return item in container
            elif isinstance(container, dict):
                return item in container
            elif isinstance(container, str):
                return item in container
            return False
        
        elif name == 'find':
            if len(args) != 2:
                raise RuntimeError_("find requires 2 arguments", line)
            container, item = args
            if isinstance(container, list):
                try:
                    return container.index(item) + 1  # 1-indexed
                except ValueError:
                    return 0
            elif isinstance(container, str):
                return container.find(item) + 1 if item in container else 0
            return 0
        
        elif name == 'empty':
            if len(args) != 1:
                raise RuntimeError_("empty requires 1 argument", line)
            return len(args[0]) == 0
        
        elif name == 'sort':
            if len(args) != 1:
                raise RuntimeError_("sort requires 1 argument", line)
            if not isinstance(args[0], list):
                raise TypeError_("sort requires a list", line)
            args[0].sort()
            return None
        
        elif name == 'reverse':
            if len(args) != 1:
                raise RuntimeError_("reverse requires 1 argument", line)
            if isinstance(args[0], list):
                args[0].reverse()
            elif isinstance(args[0], str):
                return args[0][::-1]
            return None
        
        elif name == 'shuffle':
            if len(args) != 1:
                raise RuntimeError_("shuffle requires 1 argument", line)
            if not isinstance(args[0], list):
                raise TypeError_("shuffle requires a list", line)
            random.shuffle(args[0])
            return None
        
        elif name == 'copy':
            if len(args) != 1:
                raise RuntimeError_("copy requires 1 argument", line)
            if isinstance(args[0], list):
                return args[0].copy()
            elif isinstance(args[0], dict):
                return args[0].copy()
            return args[0]
        
        elif name == 'combine':
            if len(args) != 2:
                raise RuntimeError_("combine requires 2 arguments", line)
            if not isinstance(args[0], list) or not isinstance(args[1], list):
                raise TypeError_("combine requires two lists", line)
            args[0].extend(args[1])
            return None
        
        elif name == 'join':
            if len(args) != 2:
                raise RuntimeError_("join requires 2 arguments", line)
            if not isinstance(args[0], list):
                raise TypeError_("join requires a list", line)
            return args[1].join(self._to_string(x) for x in args[0])
        
        elif name == 'split':
            if len(args) != 2:
                raise RuntimeError_("split requires 2 arguments", line)
            return args[0].split(args[1])
        
        elif name == 'clear':
            if len(args) != 1:
                raise RuntimeError_("clear requires 1 argument", line)
            if isinstance(args[0], list):
                args[0].clear()
            elif isinstance(args[0], dict):
                args[0].clear()
            return None
        
        elif name == 'unique':
            if len(args) != 1:
                raise RuntimeError_("unique requires 1 argument", line)
            if not isinstance(args[0], list):
                raise TypeError_("unique requires a list", line)
            return list(dict.fromkeys(args[0]))
        
        elif name == 'replace':
            if len(args) < 2:
                raise RuntimeError_("replace requires at least 2 arguments", line)
            # String replace: replace text old new
            if isinstance(args[0], str) and len(args) == 3:
                return self._to_string(args[0]).replace(
                    self._to_string(args[1]),
                    self._to_string(args[2])
                )
            # List replace: replace list at index with value
            if len(args) >= 5 and args[1] == 'at' and args[3] == 'with':
                lst = args[0]
                if not isinstance(lst, list):
                    raise TypeError_("replace requires a list", line)
                idx = int(args[2]) - 1
                if idx < 0 or idx >= len(lst):
                    raise IndexError_(f"Index {int(args[2])} out of range", line)
                lst[idx] = args[4]
                return None
            # Also handle string replace with 3 args where first is not str
            if len(args) == 3:
                return self._to_string(args[0]).replace(
                    self._to_string(args[1]),
                    self._to_string(args[2])
                )
            raise RuntimeError_("replace syntax: replace text old new OR replace list at index with value", line)
        
        elif name == 'substring':
            if len(args) != 3:
                raise RuntimeError_("substring requires 3 arguments: text, start, length", line)
            text = self._to_string(args[0])
            start = int(args[1]) - 1
            length = int(args[2])
            return text[start:start + length]
        
        # String operations
        elif name == 'uppercase':
            if len(args) != 1:
                raise RuntimeError_("uppercase requires 1 argument", line)
            return self._to_string(args[0]).upper()
        
        elif name == 'lowercase':
            if len(args) != 1:
                raise RuntimeError_("lowercase requires 1 argument", line)
            return self._to_string(args[0]).lower()
        
        elif name == 'trim':
            if len(args) != 1:
                raise RuntimeError_("trim requires 1 argument", line)
            return self._to_string(args[0]).strip()
        
        elif name == 'replace':
            if len(args) != 3:
                raise RuntimeError_("replace requires 3 arguments", line)
            return self._to_string(args[0]).replace(
                self._to_string(args[1]),
                self._to_string(args[2])
            )
        
        # Type operations
        elif name == 'type':
            if len(args) != 1:
                raise RuntimeError_("type requires 1 argument", line)
            val = args[0]
            if isinstance(val, bool):
                return 'yesno'
            elif isinstance(val, int):
                return 'number'
            elif isinstance(val, float):
                return 'number'
            elif isinstance(val, str):
                return 'string'
            elif isinstance(val, list):
                return 'list'
            elif isinstance(val, dict):
                return 'dict'
            elif val is None:
                return 'nothing'
            return 'unknown'
        
        elif name == 'as':
            if len(args) < 2:
                raise RuntimeError_("as requires 2 arguments", line)
            target_type = args[0] if isinstance(args[0], str) else self._to_string(args[0])
            value = args[1]
            
            if target_type == 'string':
                return self._to_string(value)
            elif target_type == 'number':
                try:
                    if isinstance(value, str) and '.' in value:
                        return float(value)
                    return int(value)
                except ValueError:
                    raise ValueError_(f"Cannot convert '{value}' to number", line)
            elif target_type == 'yesno':
                return self._is_truthy(value)
            return value
        
        # Math operations
        elif name == 'abs':
            return abs(args[0])
        elif name == 'round':
            return round(args[0])
        elif name == 'floor':
            return math.floor(args[0])
        elif name == 'ceil':
            return math.ceil(args[0])
        elif name == 'sqrt':
            return math.sqrt(args[0])
        elif name == 'min':
            if len(args) == 1 and isinstance(args[0], list):
                return min(args[0])
            return min(args)
        elif name == 'max':
            if len(args) == 1 and isinstance(args[0], list):
                return max(args[0])
            return max(args)
        elif name == 'sum':
            if len(args) == 1 and isinstance(args[0], list):
                if len(args[0]) == 0:
                    raise RuntimeError_("Cannot sum an empty list", line)
                return sum(args[0])
            return sum(args)
        elif name == 'average':
            if len(args) == 1 and isinstance(args[0], list):
                lst = args[0]
            else:
                lst = args
            if len(lst) == 0:
                raise RuntimeError_("Cannot average an empty list", line)
            return sum(lst) / len(lst)
        
        # Random
        elif name == 'random':
            if len(args) == 0:
                return random.random()
            elif len(args) == 1:
                if isinstance(args[0], list):
                    return random.choice(args[0]) if args[0] else None
                return random.randint(1, int(args[0]))
            elif len(args) == 2:
                return random.randint(int(args[0]), int(args[1]))
        
        # Dict operations
        elif name == 'set':
            if len(args) >= 3 and isinstance(args[0], dict):
                args[0][args[1]] = args[2]
                return None
            raise RuntimeError_("set requires: set dict key value", line)
        
        elif name == 'get':
            if len(args) >= 2 and isinstance(args[0], dict):
                return args[0].get(args[1])
            raise RuntimeError_("get requires: get dict key", line)
        
        elif name == 'keys':
            if len(args) != 1 or not isinstance(args[0], dict):
                raise TypeError_("keys requires a dictionary", line)
            return list(args[0].keys())
        
        elif name == 'values':
            if len(args) != 1 or not isinstance(args[0], dict):
                raise TypeError_("values requires a dictionary", line)
            return list(args[0].values())
        
        # File operations (sandboxed under project base_dir)
        elif name == 'read':
            if len(args) < 1:
                raise RuntimeError_("read requires a filename", line)
            # Handle "read lines file" and "read json file" and "read csv file"
            if isinstance(args[0], str) and args[0] in ('lines', 'json', 'csv'):
                if len(args) < 2:
                    raise RuntimeError_(f"read {args[0]} requires a filename", line)
                filepath = self._safe_path(args[1], line, must_exist=True)
                check_file_size(filepath, line)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                if args[0] == 'lines':
                    return content.splitlines()
                elif args[0] == 'json':
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        raise ValueError_("Invalid JSON in file", line)
                elif args[0] == 'csv':
                    return content.strip().split(',')
            filepath = self._safe_path(args[0], line, must_exist=True)
            check_file_size(filepath, line)
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif name == 'write':
            if len(args) < 2:
                raise RuntimeError_("write syntax: write content to filename", line)
            # Handle "write content to filename" (args[1] might be 'to')
            if len(args) >= 3 and args[1] == 'to':
                user_path = args[2]
                content = args[0]
            elif len(args) == 2:
                user_path = args[1]
                content = args[0]
            else:
                raise RuntimeError_("write syntax: write content to filename", line)
            
            if isinstance(content, str) and content == 'as':
                pass  # reserved for future json serialization syntax
            
            text = (
                json.dumps(content, indent=2)
                if isinstance(content, (dict, list))
                else self._to_string(content)
            )
            if len(text.encode('utf-8', errors='replace')) > MAX_FILE_BYTES:
                raise SecurityError_(
                    f"Content too large to write (max {MAX_FILE_BYTES} bytes).",
                    line
                )
            filepath = self._safe_path(user_path, line, for_write=True)
            parent = os.path.dirname(filepath)
            if parent and not os.path.isdir(parent):
                # Only create parents that stay inside sandbox (already validated)
                os.makedirs(parent, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            return None
        
        elif name == 'append':
            if len(args) < 2:
                raise RuntimeError_("append syntax: append content to filename", line)
            if len(args) >= 3 and args[1] == 'to':
                user_path = args[2]
                content = args[0]
            elif len(args) == 2:
                user_path = args[1]
                content = args[0]
            else:
                raise RuntimeError_("append syntax: append content to filename", line)
            
            text = self._to_string(content)
            filepath = self._safe_path(user_path, line, for_write=True)
            # Cap append so a loop cannot fill the disk
            existing = 0
            if os.path.exists(filepath):
                try:
                    existing = os.path.getsize(filepath)
                except OSError:
                    existing = 0
            if existing + len(text.encode('utf-8', errors='replace')) > MAX_FILE_BYTES:
                raise SecurityError_(
                    f"File would exceed max size ({MAX_FILE_BYTES} bytes).",
                    line
                )
            parent = os.path.dirname(filepath)
            if parent and not os.path.isdir(parent):
                os.makedirs(parent, exist_ok=True)
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(text)
            return None
        
        elif name == 'delete':
            if len(args) != 1:
                raise RuntimeError_("delete requires a filename", line)
            filepath = self._safe_path(args[0], line)
            # Refuse to delete directories; only regular files
            if os.path.isfile(filepath):
                os.remove(filepath)
            elif os.path.isdir(filepath):
                raise SecurityError_(
                    "Cannot delete a folder with 'delete'.",
                    line,
                    "Only files can be deleted."
                )
            return None
        
        elif name == 'file':
            if len(args) >= 2 and args[0] == 'exists':
                try:
                    filepath = self._safe_path(args[1], line)
                    return os.path.exists(filepath)
                except SecurityError_:
                    return False
            if len(args) >= 2 and args[0] == 'size':
                filepath = self._safe_path(args[1], line, must_exist=True)
                return os.path.getsize(filepath)
            raise RuntimeError_("Unknown file operation", line)
        
        elif name == 'folder':
            if len(args) >= 2 and args[0] == 'exists':
                try:
                    dirpath = self._safe_path(args[1], line)
                    return os.path.isdir(dirpath)
                except SecurityError_:
                    return False
            raise RuntimeError_("Unknown folder operation", line)
        
        elif name == 'create':
            if len(args) >= 2 and args[0] == 'folder':
                dirpath = self._safe_path(args[1], line, for_write=True)
                os.makedirs(dirpath, exist_ok=True)
                return None
            raise RuntimeError_("Unknown create operation", line)
        
        # Date/Time
        elif name == 'today':
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif name == 'year':
            return datetime.now().year
        elif name == 'month':
            return datetime.now().month
        elif name == 'day':
            return datetime.now().day
        elif name == 'hour':
            return datetime.now().hour
        elif name == 'minute':
            return datetime.now().minute
        
        raise RuntimeError_(f"Unknown function: {name}", line)
    
    def evaluate_list_access(self, expr, env):
        lst = self.evaluate(expr.list_expr, env)
        index = self.evaluate(expr.index, env)
        
        if isinstance(lst, list):
            if not isinstance(index, (int, float)):
                raise TypeError_("List index must be a number", expr.line)
            idx = int(index) - 1  # Convert to 0-indexed
            if idx < 0 or idx >= len(lst):
                raise IndexError_(
                    f"List index {int(index)} out of range (1 to {len(lst)})",
                    expr.line
                )
            return lst[idx]
        elif isinstance(lst, dict):
            if index not in lst:
                raise KeyError_(f"Key '{index}' not found", expr.line)
            return lst[index]
        elif isinstance(lst, str):
            if not isinstance(index, (int, float)):
                raise TypeError_("String index must be a number", expr.line)
            idx = int(index) - 1
            if idx < 0 or idx >= len(lst):
                raise IndexError_(
                    f"String index {int(index)} out of range",
                    expr.line
                )
            return lst[idx]
        
        raise TypeError_("Cannot use 'at' with this type", expr.line)
    
    def evaluate_dict_access(self, expr, env):
        dct = self.evaluate(expr.dict_expr, env)
        key = self.evaluate(expr.key, env)
        
        if not isinstance(dct, dict):
            raise TypeError_("Expected dictionary", expr.line)
        if key not in dct:
            raise KeyError_(f"Key '{key}' not found", expr.line)
        return dct[key]
    
    def _is_truthy(self, value):
        """Check if a value is truthy"""
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True
    
    def _to_string(self, value):
        """Convert a value to string for display"""
        if value is None:
            return 'nothing'
        if isinstance(value, bool):
            return 'yes' if value else 'no'
        if isinstance(value, list):
            return ' '.join(self._to_string(x) for x in value)
        if isinstance(value, dict):
            return str(value)
        return str(value)


def run(source, filename="<input>", base_dir=None):
    """Run KIDO source code"""
    from .lexer import tokenize
    from .parser import parse

    check_source_size(source)
    tokens = tokenize(source, filename)
    program = parse(tokens, filename)
    interpreter = Interpreter(filename, base_dir)
    interpreter.execute(program)
    return interpreter


def run_file(filepath):
    """Run a .kd file"""
    abs_path = os.path.realpath(os.path.abspath(filepath))
    if not os.path.isfile(abs_path):
        raise FileNotFoundError_(f"File not found: {filepath}")
    if not abs_path.lower().endswith('.kd'):
        raise SecurityError_(
            "Only .kd files can be run.",
            suggestion="Use a file ending in .kd"
        )
    check_file_size(abs_path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        source = f.read()
    return run(source, abs_path, os.path.dirname(abs_path))
