class Semantic:

    def analyze_code(lines):
        errors = False  # Flag to track if any errors are found
        struct_definitions = set()  # Track defined structs
        declared_variables = {}  # Track declared variables with their types (case-sensitive)

        for i, line in enumerate(lines):
            line = line.strip()

            # Rule 1: Check if the line ends with a semicolon
            if not line.endswith(";") and "struct" not in line:
                print(f"Line {i + 1}: Missing semicolon at the end.")
                errors = True
                continue  # Skip further checks for this line

            # Rule: Detect struct definitions
            struct_match = re.match(r"struct\s+(\w+)\s*{", line)
            if struct_match:
                struct_name = struct_match.group(1)
                struct_definitions.add(struct_name)
                continue  # Skip further checks for struct definitions

            # Rule 2-5: Check initialization rules
            if "=" in line:
                parts = line.split("=", 1)  # Ensure we only split at the first "="
                var_decl = parts[0].strip()
                value = parts[1].strip(";").strip()  # Remove semicolon before checking
            else:
                var_decl = line.strip(";").strip()
                value = None  # No initialization

            # Extract datatype and variable name
            var_parts = var_decl.split()
            if len(var_parts) < 2:
                print(f"Line {i + 1}: Invalid variable declaration.")
                errors = True
                continue

            # Check for multiple variable declarations without commas
            if any(var_parts[j] in ["int", "float", "char", "double", "bool", "long", "short"] for j in range(1, len(var_parts))):
                print(f"Line {i + 1}: Error - Multiple variable declarations must use commas, not repeated types.")
                errors = True
                continue

            var_type = var_parts[0]
            var_name = var_parts[1]

            # Check for explicit array size (e.g., int arr[2][3])
            size_match = re.findall(r"\[(\d*)\]", var_name)  # Finds all dimensions
            dimensions = [int(dim) for dim in size_match if dim.isdigit()]  # Ignore empty brackets
            is_2d_array = len(dimensions) == 2
            is_1d_array = len(dimensions) == 1 or "[]" in var_name  # Support implicit sizing
            is_array = is_1d_array or is_2d_array

            if is_array:
                var_type = var_type.replace("[]", "")  # Extract base type
                var_name = var_name.split("[")[0]  # Extract array name only

            # Prevent Redeclaration Rule (including distinction between 1D and 2D arrays)
            if var_name in declared_variables:
                existing_type = declared_variables[var_name]
                if (is_1d_array and existing_type == "2D") or (is_2d_array and existing_type == "1D"):
                    print(f"Line {i + 1}: Error - '{var_name}' cannot be declared as both 1D and 2D array.")
                    errors = True
                else:
                    print(f"Line {i + 1}: Error - Variable '{var_name}' is already declared.")
                    errors = True
            else:
                declared_variables[var_name] = "2D" if is_2d_array else "1D" if is_1d_array else "scalar"

            # Type checking
            if var_type in ["int", "long", "long long", "short"]:
                if is_2d_array:
                    if not (value.startswith("{{") and value.endswith("}}")):
                        print(f"Line {i + 1}: Invalid initialization for 2D '{var_type}[][]'. Must use nested {{}}.")
                        errors = True
                elif is_1d_array:
                    if not (value.startswith("{") and value.endswith("}")):
                        print(f"Line {i + 1}: Invalid array initialization for '{var_type}[]'. Must use {{}}.")
                        errors = True
                    else:
                        elements = value.strip("{} ").split(",")
                        elements = [ele.strip() for ele in elements]
                        if not all(ele.isdigit() for ele in elements):
                            print(f"Line {i + 1}: Datatype mismatch in '{var_type}[]' initialization.")
                            errors = True
                        if dimensions and len(elements) != dimensions[0]:
                            print(f"Line {i + 1}: Expected {dimensions[0]} elements, but found {len(elements)}.")
                            errors = True
                else:
                    if value and not value.isdigit():
                        print(f"Line {i + 1}: Datatype mismatch for '{var_type}'.")
                        errors = True

            elif var_type in ["float", "double", "long double"]:
                try:
                    if value:
                        float(value)
                except ValueError:
                    print(f"Line {i + 1}: Datatype mismatch for '{var_type}'.")
                    errors = True

            elif var_type == "bool":
                if value and value not in ["true", "false"]:
                    print(f"Line {i + 1}: Invalid initialization for 'bool'. Must be 'true' or 'false'.")
                    errors = True

            elif var_type in struct_definitions:
                if not value.startswith("{") or not value.endswith("}"):
                    print(f"Line {i + 1}: Invalid struct initialization. Must use '{{}}'.")
                    errors = True

            elif var_type == "char":
                if value:
                    value = value.strip()
                    if len(value) != 3 or value[0] != "'" or value[-1] != "'":
                        print(f"Line {i + 1}: Invalid initialization for 'char'.")
                        errors = True

            elif var_type == "char[]" or (var_type == "char" and is_array):
                if value and (not value.startswith("\"") or not value.endswith("\"")):
                    print(f"Line {i + 1}: Datatype mismatch for 'char[]'. Use double quotes.")
                    errors = True

            else:
                print(f"Line {i + 1}: Unknown data type '{var_type}'.")
                errors = True

        if not errors:
            print("No errors found.")  # Display message if all lines pass

    # Main program
    def main():
        print("Enter your code line by line. Press Enter on a blank line to finish.")
        user_code = []
        while True:
            line = input("> ")
            if not line.strip():  # Stop when the user enters a blank line
                break
            user_code.append(line)
        analyze_code(user_code)

    # Run the program
    if __name__ == "__main__":
        main()
