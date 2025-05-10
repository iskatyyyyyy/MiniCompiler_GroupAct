from lexical import Lexical, Tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_pos = -1
        self.current_token = None
        self.errors = []
        self.advance()

    def advance(self):
        self.current_pos += 1
        if self.current_pos < len(self.tokens):
            self.current_token = self.tokens[self.current_pos]
        else:
            self.current_token = None

    def error(self, message):
        if self.current_token:
            self.errors.append(f"Syntax Error at line {self.current_token.line}: {message}")
        else:
            self.errors.append(f"Syntax Error: {message}")

    def match(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            self.advance()
            return True
        return False

    def expect(self, token_type, error_message):
        if not self.match(token_type):
            self.error(error_message)
            return False
        return True

    def parse_program(self):
        """
        program -> declaration*
        """
        while self.current_token:
            self.parse_declaration()

    def parse_declaration(self):
        """
        declaration -> variable_declaration | function_declaration
        """
        if not self.current_token:
            return

        # Check if it's a type specifier
        if self.current_token.type == 'KEYWORD':
            token_backup = self.current_token
            self.advance()
            
            if not self.current_token:
                self.error("Unexpected end of input after type specifier")
                return

            if self.current_token.type == 'IDENTIFIER':
                self.advance()
                # Check if it's a function declaration
                if self.current_token and self.current_token.value == '(':
                    self.current_pos -= 2  # Reset to start of declaration
                    self.current_token = token_backup
                    self.parse_function_declaration()
                else:
                    self.current_pos -= 2  # Reset to start of declaration
                    self.current_token = token_backup
                    self.parse_variable_declaration()
            else:
                self.error("Expected identifier after type specifier")

    def parse_variable_declaration(self):
        """
        variable_declaration -> type_specifier identifier ';'
        """
        if not self.expect('KEYWORD', "Expected type specifier"):
            return

        if not self.expect('IDENTIFIER', "Expected identifier"):
            return

        if not self.expect('SYMBOL', "Expected semicolon"):
            if self.current_token:
                self.error(f"Expected ';' but found '{self.current_token.value}'")
            else:
                self.error("Expected ';' at end of declaration")

    def parse_function_declaration(self):
        """
        function_declaration -> type_specifier identifier '(' parameter_list? ')' compound_statement
        """
        if not self.expect('KEYWORD', "Expected return type"):
            return

        if not self.expect('IDENTIFIER', "Expected function name"):
            return

        if not self.expect('SYMBOL', "Expected '('"):
            return

        # Parse parameter list if exists
        if self.current_token and self.current_token.value != ')':
            self.parse_parameter_list()

        if not self.expect('SYMBOL', "Expected ')'"):
            return

        self.parse_compound_statement()

    def parse_parameter_list(self):
        """
        parameter_list -> parameter (',' parameter)*
        parameter -> type_specifier identifier
        """
        while True:
            if not self.expect('KEYWORD', "Expected parameter type"):
                return

            if not self.expect('IDENTIFIER', "Expected parameter name"):
                return

            if self.current_token and self.current_token.value == ',':
                self.advance()
            else:
                break

    def parse_compound_statement(self):
        """
        compound_statement -> '{' statement* '}'
        """
        if not self.expect('SYMBOL', "Expected '{'"):
            return

        while self.current_token and self.current_token.value != '}':
            self.parse_statement()

        if not self.expect('SYMBOL', "Expected '}'"):
            return

    def parse_statement(self):
        """
        statement -> expression_statement | compound_statement | if_statement | while_statement | return_statement
        """
        if not self.current_token:
            return

        if self.current_token.value == '{':
            self.parse_compound_statement()
        elif self.current_token.type == 'CONTROL_FLOW':
            if self.current_token.value == 'if':
                self.parse_if_statement()
            elif self.current_token.value == 'while':
                self.parse_while_statement()
            elif self.current_token.value == 'return':
                self.parse_return_statement()
        else:
            self.parse_expression_statement()

    def parse_if_statement(self):
        """
        if_statement -> 'if' '(' expression ')' statement ('else' statement)?
        """
        self.advance()  # consume 'if'
        if not self.expect('SYMBOL', "Expected '(' after 'if'"):
            return

        self.parse_expression()

        if not self.expect('SYMBOL', "Expected ')' after condition"):
            return

        self.parse_statement()

        if self.current_token and self.current_token.value == 'else':
            self.advance()
            self.parse_statement()

    def parse_while_statement(self):
        """
        while_statement -> 'while' '(' expression ')' statement
        """
        self.advance()  # consume 'while'
        if not self.expect('SYMBOL', "Expected '(' after 'while'"):
            return

        self.parse_expression()

        if not self.expect('SYMBOL', "Expected ')' after condition"):
            return

        self.parse_statement()

    def parse_return_statement(self):
        """
        return_statement -> 'return' expression? ';'
        """
        self.advance()  # consume 'return'
        
        if self.current_token and self.current_token.value != ';':
            self.parse_expression()

        if not self.expect('SYMBOL', "Expected ';' after return statement"):
            return

    def parse_expression_statement(self):
        """
        expression_statement -> expression? ';'
        """
        if self.current_token and self.current_token.value != ';':
            self.parse_expression()

        if not self.expect('SYMBOL', "Expected ';' after expression"):
            return

    def parse_expression(self):
        """
        expression -> identifier '=' expression | simple_expression
        """
        # Basic expression parsing - can be extended for more complex expressions
        if self.current_token:
            self.advance()

    def parse(self):
        """
        Main parsing method
        """
        self.parse_program()
        return self.errors

def main():
    print("Enter C code (press Enter twice to finish input):")
    user_input = ''
    while True:
        line = input()
        if line == '':
            break
        user_input += line + '\n'

    lexer = Lexical(user_input)
    tokens, lexical_errors = lexer.get_tokens()  # get tokens from lexer using get_tokens()

    # Second pass: Syntax analysis
    parser = Parser(tokens)
    syntax_errors = parser.parse()

    # Display syntax errors if any
    if syntax_errors:
        print("\nSyntax Errors:")
        for error in syntax_errors:
            print(error)
    else:
        print("\nParsing completed successfully. No syntax errors found.")

if __name__ == "__main__":
    main()
