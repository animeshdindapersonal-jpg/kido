"""
KIDO Environment - Variable scope management
"""

from .errors import NameError_


class Environment:
    """Manages variable scope (global and local)"""
    
    def __init__(self, parent=None):
        self.variables = {}
        self.constants = {}
        self.parent = parent  # Parent scope (for function calls)
    
    def get(self, name, line=None, col=None):
        """Get a variable value"""
        # Check current scope
        if name in self.variables:
            return self.variables[name]
        if name in self.constants:
            return self.constants[name]
        
        # Check parent scope
        if self.parent:
            return self.parent.get(name, line, col)
        
        # Not found - suggest similar names
        similar = self._find_similar(name)
        raise NameError_(name, line, col, similar)
    
    def set(self, name, value, is_const=False):
        """Set a variable value"""
        if is_const:
            if name in self.constants:
                from .errors import RuntimeError_
                raise RuntimeError_(
                    f"Cannot change constant '{name}'",
                    suggestion="Constants cannot be changed after creation."
                )
            self.constants[name] = value
        else:
            self.variables[name] = value
    
    def update(self, name, value, line=None, col=None):
        """Update an existing variable"""
        # Check if it's a constant
        if name in self.constants:
            from .errors import RuntimeError_
            raise RuntimeError_(
                f"Cannot change constant '{name}'",
                line, col,
                "Constants cannot be changed after creation."
            )
        
        # Check current scope
        if name in self.variables:
            self.variables[name] = value
            return
        
        # Check parent scope
        if self.parent:
            self.parent.update(name, value, line, col)
            return
        
        # Not found
        similar = self._find_similar(name)
        raise NameError_(name, line, col, similar)
    
    def has(self, name):
        """Check if variable exists"""
        if name in self.variables or name in self.constants:
            return True
        if self.parent:
            return self.parent.has(name)
        return False
    
    def is_constant(self, name):
        """Check if variable is a constant"""
        if name in self.constants:
            return True
        if self.parent:
            return self.parent.is_constant(name)
        return False
    
    def _find_similar(self, name):
        """Find similar variable names (for suggestions)"""
        all_names = list(self.variables.keys()) + list(self.constants.keys())
        if self.parent:
            all_names.extend(self.parent._get_all_names())
        
        # Simple similarity: same length or one character different
        similar = []
        for n in all_names:
            if abs(len(n) - len(name)) <= 2:
                # Check if most characters match
                matches = sum(1 for a, b in zip(n, name) if a == b)
                if matches >= len(name) * 0.6:
                    similar.append(n)
        
        return similar[0] if similar else None
    
    def _get_all_names(self):
        """Get all variable names in this scope and parents"""
        names = list(self.variables.keys()) + list(self.constants.keys())
        if self.parent:
            names.extend(self.parent._get_all_names())
        return names
    
    def child_scope(self):
        """Create a child scope (for function calls)"""
        return Environment(parent=self)
