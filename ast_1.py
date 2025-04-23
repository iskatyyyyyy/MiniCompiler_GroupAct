class ASTNode:
    def __init__(self, kind, value=None, children=None, line=None, col=None):
        self.kind = kind              # Node type (e.g., 'FunctionDef', 'IfStmt')
        self.value = value            # Value for literals or identifiers
        self.children = children or []
        self.line = line
        self.col = col

    def __repr__(self, level=0):
        indent = '  ' * level
        result = f"{indent}{self.kind}"
        if self.value is not None:
            result += f": {self.value}"
        if self.line is not None:
            result += f" @({self.line}:{self.col})"
        for child in self.children:
            result += "\n" + child.__repr__(level + 1)
        return result
