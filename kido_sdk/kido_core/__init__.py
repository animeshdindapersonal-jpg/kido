"""KIDO Core - Interpreter components"""

__version__ = "1.1.0"

from .errors import (
    KidoError,
    SyntaxError_,
    NameError_,
    TypeError_,
    ValueError_,
    IndexError_,
    KeyError_,
    ZeroDivisionError_,
    FileNotFoundError_,
    ImportError_,
    RuntimeError_,
    SecurityError_,
)
from .interpreter import Interpreter, run, run_file

__all__ = [
    "__version__",
    "Interpreter",
    "run",
    "run_file",
    "KidoError",
    "SyntaxError_",
    "NameError_",
    "TypeError_",
    "ValueError_",
    "IndexError_",
    "KeyError_",
    "ZeroDivisionError_",
    "FileNotFoundError_",
    "ImportError_",
    "RuntimeError_",
    "SecurityError_",
]
