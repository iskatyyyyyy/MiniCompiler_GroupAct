class ASTNode:
    pass

# === Expressions ===

class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"VariableNode({self.name})"

    def __str__(self):
        return self.name

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"

    def __str__(self):
        return str(self.value)

class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"StringNode({self.value})"

    def __str__(self):
        return f'"{self.value}"'

class CharNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"CharNode({self.value})"

    def __str__(self):
        return f"'{self.value}'"

class UnaryOperation(ASTNode):
    def __init__(self, operator, operand, postfix=False):
        self.operator = operator
        self.operand = operand
        self.postfix = postfix

    def __repr__(self):
        return f"UnaryOperation(op={self.operator!r}, operand={self.operand!r}, postfix={self.postfix})"

    def __str__(self):
        if self.postfix:
            return f"{self.operand}{self.operator}"
        return f"{self.operator}{self.operand}"

class BinaryOperation(ASTNode):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinaryOperation(op={self.operator!r}, left={self.left!r}, right={self.right!r})"

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

class FunctionCallNode(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FunctionCallNode({self.name}, {self.args!r})"

    def __str__(self):
        return f"{self.name}({', '.join(str(arg) for arg in self.args)})"

# === Statements ===

class ExpressionStatement(ASTNode):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"ExpressionStatement({self.expression!r})"

    def __str__(self):
        return f"{self.expression};"

class VariableDeclaration(ASTNode):
    def __init__(self, var_type, name, initializer=None):
        self.var_type = var_type
        self.name = name
        self.initializer = initializer

    def __repr__(self):
        return f"VariableDeclaration({self.var_type}, {self.name}, {self.initializer!r})"

    def __str__(self):
        if self.initializer:
            return f"{self.var_type} {self.name} = {self.initializer};"
        return f"{self.var_type} {self.name};"
    
class AssignmentExpression(ASTNode):
    def __init__(self, operator, left, right):
        self.operator = operator  # '=', '+=', '-=', etc.
        self.left = left          # should be VariableNode or something assignable
        self.right = right        # expression on the right side

    def __repr__(self):
        return f"AssignmentExpression({self.left} {self.operator} {self.right})"
    
    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"


class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"IfStatement({self.condition!r}, {self.then_branch!r}, {self.else_branch!r})"

    def __str__(self):
        result = f"if ({self.condition}) {self.then_branch}"
        if self.else_branch:
            result += f" else {self.else_branch}"
        return result

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileStatement({self.condition!r}, {self.body!r})"

    def __str__(self):
        return f"while ({self.condition}) {self.body}"

class ForStatement(ASTNode):
    def __init__(self, init, condition, increment, body):
        self.init = init
        self.condition = condition
        self.increment = increment
        self.body = body

    def __repr__(self):
        return f"ForStatement({self.init!r}, {self.condition!r}, {self.increment!r}, {self.body!r})"

    def __str__(self):
        return f"for ({self.init}; {self.condition}; {self.increment}) {self.body}"

class BreakStatement(ASTNode):
    def __repr__(self):
        return "BreakStatement()"

    def __str__(self):
        return "break;"

class ContinueStatement(ASTNode):
    def __repr__(self):
        return "ContinueStatement()"

    def __str__(self):
        return "continue;"

class SwitchCase(ASTNode):
    def __init__(self, value, body):
        self.value = value
        self.body = body

    def __repr__(self):
        return f"SwitchCase({self.value!r}, {self.body!r})"

    def __str__(self):
        return f"case {self.value}:\n{self.body}"

class SwitchStatement(ASTNode):
    def __init__(self, expression, cases, default=None):
        self.expression = expression
        self.cases = cases  # list of SwitchCase
        self.default = default

    def __repr__(self):
        return f"SwitchStatement({self.expression!r}, {self.cases!r}, default={self.default!r})"

    def __str__(self):
        result = f"switch ({self.expression}) {{\n"
        result += "\n".join(str(case) for case in self.cases)
        if self.default:
            result += f"\ndefault:\n{self.default}"
        result += "\n}"
        return result



class ReturnStatement(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"ReturnStatement({self.value!r})"

    def __str__(self):
        return f"return {self.value};"
    
class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Block({self.statements!r})"

    def __str__(self):
        body = '\n'.join(str(stmt) for stmt in self.statements)
        return f"{{\n{body}\n}}"

class FunctionDeclaration(ASTNode):
    def __init__(self, return_type, name, parameters, body):
        self.return_type = return_type
        self.name = name
        self.parameters = parameters
        self.body = body

    def __repr__(self):
        return f"FunctionDeclaration({self.return_type}, {self.name}, {self.parameters!r}, {self.body!r})"

    def __str__(self):
        params = ', '.join(f"{typ} {name}" for typ, name in self.parameters)
        return f"{self.return_type} {self.name}({params}) {self.body}"
