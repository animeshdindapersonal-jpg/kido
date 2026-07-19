"""
KIDO Lexer - Tokenizes .kd source code into tokens
"""

from .errors import SyntaxError_


# Token types
KEYWORD = 'KEYWORD'
IDENT = 'IDENT'
STRING = 'STRING'
NUMBER = 'NUMBER'
PLUS = 'PLUS'
MINUS = 'MINUS'
STAR = 'STAR'
SLASH = 'SLASH'
EQUALS = 'EQUALS'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
LBRACE = 'LBRACE'
RBRACE = 'RBRACE'
LBRACKET = 'LBRACKET'
RBRACKET = 'RBRACKET'
COLON = 'COLON'
COMMA = 'COMMA'
NEWLINE = 'NEWLINE'
INDENT = 'INDENT'
DEDENT = 'DEDENT'
EOF = 'EOF'


class Token:
    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col
    
    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, L{self.line})"


# All KIDO keywords (case insensitive)
KEYWORDS = {
    'print', 'remember', 'ask', 'if', 'else', 'repeat', 'times',
    'forever', 'fun', 'return', 'list', 'dict', 'add', 'remove',
    'at', 'length', 'has', 'is', 'bigger', 'smaller', 'and', 'or',
    'not', 'stop', 'skip', 'try', 'catch', 'throw', 'yes', 'no',
    'nothing', 'as', 'for', 'each', 'in', 'const', 'use', 'bring',
    'write', 'read', 'to', 'append', 'delete', 'file', 'exists',
    'type', 'wait', 'random', 'sort', 'reverse', 'clear', 'empty',
    'find', 'copy', 'combine', 'join', 'split', 'uppercase',
    'lowercase', 'trim', 'replace', 'format', 'keys', 'values',
    'set', 'get', 'safe', 'lines', 'csv', 'json', 'folder',
    'create', 'abs', 'round', 'floor', 'ceil', 'sqrt', 'min',
    'max', 'sum', 'average', 'pi', 'power', 'string', 'number',
    'yesno', 'starts', 'with', 'ends', 'first', 'last', 'from',
    'same', 'delta', 'time', 'today', 'year', 'month', 'day',
    'hour', 'minute', 'beep', 'play', 'say', 'draw', 'color',
    'move', 'unique', 'shuffle', 'status', 'send', 'post',
    'download', 'fetch', 'the', 'cube', 'root', 'line', 'files',
    'same', 'or'
}


class Lexer:
    def __init__(self, source, filename="<input>"):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        self.indent_stack = [0]
    
    def error(self, msg):
        raise SyntaxError_(msg, self.line, self.col)
    
    def peek(self, offset=0):
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return '\0'
    
    def advance(self):
        if self.pos >= len(self.source):
            return '\0'
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch
    
    def skip_line_comment(self):
        """Skip # comment to end of line"""
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self.advance()
    
    def skip_block_comment(self):
        """Skip /* ... */ comment"""
        self.advance()  # /
        self.advance()  # *
        while self.pos < len(self.source):
            if self.peek() == '*' and self.peek(1) == '/':
                self.advance()  # *
                self.advance()  # /
                return
            self.advance()
        self.error("Unterminated block comment (missing */)")
    
    def read_string(self):
        """Read a quoted string"""
        quote = self.advance()  # opening quote
        start_line = self.line
        start_col = self.col
        result = []
        
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch == quote:
                self.advance()
                return Token(STRING, ''.join(result), start_line, start_col)
            elif ch == '\\':
                self.advance()
                if self.pos < len(self.source):
                    next_ch = self.advance()
                    escape_map = {
                        'n': '\n', 't': '\t', '\\': '\\',
                        '"': '"', "'": "'", '0': '\0'
                    }
                    result.append(escape_map.get(next_ch, next_ch))
            elif ch == '\n':
                self.error(f"Unterminated string (started at line {start_line})")
            else:
                result.append(self.advance())
        
        self.error(f"Unterminated string (started at line {start_line})")
    
    def read_number(self):
        """Read a number (int or float)"""
        start_col = self.col
        result = []
        has_dot = False
        
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch.isdigit():
                result.append(self.advance())
            elif ch == '.' and not has_dot and self.peek(1).isdigit():
                has_dot = True
                result.append(self.advance())
            else:
                break
        
        value = ''.join(result)
        if has_dot:
            return Token(NUMBER, float(value), self.line, start_col)
        else:
            return Token(NUMBER, int(value), self.line, start_col)
    
    def read_word(self):
        """Read a keyword or identifier"""
        start_col = self.col
        result = []
        
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch.isalnum() or ch == '_':
                result.append(self.advance())
            else:
                break
        
        value = ''.join(result)
        lower = value.lower()
        
        if lower in KEYWORDS:
            return Token(KEYWORD, lower, self.line, start_col)
        else:
            return Token(IDENT, value, self.line, start_col)
    
    def calculate_indent(self):
        """Calculate indentation at current position"""
        indent = 0
        while self.pos < len(self.source) and self.source[self.pos] in ' \t':
            if self.source[self.pos] == ' ':
                indent += 1
            else:  # tab
                indent += 4
            self.pos += 1
            self.col += 1
        return indent
    
    def tokenize(self):
        """Tokenize the entire source code"""
        at_line_start = True
        
        while self.pos < len(self.source):
            ch = self.peek()
            
            # Handle line start (indentation)
            if at_line_start:
                # Calculate indentation
                indent = self.calculate_indent()
                
                # Skip blank lines and comment-only lines
                if self.pos < len(self.source) and self.source[self.pos] == '\n':
                    self.advance()
                    continue
                if self.pos >= len(self.source):
                    break
                if self.source[self.pos] == '#':
                    self.skip_line_comment()
                    if self.pos < len(self.source):
                        self.advance()  # skip newline
                    continue
                if (self.source[self.pos] == '/' and 
                    self.pos + 1 < len(self.source) and 
                    self.source[self.pos + 1] == '*'):
                    self.skip_block_comment()
                    at_line_start = True
                    continue
                
                # Emit INDENT/DEDENT tokens
                if indent > self.indent_stack[-1]:
                    self.indent_stack.append(indent)
                    self.tokens.append(Token(INDENT, indent, self.line, 1))
                else:
                    while indent < self.indent_stack[-1]:
                        self.indent_stack.pop()
                        self.tokens.append(Token(DEDENT, indent, self.line, 1))
                
                at_line_start = False
                continue
            
            # Skip inline whitespace
            if ch in ' \t':
                self.advance()
                continue
            
            # Newline
            if ch == '\n':
                self.advance()
                # Only emit NEWLINE if last token isn't already a NEWLINE/INDENT/DEDENT
                if (self.tokens and 
                    self.tokens[-1].type not in (NEWLINE, INDENT, DEDENT)):
                    self.tokens.append(Token(NEWLINE, '\n', self.line - 1, 1))
                at_line_start = True
                continue
            
            # Comments
            if ch == '#':
                self.skip_line_comment()
                continue
            
            if ch == '/' and self.peek(1) == '*':
                self.skip_block_comment()
                continue
            
            # Strings
            if ch in '"\'':
                self.tokens.append(self.read_string())
                continue
            
            # Numbers
            if ch.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Negative numbers (only if preceded by operator or at start of expression)
            if ch == '-' and self.peek(1).isdigit():
                if (not self.tokens or 
                    self.tokens[-1].type in (KEYWORD, EQUALS, LPAREN, COMMA, 
                                              NEWLINE, INDENT, PLUS, MINUS, 
                                              STAR, SLASH, COLON)):
                    self.advance()  # consume -
                    num_token = self.read_number()
                    num_token.value = -num_token.value
                    self.tokens.append(num_token)
                    continue
            
            # Identifiers and keywords
            if ch.isalpha() or ch == '_':
                self.tokens.append(self.read_word())
                continue
            
            # Operators
            if ch == '+':
                self.tokens.append(Token(PLUS, '+', self.line, self.col))
                self.advance()
                continue
            if ch == '-':
                self.tokens.append(Token(MINUS, '-', self.line, self.col))
                self.advance()
                continue
            if ch == '*':
                self.tokens.append(Token(STAR, '*', self.line, self.col))
                self.advance()
                continue
            if ch == '/':
                self.tokens.append(Token(SLASH, '/', self.line, self.col))
                self.advance()
                continue
            if ch == '=':
                self.tokens.append(Token(EQUALS, '=', self.line, self.col))
                self.advance()
                continue
            
            # Symbols
            if ch == '(':
                self.tokens.append(Token(LPAREN, '(', self.line, self.col))
                self.advance()
                continue
            if ch == ')':
                self.tokens.append(Token(RPAREN, ')', self.line, self.col))
                self.advance()
                continue
            if ch == '{':
                self.tokens.append(Token(LBRACE, '{', self.line, self.col))
                self.advance()
                continue
            if ch == '}':
                self.tokens.append(Token(RBRACE, '}', self.line, self.col))
                self.advance()
                continue
            if ch == '[':
                self.tokens.append(Token(LBRACKET, '[', self.line, self.col))
                self.advance()
                continue
            if ch == ']':
                self.tokens.append(Token(RBRACKET, ']', self.line, self.col))
                self.advance()
                continue
            if ch == ':':
                self.tokens.append(Token(COLON, ':', self.line, self.col))
                self.advance()
                continue
            if ch == ',':
                self.tokens.append(Token(COMMA, ',', self.line, self.col))
                self.advance()
                continue
            
            # Unknown character
            self.error(f"Unexpected character: '{ch}'")
        
        # Add final NEWLINE if needed
        if self.tokens and self.tokens[-1].type not in (NEWLINE, INDENT, DEDENT):
            self.tokens.append(Token(NEWLINE, '\n', self.line, 1))
        
        # Close remaining indentation
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(DEDENT, 0, self.line, 1))
        
        # Add EOF
        self.tokens.append(Token(EOF, None, self.line, 1))
        
        return self.tokens


def tokenize(source, filename="<input>"):
    """Convenience function to tokenize source code"""
    lexer = Lexer(source, filename)
    return lexer.tokenize()
