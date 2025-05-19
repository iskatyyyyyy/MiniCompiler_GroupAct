from ast_nodes import *
from lexical import Lexical, Tokens

class Parser:
    # Tokens and Position Tracking
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None

    # Token Navigation
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Tokens('EOF', 'EOF', self.current_token.line)

    def match(self, token_type, value=None):
        if self.current_token and self.current_token.type == token_type:
            if value is None or self.current_token.value == value:
                matched_token = self.current_token
                self.advance()
                return matched_token
        return None

    def expect(self, token_type, value=None):
        token = self.match(token_type, value)
        if not token:
            raise SyntaxError(f"Expected {token_type} '{value}' at line {self.current_token.line if self.current_token else 'EOF'}")
        return token
    
    def eat(self, expected_type_or_value):
        token = self.current_token
        if token.type == expected_type_or_value or token.value == expected_type_or_value:
            self.advance()
        else:
            raise SyntaxError(f"Expected '{expected_type_or_value}', but got {token.type}('{token.value}') on line {token.line}")

    # Parse the entire program
    def parse(self):
        declarations = []
        while self.current_token and self.current_token.type != 'EOF':
            if self.current_token.type == 'KEYWORD':
                decl = self.parse_declaration_or_function()
                declarations.append(decl)
            else:
                # Unexpected token or end of declarations
                break
        return declarations

    # Parsing Declarations and Functions
    def parse_declaration_or_function(self):
        var_type = self.expect('KEYWORD').value
        name = self.expect('IDENTIFIER').value

        if self.match('SYMBOL', '('):
            parameters = []
            # Parse parameters properly without consuming the closing ')'
            if self.current_token.value != ')':
                while True:
                    param_type = self.expect('KEYWORD').value
                    param_name = self.expect('IDENTIFIER').value
                    parameters.append((param_type, param_name))
                    if self.current_token.value == ')':
                        break
                    self.expect('SYMBOL', ',')
            self.expect('SYMBOL', ')')  # Consume the closing ')'

            body = self.parse_compound_statement()
            return FunctionDeclaration(var_type, name, parameters, body)

        else:
            initializer = None
            if self.match('SYMBOL', '='):
                initializer = self.parse_expression()
            self.expect('SYMBOL', ';')
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
        if self.current_token.value == 'if':
            return self.parse_if_statement()
        elif self.current_token.value == 'while':
            return self.parse_while_statement()
        elif self.current_token.value == 'for':
            return self.parse_for_statement()
        elif self.current_token.value == 'return':
            return self.parse_return_statement()
        elif self.current_token.value in ('int', 'char', 'float', 'double', 'void'):
            return self.parse_declaration()
        elif self.current_token.value == '{':
            return self.parse_compound_statement()
        else:
            expr = self.parse_expression()
            self.eat(';')
            return ExpressionStatement(expr)

    def parse_declaration(self):
        var_type = self.current_token.value
        self.eat('KEYWORD')
        var_name = self.current_token.value
        self.eat('IDENTIFIER')

        initializer = None
        if self.current_token.value == '=':
            self.eat('=')
            initializer = self.parse_expression()

        self.eat(';')
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
            return BinaryOperation(op, left, right)
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

        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return Number(token.value)

        elif token.type == 'STRING':
            self.eat('STRING')
            return StringNode(token.value)

        elif token.type == 'CHAR_LITERAL':
            self.eat('CHAR_LITERAL')
            return CharNode(token.value)  # Make sure you have CharNode in your AST nodes

        elif token.type == 'IDENTIFIER':
            identifier_token = token
            self.eat('IDENTIFIER')

            if self.current_token and self.current_token.value == '(':
                self.eat('(')
                args = []
                if self.current_token.value != ')':
                    while True:
                        args.append(self.parse_expression())
                        if self.current_token.value == ',':
                            self.eat(',')
                        else:
                            break
                self.eat(')')
                return FunctionCallNode(identifier_token.value, args)
            else:
                return VariableNode(identifier_token.value)

        elif token.value == '(':
            self.eat('(')
            expr = self.parse_expression()
            self.eat(')')
            return expr

        raise SyntaxError(f"Unexpected token {token.type}('{token.value}') on line {token.line}")

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
        self.expect('KEYWORD', 'if')
        self.expect('SYMBOL', '(')
        condition = self.parse_expression()
        self.expect('SYMBOL', ')')
        then_branch = self.parse_statement()

        else_branch = None
        if self.match('KEYWORD', 'else'):
            else_branch = self.parse_statement()

        return IfStatement(condition, then_branch, else_branch)

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
        self.expect('KEYWORD', 'return')
        value = None
        if self.current_token.value != ';':
            value = self.parse_expression()
        self.expect('SYMBOL', ';')
        return ReturnStatement(value)

