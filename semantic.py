class Semantic:
    def __init__(self):
        self.errors = False
        self.struct_definitions = set()
        self.declared_variables = {}

    def analyze_code(self, lines):
        self.errors = False
        self.struct_definitions.clear()
        self.declared_variables.clear()

        for i, line in enumerate(lines):
            line = line.strip()

            # Rule: Detect division by zero (manual)
            if "/ 0" in line or "/0" in line:
                idx = line.find("/0")
                if idx != -1 and (idx + 2 == len(line) or not line[idx + 2].isdigit()):
                    print(f"Line {i + 1}: Error - Division by zero detected.")
                    self.errors = True

            # Rule: Check for missing semicolon
            if not line.endswith(";") and "struct" not in line:
                print(f"Line {i + 1}: Missing semicolon at the end.")
                self.errors = True
                continue

            # Detect struct definition manually
            if line.startswith("struct") and "{" in line:
                tokens = line.split()
                if len(tokens) >= 2:
                    self.struct_definitions.add(tokens[1])
                continue

            # Detect initialization
            if "=" in line:
                var_decl, value = line.split("=", 1)
                var_decl = var_decl.strip()
                value = value.strip().strip(";")
            else:
                var_decl = line.strip(";").strip()
                value = None

            var_parts = var_decl.split()
            if len(var_parts) < 2:
                print(f"Line {i + 1}: Invalid variable declaration.")
                self.errors = True
                continue

            var_type = var_parts[0]
            var_name = var_parts[1]

            # Manually extract array dimensions
            dimensions = []
            temp_name = ""
            reading = False
            dim = ""
            for ch in var_name:
                if ch == "[":
                    reading = True
                    temp_name = var_name.split("[")[0]
                    continue
                if ch == "]":
                    if dim.isdigit():
                        dimensions.append(int(dim))
                    dim = ""
                    reading = False
                    continue
                if reading:
                    dim += ch

            if "[" in var_name:
                var_name = var_name.split("[")[0]
            is_2d_array = len(dimensions) == 2
            is_1d_array = len(dimensions) == 1
            is_array = is_1d_array or is_2d_array

            # Redeclaration check
            if var_name in self.declared_variables:
                existing_type = self.declared_variables[var_name]
                if (is_1d_array and existing_type == "2D") or (is_2d_array and existing_type == "1D"):
                    print(f"Line {i + 1}: Error - '{var_name}' cannot be declared as both 1D and 2D array.")
                    self.errors = True
                else:
                    print(f"Line {i + 1}: Error - Variable '{var_name}' is already declared.")
                    self.errors = True
            else:
                self.declared_variables[var_name] = "2D" if is_2d_array else "1D" if is_1d_array else "scalar"

            # Type Checking
            if var_type in ["int", "long", "long long", "short"]:
                if is_2d_array:
                    if not (value.startswith("{{") and value.endswith("}}")):
                        print(f"Line {i + 1}: Invalid initialization for 2D '{var_type}[][]'. Must use nested {{}}.")
                        self.errors = True
                    else:
                        inner = value.strip("{}").strip()
                        rows = inner.split("},{")
                        if len(rows) != dimensions[0]:
                            print(f"Line {i + 1}: Expected {dimensions[0]} rows, but found {len(rows)}.")
                            self.errors = True
                        else:
                            for row_idx, row in enumerate(rows):
                                row = row.replace("{", "").replace("}", "").strip()
                                elements = [ele.strip() for ele in row.split(",") if ele.strip()]
                                if len(elements) != dimensions[1]:
                                    print(f"Line {i + 1}: Row {row_idx + 1} must have {dimensions[1]} elements, but found {len(elements)}.")
                                    self.errors = True
                                elif not all(ele.isdigit() for ele in elements):
                                    print(f"Line {i + 1}: Datatype mismatch in 2D array. All elements must be integers.")
                                    self.errors = True

                elif is_1d_array:
                    if not (value.startswith("{") and value.endswith("}")):
                        print(f"Line {i + 1}: Invalid array initialization for '{var_type}[]'. Must use {{}}.")
                        self.errors = True
                    else:
                        elements = [ele.strip() for ele in value.strip("{}").split(",")]
                        if not all(ele.isdigit() for ele in elements):
                            print(f"Line {i + 1}: Datatype mismatch in '{var_type}[]' initialization.")
                            self.errors = True
                        if dimensions and len(elements) != dimensions[0]:
                            print(f"Line {i + 1}: Expected {dimensions[0]} elements, but found {len(elements)}.")
                            self.errors = True
                else:
                    if value and not value.isdigit():
                        print(f"Line {i + 1}: Datatype mismatch for '{var_type}'.")
                        self.errors = True

            elif var_type in ["float", "double", "long double"]:
                try:
                    if value:
                        float(value)
                except ValueError:
                    print(f"Line {i + 1}: Datatype mismatch for '{var_type}'.")
                    self.errors = True

            elif var_type == "bool":
                if value and value not in ["true", "false"]:
                    print(f"Line {i + 1}: Invalid initialization for 'bool'. Must be 'true' or 'false'.")
                    self.errors = True

            elif var_type in self.struct_definitions:
                if not value.startswith("{") or not value.endswith("}"):
                    print(f"Line {i + 1}: Invalid struct initialization. Must use '{{}}'.")
                    self.errors = True

            elif var_type == "char":
                if value:
                    value = value.strip()
                    if len(value) != 3 or value[0] != "'" or value[-1] != "'":
                        print(f"Line {i + 1}: Invalid initialization for 'char'.")
                        self.errors = True

            elif var_type == "char[]" or (var_type == "char" and is_array):
                if value and (not value.startswith("\"") or not value.endswith("\"")):
                    print(f"Line {i + 1}: Datatype mismatch for 'char[]'. Use double quotes.")
                    self.errors = True

            else:
                print(f"Line {i + 1}: Unknown data type '{var_type}'.")
                self.errors = True

        if not self.errors:
            print("No errors found.")

    def run(self):
        print("Enter your code line by line. Press Enter on a blank line to finish.")
        user_code = []
        while True:
            line = input("> ")
            if not line.strip():
                break
            user_code.append(line)
        self.analyze_code(user_code)


# Run the semantic analyzer
if __name__ == "__main__":
    analyzer = Semantic()
    analyzer.run()
