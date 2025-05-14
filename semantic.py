
import re

# Import token types and lexical analyzer 
from lexical import Tokens, Lexical

# Import (AST) node classes
from ast_nodes import (
    ASTNode, ProgramNode, DeclarationNode, FunctionNode, ParameterNode,
    BlockNode, IfNode, WhileNode, DoWhileNode, ForNode, SwitchNode, CaseNode,
    BreakNode, ContinueNode, ReturnNode, BinaryOpNode, UnaryOpNode, AssignmentNode,
    IdentifierNode, LiteralNode, FunctionCallNode
)

class Semantic:

    # Static method to analyze code line by line
    @staticmethod
    def analyze_code(lines):
        errors = []                     
        struct_definitions = set()      # Track defined struct names
        declared_variables = {}         
        user_defined_types = set()      # Set to store any custom user-defined types

        # Define a set of known standard library functions
        known_functions = {"rand", "srand", "printf", "time", "main"}

        for i, line in enumerate(lines):
            line = line.strip()  
            
            # Skip empty lines or comments
            if not line or line.startswith("//"):
                continue

            # Skip preprocessor directives like #include
            if line.startswith("#include"):
                continue

            # Skip 'case' and 'default' labels which are not variable declarations
            if "case" in line or line.startswith("default:"):
                continue

            # Skip break statements
            if "break;" in line:
                continue

            # Skip function call lines like printf("hello");
            if re.match(r"\w+\s*\(.*\)\s*;", line):
                continue

            # Skip control flow structures and opening/closing braces
            if (line.endswith("{") or line == "}" or
                re.match(r".*\)\s*{", line) or
                re.match(r"\s*(if|while|for|switch)\s*\(.*\)\s*{?", line)):
                continue

            # Check for missing semicolon after return statement
            if line.startswith("return"):
                if not line.endswith(";"):
                    errors.append(f"\nLine {i + 1}: Missing semicolon after return.")
                continue

            # Skip function calls again for redundancy
            if re.match(r"\w+\s*\(.*\)\s*;", line):
                continue

            # Report error if declaration/assignment line does not end with semicolon
            if not line.endswith(";"):
                errors.append(f"\nLine {i + 1}: Missing semicolon at the end.")
                continue

            # Remove trailing semicolon for further analysis
            clean_line = line.rstrip(";")

            # Again, skip control structure braces
            if (line.endswith("{") or line == "}" or
                re.match(r".*\)\s*{", line) or
                re.match(r"\s*(if|while|for|switch)\s*\(.*\)\s*{?", line)):
                continue

            # Detect struct definition like: struct Name {
            struct_match = re.match(r"struct\s+(\w+)\s*{", clean_line)
            if struct_match:
                struct_definitions.add(struct_match.group(1))
                continue

            # Handle typedef struct { ... } Name;
            typedef_struct_match = re.match(r"typedef\s+struct\s+(\w*)\s*{", clean_line)
            if typedef_struct_match:
                continue  # Logic can be expanded later for full typedef handling
            elif re.match(r"typedef\s+struct\s*{[^}]*}\s*(\w+);", clean_line):
                typedef_name = re.findall(r"}\s*(\w+);", clean_line)[0]
                struct_definitions.add(typedef_name)
                continue

            # Attempt to split line into datatype and variable declaration(s)
            # Same semantic rules (e.g., type checking, initialization format) But since the parsing is structurally different, the analysis must be reapplied in both blocks.
            tokens = clean_line.split(None, 1)
            if len(tokens) == 2:
                var_type, rest = tokens
                variables = [v.strip() for v in rest.split(",")]  # Support comma-separated declarations

                for var in variables:
                    var_name = var
                    value = None  # Default value to None

                    # Handle inline initialization like int x = 10;
                    if "=" in var:
                        var_name, value = [x.strip() for x in var.split("=", 1)]

                    # Skip already declared or function-named variables
                    if var_name in declared_variables or var_name in known_functions:
                        continue  

                    # Detect array dimensions like arr[2][3]
                    size_match = re.findall(r"\[(\d*)\]", var_name)
                    dimensions = [int(dim) for dim in size_match if dim.isdigit()]
                    is_2d_array = len(dimensions) == 2
                    is_1d_array = len(dimensions) == 1 or "[]" in var_name
                    is_array = is_1d_array or is_2d_array

                    # Extract actual variable name from array notation
                    if is_array:
                        var_type = var_type.replace("[]", "")
                        var_name = var_name.split("[")[0]

                    # Check if variable was already declared
                    if var_name in declared_variables:
                        existing_type = declared_variables[var_name]
                        if (is_1d_array and existing_type == "2D") or (is_2d_array and existing_type == "1D"):
                            errors.append(f"\nLine {i + 1}: Error - '{var_name}' cannot be declared as both 1D and 2D array.")
                        else:
                            errors.append(f"\nLine {i + 1}: Error - Variable '{var_name}' is already declared.")
                        continue
                    else:
                        declared_variables[var_name] = "2D" if is_2d_array else "1D" if is_1d_array else "scalar"

                    # Perform type checking and value validation
                    if var_type in ["int", "long", "long long", "short"]:
                        if is_2d_array:
                            if not (value and value.startswith("{{") and value.endswith("}}")):
                                errors.append(f"\nLine {i + 1}: Invalid initialization for 2D '{var_type}[][]'. Must use nested {{}}.")
                        elif is_1d_array:
                            if not (value and value.startswith("{") and value.endswith("}")):
                                errors.append(f"\nLine {i + 1}: Invalid array initialization for '{var_type}[]'. Must use {{}}.")
                            else:
                                elements = value.strip("{}").split(",")
                                elements = [ele.strip() for ele in elements]
                                if not all(ele.isdigit() for ele in elements):
                                    errors.append(f"\nLine {i + 1}: Datatype mismatch in '{var_type}[]' initialization.")
                                if dimensions and len(elements) != dimensions[0]:
                                    errors.append(f"\nLine {i + 1}: Expected {dimensions[0]} elements, but found {len(elements)}.")
                        else:
                            if value:
                                tokens = re.findall(r'\b\w+\b', value)
                                for token in tokens:
                                    if not token.isdigit() and token not in declared_variables:
                                        errors.append(f"\nLine {i + 1}: Unknown variable '{token}' used in initialization.")

                    elif var_type in ["float", "double", "long double"]:
                        if value:
                            tokens = re.findall(r'\b\w+\b', value)
                            for token in tokens:
                                if not token.replace('.', '', 1).isdigit() and token not in declared_variables:
                                    errors.append(f"\nLine {i + 1}: Unknown variable '{token}' used in initialization.")

                    elif var_type == "bool":
                        if value and value not in ["true", "false"]:
                            errors.append(f"\nLine {i + 1}: Invalid initialization for 'bool'. Must be 'true' or 'false'.")

                    elif var_type in struct_definitions or var_type in user_defined_types:
                        if not (value and value.startswith("{") and value.endswith("}")):
                            errors.append(f"\nLine {i + 1}: Invalid struct initialization. Must use '{{}}'.")

                    elif var_type == "char":
                        if value:
                            value = value.strip()
                            if len(value) != 3 or value[0] != "'" or value[-1] != "'":
                                errors.append(f"\nLine {i + 1}: Invalid initialization for 'char'.")

                    elif var_type == "char[]" or (var_type == "char" and is_array):
                        if value and value.startswith("{") and value.endswith("}"):
                            if not all(c.startswith('"') and c.endswith('"') for c in value.strip("{}").split(",")):
                                errors.append(f"\nLine {i + 1}: Invalid character array initialization.")
                        else:
                            errors.append(f"\nLine {i + 1}: Invalid initialization for 'char[]'. Must be enclosed in {{}}.")
                    else:
                        errors.append(f"\nLine {i + 1}: Unsupported datatype '{var_type}'.")
                continue  # Skip remaining logic if this multi-declaration was handled

# Same semantic rules (e.g., type checking, initialization format) But since the parsing is structurally different, the analysis must be reapplied in both blocks.
            # Fallback to handle simple single variable declarations or assignments
            if "=" in clean_line:
                parts = clean_line.split("=", 1)
                left = parts[0].strip()
                right = parts[1].strip()
                tokens = left.split()

                if len(tokens) == 2:
                    var_type, var_name = tokens
                    value = right
                    is_declaration = True
                else:
                    var_name = left
                    value = right
                    is_declaration = False

                # Skip lines like int x = rand();
                if "rand()" in line or "srand()" in line:
                    continue

                if var_name == "rand" or var_name == "srand":
                    continue

                if var_type in ["float", "double", "long double"]:
                    try:
                        if value:
                            float(value)
                    except ValueError:
                        errors.append(f"\nLine {i + 1}: Datatype mismatch for '{var_type}'.")

                if not is_declaration:
                    if var_name not in declared_variables:
                        errors.append(f"\nLine {i + 1}: Assignment to undeclared variable '{var_name}'.")
                    continue
            else:
                # Split declaration like int x;
                tokens = clean_line.split()
                if len(tokens) != 2:
                    errors.append(f"\nLine {i + 1}: Invalid variable declaration.")
                    continue
                var_type, var_name = tokens
                value = None

            # Handle array detection again
            size_match = re.findall(r"\[(\d*)\]", var_name)
            dimensions = [int(dim) for dim in size_match if dim.isdigit()]
            is_2d_array = len(dimensions) == 2
            is_1d_array = len(dimensions) == 1 or "[]" in var_name
            is_array = is_1d_array or is_2d_array

            if is_array:
                var_type = var_type.replace("[]", "")
                var_name = var_name.split("[")[0]

            # Redeclaration check
            if var_name in declared_variables:
                existing_type = declared_variables[var_name]
                if (is_1d_array and existing_type == "2D") or (is_2d_array and existing_type == "1D"):
                    errors.append(f"\nLine {i + 1}: Error - '{var_name}' cannot be declared as both 1D and 2D array.")
                else:
                    errors.append(f"\nLine {i + 1}: Error - Variable '{var_name}' is already declared.")
                continue
            else:
                declared_variables[var_name] = "2D" if is_2d_array else "1D" if is_1d_array else "scalar"

            # Type checking repeated for fallback block
            if var_type in ["int", "long", "long long", "short"]:
                if is_2d_array:
                    if not (value and value.startswith("{{") and value.endswith("}}")):
                        errors.append(f"\nLine {i + 1}: Invalid initialization for 2D '{var_type}[][]'. Must use nested {{}}.")
                elif is_1d_array:
                    if not (value and value.startswith("{") and value.endswith("}")):
                        errors.append(f"\nLine {i + 1}: Invalid array initialization for '{var_type}[]'. Must use {{}}.")
                    else:
                        elements = value.strip("{}").split(",")
                        elements = [ele.strip() for ele in elements]
                        if not all(ele.isdigit() for ele in elements):
                            errors.append(f"\nLine {i + 1}: Datatype mismatch in '{var_type}[]' initialization.")
                        if dimensions and len(elements) != dimensions[0]:
                            errors.append(f"\nLine {i + 1}: Expected {dimensions[0]} elements, but found {len(elements)}.")
                else:
                    if value:
                        tokens = re.findall(r'\b\w+\b', value)
                        for token in tokens:
                            if not token.isdigit() and token not in declared_variables:
                                errors.append(f"\nLine {i + 1}: Unknown variable '{token}' used in initialization.")

            elif var_type in ["float", "double", "long double"]:
                try:
                    if value:
                        float(value)
                except ValueError:
                    errors.append(f"\nLine {i + 1}: Datatype mismatch for '{var_type}'.")

            elif var_type == "bool":
                if value and value not in ["true", "false"]:
                    errors.append(f"\nLine {i + 1}: Invalid initialization for 'bool'. Must be 'true' or 'false'.")

            elif var_type in struct_definitions:
                if not (value and value.startswith("{") and value.endswith("}")):
                    errors.append(f"\nLine {i + 1}: Invalid struct initialization. Must use '{{}}'.")

            elif var_type == "char":
                if value:
                    value = value.strip()
                    if len(value) != 3 or value[0] != "'" or value[-1] != "'":
                        errors.append(f"\nLine {i + 1}: Invalid initialization for 'char'.")

            elif var_type == "char[]" or (var_type == "char" and is_array):
                if value and value.startswith("{") and value.endswith("}"):
                    if not all(c.startswith('"') and c.endswith('"') for c in value.strip("{}").split(",")):
                        errors.append(f"\nLine {i + 1}: Invalid character array initialization.")
                else:
                    errors.append(f"\nLine {i + 1}: Invalid initialization for 'char[]'. Must be enclosed in {{}}.")
            else:
                errors.append(f"\nLine {i + 1}: Unsupported datatype '{var_type}'.")

        # Return all collected semantic errors
        return errors
