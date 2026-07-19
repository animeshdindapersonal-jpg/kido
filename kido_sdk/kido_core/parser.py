"""
KIDO Parser - Builds AST from tokens
"""

from .lexer import *
from .errors import SyntaxError_


# AST Node Types
class ASTNode:
    pass


class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements


class PrintStatement(ASTNode):
    def __init__(self, expressions, line):
        self.expressions = expressions
        self.line = line


class RememberStatement(ASTNode):
    def __init__(self, name, value, line):
        self.name = name
        self.value = value
        self.line = line


class MultiRememberStatement(ASTNode):
    def __init__(self, names, value, line):
        self.names = names
        self.value = value
        self.line = line


class ConstStatement(ASTNode):
    def __init__(self, name, value, line):
        self.name = name
        self.value = value
        self.line = line


class AskStatement(ASTNode):
    def __init__(self, prompt, variable, line):
        self.prompt = prompt
        self.variable = variable
        self.line = line


class IfStatement(ASTNode):
    def __init__(self, condition, then_block, else_block, line):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
        self.line = line


class RepeatTimesStatement(ASTNode):
    def __init__(self, count, counter_var, block, line):
        self.count = count
        self.counter_var = counter_var
        self.block = block
        self.line = line


class RepeatForeverStatement(ASTNode):
    def __init__(self, block, line):
        self.block = block
        self.line = line


class ForEachStatement(ASTNode):
    def __init__(self, variable, iterable, block, line):
        self.variable = variable
        self.iterable = iterable
        self.block = block
        self.line = line


class FunDefStatement(ASTNode):
    def __init__(self, name, params, block, line):
        self.name = name
        self.params = params
        self.block = block
        self.line = line


class ReturnStatement(ASTNode):
    def __init__(self, values, line):
        self.values = values
        self.line = line


class StopStatement(ASTNode):
    def __init__(self, line):
        self.line = line


class SkipStatement(ASTNode):
    def __init__(self, line):
        self.line = line


class ThrowStatement(ASTNode):
    def __init__(self, message, line):
        self.message = message
        self.line = line


class TryCatchStatement(ASTNode):
    def __init__(self, try_block, catch_var, catch_block, line):
        self.try_block = try_block
        self.catch_var = catch_var
        self.catch_block = catch_block
        self.line = line


class WaitStatement(ASTNode):
    def __init__(self, seconds, line):
        self.seconds = seconds
        self.line = line


class ListStatement(ASTNode):
    def __init__(self, name, items, line):
        self.name = name
        self.items = items
        self.line = line


class DictStatement(ASTNode):
    def __init__(self, name, pairs, line):
        self.name = name
        self.pairs = pairs
        self.line = line


class UseStatement(ASTNode):
    def __init__(self, filename, imports, line):
        self.filename = filename
        self.imports = imports  # None means import all
        self.line = line


class ExpressionStatement(ASTNode):
    def __init__(self, expression, line):
        self.expression = expression
        self.line = line


# Expression nodes
class NumberLiteral(ASTNode):
    def __init__(self, value, line):
        self.value = value
        self.line = line


class StringLiteral(ASTNode):
    def __init__(self, value, line):
        self.value = value
        self.line = line


class BooleanLiteral(ASTNode):
    def __init__(self, value, line):
        self.value = value
        self.line = line


class NothingLiteral(ASTNode):
    def __init__(self, line):
        self.line = line


class Identifier(ASTNode):
    def __init__(self, name, line):
        self.name = name
        self.line = line


class BinaryOp(ASTNode):
    def __init__(self, left, op, right, line):
        self.left = left
        self.op = op
        self.right = right
        self.line = line


class UnaryOp(ASTNode):
    def __init__(self, op, operand, line):
        self.op = op
        self.operand = operand
        self.line = line


class FunctionCall(ASTNode):
    def __init__(self, name, args, line):
        self.name = name
        self.args = args
        self.line = line


class ListAccess(ASTNode):
    def __init__(self, list_expr, index, line):
        self.list_expr = list_expr
        self.index = index
        self.line = line


class DictAccess(ASTNode):
    def __init__(self, dict_expr, key, line):
        self.dict_expr = dict_expr
        self.key = key
        self.line = line


class ListLiteral(ASTNode):
    def __init__(self, items, line):
        self.items = items
        self.line = line


class DictLiteral(ASTNode):
    def __init__(self, pairs, line):
        self.pairs = pairs
        self.line = line


class Parser:
    def __init__(self, tokens, filename="<input>"):
        self.tokens = tokens
        self.filename = filename
        self.pos = 0

    def error(self, msg, token=None):
        if token is None:
            token = self.current()
        raise SyntaxError_(msg, token.line, token.col)

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(EOF, None, 0, 0)

    def peek(self, offset=1):
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return Token(EOF, None, 0, 0)

    def advance(self):
        token = self.current()
        self.pos += 1
        return token

    def expect(self, type_, value=None):
        token = self.current()
        if token.type != type_:
            self.error(f"Expected {type_}, got {token.type}", token)
        if value is not None and token.value != value:
            self.error(f"Expected '{value}', got '{token.value}'", token)
        return self.advance()

    def match(self, type_, value=None):
        token = self.current()
        if token.type == type_:
            if value is None or token.value == value:
                return self.advance()
        return None

    def skip_newlines(self):
        while self.current().type == NEWLINE:
            self.advance()

    def parse(self):
        """Parse the entire program"""
        statements = []
        self.skip_newlines()

        while self.current().type != EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()

        return Program(statements)

    def parse_statement(self):
        """Parse a single statement"""
        token = self.current()

        if token.type == KEYWORD:
            if token.value == "print":
                return self.parse_print()
            elif token.value == "remember":
                return self.parse_remember()
            elif token.value == "const":
                return self.parse_const()
            elif token.value == "ask":
                return self.parse_ask()
            elif token.value == "if":
                return self.parse_if()
            elif token.value == "repeat":
                return self.parse_repeat()
            elif token.value == "for":
                return self.parse_for_each()
            elif token.value == "fun":
                return self.parse_fun_def()
            elif token.value == "return":
                return self.parse_return()
            elif token.value == "stop":
                return self.parse_stop()
            elif token.value == "skip":
                return self.parse_skip()
            elif token.value == "throw":
                return self.parse_throw()
            elif token.value == "try":
                return self.parse_try_catch()
            elif token.value == "wait":
                return self.parse_wait()
            elif token.value == "list":
                return self.parse_list()
            elif token.value == "dict":
                return self.parse_dict()
            elif token.value == "use":
                return self.parse_use()

        # Expression statement (function call, assignment, etc.)
        return self.parse_expression_statement()

    def parse_print(self):
        line = self.current().line
        self.expect(KEYWORD, "print")
        expressions = []

        while self.current().type not in (NEWLINE, EOF, DEDENT) and not (
            self.current().type == KEYWORD and self.current().value in ("else", "catch")
        ):
            expressions.append(self._parse_simple_expr())

        return PrintStatement(expressions, line)

    def parse_remember(self):
        line = self.current().line
        self.expect(KEYWORD, "remember")

        # Accept IDENT or KEYWORD as variable name
        token = self.current()
        if token.type == IDENT:
            name = self.advance().value
        elif token.type == KEYWORD:
            name = self.advance().value
        else:
            self.error(f"Expected variable name", token)

        # Check for multiple assignment: remember a b = func()
        names = [name]
        while self.current().type == IDENT:
            names.append(self.advance().value)

        self.expect(EQUALS)
        value = self.parse_expression()

        if len(names) == 1:
            return RememberStatement(names[0], value, line)
        else:
            return MultiRememberStatement(names, value, line)

    def parse_const(self):
        line = self.current().line
        self.expect(KEYWORD, "const")
        # Accept IDENT or KEYWORD as constant name (e.g., const PI = 3.14)
        token = self.current()
        if token.type == IDENT:
            name = self.advance().value
        elif token.type == KEYWORD:
            name = self.advance().value
        else:
            self.error(f"Expected constant name", token)
        self.expect(EQUALS)
        value = self.parse_expression()
        return ConstStatement(name, value, line)

    def parse_ask(self):
        line = self.current().line
        self.expect(KEYWORD, "ask")
        prompt = self.parse_expression()
        variable = self.expect(IDENT).value
        return AskStatement(prompt, variable, line)

    def parse_if(self):
        line = self.current().line
        self.expect(KEYWORD, "if")
        condition = self.parse_expression()

        self.skip_newlines()
        self.expect(INDENT)
        then_block = self.parse_block()
        self.expect(DEDENT)

        else_block = []
        self.skip_newlines()
        if self.match(KEYWORD, "else"):
            if self.current().type == KEYWORD and self.current().value == "if":
                # else if
                else_block = [self.parse_if()]
            else:
                self.skip_newlines()
                self.expect(INDENT)
                else_block = self.parse_block()
                self.expect(DEDENT)

        return IfStatement(condition, then_block, else_block, line)

    def parse_repeat(self):
        line = self.current().line
        self.expect(KEYWORD, "repeat")

        if self.match(KEYWORD, "forever"):
            self.skip_newlines()
            self.expect(INDENT)
            block = self.parse_block()
            self.expect(DEDENT)
            return RepeatForeverStatement(block, line)

        count = self.parse_expression()
        self.expect(KEYWORD, "times")

        counter_var = None
        if self.match(KEYWORD, "as"):
            counter_var = self.expect(IDENT).value

        self.skip_newlines()
        self.expect(INDENT)
        block = self.parse_block()
        self.expect(DEDENT)

        return RepeatTimesStatement(count, counter_var, block, line)

    def parse_for_each(self):
        line = self.current().line
        self.expect(KEYWORD, "for")
        self.expect(KEYWORD, "each")
        variable = self.expect(IDENT).value
        self.expect(KEYWORD, "in")
        iterable = self.parse_expression()

        self.skip_newlines()
        self.expect(INDENT)
        block = self.parse_block()
        self.expect(DEDENT)

        return ForEachStatement(variable, iterable, block, line)

    def parse_fun_def(self):
        line = self.current().line
        self.expect(KEYWORD, "fun")
        # Accept IDENT or KEYWORD as function name (e.g., fun add a b)
        token = self.current()
        if token.type == IDENT:
            name = self.advance().value
        elif token.type == KEYWORD:
            name = self.advance().value
        else:
            self.error(f"Expected function name", token)

        params = []
        while self.current().type == IDENT:
            params.append(self.advance().value)

        self.skip_newlines()
        self.expect(INDENT)
        block = self.parse_block()
        self.expect(DEDENT)

        return FunDefStatement(name, params, block, line)

    def parse_return(self):
        line = self.current().line
        self.expect(KEYWORD, "return")

        values = []
        while self.current().type not in (NEWLINE, EOF, DEDENT):
            values.append(self.parse_expression())

        return ReturnStatement(values, line)

    def parse_stop(self):
        line = self.current().line
        self.expect(KEYWORD, "stop")
        return StopStatement(line)

    def parse_skip(self):
        line = self.current().line
        self.expect(KEYWORD, "skip")
        return SkipStatement(line)

    def parse_throw(self):
        line = self.current().line
        self.expect(KEYWORD, "throw")
        message = self.parse_expression()
        return ThrowStatement(message, line)

    def parse_try_catch(self):
        line = self.current().line
        self.expect(KEYWORD, "try")
        self.skip_newlines()
        self.expect(INDENT)
        try_block = self.parse_block()
        self.expect(DEDENT)

        self.skip_newlines()
        self.expect(KEYWORD, "catch")
        catch_var = self.expect(IDENT).value

        self.skip_newlines()
        self.expect(INDENT)
        catch_block = self.parse_block()
        self.expect(DEDENT)

        return TryCatchStatement(try_block, catch_var, catch_block, line)

    def parse_wait(self):
        line = self.current().line
        self.expect(KEYWORD, "wait")
        seconds = self.parse_expression()
        return WaitStatement(seconds, line)

    def parse_list(self):
        line = self.current().line
        self.expect(KEYWORD, "list")
        name = self.expect(IDENT).value

        items = []
        if self.match(EQUALS):
            while self.current().type not in (NEWLINE, EOF, DEDENT):
                items.append(self.parse_expression())

        return ListStatement(name, items, line)

    def parse_dict(self):
        line = self.current().line
        self.expect(KEYWORD, "dict")
        name = self.expect(IDENT).value

        pairs = {}
        if self.match(EQUALS):
            self.expect(LBRACE)
            self.skip_newlines()

            # Handle optional INDENT inside braces
            has_indent = False
            if self.current().type == INDENT:
                self.advance()
                has_indent = True

            while self.current().type not in (RBRACE, DEDENT, EOF):
                self.skip_newlines()
                if self.current().type in (RBRACE, DEDENT, EOF):
                    break

                key = self.parse_expression()
                self.expect(COLON)
                value = self.parse_expression()
                key_str = (
                    key.value if isinstance(key, StringLiteral) else str(key.value)
                )
                pairs[key_str] = value

                if not self.match(COMMA):
                    self.skip_newlines()

            if has_indent and self.current().type == DEDENT:
                self.advance()

            self.skip_newlines()
            self.expect(RBRACE)

        return DictStatement(name, pairs, line)

    def parse_use(self):
        line = self.current().line
        self.expect(KEYWORD, "use")
        filename = self.expect(STRING).value

        imports = None
        if self.match(KEYWORD, "bring"):
            imports = []
            while self.current().type == IDENT:
                imports.append(self.advance().value)

        return UseStatement(filename, imports, line)

    def parse_expression_statement(self):
        """Parse expression statement (function call or assignment)"""
        line = self.current().line

        # Special handling for write/append statements
        if self.current().type == KEYWORD and self.current().value in (
            "write",
            "append",
        ):
            return self.parse_write_append(line)

        # Special handling for replace statement: replace list at index with value
        # Only trigger if it looks like: replace IDENT at ...
        if (
            self.current().type == KEYWORD
            and self.current().value == "replace"
            and self.peek().type == IDENT
        ):
            # Peek further to see if 'at' follows the identifier
            save_pos = self.pos
            self.advance()  # replace
            self.advance()  # IDENT
            is_list_replace = (
                self.current().type == KEYWORD and self.current().value == "at"
            )
            self.pos = save_pos  # restore

            if is_list_replace:
                return self.parse_replace(line)

        # Special handling for remove at: remove list at index
        if self.current().type == KEYWORD and self.current().value == "remove":
            return self.parse_remove(line)

        # Special handling for delete
        if self.current().type == KEYWORD and self.current().value == "delete":
            self.advance()
            filepath = self.parse_expression()
            return ExpressionStatement(FunctionCall("delete", [filepath], line), line)

        # Special handling for set (dict/element)
        if self.current().type == KEYWORD and self.current().value == "set":
            return self.parse_set_statement(line)

        expr = self.parse_expression()

        # Check for assignment
        if isinstance(expr, Identifier) and self.match(EQUALS):
            value = self.parse_expression()
            return RememberStatement(expr.name, value, line)

        return ExpressionStatement(expr, line)

    def parse_replace(self, line):
        """Parse: replace list at index with value"""
        self.advance()  # consume 'replace'
        # Parse just the list name (identifier only, not postfix)
        list_token = self.expect(IDENT)
        list_expr = Identifier(list_token.value, list_token.line)
        self.expect(KEYWORD, "at")
        index_expr = self._parse_simple_expr()
        self.expect(KEYWORD, "with")
        value_expr = self._parse_simple_expr()

        return ExpressionStatement(
            FunctionCall(
                "replace",
                [
                    list_expr,
                    StringLiteral("at", line),
                    index_expr,
                    StringLiteral("with", line),
                    value_expr,
                ],
                line,
            ),
            line,
        )

    def parse_remove(self, line):
        """Parse: remove list at index OR remove list value"""
        self.advance()  # consume 'remove'
        list_token = self.expect(IDENT)
        list_expr = Identifier(list_token.value, list_token.line)

        if self.current().type == KEYWORD and self.current().value == "at":
            self.advance()  # consume 'at'
            index_expr = self._parse_simple_expr()
            return ExpressionStatement(
                FunctionCall(
                    "remove", [list_expr, StringLiteral("at", line), index_expr], line
                ),
                line,
            )
        else:
            value_expr = self._parse_simple_expr()
            return ExpressionStatement(
                FunctionCall("remove", [list_expr, value_expr], line), line
            )

    def parse_write_append(self, line):
        """Parse write/append statements: write content to file"""
        op = self.advance().value  # 'write' or 'append'

        # Collect content (everything before 'to')
        content_parts = []
        while self.current().type not in (NEWLINE, EOF, DEDENT) and not (
            self.current().type == KEYWORD and self.current().value == "to"
        ):
            content_parts.append(self._parse_simple_expr())

        self.expect(KEYWORD, "to")
        filepath = self._parse_simple_expr()

        # Build the content expression
        if len(content_parts) == 1:
            content = content_parts[0]
        else:
            # Join multiple parts with string concat
            content = content_parts[0]
            for part in content_parts[1:]:
                content = BinaryOp(content, "+", part, line)

        return ExpressionStatement(
            FunctionCall(op, [content, StringLiteral("to", line), filepath], line), line
        )

    def parse_set_statement(self, line):
        """Parse set statement: set dict "key" value"""
        self.advance()  # consume 'set'

        # First arg: the container (identifier or expression)
        target = self._parse_simple_expr()

        # Collect remaining args
        args = [target]
        while self.current().type not in (NEWLINE, EOF, DEDENT):
            # Stop at keywords that indicate end of statement
            if self.current().type == KEYWORD and self.current().value not in (
                "color",
                "size",
                "position",
                "font",
            ):
                break
            args.append(self._parse_simple_expr())

        return ExpressionStatement(FunctionCall("set", args, line), line)

    def parse_block(self):
        """Parse a block of statements"""
        statements = []
        self.skip_newlines()

        while self.current().type not in (DEDENT, EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()

        return statements

    def parse_expression(self):
        """Parse an expression"""
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.match(KEYWORD, "or"):
            right = self.parse_and()
            left = BinaryOp(left, "or", right, left.line)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.match(KEYWORD, "and"):
            right = self.parse_not()
            left = BinaryOp(left, "and", right, left.line)
        return left

    def parse_not(self):
        if self.match(KEYWORD, "not"):
            operand = self.parse_not()
            return UnaryOp("not", operand, operand.line)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_addition()

        while True:
            if self.match(KEYWORD, "is"):
                right = self.parse_addition()
                left = BinaryOp(left, "is", right, left.line)
            elif self.match(KEYWORD, "bigger"):
                if self.match(KEYWORD, "or") and self.match(KEYWORD, "same"):
                    right = self.parse_addition()
                    left = BinaryOp(left, ">=", right, left.line)
                else:
                    right = self.parse_addition()
                    left = BinaryOp(left, ">", right, left.line)
            elif self.match(KEYWORD, "smaller"):
                if self.match(KEYWORD, "or") and self.match(KEYWORD, "same"):
                    right = self.parse_addition()
                    left = BinaryOp(left, "<=", right, left.line)
                else:
                    right = self.parse_addition()
                    left = BinaryOp(left, "<", right, left.line)
            elif self.match(KEYWORD, "has"):
                right = self.parse_addition()
                left = BinaryOp(left, "has", right, left.line)
            elif self.current().type == KEYWORD and self.current().value == "starts":
                self.advance()
                self.expect(KEYWORD, "with")
                right = self.parse_addition()
                left = BinaryOp(left, "starts_with", right, left.line)
            elif self.current().type == KEYWORD and self.current().value == "ends":
                self.advance()
                self.expect(KEYWORD, "with")
                right = self.parse_addition()
                left = BinaryOp(left, "ends_with", right, left.line)
            else:
                break

        return left

    def parse_addition(self):
        left = self.parse_multiplication()

        while True:
            if self.match(PLUS):
                right = self.parse_multiplication()
                left = BinaryOp(left, "+", right, left.line)
            elif self.match(MINUS):
                right = self.parse_multiplication()
                left = BinaryOp(left, "-", right, left.line)
            else:
                break

        return left

    def parse_multiplication(self):
        left = self.parse_power()

        while True:
            if self.match(STAR):
                right = self.parse_power()
                left = BinaryOp(left, "*", right, left.line)
            elif self.match(SLASH):
                right = self.parse_power()
                left = BinaryOp(left, "/", right, left.line)
            else:
                break

        return left

    def parse_power(self):
        left = self.parse_unary()

        if (
            self.current().type == KEYWORD
            and self.current().value == "to"
            and self.peek().type == KEYWORD
            and self.peek().value == "the"
        ):
            self.advance()  # to
            self.advance()  # the
            self.expect(KEYWORD, "power")
            right = self.parse_unary()
            left = BinaryOp(left, "**", right, left.line)

        return left

    def parse_unary(self):
        if self.match(MINUS):
            operand = self.parse_unary()
            return UnaryOp("-", operand, operand.line)
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()

        while True:
            if self.match(KEYWORD, "at"):
                index = self.parse_primary()
                expr = ListAccess(expr, index, expr.line)
            else:
                break

        return expr

    def parse_primary(self):
        token = self.current()

        # Number
        if token.type == NUMBER:
            self.advance()
            return NumberLiteral(token.value, token.line)

        # String
        if token.type == STRING:
            self.advance()
            return StringLiteral(token.value, token.line)

        # Boolean
        if token.type == KEYWORD and token.value in ("yes", "no"):
            self.advance()
            return BooleanLiteral(token.value == "yes", token.line)

        # Nothing
        if token.type == KEYWORD and token.value == "nothing":
            self.advance()
            return NothingLiteral(token.line)

        # Identifier or function call
        if token.type == IDENT:
            self.advance()

            # Check for function call with parentheses
            if self.current().type == LPAREN:
                self.advance()  # consume (
                args = []
                while self.current().type != RPAREN:
                    args.append(self.parse_expression())
                    if not self.match(COMMA):
                        break
                self.expect(RPAREN)
                return FunctionCall(token.value, args, token.line)

            # Check for function call with space-separated args
            # Only if next token could be an argument
            next_tok = self.current()
            if next_tok.type in (STRING, NUMBER, IDENT) or (
                next_tok.type == KEYWORD
                and next_tok.value
                in (
                    "yes",
                    "no",
                    "nothing",
                    "not",
                    "pi",
                    "e",
                    "today",
                    "length",
                    "type",
                    "abs",
                    "sqrt",
                    "random",
                    "uppercase",
                    "lowercase",
                    "trim",
                    "min",
                    "max",
                    "sum",
                    "average",
                    "empty",
                    "find",
                    "copy",
                    "join",
                    "split",
                    "keys",
                    "values",
                    "as",
                )
            ):
                # This looks like a function call - parse all args
                args = []
                while self.current().type not in (
                    NEWLINE,
                    EOF,
                    DEDENT,
                    RPAREN,
                    COMMA,
                    COLON,
                    EQUALS,
                ):
                    # Stop at keywords that indicate end of args
                    if self.current().type == KEYWORD and self.current().value in (
                        "else",
                        "catch",
                        "times",
                        "and",
                        "or",
                        "is",
                        "bigger",
                        "smaller",
                        "to",
                        "at",
                        "from",
                        "with",
                        "in",
                        "if",
                        "as",
                        "forever",
                    ):
                        break
                    args.append(self._parse_simple_unary())
                    # After parsing an argument, check if we should stop
                    # Stop at binary operators
                    if self.current().type in (PLUS, STAR, SLASH, MINUS):
                        break
                    if self.current().type in (
                        NEWLINE,
                        EOF,
                        DEDENT,
                        RPAREN,
                        COMMA,
                        COLON,
                        EQUALS,
                    ):
                        break
                    if self.current().type == KEYWORD:
                        break
                if args:
                    return FunctionCall(token.value, args, token.line)

            return Identifier(token.value, token.line)

        # Parenthesized expression
        if token.type == LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(RPAREN)
            return expr

        # List literal
        if token.type == LBRACKET:
            return self.parse_list_literal()

        # Dict literal
        if token.type == LBRACE:
            return self.parse_dict_literal()

        # Keywords that can be used as function calls
        if token.type == KEYWORD:
            self.advance()

            # Constants and values that are keywords
            if token.value in ("pi", "e", "today", "yes", "no", "nothing"):
                if token.value == "pi":
                    return NumberLiteral(3.14159265358979, token.line)
                elif token.value == "e":
                    return NumberLiteral(2.71828182845905, token.line)
                elif token.value == "today":
                    return FunctionCall("today", [], token.line)
                elif token.value == "yes":
                    return BooleanLiteral(True, token.line)
                elif token.value == "no":
                    return BooleanLiteral(False, token.line)
                elif token.value == "nothing":
                    return NothingLiteral(token.line)

            # These keywords can be called like functions (CHECK FIRST)
            if token.value in (
                "length",
                "type",
                "uppercase",
                "lowercase",
                "trim",
                "abs",
                "round",
                "floor",
                "ceil",
                "sqrt",
                "random",
                "shuffle",
                "sort",
                "reverse",
                "clear",
                "empty",
                "has",
                "find",
                "copy",
                "combine",
                "join",
                "split",
                "replace",
                "format",
                "keys",
                "values",
                "add",
                "remove",
                "read",
                "write",
                "append",
                "delete",
                "file",
                "folder",
                "create",
                "min",
                "max",
                "sum",
                "average",
                "year",
                "month",
                "day",
                "hour",
                "minute",
                "as",
                "fetch",
                "send",
                "download",
                "get",
                "set",
                "unique",
                "beep",
                "play",
                "say",
                "draw",
                "color",
                "move",
            ):
                args = []
                while self.current().type not in (
                    NEWLINE,
                    EOF,
                    DEDENT,
                    RPAREN,
                    COMMA,
                    COLON,
                    EQUALS,
                ):
                    # Stop at binary operators (keyword used as variable name)
                    if self.current().type in (PLUS, STAR, SLASH, MINUS):
                        break

                    # Allow keywords like 'number', 'string', 'yesno', 'yes', 'no',
                    # 'to', 'lines', 'json', 'csv', 'exists' as arguments
                    if self.current().type == KEYWORD and self.current().value in (
                        "number",
                        "string",
                        "yesno",
                        "yes",
                        "no",
                        "to",
                        "lines",
                        "json",
                        "csv",
                        "exists",
                        "folder",
                        "file",
                        "reverse",
                    ):
                        kw = self.advance()
                        args.append(StringLiteral(kw.value, kw.line))
                        continue

                    # Stop at certain structural keywords
                    if self.current().type == KEYWORD and self.current().value in (
                        "else",
                        "catch",
                        "times",
                        "forever",
                        "and",
                        "or",
                        "is",
                        "bigger",
                        "smaller",
                        "not",
                        "at",
                        "in",
                        "as",
                        "from",
                        "with",
                        "if",
                    ):
                        break

                    args.append(self._parse_simple_expr())
                    if self.current().type in (
                        NEWLINE,
                        EOF,
                        DEDENT,
                        RPAREN,
                        COMMA,
                        COLON,
                        EQUALS,
                    ):
                        break
                return FunctionCall(token.value, args, token.line)

            # Keywords that can be used as variable names (when referenced as values)
            if token.value in (
                "bigger",
                "smaller",
                "is",
                "and",
                "or",
                "not",
                "set",
                "get",
                "has",
                "find",
                "empty",
                "copy",
                "combine",
                "join",
                "split",
                "replace",
                "format",
                "keys",
                "values",
                "type",
                "unique",
                "first",
                "last",
                "starts",
                "ends",
                "with",
                "same",
                "times",
                "forever",
                "each",
                "in",
                "lines",
                "csv",
                "json",
                "exists",
                "year",
                "month",
                "day",
                "hour",
                "minute",
                "file",
                "folder",
                "create",
                "at",
                "from",
                "to",
                "as",
                "number",
                "string",
                "yesno",
                "power",
                "the",
                "cube",
                "root",
                "status",
                "send",
                "post",
                "download",
                "fetch",
                "safe",
                "delta",
                "time",
            ):
                # Treat as identifier value when used as data
                return Identifier(token.value, token.line)

            self.error(f"Unexpected keyword: {token.value}", token)

        self.error(f"Unexpected token: {token.type}", token)

    def parse_list_literal(self):
        line = self.current().line
        self.expect(LBRACKET)
        items = []

        while self.current().type != RBRACKET:
            items.append(self.parse_expression())
            if not self.match(COMMA):
                break

        self.expect(RBRACKET)
        return ListLiteral(items, line)

    def parse_dict_literal(self):
        line = self.current().line
        self.expect(LBRACE)
        pairs = {}

        while self.current().type != RBRACE:
            key = self.parse_expression()
            self.expect(COLON)
            value = self.parse_expression()
            pairs[key.value if isinstance(key, StringLiteral) else str(key.value)] = (
                value
            )

            if not self.match(COMMA):
                break

        self.expect(RBRACE)
        return DictLiteral(pairs, line)

    def _parse_simple_expr(self):
        """Parse a simple expression (no auto function call on identifiers)"""
        return self._parse_simple_or()

    def _parse_simple_or(self):
        left = self._parse_simple_and()
        while self.match(KEYWORD, "or"):
            right = self._parse_simple_and()
            left = BinaryOp(left, "or", right, left.line)
        return left

    def _parse_simple_and(self):
        left = self._parse_simple_not()
        while self.match(KEYWORD, "and"):
            right = self._parse_simple_not()
            left = BinaryOp(left, "and", right, left.line)
        return left

    def _parse_simple_not(self):
        if self.match(KEYWORD, "not"):
            operand = self._parse_simple_not()
            return UnaryOp("not", operand, operand.line)
        return self._parse_simple_comparison()

    def _parse_simple_comparison(self):
        left = self._parse_simple_addition()

        while True:
            if self.match(KEYWORD, "is"):
                right = self._parse_simple_addition()
                left = BinaryOp(left, "is", right, left.line)
            elif self.current().type == KEYWORD and self.current().value == "bigger":
                # Peek ahead to see if this is a comparison or variable name
                # If next token is NEWLINE/EOF/DEDENT, it's a variable name
                next_tok = self.peek()
                if next_tok.type in (NEWLINE, EOF, DEDENT, KEYWORD):
                    # Likely a variable name, not a comparison
                    break
                # Otherwise, treat as comparison operator
                self.advance()  # consume 'bigger'
                if self.match(KEYWORD, "or") and self.match(KEYWORD, "same"):
                    right = self._parse_simple_addition()
                    left = BinaryOp(left, ">=", right, left.line)
                else:
                    right = self._parse_simple_addition()
                    left = BinaryOp(left, ">", right, left.line)
            elif self.current().type == KEYWORD and self.current().value == "smaller":
                # Peek ahead to see if this is a comparison or variable name
                next_tok = self.peek()
                if next_tok.type in (NEWLINE, EOF, DEDENT, KEYWORD):
                    # Likely a variable name, not a comparison
                    break
                # Otherwise, treat as comparison operator
                self.advance()  # consume 'smaller'
                if self.match(KEYWORD, "or") and self.match(KEYWORD, "same"):
                    right = self._parse_simple_addition()
                    left = BinaryOp(left, "<=", right, left.line)
                else:
                    right = self._parse_simple_addition()
                    left = BinaryOp(left, "<", right, left.line)
            elif self.match(KEYWORD, "has"):
                right = self._parse_simple_addition()
                left = BinaryOp(left, "has", right, left.line)
            else:
                break

        return left

    def _parse_simple_addition(self):
        left = self._parse_simple_multiplication()

        while True:
            if self.match(PLUS):
                right = self._parse_simple_multiplication()
                left = BinaryOp(left, "+", right, left.line)
            elif self.match(MINUS):
                right = self._parse_simple_multiplication()
                left = BinaryOp(left, "-", right, left.line)
            else:
                break

        return left

    def _parse_simple_multiplication(self):
        left = self._parse_simple_power()

        while True:
            if self.match(STAR):
                right = self._parse_simple_power()
                left = BinaryOp(left, "*", right, left.line)
            elif self.match(SLASH):
                right = self._parse_simple_power()
                left = BinaryOp(left, "/", right, left.line)
            else:
                break

        return left

    def _parse_simple_power(self):
        left = self._parse_simple_unary()

        # Check for "to the power" - only if next two tokens are "to" "the"
        if (
            self.current().type == KEYWORD
            and self.current().value == "to"
            and self.peek().type == KEYWORD
            and self.peek().value == "the"
        ):
            self.advance()  # to
            self.advance()  # the
            self.expect(KEYWORD, "power")
            right = self._parse_simple_unary()
            left = BinaryOp(left, "**", right, left.line)

        return left

    def _parse_simple_unary(self):
        if self.match(MINUS):
            operand = self._parse_simple_unary()
            return UnaryOp("-", operand, operand.line)
        return self._parse_simple_postfix()

    def _parse_simple_postfix(self):
        expr = self._parse_simple_primary()

        while True:
            if self.match(KEYWORD, "at"):
                index = self._parse_simple_primary()
                expr = ListAccess(expr, index, expr.line)
            else:
                break

        return expr

    def _parse_simple_primary(self):
        """Parse primary expression without auto function call on identifiers"""
        token = self.current()

        if token.type == NUMBER:
            self.advance()
            return NumberLiteral(token.value, token.line)

        if token.type == STRING:
            self.advance()
            return StringLiteral(token.value, token.line)

        if token.type == KEYWORD and token.value in ("yes", "no"):
            self.advance()
            return BooleanLiteral(token.value == "yes", token.line)

        if token.type == KEYWORD and token.value == "nothing":
            self.advance()
            return NothingLiteral(token.line)

        if token.type == IDENT:
            self.advance()

            # Check for function call with parentheses
            if self.current().type == LPAREN:
                self.advance()
                args = []
                while self.current().type != RPAREN:
                    args.append(self._parse_simple_expr())
                    if not self.match(COMMA):
                        break
                self.expect(RPAREN)
                return FunctionCall(token.value, args, token.line)

            return Identifier(token.value, token.line)

        if token.type == LPAREN:
            self.advance()
            expr = self._parse_simple_expr()
            self.expect(RPAREN)
            return expr

        if token.type == LBRACKET:
            return self.parse_list_literal()

        if token.type == LBRACE:
            return self.parse_dict_literal()

        # Keywords that can be function calls (nested)
        if token.type == KEYWORD:
            if token.value in (
                "length",
                "type",
                "uppercase",
                "lowercase",
                "trim",
                "abs",
                "round",
                "floor",
                "ceil",
                "sqrt",
                "random",
                "shuffle",
                "sort",
                "reverse",
                "clear",
                "empty",
                "has",
                "find",
                "copy",
                "combine",
                "join",
                "split",
                "replace",
                "format",
                "keys",
                "values",
                "min",
                "max",
                "sum",
                "average",
                "today",
                "year",
                "month",
                "day",
                "hour",
                "minute",
                "as",
                "substring",
                "read",
                "write",
                "append",
                "delete",
                "file",
                "folder",
                "create",
                "add",
                "remove",
                "beep",
                "play",
                "say",
                "draw",
                "color",
                "move",
                "unique",
                "fetch",
                "send",
                "download",
                "get",
                "set",
            ):
                self.advance()
                args = []
                while self.current().type not in (
                    NEWLINE,
                    EOF,
                    DEDENT,
                    RPAREN,
                    COMMA,
                    COLON,
                    EQUALS,
                ):
                    # Allow 'nothing' as an argument
                    if (
                        self.current().type == KEYWORD
                        and self.current().value == "nothing"
                    ):
                        args.append(NothingLiteral(self.current().line))
                        self.advance()
                        continue
                    # Stop at other keywords
                    if self.current().type == KEYWORD:
                        break
                    args.append(self._parse_simple_unary())
                    # After parsing an argument, check if we should stop
                    # Stop at binary operators, UNLESS it's a unary minus followed by a number
                    if self.current().type in (PLUS, STAR, SLASH):
                        break
                    if self.current().type == MINUS:
                        # Check if this is a unary minus (next token is NUMBER)
                        # or a binary minus (next token is something else)
                        if (
                            self.pos + 1 < len(self.tokens)
                            and self.tokens[self.pos + 1].type == NUMBER
                        ):
                            # This is a unary minus, continue parsing arguments
                            pass
                        else:
                            # This is a binary minus, stop
                            break
                    if self.current().type in (
                        NEWLINE,
                        EOF,
                        DEDENT,
                        RPAREN,
                        COMMA,
                        COLON,
                        EQUALS,
                    ):
                        break
                return FunctionCall(token.value, args, token.line)

            # Keywords that can be used as variable names (when referenced as values)
            if token.value in (
                "bigger",
                "smaller",
                "is",
                "and",
                "or",
                "not",
                "set",
                "get",
                "has",
                "find",
                "empty",
                "copy",
                "combine",
                "join",
                "split",
                "replace",
                "format",
                "keys",
                "values",
                "type",
                "unique",
                "first",
                "last",
                "starts",
                "ends",
                "with",
                "same",
                "times",
                "forever",
                "each",
                "in",
                "lines",
                "csv",
                "json",
                "exists",
                "year",
                "month",
                "day",
                "hour",
                "minute",
                "file",
                "folder",
                "create",
                "at",
                "from",
                "to",
                "as",
                "number",
                "string",
                "yesno",
                "power",
                "the",
                "cube",
                "root",
                "status",
                "send",
                "post",
                "download",
                "fetch",
                "safe",
                "delta",
                "time",
                "add",
                "remove",
                "sort",
                "reverse",
                "clear",
                "shuffle",
                "read",
                "write",
                "append",
                "delete",
                "min",
                "max",
                "sum",
                "average",
                "abs",
                "round",
                "floor",
                "ceil",
                "sqrt",
                "uppercase",
                "lowercase",
                "trim",
                "random",
                "length",
                "beep",
                "play",
                "say",
                "draw",
                "color",
                "move",
                "unique",
                "list",
                "dict",
                "fun",
                "return",
                "if",
                "else",
                "repeat",
                "for",
                "try",
                "catch",
                "throw",
                "stop",
                "skip",
                "wait",
                "use",
                "bring",
                "remember",
                "const",
                "ask",
                "print",
            ):
                self.advance()
                return Identifier(token.value, token.line)

        self.error(f"Unexpected token: {token.type}", token)


def parse(tokens, filename="<input>"):
    """Convenience function to parse tokens"""
    parser = Parser(tokens, filename)
    return parser.parse()
