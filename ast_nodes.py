class ASTNode:
    def __init__(self):
        pass

class ProgramNode(ASTNode):
    def __init__(self, declarations):
        super().__init__()
        self.declarations = declarations

class DeclarationNode(ASTNode):
    def __init__(self, type_name, name, init_value=None, line=None):
        super().__init__()
        self.type_name = type_name
        self.name = name
        self.init_value = init_value
        self.line = line

class FunctionNode(ASTNode):
    def __init__(self, return_type, name, parameters, body, line=None):
        super().__init__()
        self.return_type = return_type
        self.name = name
        self.parameters = parameters
        self.body = body
        self.line = line

class ParameterNode(ASTNode):
    def __init__(self, type_name, name, line=None):
        super().__init__()
        self.type_name = type_name
        self.name = name
        self.line = line

class BlockNode(ASTNode):
    def __init__(self, statements, line=None):
        super().__init__()
        self.statements = statements
        self.line = line

class IfNode(ASTNode):
    def __init__(self, condition, true_body, false_body=None, line=None):
        super().__init__()
        self.condition = condition
        self.true_body = true_body
        self.false_body = false_body
        self.line = line

class WhileNode(ASTNode):
    def __init__(self, condition, body, line=None):
        super().__init__()
        self.condition = condition
        self.body = body
        self.line = line

class DoWhileNode(ASTNode):
    def __init__(self, body, condition, line=None):
        super().__init__()
        self.body = body
        self.condition = condition
        self.line = line

class ForNode(ASTNode):
    def __init__(self, init, condition, update, body, line=None):
        super().__init__()
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
        self.line = line

class SwitchNode(ASTNode):
    def __init__(self, expression, cases, line=None):
        super().__init__()
        self.expression = expression
        self.cases = cases
        self.line = line

class CaseNode(ASTNode):
    def __init__(self, value, statements, line=None):
        super().__init__()
        self.value = value
        self.statements = statements
        self.line = line

class BreakNode(ASTNode):
    def __init__(self, line=None):
        super().__init__()
        self.line = line

class ContinueNode(ASTNode):
    def __init__(self, line=None):
        super().__init__()
        self.line = line

class ReturnNode(ASTNode):
    def __init__(self, value=None, line=None):
        super().__init__()
        self.value = value
        self.line = line

class BinaryOpNode(ASTNode):
    def __init__(self, operator, left, right, line=None):
        super().__init__()
        self.operator = operator
        self.left = left
        self.right = right
        self.line = line

class UnaryOpNode(ASTNode):
    def __init__(self, operator, operand, is_prefix=True, line=None):
        super().__init__()
        self.operator = operator
        self.operand = operand
        self.is_prefix = is_prefix
        self.line = line

class AssignmentNode(ASTNode):
    def __init__(self, target, operator, value, line=None):
        super().__init__()
        self.target = target
        self.operator = operator
        self.value = value
        self.line = line

class FunctionCallNode(ASTNode):
    def __init__(self, name, arguments, line=None):
        super().__init__()
        self.name = name
        self.arguments = arguments
        self.line = line

class IdentifierNode(ASTNode):
    def __init__(self, name, line=None):
        super().__init__()
        self.name = name
        self.line = line

class LiteralNode(ASTNode):
    def __init__(self, value, type_name, line=None):
        super().__init__()
        self.value = value
        self.type_name = type_name
        self.line = line

    def __repr__(self):
        return f"LiteralNode({self.value}, {self.type_name})"
