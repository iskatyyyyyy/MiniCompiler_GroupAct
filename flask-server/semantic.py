import re
from lexical import Tokens, Lexical

# Import updated AST node names
from ast_nodes import (
    ASTNode, ProgramNode, DeclarationNode, FunctionNode, ParameterNode,
    BlockNode, IfNode, WhileNode, DoWhileNode, ForNode, SwitchNode, CaseNode,
    BreakNode, ContinueNode, ReturnNode, BinaryOpNode, UnaryOpNode, AssignmentNode,
    IdentifierNode, LiteralNode, FunctionCallNode
)

class Semantic:

    @staticmethod
    def analyze_code(lines):
        errors = []
        struct_definitions = set()
        declared_variables = {}
        user_defined_types = set()  

        # Add 'rand' and other common library functions as known functions
        known_functions = {"rand", "srand", "printf", "time", "main"}

        for i, line in enumerate(lines):
            line = line.strip()

            # Skip empty lines and comment lines
            if not line or line.startswith("//"):
                continue

            # Ignore preprocessor directives
            if line.startswith("#include"):
                continue

            # Handle case and default statements differently (no semicolon required)
            if "case" in line or line.startswith("default:"):
                continue

            # Handle break statement (ignore as invalid variable declaration)
            if "break;" in line:
                continue

            # Handle function calls (no semicolon check needed)
            if re.match(r"\w+\s*\(.*\)\s*;", line):
                continue

            # Skip control structures or braces (no semicolon needed after these)
            if (line.endswith("{") or line == "}" or
                re.match(r".*\)\s*{", line) or
                re.match(r"\s*(if|while|for|switch)\s*\(.*\)\s*{?", line)):
                continue

            # Handle return statement
            if line.startswith("return"):
                if not line.endswith(";"):
                    errors.append(f"\nLine {i + 1}: Missing semicolon after return.")
                continue

            # Skip function calls
            if re.match(r"\w+\s*\(.*\)\s*;", line):
                continue

            # Require semicolon for declarations/assignments
            if not line.endswith(";"):
                errors.append(f"\nLine {i + 1}: Missing semicolon at the end.")
                continue

            clean_line = line.rstrip(";")

            # Skip control structures or braces
            if (line.endswith("{") or line == "}" or
                re.match(r".*\)\s*{", line) or
                re.match(r"\s*(if|while|for|switch)\s*\(.*\)\s*{?", line)):
                continue

            # Struct definition
            struct_match = re.match(r"struct\s+(\w+)\s*{", clean_line)
            if struct_match:
                struct_definitions.add(struct_match.group(1))
                continue

            typedef_struct_match = re.match(r"typedef\s+struct\s+(\w*)\s*{", clean_line)
            if typedef_struct_match:
                # Handle case: typedef struct { ... } Name;
                continue  # You could expand logic here later
            elif re.match(r"typedef\s+struct\s*{[^}]*}\s*(\w+);", clean_line):
                typedef_name = re.findall(r"}\s*(\w+);", clean_line)[0]
                struct_definitions.add(typedef_name)
                continue

            # Detect multiple declarations (with or without initialization)
            tokens = clean_line.split(None, 1)
            if len(tokens) == 2:
                var_type, rest = tokens
                variables = [v.strip() for v in rest.split(",")]

                for var in variables:
                    var_name = var
                    value = None

                    # Handle initialization
                    if "=" in var:
                        var_name, value = [x.strip() for x in var.split("=", 1)]

                    if var_name in declared_variables or var_name in known_functions:
                        continue  

                    # Array detection
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

                    # Type validation (same as original logic)
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
                continue  # Skip the old declaration logic if multi-decl was used

            # === FALLBACK to existing single-declaration logic ===

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

                # Skip 'rand' and 'srand' function calls in initialization
                if "rand()" in line or "srand()" in line:
                    continue  # Ignore this line as it's a valid function call

                if var_name == "rand" or var_name == "srand":
                    continue  # Skip 'rand' and 'srand' checks, treat them as valid functions

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
                tokens = clean_line.split()
                if len(tokens) != 2:
                    errors.append(f"\nLine {i + 1}: Invalid variable declaration.")
                    continue
                var_type, var_name = tokens
                value = None

            # Array detection
            size_match = re.findall(r"\[(\d*)\]", var_name)
            dimensions = [int(dim) for dim in size_match if dim.isdigit()]
            is_2d_array = len(dimensions) == 2
            is_1d_array = len(dimensions) == 1 or "[]" in var_name
            is_array = is_1d_array or is_2d_array

            if is_array:
                var_type = var_type.replace("[]", "")
                var_name = var_name.split("[")[0]

            # Check for redeclaration
            if var_name in declared_variables:
                existing_type = declared_variables[var_name]
                if (is_1d_array and existing_type == "2D") or (is_2d_array and existing_type == "1D"):
                    errors.append(f"\nLine {i + 1}: Error - '{var_name}' cannot be declared as both 1D and 2D array.")
                else:
                    errors.append(f"\nLine {i + 1}: Error - Variable '{var_name}' is already declared.")
                continue
            else:
                declared_variables[var_name] = "2D" if is_2d_array else "1D" if is_1d_array else "scalar"

            # Type validation
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

        # Return the errors list to ensure the semantic output is populated
        return errors
