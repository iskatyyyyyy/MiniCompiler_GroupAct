from ast_nodes import *
from lexical import Lexical, Tokens

class Parser:
    # Tokens and Position Tracking
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.errors = []
        
    # Token Navigation
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def match(self, token_type, value=None):
        if self.current_token and self.current_token.type == token_type:
            if value is None or self.current_token.value == value:
                matched_token = self.current_token
                self.advance()
                return matched_token
        return None

    def expect(self, token_type, value=None):
        if self.current_token is None:
            self.report_error(f"[Parser Error] Unexpected end of input, expected {token_type} '{value}'")
            return None

        token = self.match(token_type, value)
        if not token:
            expected_val = f" '{value}'" if value is not None else ""
            actual_val = f"{self.current_token.type}('{self.current_token.value}')" if self.current_token else "None"
            line = self.current_token.line if self.current_token else "EOF"
            self.report_error(f"[Parser Error] Expected {token_type}{expected_val}, but got {actual_val} at line {line}")
            return None

        return token


    
    def eat(self, expected_type, expected_value=None):
        token = self.current_token
        if not token:
            self.report_error("Unexpected end of input")
            return
        if token.type != expected_type:
            self.report_error(f"Expected type '{expected_type}', but got {token.type}('{token.value}') on line {token.line}")
            return
        if expected_value is not None and token.value != expected_value:
            self.report_error(f"Expected value '{expected_value}', but got '{token.value}' on line {token.line}")
            return
        self.advance()
    
    def report_error(self, message):
        self.errors.append(message)
        print(f"[Parser Error] {message}")

    def synchronize(self, stop_tokens=(';', '}', '{')):
        """
        Skip tokens until a likely recovery point (e.g., end of statement or block).
        You can provide custom stop tokens like [')', '{', ';'] depending on context.
        """
        while self.current_token and self.current_token.value not in stop_tokens:
            self.advance()

        # Optionally consume the stop token too (to move past it)
        if self.current_token and self.current_token.value in stop_tokens:
            self.advance()



    # Parse the entire program
    def parse(self):
        statements = []
        while self.current_token and self.current_token.type != 'EOF':
            try:
                if self.current_token.type == 'KEYWORD' and self.current_token.value in ('int', 'float', 'char', 'void'):
                    node = self.parse_declaration_or_function()
                else:
                    node = self.parse_statement()
                    if node is None:
                        raise SyntaxError(f"Unexpected token {self.current_token.type}('{self.current_token.value}') on line {self.current_token.line}")
                statements.append(node)
            except SyntaxError as e:
                self.report_error(str(e))
                self.synchronize()
        return statements

    # Parsing Declarations and Functions
    def parse_declaration_or_function(self):
        var_type_token = self.expect('KEYWORD')
        if not var_type_token:
            self.synchronize([';', '}'])
            return None

        name_token = self.expect('IDENTIFIER')
        if not name_token:
            self.synchronize([';', '}'])
            return None

        var_type = var_type_token.value
        name = name_token.value

        if self.match('SYMBOL', '('):
            parameters = []

            if self.current_token and self.current_token.value != ')':
                while True:
                    param_type_token = self.expect('KEYWORD')
                    param_name_token = self.expect('IDENTIFIER')

                    if not param_type_token or not param_name_token:
                        self.report_error("Invalid parameter in function declaration.")
                        self.synchronize([')', '{'])
                        break

                    parameters.append((param_type_token.value, param_name_token.value))

                    if self.current_token and self.current_token.value == ')':
                        break
                    if not self.expect('SYMBOL', ','):
                        self.report_error("Expected ',' or ')' after function parameter.")
                        self.synchronize([')', '{'])
                        break

            if not self.expect('SYMBOL', ')'):
                self.report_error("Expected ')' to close parameter list.")
                self.synchronize(['{', ';'])  # Try to recover to the start of function body or next decl
                return None

            body = self.parse_compound_statement()
            if not body:
                self.report_error(f"Invalid function body for '{name}'.")
            return FunctionDeclaration(var_type, name, parameters, body)

        else:
            initializer = None
            if self.match('OPERATOR', '='):
                initializer = self.parse_expression()
            if not self.expect('SYMBOL', ';'):
                self.report_error(f"Expected ';' after variable declaration '{name}'.")
                self.synchronize([';', '}'])
                return None
            return VariableDeclaration(var_type, name, initializer)



    # Parsing Compound Statements (Blocks)
    def parse_compound_statement(self):
        self.expect('SYMBOL', '{')
        statements = []
        # Only peek for '}', do NOT consume it here
        while self.current_token and self.current_token.value != '}':
            stmt = self.parse_statement()
            statements.append(stmt)
        self.expect('SYMBOL', '}')  # Consume the closing '}'
        return Block(statements)

    # Parsing Statements
    def parse_statement(self):
        try:
            if self.current_token.value == 'if':
                return self.parse_if_statement()
            elif self.current_token.value == 'while':
                return self.parse_while_statement()
            elif self.current_token.value == 'for':
                return self.parse_for_statement()
            elif self.current_token.value == 'switch':
                return self.parse_switch_statement()
            elif self.current_token.value == 'break':
                self.eat('KEYWORD', 'break')
                self.expect('SYMBOL', ';')
                return BreakStatement()
            elif self.current_token.value == 'continue':
                self.eat('KEYWORD', 'continue')
                self.expect('SYMBOL', ';')
                return ContinueStatement()
            elif self.current_token.value == 'return':
                return self.parse_return_statement()
            elif self.current_token.value in ('int', 'char', 'float', 'double', 'void'):
                return self.parse_declaration()
            elif self.current_token.value == '{':
                return self.parse_compound_statement()
            else:
                expr = self.parse_expression()
                self.expect('SYMBOL', ';')
                return ExpressionStatement(expr)
        except SyntaxError as e:
            self.report_error(str(e))
            self.synchronize()
            return None

    def parse_declaration(self):
        var_type = self.current_token.value
        self.eat('KEYWORD')
        var_name = self.current_token.value
        self.eat('IDENTIFIER')

        initializer = None
        if self.current_token.value == '=':
            self.expect('OPERATOR','=')
            initializer = self.parse_expression()

        self.expect('SYMBOL',';')
        
        return VariableDeclaration(var_type, var_name, initializer)

    # Parsing Expressions
    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        left = self.parse_binary_op()

        if self.current_token and self.current_token.type == 'OPERATOR' and self.current_token.value in ('=', '+=', '-=', '*=', '/=', '%='):
            op = self.current_token.value
            self.eat('OPERATOR')
            right = self.parse_assignment()

            # Validate left side is assignable (e.g., VariableNode)
            if not isinstance(left, VariableNode):
                raise SyntaxError(f"Invalid left-hand side in assignment at line {self.current_token.line}")

            return AssignmentExpression(op, left, right)
        return left
    
    def parse_unary(self):
        if self.current_token.type == 'OPERATOR' and self.current_token.value in ('+', '-', '!', '~', '++', '--'):
            op = self.current_token.value
            self.eat('OPERATOR')
            operand = self.parse_unary()
            return UnaryOperation(op, operand)
        return self.parse_postfix()

    def parse_binary_op(self, min_prec=0):
        left = self.parse_unary()  # use parse_unary here instead of parse_postfix

        while self.current_token and self.current_token.type == 'OPERATOR':
            op = self.current_token.value
            prec = self.get_precedence(op)
            if prec < min_prec:
                break

            self.eat('OPERATOR')

            right = self.parse_binary_op(prec + 1)
            left = BinaryOperation(op, left, right)

        return left


    def parse_primary(self):
        token = self.current_token
        if token is None:
            self.report_error("Unexpected end of input in primary expression")
            return None

        try:
            if token.type == 'NUMBER':
                self.eat('NUMBER')
                return Number(token.value)
            elif token.type == 'STRING':
                self.eat('STRING')
                return StringNode(token.value)
            elif token.type == 'CHAR_LITERAL':
                self.eat('CHAR_LITERAL')
                return CharNode(token.value)
            elif token.type == 'IDENTIFIER':
                name = token.value
                self.eat('IDENTIFIER')
                if self.current_token and self.current_token.value == '(':
                    self.eat('SYMBOL', '(')
                    args = []
                    if self.current_token.value != ')':
                        while True:
                            args.append(self.parse_expression())
                            if self.current_token.value == ',':
                                self.eat('SYMBOL', ',')
                            else:
                                break
                    self.expect('SYMBOL', ')')
                    return FunctionCallNode(name, args)
                else:
                    return VariableNode(name)
            elif token.value == '(':
                self.eat('SYMBOL', '(')
                expr = self.parse_expression()
                self.expect('SYMBOL', ')')
                return expr
        except SyntaxError as e:
            self.report_error(str(e))
            self.synchronize()
            return None

        self.report_error(f"Unexpected token {token.type}('{token.value}') on line {token.line}")
        self.advance()
        return None

    def parse_postfix(self):
        expr = self.parse_primary()

        while self.current_token and self.current_token.type == 'OPERATOR' and self.current_token.value in ('++', '--'):
            op = self.current_token.value
            self.eat('OPERATOR')
            expr = UnaryOperation(op, expr, postfix=True)  # Define postfix=True for your AST node
        return expr

    def get_precedence(self, op):
        precedence = {
            '=': 1,
            '||': 2,
            '&&': 3,
            '==': 4, '!=': 4,
            '<': 5, '<=': 5, '>': 5, '>=': 5,
            '+': 6, '-': 6,
            '*': 7, '/': 7, '%': 7,
            '++': 8, '--': 8
        }
        return precedence.get(op, -1)

    # Control structures

    def parse_if_statement(self):
        try:
            self.eat('KEYWORD', 'if')
            self.expect('SYMBOL', '(')
            condition = self.parse_expression()
            self.expect('SYMBOL', ')')
            then_branch = self.parse_statement()
            else_branch = None
            if self.current_token and self.current_token.value == 'else':
                self.eat('KEYWORD', 'else')
                else_branch = self.parse_statement()
            return IfStatement(condition, then_branch, else_branch)
        except SyntaxError as e:
            self.report_error(str(e))
            self.synchronize()
            return None

    def parse_while_statement(self):
        self.expect('KEYWORD', 'while')
        self.expect('SYMBOL', '(')
        condition = self.parse_expression()
        self.expect('SYMBOL', ')')
        body = self.parse_statement()
        return WhileStatement(condition, body)

    def parse_for_statement(self):
        self.expect('KEYWORD', 'for')
        self.expect('SYMBOL', '(')

        # Parse init part: declaration, expression, or empty
        if self.current_token.value in ('int', 'char', 'float', 'double', 'void'):
            init = self.parse_declaration()
        elif self.current_token.value != ';':
            init_expr = self.parse_expression()
            self.expect('SYMBOL', ';')
            init = ExpressionStatement(init_expr)
        else:
            init = None
            self.expect('SYMBOL', ';')

        # Parse condition part: expression or empty
        if self.current_token.value != ';':
            condition = self.parse_expression()
            self.expect('SYMBOL', ';')
        else:
            condition = None
            self.expect('SYMBOL', ';')

        # Parse increment part: expression or empty
        if self.current_token.value != ')':
            increment = self.parse_expression()
            self.expect('SYMBOL', ')')
        else:
            increment = None
            self.expect('SYMBOL', ')')

        body = self.parse_statement()

        return ForStatement(init, condition, increment, body)


    def parse_return_statement(self):
        try:
            self.eat('KEYWORD', 'return')
            if self.current_token.value != ';':
                expr = self.parse_expression()
            else:
                expr = None
            self.expect('SYMBOL', ';')
            return ReturnStatement(expr)
        except SyntaxError as e:
            self.report_error(str(e))
            self.synchronize()
            return None

    def parse_switch_statement(self):
        try:
            self.expect('KEYWORD', 'switch')
            self.expect('SYMBOL', '(')
            expr = self.parse_expression()
            self.expect('SYMBOL', ')')
            self.expect('SYMBOL', '{')
        except SyntaxError as e:
            self.errors.append(str(e))
            self.synchronize(['}'])  # Skip to the end of switch block
            return None

        cases = []
        default_case = None

        while self.current_token and self.current_token.value != '}':
            try:
                if self.match('KEYWORD', 'case'):
                    value = self.parse_expression()
                    self.expect('SYMBOL', ':')

                    case_statements = []
                    while self.current_token and self.current_token.value not in ('case', 'default', '}'):
                        try:
                            stmt = self.parse_statement()
                            if stmt:
                                case_statements.append(stmt)
                        except SyntaxError as e:
                            self.errors.append(str(e))
                            self.synchronize(['case', 'default', '}'])

                    case_block = Block(case_statements)
                    cases.append(SwitchCase(value, case_block))

                elif self.match('KEYWORD', 'default'):
                    self.expect('SYMBOL', ':')

                    default_statements = []
                    while self.current_token and self.current_token.value not in ('case', 'default', '}'):
                        try:
                            stmt = self.parse_statement()
                            if stmt:
                                default_statements.append(stmt)
                        except SyntaxError as e:
                            self.errors.append(str(e))
                            self.synchronize(['case', 'default', '}'])

                    default_case = SwitchCase(None, Block(default_statements))

                else:
                    raise SyntaxError(f"Unexpected token {self.current_token.value} in switch block")

            except SyntaxError as e:
                self.errors.append(str(e))
                self.synchronize(['case', 'default', '}'])

        try:
            self.expect('SYMBOL', '}')
        except SyntaxError as e:
            self.errors.append(str(e))
            self.synchronize([';'])  # Assume switch is terminated and continue

        return SwitchStatement(expr, cases, default_case)

<<<<<<< HEAD
## Example usage

=======
## Example usage
>>>>>>> origin/master
