<<<<<<< HEAD
#will update if changes are made in parser
from ast_nodes import *
from ast_utils import expression_to_str

class Semantic:
    def __init__(self):
        self.errors = False
=======
# semantic.py (No changes needed for error collection)

from ast_nodes import *
from ast_utils import expression_to_str

class SemanticAnalyzer:
    def __init__(self):
        self.errors = []
>>>>>>> origin/master
        self.symbol_table = {}
        self.struct_definitions = set()

    def analyze(self, node):
<<<<<<< HEAD
=======
        # ... (Your existing analysis logic) ...
>>>>>>> origin/master
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
<<<<<<< HEAD
                print(f"Error: Variable '{var_name}' redeclared.")
                self.errors = True
                return

            # Store variable
            self.symbol_table[var_name] = var_type

            # Check initializer
=======
                self.errors.append(f"Variable '{var_name}' redeclared.")
                # No return here, allow further analysis for other potential errors
            else:
                self.symbol_table[var_name] = var_type

>>>>>>> origin/master
            if initializer:
                self.check_initialization(var_type, var_name, initializer)

        elif isinstance(node, AssignmentExpression):
            left = node.left
            right = node.right

            if isinstance(left, VariableNode):
                if left.name not in self.symbol_table:
<<<<<<< HEAD
                    print(f"Error: Variable '{left.name}' used before declaration.")
                    self.errors = True
                else:
                    self.check_assignment(self.symbol_table[left.name], right)
=======
                    self.errors.append(f"Variable '{left.name}' used before declaration.")
                else:
                    self.check_assignment(self.symbol_table[left.name], right)
            # Add analysis for other types of left-hand sides if needed (e.g., array access)
>>>>>>> origin/master

        elif isinstance(node, IfStatement):
            self.analyze(node.condition)
            self.analyze(node.then_branch)
            if node.else_branch:
                self.analyze(node.else_branch)

        elif isinstance(node, WhileStatement):
            self.analyze(node.condition)
            self.analyze(node.body)

        elif isinstance(node, ForStatement):
<<<<<<< HEAD
            self.analyze(node.init)
            self.analyze(node.condition)
            self.analyze(node.increment)
            self.analyze(node.body)

        elif isinstance(node, FunctionDeclaration):
            for _, param_name in node.parameters:
                self.symbol_table[param_name] = "param"
            self.analyze(node.body)
=======
            # Ensure init, condition, increment are analyzed
            if node.init: self.analyze(node.init)
            if node.condition: self.analyze(node.condition)
            if node.increment: self.analyze(node.increment)
            self.analyze(node.body)

        elif isinstance(node, FunctionDeclaration):
            # Store current symbol table to restore after function scope
            # This is a simplified approach; a proper scope management would be better
            old_symbol_table = self.symbol_table.copy()
            # Add function parameters to symbol table
            for param_type, param_name in node.parameters:
                self.symbol_table[param_name] = param_type # Use param_type for better checking
            self.analyze(node.body)
            # Restore symbol table after function analysis
            self.symbol_table = old_symbol_table
>>>>>>> origin/master

        elif isinstance(node, ExpressionStatement):
            self.analyze(node.expression)

        elif isinstance(node, ReturnStatement):
<<<<<<< HEAD
            self.analyze(node.value)

        elif isinstance(node, BinaryOperation):
            if node.operator == '/' and isinstance(node.right, Number) and node.right.value == 0:
                print("Error: Division by zero.")
                self.errors = True
=======
            # Check if return value matches function's return type (requires function symbol table)
            self.analyze(node.value)

        elif isinstance(node, BinaryOperation):
            # Check for division by zero
            if node.operator == '/' and isinstance(node.right, Number) and node.right.value == 0:
                self.errors.append("Division by zero.")
>>>>>>> origin/master
            self.analyze(node.left)
            self.analyze(node.right)

        elif isinstance(node, UnaryOperation):
            self.analyze(node.operand)

        elif isinstance(node, FunctionCallNode):
<<<<<<< HEAD
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
=======
            # Basic check: ensure the function is declared (e.g., in symbol table)
            # More advanced: check argument types and count
            if node.name not in self.symbol_table: # This assumes functions are in symbol table
                self.errors.append(f"Function '{node.name}' called before declaration.")
            for arg in node.args:
                self.analyze(arg)

        # Add more AST node types as needed (e.g., ArrayAccess, StructDeclaration, etc.)
        # If a node type is not handled, you might want to add a default error or log
        # else:
        #    self.errors.append(f"Unhandled AST node type in semantic analysis: {type(node).__name__}")


    def check_initialization(self, var_type, var_name, initializer):
        # This needs to recursively check the type of the initializer expression
        # For simplicity, I'll keep your existing checks.
        # A full type system would involve inferring the type of initializer.
        if isinstance(initializer, Number):
            if var_type not in ["int", "short", "long", "long long", "float", "double", "long double"]:
                self.errors.append(f"Type mismatch in initialization of '{var_name}' with number.")
        elif isinstance(initializer, CharNode):
            if var_type != "char":
                self.errors.append(f"Type mismatch in initialization of '{var_name}' with char.")
        elif isinstance(initializer, StringNode):
            if var_type != "char[]": # This might need to be 'char*' or more complex for C strings
                self.errors.append(f"Type mismatch in initialization of '{var_name}' with string.")
        elif isinstance(initializer, BinaryOperation) or isinstance(initializer, UnaryOperation):
            self.analyze(initializer) # Analyze the expression to catch errors within it
        elif isinstance(initializer, VariableNode): # Check if initializing with another variable
            if initializer.name not in self.symbol_table:
                self.errors.append(f"Variable '{initializer.name}' used before declaration in initializer.")
            else:
                # Basic type compatibility check (can be expanded)
                init_var_type = self.symbol_table[initializer.name]
                if init_var_type != var_type: # Very simplistic type check
                    self.errors.append(f"Type mismatch: '{var_name}' ({var_type}) initialized with '{initializer.name}' ({init_var_type}).")
        elif isinstance(initializer, list): # For array initializers
            if isinstance(initializer[0], list): # 2D array
                rows = len(initializer)
                cols = [len(r) for r in initializer]
                if len(set(cols)) > 1:
                    self.errors.append(f"Inconsistent number of columns in 2D array '{var_name}'.")
                # Further check element types in 2D array
                for row in initializer:
                    for element in row:
                        self.analyze(element) # Analyze each element
            else: # 1D array
                if not all(isinstance(e, (Number, CharNode, StringNode, VariableNode)) for e in initializer):
                    self.errors.append(f"Invalid elements in array initialization of '{var_name}'.")
                # Further check element types in 1D array
                for element in initializer:
                    self.analyze(element) # Analyze each element
        else:
            self.errors.append(f"Unhandled initializer type for '{var_name}': {type(initializer).__name__}")


    def check_assignment(self, expected_type, right_expr):
        # This also needs to recursively check the type of the right_expr
        # A full type system would involve inferring the type of right_expr.
        if isinstance(right_expr, Number):
            if expected_type not in ["int", "short", "long", "long long", "float", "double", "long double"]:
                self.errors.append(f"Type mismatch in assignment to '{expected_type}' with number.")
        elif isinstance(right_expr, CharNode):
            if expected_type != "char":
                self.errors.append(f"Type mismatch in assignment to 'char' with char.")
        elif isinstance(right_expr, StringNode):
            if expected_type != "char[]":
                self.errors.append(f"Type mismatch in assignment to 'char[]' with string.")
        elif isinstance(right_expr, BinaryOperation) or isinstance(right_expr, UnaryOperation):
            self.analyze(right_expr) # Analyze the expression to catch errors within it
        elif isinstance(right_expr, VariableNode):
            if right_expr.name not in self.symbol_table:
                self.errors.append(f"Variable '{right_expr.name}' used before declaration in assignment.")
            else:
                # Basic type compatibility check (can be expanded)
                right_var_type = self.symbol_table[right_expr.name]
                if right_var_type != expected_type: # Very simplistic type check
                    self.errors.append(f"Type mismatch: assigning '{right_var_type}' to '{expected_type}'.")
        elif isinstance(right_expr, FunctionCallNode):
            self.analyze(right_expr) # Analyze the function call
            # More advanced: check return type of function call against expected_type
        else:
            self.errors.append(f"Unhandled assignment expression type: {type(right_expr).__name__}")
>>>>>>> origin/master
