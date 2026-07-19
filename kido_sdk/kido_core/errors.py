"""
KIDO Error Classes - Friendly error messages for kids
"""


class KidoError(Exception):
    """Base class for all KIDO errors"""
    def __init__(self, message, line=None, col=None, suggestion=None):
        self.message = message
        self.line = line
        self.col = col
        self.suggestion = suggestion
        super().__init__(self.friendly_message())
    
    def friendly_message(self):
        parts = ["🤔 Oops!"]
        if self.line:
            parts.append(f"Line {self.line}:")
        parts.append(self.message)
        if self.suggestion:
            parts.append(f"\n💡 {self.suggestion}")
        return " ".join(parts)


class SyntaxError_(KidoError):
    """Syntax errors in KIDO code"""
    pass


class NameError_(KidoError):
    """Variable not found"""
    def __init__(self, name, line=None, col=None, similar=None):
        suggestion = None
        if similar:
            suggestion = f"Did you mean '{similar}'?"
        super().__init__(
            f"I don't remember a thing called '{name}'.",
            line, col, suggestion
        )


class TypeError_(KidoError):
    """Type mismatch errors"""
    pass


class ValueError_(KidoError):
    """Invalid value errors"""
    pass


class IndexError_(KidoError):
    """List/string index errors"""
    pass


class KeyError_(KidoError):
    """Dictionary key errors"""
    pass


class ZeroDivisionError_(KidoError):
    """Division by zero"""
    def __init__(self, line=None, col=None):
        super().__init__(
            "You can't divide by zero!",
            line, col,
            "It's like sharing 5 cookies with 0 friends — it doesn't work!"
        )


class FileNotFoundError_(KidoError):
    """File not found"""
    pass


class ImportError_(KidoError):
    """Module import errors"""
    pass


class RuntimeError_(KidoError):
    """Runtime errors"""
    pass


class SecurityError_(KidoError):
    """Sandbox / resource-limit violations"""
    def __init__(self, message, line=None, col=None, suggestion=None):
        # Allow suggestion as 3rd positional (common call style: msg, line, suggestion)
        if suggestion is None and isinstance(col, str):
            suggestion = col
            col = None
        super().__init__(
            message if message.startswith("Security:") else f"Security: {message}",
            line,
            col,
            suggestion,
        )


class StopExecution(Exception):
    """Signal to stop the entire program"""
    pass


class BreakLoop(Exception):
    """Signal to break out of the current loop"""
    pass


class SkipIteration(Exception):
    """Signal to skip to next iteration (for 'skip' keyword)"""
    pass


class ReturnSignal(Exception):
    """Signal to return from function"""
    def __init__(self, value=None):
        self.value = value
        super().__init__()


# Control-flow signals that must NEVER be swallowed by try/catch
CONTROL_FLOW = (StopExecution, BreakLoop, SkipIteration, ReturnSignal)
