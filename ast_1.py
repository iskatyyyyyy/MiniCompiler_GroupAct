"""
AST (Abstract Syntax Tree) node classes for C language parsing.
These classes represent the structure of C programs including declarations,
statements, expressions, and control flow constructs.
"""

class ASTNode:
    """Base class for all AST nodes."""
    def __init__(self, node_type):
        self.type = node_type
        
    def __str__(self):
        return f"{self.type}"

# Program node (root of AST)
class Program(ASTNode):
    """Root node representing an entire C program."""
    def __init__(self, declarations):
        super().__init__("Program")
        self.declarations = declarations  # List of declarations (functions or variables)
    
    def __str__(self):
        result = "Program:\n"
        for decl in self.declarations:
            result += str(decl) + "\n"
        return result

#==========================================================
# Declaration nodes
#==========================================================
class VarDeclaration(ASTNode):
    """Variable declaration node (e.g., int x = 5;)."""
    def __init__(self, var_type, identifier, init_expr=None):
        super().__init__("VarDeclaration")
        self.var_type = var_type      # Type (e.g., int, float)
        self.identifier = identifier  # Variable name
        self.init_expr = init_expr    # Optional initialization expression
    
    def __str__(self):
        init_str = f" = {self.init_expr}" if self.init_expr else ""
        return f"VarDeclaration: {self.var_type} {self.identifier}{init_str}"

class FunctionDeclaration(ASTNode):
    """Function declaration node (e.g., int foo(int x) { ... })."""
    def __init__(self, return_type, identifier, parameters, body):
        super().__init__("FunctionDeclaration")
        self.return_type = return_type  # Return type
        self.identifier = identifier    # Function name
        self.parameters = parameters    # List of Parameter objects
        self.body = body                # BlockStatement object
    
    def __str__(self):
        params_str = ", ".join([str(param) for param in self.parameters])
        return f"FunctionDeclaration: {self.return_type} {self.identifier}({params_str})"

class Parameter(ASTNode):
    """Function parameter node."""
    def __init__(self, param_type, identifier):
        super().__init__("Parameter")
        self.param_type = param_type    # Parameter type
        self.identifier = identifier    # Parameter name
    
    def __str__(self):
        return f"{self.param_type} {self.identifier}"

#==========================================================
# Statement nodes
#==========================================================
class BlockStatement(ASTNode):
    """Block statement node (enclosed in { ... })."""
    def __init__(self, statements):
        super().__init__("BlockStatement")
        self.statements = statements  # List of statements
    
    def __str__(self):
        result = "BlockStatement {\n"
        for stmt in self.statements:
            result += "  " + str(stmt).replace("\n", "\n  ") + "\n"
        result += "}"
        return result

class ExpressionStatement(ASTNode):
    """Expression statement node (e.g., x = 5;)."""
    def __init__(self, expression):
        super().__init__("ExpressionStatement")
        self.expression = expression  # Expression object
    
    def __str__(self):
        return f"ExpressionStatement: {self.expression}"

#==========================================================
# Control Flow nodes
#==========================================================
class IfStatement(ASTNode):
    """If statement node with optional else branch."""
    def __init__(self, condition, true_branch, false_branch=None):
        super().__init__("IfStatement")
        self.condition = condition      # Expression object
        self.true_branch = true_branch  # Statement to execute if condition is true
        self.false_branch = false_branch  # Optional statement for else branch
    
    def __str__(self):
        result = f"IfStatement: (condition: {self.condition})\n"
        result += f"  Then: {str(self.true_branch).replace('\n', '\n  ')}"
        if self.false_branch:
            result += f"\n  Else: {str(self.false_branch).replace('\n', '\n  ')}"
        return result

class WhileStatement(ASTNode):
    """While loop node."""
    def __init__(self, condition, body):
        super().__init__("WhileStatement")
        self.condition = condition  # Expression object
        self.body = body            # Statement object
    
    def __str__(self):
        return f"WhileStatement: (condition: {self.condition})\n  Body: {str(self.body).replace('\n', '\n  ')}"

class DoWhileStatement(ASTNode):
    """Do-while loop node."""
    def __init__(self, body, condition):
        super().__init__("DoWhileStatement")
        self.body = body            # Statement object
        self.condition = condition  # Expression object
    
    def __str__(self):
        return f"DoWhileStatement: \n  Body: {str(self.body).replace('\n', '\n  ')}\n  Condition: {self.condition}"

class ForStatement(ASTNode):
    """For loop node."""
    def __init__(self, init, condition, update, body):
        super().__init__("ForStatement")
        self.init = init            # Expression or VarDeclaration
        self.condition = condition  # Expression object
        self.update = update        # Expression object
        self.body = body            # Statement object
    
    def __str__(self):
        return f"ForStatement: (init: {self.init}, condition: {self.condition}, update: {self.update})\n  Body: {str(self.body).replace('\n', '\n  ')}"

class SwitchStatement(ASTNode):
    """Switch statement node."""
    def __init__(self, expression, cases):
        super().__init__("SwitchStatement")
        self.expression = expression  # Expression object
        self.cases = cases            # List of CaseStatement objects
    
    def __str__(self):
        result = f"SwitchStatement: (expression: {self.expression})\n"
        for case in self.cases:
            result += f"  {str(case).replace('\n', '\n  ')}\n"
        return result

class CaseStatement(ASTNode):
    """Case label within a switch statement."""
    def __init__(self, value, statements):
        super().__init__("CaseStatement")
        self.value = value          # Expression object or None for default
        self.statements = statements  # List of statements
    
    def __str__(self):
        case_str = "default" if self.value is None else f"case {self.value}"
        result = f"{case_str}:\n"
        for stmt in self.statements:
            result += f"  {str(stmt).replace('\n', '\n  ')}\n"
        return result

class BreakStatement(ASTNode):
    """Break statement node."""
    def __init__(self):
        super().__init__("BreakStatement")
    
    def __str__(self):
        return "break;"

class ContinueStatement(ASTNode):
    """Continue statement node."""
    def __init__(self):
        super().__init__("ContinueStatement")
    
    def __str__(self):
        return "continue;"

class ReturnStatement(ASTNode):
    """Return statement node with optional expression."""
    def __init__(self, expression=None):
        super().__init__("ReturnStatement")
        self.expression = expression  # Optional expression object
    
    def __str__(self):
        expr_str = str(self.expression) if self.expression else ""
        return f"return {expr_str};"

#==========================================================
# Expression nodes
#==========================================================
class BinaryExpression(ASTNode):
    """Binary expression node (e.g., a + b, x == y)."""
    def __init__(self, left, operator, right):
        super().__init__("BinaryExpression")
        self.left = left          # Left operand (Expression)
        self.operator = operator  # Operator string (+, -, *, /, etc.)
        self.right = right        # Right operand (Expression)
    
    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

class UnaryExpression(ASTNode):
    """Unary expression node (e.g., !x, ++i, j--)."""
    def __init__(self, operator, expression, is_prefix=True):
        super().__init__("UnaryExpression")
        self.operator = operator      # Operator string (!, ++, --, etc.)
        self.expression = expression  # Expression object
        self.is_prefix = is_prefix    # True for prefix (++x), False for postfix (x++)
    
    def __str__(self):
        if self.is_prefix:
            return f"({self.operator}{self.expression})"
        else:
            return f"({self.expression}{self.operator})"

class AssignmentExpression(ASTNode):
    """Assignment expression node (e.g., x = 5, y += 2)."""
    def __init__(self, left, operator, right):
        super().__init__("AssignmentExpression")
        self.left = left          # Left operand (usually an Identifier)
        self.operator = operator  # Assignment operator (=, +=, -=, etc.)
        self.right = right        # Right operand (Expression)
    
    def __str__(self):
        return f"{self.left} {self.operator} {self.right}"

class Identifier(ASTNode):
    """Identifier node representing a variable name."""
    def __init__(self, name):
        super().__init__("Identifier")
        self.name = name  # Variable name
    
    def __str__(self):
        return self.name

class Literal(ASTNode):
    """Literal node for constants (numbers, strings, characters)."""
    def __init__(self, value, literal_type):
        super().__init__("Literal")
        self.value = value              # Literal value
        self.literal_type = literal_type  # Type (NUMBER, STRING, CHAR_LITERAL)
    
    def __str__(self):
        if self.literal_type == "STRING":
            return f'"{self.value}"'
        elif self.literal_type == "CHAR_LITERAL":
            return f"'{self.value}'"
        else:
            return str(self.value)

class FunctionCall(ASTNode):
    """Function call node (e.g., printf("Hello"))."""
    def __init__(self, callee, arguments):
        super().__init__("FunctionCall")
        self.callee = callee        # Function name
        self.arguments = arguments  # List of Expression objects
    
    def __str__(self):
        args_str = ", ".join([str(arg) for arg in self.arguments])
        return f"{self.callee}({args_str})"

# Additional useful AST node classes
class ArrayAccess(ASTNode):
    """Array access node (e.g., arr[index])."""
    def __init__(self, array, index):
        super().__init__("ArrayAccess")
        self.array = array  # Array identifier or expression
        self.index = index  # Index expression
    
    def __str__(self):
        return f"{self.array}[{self.index}]"

class ArrayDeclaration(ASTNode):
    """Array declaration node (e.g., int arr[10])."""
    def __init__(self, element_type, identifier, size=None, initializer=None):
        super().__init__("ArrayDeclaration")
        self.element_type = element_type  # Element type
        self.identifier = identifier      # Array identifier
        self.size = size                  # Optional size expression
        self.initializer = initializer    # Optional initializer list
    
    def __str__(self):
        size_str = f"[{self.size}]" if self.size else "[]"
        init_str = f" = {self.initializer}" if self.initializer else ""
        return f"ArrayDeclaration: {self.element_type} {self.identifier}{size_str}{init_str}"

class StructDeclaration(ASTNode):
    """Struct declaration node."""
    def __init__(self, struct_name, fields):
        super().__init__("StructDeclaration")
        self.struct_name = struct_name  # Optional struct name
        self.fields = fields            # List of struct fields
    
    def __str__(self):
        name_str = f" {self.struct_name}" if self.struct_name else ""
        result = f"struct{name_str} {{\n"
        for field in self.fields:
            result += f"  {field};\n"
        result += "}"
        return result

class StructField(ASTNode):
    """Field declaration within a struct."""
    def __init__(self, field_type, identifier):
        super().__init__("StructField")
        self.field_type = field_type  # Field type
        self.identifier = identifier  # Field name
    
    def __str__(self):
        return f"{self.field_type} {self.identifier}"

class StructAccess(ASTNode):
    """Struct field access node (e.g., obj.field or ptr->field)."""
    def __init__(self, object_expr, field, is_pointer=False):
        super().__init__("StructAccess")
        self.object_expr = object_expr  # Object expression
        self.field = field              # Field name
        self.is_pointer = is_pointer    # True for -> access, False for . access
    
    def __str__(self):
        separator = "->" if self.is_pointer else "."
        return f"{self.object_expr}{separator}{self.field}"

class ConditionalExpression(ASTNode):
    """Ternary conditional expression (e.g., a > b ? a : b)."""
    def __init__(self, condition, true_expr, false_expr):
        super().__init__("ConditionalExpression")
        self.condition = condition  # Condition expression
        self.true_expr = true_expr  # Expression if condition is true
        self.false_expr = false_expr  # Expression if condition is false
    
    def __str__(self):
        return f"({self.condition} ? {self.true_expr} : {self.false_expr})"

class SizeofExpression(ASTNode):
    """Sizeof expression node."""
    def __init__(self, operand):
        super().__init__("SizeofExpression")
        self.operand = operand  # Type or expression
    
    def __str__(self):
        return f"sizeof({self.operand})"

class TypeCastExpression(ASTNode):
    """Type cast expression node (e.g., (int)x)."""
    def __init__(self, cast_type, expression):
        super().__init__("TypeCastExpression")
        self.cast_type = cast_type    # Target type
        self.expression = expression  # Expression to cast
    
    def __str__(self):
        return f"({self.cast_type}){self.expression}"
