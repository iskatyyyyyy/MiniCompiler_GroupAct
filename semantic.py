class Semantic: 

    def analyze_code(lines):  
        errors = False  # Flag to check if any semantic errors are found.
        struct_definitions = set()  # Set to store names of user-defined structs (ensures uniqueness)
        declared_variables = {}  # Dictionary to track declared variables and their types.

        for i, line in enumerate(lines):  # Loop over each line with its index
            line = line.strip()  # Remove leading and trailing whitespace.
            # Rule: Detect division by zero
            division_by_zero_pattern = r"/\s*0(\D|$)" # raw string
            if re.search(division_by_zero_pattern, line): 
                print(f"Line {i + 1}: Error - Division by zero detected.")
                errors = True

            # Rule 1: Check if the line ends with a semicolon (except struct definitions).
            if not line.endswith(";") and "struct" not in line:
                print(f"Line {i + 1}: Missing semicolon at the end.")  # Print error message.
                errors = True  # Set error flag to True.
                continue  # Skip further processing for this line.

            # SKIP
            struct_match = re.match(r"struct\s+(\w+)\s*{", line)  
            if struct_match:
                struct_name = struct_match.group(1)  
                struct_definitions.add(struct_name)  
                continue 

            # If line contains an assignment ('='), separate declaration from value.
            if "=" in line:
                parts = line.split("=", 1)  # Split into left and right part at the first '='.
                var_decl = parts[0].strip()  # Get the declaration part.
                value = parts[1].strip(";").strip()  # Get the initialization value (remove semicolon).
            else:
                var_decl = line.strip(";").strip()  # If no '=', it's a declaration without initialization.
                value = None  # No value provided.

            # Split the declaration into type and variable name.
            var_parts = var_decl.split()  # E.g., "int x" becomes ["int", "x"].
            if len(var_parts) < 2:  # Must at least have a type and a variable.
                print(f"Line {i + 1}: Invalid variable declaration.")  # Show error.
                errors = True
                continue

            # Check for repeated types instead of commas (e.g., 'int x int y' is invalid).
            if any(var_parts[j] in ["int", "float", "char", "double", "bool", "long", "short"] for j in range(1, len(var_parts))):
                print(f"Line {i + 1}: Error - Multiple variable declarations must use commas, not repeated types.")
                errors = True
                continue

            var_type = var_parts[0]  
            var_name = var_parts[1]  

            # Detect if the variable is an array and count its dimensions.
            size_match = re.findall(r"\[(\d*)\]", var_name)  # Find all index sizes like [2][3].
            dimensions = [int(dim) for dim in size_match if dim.isdigit()]  # Convert to integers if digits.
            is_2d_array = len(dimensions) == 2  # Check if it's a 2D array.
            is_1d_array = len(dimensions) == 1 or "[]" in var_name  # Check if it's a 1D array.
            is_array = is_1d_array or is_2d_array  # Boolean flag 

            if is_array:
                var_type = var_type.replace("[]", "")  # Remove '[]' if present from type.
                var_name = var_name.split("[")[0]  # Get variable name only (remove dimensions).

            # Prevent re-declaration of the same variable or arrays with different dimensions.
            if var_name in declared_variables:
                existing_type = declared_variables[var_name]  # Get previously declared type.
                if (is_1d_array and existing_type == "2D") or (is_2d_array and existing_type == "1D"):
                    print(f"Line {i + 1}: Error - '{var_name}' cannot be declared as both 1D and 2D array.")
                    errors = True
                else:
                    print(f"Line {i + 1}: Error - Variable '{var_name}' is already declared.")
                    errors = True
            else:
                declared_variables[var_name] = "2D" if is_2d_array else "1D" if is_1d_array else "scalar"  # Save variable with type info.

            # Type checking for different data types.
            if var_type in ["int", "long", "long long", "short"]:
                # For 2D array, initialization must be in nested braces {{ }}
                if is_2d_array:
                    if not (value.startswith("{{") and value.endswith("}}")):
                        print(f"Line {i + 1}: Invalid initialization for 2D '{var_type}[][]'. Must use nested {{}}.")
                        errors = True
                # For 1D array, initialization must use braces { }
                elif is_1d_array:
                    if not (value.startswith("{") and value.endswith("}")):
                        print(f"Line {i + 1}: Invalid array initialization for '{var_type}[]'. Must use {{}}.")
                        errors = True
                    else:
                        elements = value.strip("{} ").split(",")  # Split the values by comma.
                        elements = [ele.strip() for ele in elements]  # Trim whitespace around each element.
                        if not all(ele.isdigit() for ele in elements):  # Check that all values are digits.
                            print(f"Line {i + 1}: Datatype mismatch in '{var_type}[]' initialization.")
                            errors = True
                        if dimensions and len(elements) != dimensions[0]:  # Check size match for declared dimension.
                            print(f"Line {i + 1}: Expected {dimensions[0]} elements, but found {len(elements)}.")
                            errors = True
                # For scalar int types, check if the value is a number.
                else:
                    if value and not value.isdigit():
                        print(f"Line {i + 1}: Datatype mismatch for '{var_type}'.")
                        errors = True

            # For floating point types, check if value can be converted to float.
            elif var_type in ["float", "double", "long double"]:
                try:
                    if value:
                        float(value)
                except ValueError:
                    print(f"Line {i + 1}: Datatype mismatch for '{var_type}'.")
                    errors = True

            # For bool, value must be "true" or "false".
            elif var_type == "bool":
                if value and value not in ["true", "false"]:
                    print(f"Line {i + 1}: Invalid initialization for 'bool'. Must be 'true' or 'false'.")
                    errors = True

            # For struct, check initialization format.
            elif var_type in struct_definitions:
                if not value.startswith("{") or not value.endswith("}"):
                    print(f"Line {i + 1}: Invalid struct initialization. Must use '{{}}'.")
                    errors = True

            # For char, value must be a single character enclosed in single quotes.
            elif var_type == "char":
                if value:
                    value = value.strip()
                    if len(value) != 3 or value[0] != "'" or value[-1] != "'":
                        print(f"Line {i + 1}: Invalid initialization for 'char'.")
                        errors = True

            # For char arrays, value must be in double quotes (e.g., "hello").
            elif var_type == "char[]" or (var_type == "char" and is_array):
                if value and (not value.startswith("\"") or not value.endswith("\"")):
                    print(f"Line {i + 1}: Datatype mismatch for 'char[]'. Use double quotes.")
                    errors = True

            # If the type is not recognized, show an error.
            else:
                print(f"Line {i + 1}: Unknown data type '{var_type}'.")
                errors = True

        if not errors:
            print("No errors found.")  # Show success message if no errors occurred.

    # Main driver function for the program.
    def main():
        print("Enter your code line by line. Press Enter on a blank line to finish.")  # Instruction for user input.
        user_code = []  # List to store user's code.
        while True:
            line = input("> ")  # Read user input.
            if not line.strip():  # Exit input loop if blank line is entered.
                break
            user_code.append(line)  # Add the line to the code list.
        analyze_code(user_code)  # Call the analyze function with user input.

    # Program starts here if run directly.
    if __name__ == "__main__":
        main()  # Call the main function.
