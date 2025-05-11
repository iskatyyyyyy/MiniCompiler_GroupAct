from lexical import Lexical
from ast_nodes import *

class Parser:
    def __init__(self, lexer):
        self.tokens = []
        self.current_pos = -1
        self.current_token = None
        tokens, lexer_errors = lexer.get_tokens()
        self.tokens = tokens
        self.errors = lexer_errors.copy()  # Start with any lexer errors
        self.advance()  # Initialize first token

    def advance(self):
        """Advance to the next token."""
        self.current_pos += 1
        if self.current_pos < len(self.tokens):
            self.current_token = self.tokens[self.current_pos]
        else:
            self.current_token = None

    def peek(self):
        """Look at the next token without consuming it."""
        if self.current_pos + 1 < len(self.tokens):
            return self.tokens[self.current_pos + 1]
        return None

    def error(self, message):
        """Add an error message to the error list."""
        if self.current_token:
            error = f"Line {self.current_token.line}: {message}"
        else:
            error = f"End of file: {message}"
        self.errors.append(error)

    def expect(self, token_type, value=None):
        """Verify the current token matches expected type/value and advance."""
        if not self.current_token:
            self.error(f"Expected {value if value else token_type}, but found end of file")
            return False
        
        if self.current_token.type != token_type:
            self.error(f"Expected {token_type}, but found {self.current_token.type}")
            return False
        
        if value and self.current_token.value != value:
            self.error(f"Expected '{value}', but found '{self.current_token.value}'")
            return False
        
        self.advance()
        return True

    def synchronize(self):
        """Skip tokens until a safe point for error recovery."""
        while self.current_token:
            if self.current_token.type == 'SYMBOL' and self.current_token.value in {';', '}'}:
                self.advance()  # Consume the synchronization point
                return
            if self.current_token.type in {'KEYWORD', 'CONTROL_FLOW'} and \
               self.current_token.value in {'int', 'float', 'void', 'if', 'while', 'for', 'return'}:
                return  # Stop at the start of next statement/declaration
            self.advance()

    def parse_program(self):
        """Parse the entire program."""
        declarations = []
        while self.current_token:
            try:
                if self.current_token.type == 'KEYWORD':
                    # Function or variable declaration
                    if self.peek() and self.peek().type == 'IDENTIFIER':
                        if self.peek().value == 'main' or \
                           (len(self.tokens) > self.current_pos + 2 and 
                            self.tokens[self.current_pos + 2].value == '('):
                            decl = self.parse_function_definition()
                        else:
                            decl = self.parse_declaration()
                        
                        if decl:
                            declarations.append(decl)
                    else:
                        self.error("Expected identifier after type")
                        self.synchronize()
                else:
                    self.error(f"Unexpected token {self.current_token.value}")
                    self.synchronize()
            except Exception as e:
                self.error(f"Internal error: {str(e)}")
                self.synchronize()
                continue

        return ProgramNode(declarations)

    def parse_function_definition(self):
        """Parse a function definition."""
        return_type = self.current_token.value
        self.advance()

        if not self.expect('IDENTIFIER'):
            return None

        name = self.tokens[self.current_pos - 1].value
        line = self.tokens[self.current_pos - 1].line

        if not self.expect('SYMBOL', '('):
            return None

        # Parse parameters
        parameters = []
        while self.current_token and self.current_token.value != ')':
            if self.current_token.type == 'KEYWORD':
                param_type = self.current_token.value
                self.advance()

                if not self.expect('IDENTIFIER'):
                    break

                param_name = self.tokens[self.current_pos - 1].value
                param_line = self.tokens[self.current_pos - 1].line
                parameters.append(ParameterNode(param_type, param_name, param_line))

                if self.current_token and self.current_token.value == ',':
                    self.advance()
                    if self.current_token.value == ')':
                        self.error("Expected parameter after comma")
            else:
                self.error("Expected parameter type")
                break

        if not self.expect('SYMBOL', ')'):
            return None

        # Parse function body
        body = self.parse_block()
        if not body:
            return None

        return FunctionNode(return_type, name, parameters, body, line)

    def parse_declaration(self):
        """Parse a variable declaration."""
        type_name = self.current_token.value
        self.advance()

        if not self.expect('IDENTIFIER'):
            return None

        name = self.tokens[self.current_pos - 1].value
        line = self.tokens[self.current_pos - 1].line
        init_value = None

        if self.current_token and self.current_token.value == '=':
            self.advance()
            init_value = self.parse_expression()

        if not self.expect('SYMBOL', ';'):
            self.error("Expected ';' after declaration")
            self.synchronize()
            return None

        return DeclarationNode(type_name, name, init_value, line)

    def parse_block(self):
        """Parse a block of statements."""
        if not self.expect('SYMBOL', '{'):
            return None

        statements = []
        while self.current_token and self.current_token.value != '}':
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        if not self.expect('SYMBOL', '}'):
            self.error("Expected '}' at end of block")
            return None

        return BlockNode(statements)

    def parse_statement(self):
        """Parse a statement."""
        if not self.current_token:
            self.error("Unexpected end of file")
            return None

        if self.current_token.type == 'CONTROL_FLOW':
            if self.current_token.value == 'if':
                return self.parse_if_statement()
            elif self.current_token.value == 'while':
                return self.parse_while_statement()
            elif self.current_token.value == 'do':
                return self.parse_do_while_statement()
            elif self.current_token.value == 'for':
                return self.parse_for_statement()
            elif self.current_token.value == 'switch':
                return self.parse_switch_statement()
            elif self.current_token.value == 'break':
                return self.parse_break_statement()
            elif self.current_token.value == 'continue':
                return self.parse_continue_statement()
            elif self.current_token.value == 'return':
                return self.parse_return_statement()

        elif self.current_token.type == 'KEYWORD':
            return self.parse_declaration()

        elif self.current_token.type == 'SYMBOL' and self.current_token.value == '{':
            return self.parse_block()

        else:
            # Expression statement
            expr = self.parse_expression()
            if not self.expect('SYMBOL', ';'):
                self.error("Expected ';' after expression")
                self.synchronize()
                return None
            return expr

    def parse_if_statement(self):
        """Parse an if statement."""
        self.advance()  # Skip 'if'
        
        if not self.expect('SYMBOL', '('):
            return None
            
        condition = self.parse_expression()
        
        if not self.expect('SYMBOL', ')'):
            return None
            
        true_body = self.parse_statement()
        false_body = None
        
        # Check for else
        if self.current_token and self.current_token.value == 'else':
            self.advance()
            false_body = self.parse_statement()
            
        return IfNode(condition, true_body, false_body)

    def parse_while_statement(self):
        """Parse a while statement."""
        line = self.current_token.line
        self.advance()  # Skip 'while'
        
        if not self.expect('SYMBOL', '('):
            return None
            
        condition = self.parse_expression()
        
        if not self.expect('SYMBOL', ')'):
            return None
            
        body = self.parse_statement()
        return WhileNode(condition, body, line)

    def parse_do_while_statement(self):
        """Parse a do-while statement."""
        line = self.current_token.line
        self.advance()  # Skip 'do'
        
        body = self.parse_statement()
        
        if not self.expect('CONTROL_FLOW', 'while'):
            return None
            
        if not self.expect('SYMBOL', '('):
            return None
            
        condition = self.parse_expression()
        
        if not self.expect('SYMBOL', ')'):
            return None
            
        if not self.expect('SYMBOL', ';'):
            return None
            
        return DoWhileNode(body, condition, line)

    def parse_for_statement(self):
        """Parse a for statement."""
        line = self.current_token.line
        self.advance()  # Skip 'for'
        
        if not self.expect('SYMBOL', '('):
            return None
            
        # Initialize
        init = None
        if self.current_token.value != ';':
            if self.current_token.type == 'KEYWORD':
                init = self.parse_declaration()
            else:
                init = self.parse_expression()
                if not self.expect('SYMBOL', ';'):
                    return None
        else:
            self.advance()  # Skip ';'
            
        # Condition
        condition = None
        if self.current_token.value != ';':
            condition = self.parse_expression()
        if not self.expect('SYMBOL', ';'):
            return None
            
        # Update
        update = None
        if self.current_token.value != ')':
            update = self.parse_expression()
        if not self.expect('SYMBOL', ')'):
            return None
            
        body = self.parse_statement()
        return ForNode(init, condition, update, body, line)

    def parse_switch_statement(self):
        """Parse a switch statement."""
        line = self.current_token.line
        self.advance()  # Skip 'switch'
        
        if not self.expect('SYMBOL', '('):
            return None
            
        expression = self.parse_expression()
        
        if not self.expect('SYMBOL', ')'):
            return None
            
        if not self.expect('SYMBOL', '{'):
            return None
            
        cases = []
        while self.current_token and self.current_token.value != '}':
            if self.current_token.value == 'case' or self.current_token.value == 'default':
                case = self.parse_case()
                if case:
                    cases.append(case)
            else:
                self.error("Expected 'case' or 'default'")
                self.synchronize()
                
        if not self.expect('SYMBOL', '}'):
            return None
            
        return SwitchNode(expression, cases, line)

    def parse_case(self):
        """Parse a case in a switch statement."""
        is_default = self.current_token.value == 'default'
        line = self.current_token.line
        self.advance()
        
        value = None
        if not is_default:
            value = self.parse_expression()
            
        if not self.expect('SYMBOL', ':'):
            return None
            
        statements = []
        while self.current_token and self.current_token.value not in {'case', 'default', '}'}:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
                
        return CaseNode(value, statements, line)

    def parse_break_statement(self):
        """Parse a break statement."""
        line = self.current_token.line
        self.advance()  # Skip 'break'
        
        if not self.expect('SYMBOL', ';'):
            return None
            
        return BreakNode(line)

    def parse_continue_statement(self):
        """Parse a continue statement."""
        line = self.current_token.line
        self.advance()  # Skip 'continue'
        
        if not self.expect('SYMBOL', ';'):
            return None
            
        return ContinueNode(line)

    def parse_return_statement(self):
        """Parse a return statement."""
        line = self.current_token.line
        self.advance()  # Skip 'return'
        
        value = None
        if self.current_token.value != ';':
            value = self.parse_expression()
            
        if not self.expect('SYMBOL', ';'):
            return None
            
        return ReturnNode(value, line)

    def parse_expression(self):
        """Parse an expression using operator precedence."""
        return self.parse_assignment()

    def parse_assignment(self):
        """Parse an assignment expression."""
        expr = self.parse_logical_or()
        
        if self.current_token and self.current_token.value in {'=', '+=', '-=', '*=', '/=', '%='}:
            operator = self.current_token.value
            line = self.current_token.line
            self.advance()
            
            value = self.parse_assignment()
            return AssignmentNode(expr, operator, value, line)
            
        return expr

    def parse_logical_or(self):
        """Parse logical OR expression."""
        expr = self.parse_logical_and()
        
        while self.current_token and self.current_token.value == '||':
            operator = self.current_token.value
            line = self.current_token.line
            self.advance()
            
            right = self.parse_logical_and()
            expr = BinaryOpNode(operator, expr, right, line)
            
        return expr

    def parse_logical_and(self):
        """Parse logical AND expression."""
        expr = self.parse_equality()
        
        while self.current_token and self.current_token.value == '&&':
            operator = self.current_token.value
            line = self.current_token.line
            self.advance()
            
            right = self.parse_equality()
            expr = BinaryOpNode(operator, expr, right, line)
            
        return expr

    def parse_equality(self):
        """Parse equality expression."""
        expr = self.parse_relational()
        
        while self.current_token and self.current_token.value in {'==', '!='}:
            operator = self.current_token.value
            line = self.current_token.line
            self.advance()
            
            right = self.parse_relational()
            expr = BinaryOpNode(operator, expr, right, line)
            
        return expr

    def parse_relational(self):
        """Parse relational expression."""
        expr = self.parse_additive()
        
        while self.current_token and self.current_token.value in {'<', '>', '<=', '>='}:
            operator = self.current_token.value
            line = self.current_token.line
            self.advance()
            
            right = self.parse_additive()
            expr = BinaryOpNode(operator, expr, right, line)
            
        return expr

    def parse_additive(self):
        """Parse additive expression."""
        expr = self.parse_multiplicative()
        
        while self.current_token and self.current_token.value in {'+', '-'}:
            operator = self.current_token.value
            line = self.current_token.line
            self.advance()
            
            right = self.parse_multiplicative()
            expr = BinaryOpNode(operator, expr, right, line)
            
        return expr

    def parse_multiplicative(self):
        """Parse multiplicative expression."""
        expr = self.parse_unary()
        
        while self.current_token and self.current_token.value in {'*', '/', '%'}:
            operator = self.current_token.value
            line = self.current_token.line
            self.advance()
            
            right = self.parse_unary()
            expr = BinaryOpNode(operator, expr, right, line)
            
        return expr

    def parse_unary(self):
        """Parse unary expression."""
        if self.current_token and self.current_token.value in {'!', '-', '++', '--'}:
            operator = self.current_token.value
            line = self.current_token.line
            self.advance()
            
            operand = self.parse_unary()
            return UnaryOpNode(operator, operand, True, line)
            
        return self.parse_postfix()

    def parse_postfix(self):
        """Parse postfix expression."""
        expr = self.parse_primary()
        
        while self.current_token and self.current_token.value in {'++', '--'}:
            operator = self.current_token.value
            line = self.current_token.line
            self.advance()
            
            expr = UnaryOpNode(operator, expr, False, line)
            
        return expr

    def parse_primary(self):
        """Parse primary expression."""
        if not self.current_token:
            self.error("Unexpected end of input")
            return None

        token = self.current_token
        if token.type == 'NUMBER':
            self.advance()
            return LiteralNode(token.value, 'number', token.line)
            
        elif token.type == 'STRING':
            self.advance()
            return LiteralNode(token.value, 'string', token.line)
            
        elif token.type == 'CHAR_LITERAL':
            self.advance()
            return LiteralNode(token.value, 'char', token.line)
            
        elif token.type == 'IDENTIFIER':
            self.advance()
            # Check if it's a function call
            if self.current_token and self.current_token.value == '(':
                self.advance()  # consume '('
                arguments = []
                
                if self.current_token.value != ')':
                    while True:
                        arg = self.parse_expression()
                        if arg:
                            arguments.append(arg)
                            
                        if self.current_token.value == ')':
                            break
                            
                        if not self.expect('SYMBOL', ','):
                            return None
                            
                if not self.expect('SYMBOL', ')'):
                    self.error("Expected closing parenthesis")
                    return None
                    
                return FunctionCallNode(token.value, arguments, token.line)
            else:
                return IdentifierNode(token.value, token.line)
                
        elif token.value == '(':
            self.advance()  # consume '('
            expr = self.parse_expression()
            
            if not self.expect('SYMBOL', ')'):
                self.error("Expected closing parenthesis")
                return None
                
            return expr
            
        self.error(f"Unexpected token: {token.value}")
        self.advance()
        return None

def pretty_print_ast(node, indent=""):
    """Helper function to print the AST in a readable format."""
    if not node:
        return indent + "None"

    if isinstance(node, ProgramNode):
        result = indent + "Program:\n"
        for decl in node.declarations:
            result += pretty_print_ast(decl, indent + "  ")
        return result

    elif isinstance(node, FunctionNode):
        result = f"{indent}Function {node.name} (returns {node.return_type}):\n"
        result += indent + "  Parameters:\n"
        for param in node.parameters:
            result += pretty_print_ast(param, indent + "    ")
        result += indent + "  Body:\n"
        result += pretty_print_ast(node.body, indent + "    ")
        return result

    elif isinstance(node, ParameterNode):
        return f"{indent}{node.type_name} {node.name}\n"

    elif isinstance(node, DeclarationNode):
        init = f" = {pretty_print_ast(node.init_value, '')}" if node.init_value else ""
        return f"{indent}Declaration: {node.type_name} {node.name}{init}\n"

    elif isinstance(node, BlockNode):
        result = indent + "Block:\n"
        for stmt in node.statements:
            result += pretty_print_ast(stmt, indent + "  ")
        return result

    elif isinstance(node, IfNode):
        result = indent + "If:\n"
        result += indent + "  Condition:\n"
        result += pretty_print_ast(node.condition, indent + "    ")
        result += indent + "  Then:\n"
        result += pretty_print_ast(node.true_body, indent + "    ")
        if node.false_body:
            result += indent + "  Else:\n"
            result += pretty_print_ast(node.false_body, indent + "    ")
        return result

    elif isinstance(node, BinaryOpNode):
        return f"{indent}({pretty_print_ast(node.left, '')} {node.operator} {pretty_print_ast(node.right, '')})\n"

    elif isinstance(node, UnaryOpNode):
        if node.is_prefix:
            return f"{indent}{node.operator}{pretty_print_ast(node.operand, '')}\n"
        else:
            return f"{indent}{pretty_print_ast(node.operand, '')}{node.operator}\n"

    elif isinstance(node, AssignmentNode):
        return f"{indent}Assignment: {pretty_print_ast(node.target, '')} {node.operator} {pretty_print_ast(node.value, '')}\n"

    elif isinstance(node, FunctionCallNode):
        args = ", ".join(pretty_print_ast(arg, "").strip() for arg in node.arguments)
        return f"{indent}Call: {node.name}({args})\n"

    elif isinstance(node, IdentifierNode):
        return node.name

    elif isinstance(node, LiteralNode):
        return str(node.value)

    elif isinstance(node, ReturnNode):
        if node.value:
            return f"{indent}Return: {pretty_print_ast(node.value, '')}\n"
        return f"{indent}Return\n"

    return f"{indent}{str(node)}\n"

def main():
        print("Enter C code (press Enter twice to finish input):")
        user_input = ''
        while True:
            line = input()
            if line == '':
                break
            user_input += line + '\n'

        # Create lexer
        lexer = Lexical(user_input)
        
        # Create parser with lexer object
        parser = Parser(lexer)
        
        # Parse the program
        ast = parser.parse_program()

        # Display errors if any
        if parser.errors:
            print("\nParsing Errors:")
            print("-" * 70)
            for error in parser.errors:
                print(f"  {error}")
        else:
            # Print AST
            print("\nAbstract Syntax Tree:")
            print("-" * 70)
            print(pretty_print_ast(ast))

if __name__ == "__main__":
    main()
