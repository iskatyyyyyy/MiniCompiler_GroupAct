#will update if changes are made in parser
from ast_nodes import *
from ast_utils import expression_to_str

class Semantic:
    def __init__(self):
        self.errors = False
        self.symbol_table = {}
        self.struct_definitions = set()

    def analyze(self, node):
        if isinstance(node, Program):
            for stmt in node.statements:
                self.analyze(stmt)

        elif isinstance(node, Block):
            for stmt in node.statements:
                self.analyze(stmt)

        elif isinstance(node, VariableDeclaration):
            var_type = node.var_type
            var_name = node.name
            initializer = node.initializer

            if var_name in self.symbol_table:
                print(f"Error: Variable '{var_name}' redeclared.")
                self.errors = True
                return

            # Store variable
            self.symbol_table[var_name] = var_type

            # Check initializer
            if initializer:
                self.check_initialization(var_type, var_name, initializer)

        elif isinstance(node, AssignmentExpression):
            left = node.left
            right = node.right

            if isinstance(left, VariableNode):
                if left.name not in self.symbol_table:
                    print(f"Error: Variable '{left.name}' used before declaration.")
                    self.errors = True
                else:
                    self.check_assignment(self.symbol_table[left.name], right)

        elif isinstance(node, IfStatement):
            self.analyze(node.condition)
            self.analyze(node.then_branch)
            if node.else_branch:
                self.analyze(node.else_branch)

        elif isinstance(node, WhileStatement):
            self.analyze(node.condition)
            self.analyze(node.body)

        elif isinstance(node, ForStatement):
            self.analyze(node.init)
            self.analyze(node.condition)
            self.analyze(node.increment)
            self.analyze(node.body)

        elif isinstance(node, FunctionDeclaration):
            for _, param_name in node.parameters:
                self.symbol_table[param_name] = "param"
            self.analyze(node.body)

        elif isinstance(node, ExpressionStatement):
            self.analyze(node.expression)

        elif isinstance(node, ReturnStatement):
            self.analyze(node.value)

        elif isinstance(node, BinaryOperation):
            if node.operator == '/' and isinstance(node.right, Number) and node.right.value == 0:
                print("Error: Division by zero.")
                self.errors = True
            self.analyze(node.left)
            self.analyze(node.right)

        elif isinstance(node, UnaryOperation):
            self.analyze(node.operand)

        elif isinstance(node, FunctionCallNode):
            for arg in node.args:
                self.analyze(arg)

        elif isinstance(node, AssignmentExpression):
            self.analyze(node.left)
            self.analyze(node.right)

    def check_initialization(self, var_type, var_name, initializer):
        if isinstance(initializer, Number):
            if var_type in ["int", "short", "long", "long long"]:
                return
            elif var_type in ["float", "double", "long double"]:
                return
            else:
                print(f"Error: Type mismatch in initialization of '{var_name}' with numeric literal.")
                self.errors = True

        elif isinstance(initializer, CharNode):
            if var_type != "char":
                print(f"Error: Type mismatch in initialization of '{var_name}' with char.")
                self.errors = True

        elif isinstance(initializer, StringNode):
            if var_type != "char[]":
                print(f"Error: Type mismatch in initialization of '{var_name}' with string.")
                self.errors = True

        elif isinstance(initializer, FunctionCallNode):
            # Basic allowance for stdlib functions like rand()
            return

        elif isinstance(initializer, BinaryOperation):
            self.analyze(initializer)

        elif isinstance(initializer, UnaryOperation):
            self.analyze(initializer)

        elif isinstance(initializer, list):
            # Array initialization check
            if isinstance(initializer[0], list):  # 2D array
                rows = len(initializer)
                cols = [len(r) for r in initializer]
                if len(set(cols)) > 1:
                    print(f"Error: Inconsistent number of columns in 2D array '{var_name}'.")
                    self.errors = True
            else:  # 1D array
                if not all(isinstance(e, Number) for e in initializer):
                    print(f"Error: Non-integer elements in array initialization of '{var_name}'.")
                    self.errors = True
        else:
            print(f"Warning: Unhandled initializer type for '{var_name}': {type(initializer).__name__}")

    def check_assignment(self, expected_type, right_expr):
        if isinstance(right_expr, Number):
            if expected_type not in ["int", "short", "long", "long long", "float", "double", "long double"]:
                print(f"Error: Type mismatch in assignment to '{expected_type}'.")
                self.errors = True

        elif isinstance(right_expr, CharNode):
            if expected_type != "char":
                print(f"Error: Type mismatch in assignment to 'char'.")
                self.errors = True

        elif isinstance(right_expr, StringNode):
            if expected_type != "char[]":
                print(f"Error: Type mismatch in assignment to 'char[]'.")
                self.errors = True

        elif isinstance(right_expr, BinaryOperation) or isinstance(right_expr, UnaryOperation):
            self.analyze(right_expr)

        elif isinstance(right_expr, VariableNode):
            if right_expr.name not in self.symbol_table:
                print(f"Error: Variable '{right_expr.name}' used before declaration.")
                self.errors = True

        else:
            print(f"Warning: Unhandled assignment expression type: {type(right_expr).__name__}")

    def report(self):
        if not self.errors:
            print("No semantic errors found.")
