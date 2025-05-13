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
        errors = []  # ← change from boolean to list
        struct_definitions = set()
        declared_variables = {}

        for i, line in enumerate(lines):
            line = line.strip()

            if re.search(r"/\s*0(\D|$)", line):
                errors.append(f"Line {i + 1}: Error - Division by zero detected.")

            if (line.endswith("{") or line == "}" or 
                re.match(r".*\)\s*{", line) or 
                re.match(r"\s*(if|while|for|switch)\s*\(.*\)\s*{?", line)):
                continue

            should_end_with_semicolon = (
                re.match(r"\s*(int|float|double|char|bool|long|short|void|struct)\b", line) or
                re.match(r"\s*[\w\[\]\"\'\(\)]+\s*=", line) or
                re.match(r"\s*\w+\s*\(.*\)\s*;?", line)
            )
            if should_end_with_semicolon and not line.endswith(";"):
                errors.append(f"Line {i + 1}: Missing semicolon at the end.")
                continue

            struct_match = re.match(r"struct\s+(\w+)\s*{", line)
            if struct_match:
                struct_definitions.add(struct_match.group(1))
                continue

            if "=" in line:
                parts = line.split("=", 1)
                var_decl = parts[0].strip()
                value = parts[1].strip(";").strip()
            else:
                var_decl = line.strip(";").strip()
                value = None

            if re.match(r"\w+\s*\(.*\)\s*;", line):
                continue
            var_parts = var_decl.split()
            if len(var_parts) < 2:
                errors.append(f"Line {i + 1}: Invalid variable declaration.")
                continue

            var_type = var_parts[0]
            var_name = var_parts[1]

            size_match = re.findall(r"\[(\d*)\]", var_name)
            dimensions = [int(dim) for dim in size_match if dim.isdigit()]
            is_2d_array = len(dimensions) == 2
            is_1d_array = len(dimensions) == 1 or "[]" in var_name
            is_array = is_1d_array or is_2d_array

            if is_array:
                var_type = var_type.replace("[]", "")
                var_name = var_name.split("[")[0]

            if var_name in declared_variables:
                existing_type = declared_variables[var_name]
                if (is_1d_array and existing_type == "2D") or (is_2d_array and existing_type == "1D"):
                    errors.append(f"Line {i + 1}: Error - '{var_name}' cannot be declared as both 1D and 2D array.")
                else:
                    errors.append(f"Line {i + 1}: Error - Variable '{var_name}' is already declared.")
            else:
                declared_variables[var_name] = "2D" if is_2d_array else "1D" if is_1d_array else "scalar"

            if var_type in ["int", "long", "long long", "short"]:
                if is_2d_array:
                    if not (value and value.startswith("{{") and value.endswith("}}")):
                        errors.append(f"Line {i + 1}: Invalid initialization for 2D '{var_type}[][]'. Must use nested {{}}.")
                elif is_1d_array:
                    if not (value and value.startswith("{") and value.endswith("}")):
                        errors.append(f"Line {i + 1}: Invalid array initialization for '{var_type}[]'. Must use {{}}.")
                    else:
                        elements = value.strip("{}").split(",")
                        elements = [ele.strip() for ele in elements]
                        if not all(ele.isdigit() for ele in elements):
                            errors.append(f"Line {i + 1}: Datatype mismatch in '{var_type}[]' initialization.")
                        if dimensions and len(elements) != dimensions[0]:
                            errors.append(f"Line {i + 1}: Expected {dimensions[0]} elements, but found {len(elements)}.")
                else:
                    if value and not value.isdigit():
                        errors.append(f"Line {i + 1}: Datatype mismatch for '{var_type}'.")

            elif var_type in ["float", "double", "long double"]:
                try:
                    if value:
                        float(value)
                except ValueError:
                    errors.append(f"Line {i + 1}: Datatype mismatch for '{var_type}'.")

            elif var_type == "bool":
                if value and value not in ["true", "false"]:
                    errors.append(f"Line {i + 1}: Invalid initialization for 'bool'. Must be 'true' or 'false'.")

            elif var_type in struct_definitions:
                if not (value and value.startswith("{") and value.endswith("}")):
                    errors.append(f"Line {i + 1}: Invalid struct initialization. Must use '{{}}'.")

            elif var_type == "char":
                if value:
                    value = value.strip()
                    if len(value) != 3 or value[0] != "'" or value[-1] != "'":
                        errors.append(f"Line {i + 1}: Invalid initialization for 'char'.")

            elif var_type == "char[]" or (var_type == "char" and is_array):
                if value and (not value.startswith("\"") or not value.endswith("\"")):
                    errors.append(f"Line {i + 1}: Datatype mismatch for 'char[]'. Use double quotes.")

            else:
                errors.append(f"Line {i + 1}: Unknown data type '{var_type}'.")

        if not errors:
            return ["No semantic errors found."]
        return errors

