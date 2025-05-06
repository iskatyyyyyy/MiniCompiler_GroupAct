# Import the Tokens and Lexical classes from the provided lexer
from lexical import Tokens, Lexical

# Import AST nodes from the separate module
from ast_1 import (
    ASTNode, Program, VarDeclaration, FunctionDeclaration, Parameter,
    BlockStatement, ExpressionStatement, IfStatement, WhileStatement,
    DoWhileStatement, ForStatement, SwitchStatement, CaseStatement,
    BreakStatement, ContinueStatement, ReturnStatement, BinaryExpression,
    UnaryExpression, AssignmentExpression, Identifier, Literal, FunctionCall,
    ArrayAccess, ArrayDeclaration, StructDeclaration, StructField, StructAccess,
    ConditionalExpression, SizeofExpression, TypeCastExpression
)

class Parser:
    def __init__(self, tokens):
        self.tokens = []
        self.current = 0
        self.errors = []
    
    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, index):
        return self.tokens[index]
    
    def parse(self):
        declarations = []
        while not self.is_at_end():
            try:
                declarations.append(self.declaration())
            except Exception as e:
                self.errors.append(f"Parse error at line {self.peek().line}: {str(e)}")
                self.synchronize()
        
        return Program(declarations), self.errors
    
    def declaration(self):
        # Check for struct declaration
        if self.match('KEYWORD') and self.previous().value == 'struct':
            return self.struct_declaration()
        
        # Check if it's a function or variable declaration
        if self.match('KEYWORD'):
            type_token = self.previous()
            
            # Check for pointer types
            pointer_count = 0
            while self.match('OPERATOR') and self.previous().value == '*':
                pointer_count += 1
            
            type_name = type_token.value
            if pointer_count > 0:
                type_name = type_name + '*' * pointer_count
            
            # Get the identifier
            if not self.check('STANDARD_IDENTIFIER') and not self.check('FUNCTION_CALL'):
                raise Exception(f"Expected identifier after type {type_name}")
            
            identifier_token = self.advance()
            
            # Check if it's a function definition
            if self.match('SYMBOL') and self.previous().value == '(':
                parameters = self.parameter_list()
                
                if not self.match('SYMBOL') or self.previous().value != ')':
                    raise Exception("Expected ')' after parameter list")
                
                # Function body
                if self.match('SYMBOL') and self.previous().value == '{':
                    body = self.block_statement()
                    return FunctionDeclaration(type_name, identifier_token.value, parameters, body)
                else:
                    raise Exception("Expected '{' before function body")
            
            # Check if it's an array declaration
            if self.match('SYMBOL') and self.previous().value == '[':
                # Array declaration
                size_expr = None
                if not self.check('SYMBOL') or self.peek().value != ']':
                    size_expr = self.expression()
                
                if not self.match('SYMBOL') or self.previous().value != ']':
                    raise Exception("Expected ']' after array size")
                
                # Handle initialization
                init_expr = None
                if self.match('OPERATOR') and self.previous().value == '=':
                    if self.match('SYMBOL') and self.previous().value == '{':
                        elements = []
                        if not self.check('SYMBOL') or self.peek().value != '}':
                            elements.append(self.expression())
                            
                            while self.match('SYMBOL') and self.previous().value == ',':
                                if self.check('SYMBOL') and self.peek().value == '}':
                                    break
                                elements.append(self.expression())
                        
                        if not self.match('SYMBOL') or self.previous().value != '}':
                            raise Exception("Expected '}' after array elements")
                        
                        init_expr = elements
                    else:
                        init_expr = self.expression()
                
                if self.match('SYMBOL') and self.previous().value == ';':
                    return ArrayDeclaration(type_name, identifier_token.value, size_expr, init_expr)
                else:
                    raise Exception("Expected ';' after array declaration")
            
            # Variable declaration
            init_expr = None
            if self.match('OPERATOR') and self.previous().value == '=':
                init_expr = self.expression()
            
            if self.match('SYMBOL') and self.previous().value == ';':
                return VarDeclaration(type_name, identifier_token.value, init_expr)
            else:
                raise Exception("Expected ';' after variable declaration")
        
        # If not a declaration, it's a statement
        return self.statement()
    
    def struct_declaration(self):
        # Get the struct name if present
        struct_name = None
        if self.check('STANDARD_IDENTIFIER') or self.check('FUNCTION_CALL'):
            struct_name = self.advance().value
        
        # Check for struct body
        if not self.match('SYMBOL') or self.previous().value != '{':
            raise Exception("Expected '{' after struct declaration")
        
        fields = []
        while not self.check('SYMBOL') or self.peek().value != '}':
            if self.is_at_end():
                raise Exception("Unterminated struct declaration")
            
            # Parse field type
            if not self.match('KEYWORD'):
                raise Exception("Expected field type in struct declaration")
            
            field_type = self.previous().value
            
            # Check for pointer types
            pointer_count = 0
            while self.match('OPERATOR') and self.previous().value == '*':
                pointer_count += 1
            
            if pointer_count > 0:
                field_type = field_type + '*' * pointer_count
            
            # Parse field name
            if not self.check('STANDARD_IDENTIFIER') and not self.check('FUNCTION_CALL'):
                raise Exception(f"Expected field name after type {field_type}")
            
            field_name = self.advance().value
            
            # Check for array field
            array_size = None
            if self.match('SYMBOL') and self.previous().value == '[':
                if not self.check('SYMBOL') or self.peek().value != ']':
                    array_size = self.expression()
                
                if not self.match('SYMBOL') or self.previous().value != ']':
                    raise Exception("Expected ']' after array size")
            
            # End of field declaration
            if not self.match('SYMBOL') or self.previous().value != ';':
                raise Exception("Expected ';' after struct field declaration")
            
            fields.append(StructField(field_type, field_name, array_size))
        
        if not self.match('SYMBOL') or self.previous().value != '}':
            raise Exception("Expected '}' after struct body")
        
        # Check for variable declaration after struct definition
        var_name = None
        if self.check('STANDARD_IDENTIFIER') or self.check('FUNCTION_CALL'):
            var_name = self.advance().value
        
        if self.match('SYMBOL') and self.previous().value == ';':
            return StructDeclaration(struct_name, fields, var_name)
        else:
            raise Exception("Expected ';' after struct declaration")
    
    def parameter_list(self):
        parameters = []
        
        if self.check('SYMBOL') and self.peek().value == ')':
            return parameters
        
        # Parse first parameter
        if self.match('KEYWORD'):
            param_type = self.previous().value
            
            # Check for pointer types
            pointer_count = 0
            while self.match('OPERATOR') and self.previous().value == '*':
                pointer_count += 1
            
            if pointer_count > 0:
                param_type = param_type + '*' * pointer_count
            
            if not self.check('STANDARD_IDENTIFIER') and not self.check('FUNCTION_CALL'):
                raise Exception(f"Expected identifier after type {param_type}")
            
            identifier_token = self.advance()
            
            # Check for array parameter
            is_array = False
            if self.match('SYMBOL') and self.previous().value == '[':
                if not self.match('SYMBOL') or self.previous().value != ']':
                    raise Exception("Expected ']' after '[' in parameter")
                is_array = True
                param_type = param_type + "[]"
            
            parameters.append(Parameter(param_type, identifier_token.value))
        else:
            raise Exception("Expected parameter type")
        
        # Parse the rest of parameters
        while self.match('SYMBOL') and self.previous().value == ',':
            if self.match('KEYWORD'):
                param_type = self.previous().value
                
                # Check for pointer types
                pointer_count = 0
                while self.match('OPERATOR') and self.previous().value == '*':
                    pointer_count += 1
                
                if pointer_count > 0:
                    param_type = param_type + '*' * pointer_count
                
                if not self.check('STANDARD_IDENTIFIER') and not self.check('FUNCTION_CALL'):
                    raise Exception(f"Expected identifier after type {param_type}")
                
                identifier_token = self.advance()
                
                # Check for array parameter
                is_array = False
                if self.match('SYMBOL') and self.previous().value == '[':
                    if not self.match('SYMBOL') or self.previous().value != ']':
                        raise Exception("Expected ']' after '[' in parameter")
                    is_array = True
                    param_type = param_type + "[]"
                
                parameters.append(Parameter(param_type, identifier_token.value))
            else:
                raise Exception("Expected parameter type")
        
        return parameters
    
    def statement(self):
        # Handle different types of statements
        if self.match('SYMBOL') and self.previous().value == '{':
            return self.block_statement()
        
        elif self.match('CONTROL_FLOW'):
            control = self.previous().value
            
            if control == 'if':
                return self.if_statement()
            elif control == 'while':
                return self.while_statement()
            elif control == 'do':
                return self.do_while_statement()
            elif control == 'for':
                return self.for_statement()
            elif control == 'switch':
                return self.switch_statement()
        
        elif self.match('KEYWORD'):
            keyword = self.previous().value
            
            if keyword == 'return':
                expression = None
                if not self.check('SYMBOL') or self.peek().value != ';':
                    expression = self.expression()
                
                if self.match('SYMBOL') and self.previous().value == ';':
                    return ReturnStatement(expression)
                else:
                    raise Exception("Expected ';' after return statement")
            
            elif keyword == 'break':
                if self.match('SYMBOL') and self.previous().value == ';':
                    return BreakStatement()
                else:
                    raise Exception("Expected ';' after break statement")
            
            elif keyword == 'continue':
                if self.match('SYMBOL') and self.previous().value == ';':
                    return ContinueStatement()
                else:
                    raise Exception("Expected ';' after continue statement")
            
            # Handle variable declarations as statements (in blocks)
            else:
                # We consumed the type, so put it back
                self.current -= 1
                return self.declaration()
        
        # Otherwise, it's an expression statement
        expression = self.expression()
        
        if self.match('SYMBOL') and self.previous().value == ';':
            return ExpressionStatement(expression)
        else:
            raise Exception(f"Expected ';' after expression, got {self.peek().value if not self.is_at_end() else 'EOF'}")
    
    def block_statement(self):
        statements = []
        
        while not self.check('SYMBOL') or self.peek().value != '}':
            if self.is_at_end():
                raise Exception("Unterminated block statement")
            
            statements.append(self.declaration())
        
        if not self.match('SYMBOL') or self.previous().value != '}':
            raise Exception("Expected '}' after block")
        
        return BlockStatement(statements)
    
    def if_statement(self):
        if not self.match('SYMBOL') or self.previous().value != '(':
            raise Exception("Expected '(' after 'if'")
        
        condition = self.expression()
        
        if not self.match('SYMBOL') or self.previous().value != ')':
            raise Exception("Expected ')' after if condition")
        
        then_branch = self.statement()
        else_branch = None
        
        if self.match('CONTROL_FLOW') and self.previous().value == 'else':
            else_branch = self.statement()
        
        return IfStatement(condition, then_branch, else_branch)
    
    def while_statement(self):
        if not self.match('SYMBOL') or self.previous().value != '(':
            raise Exception("Expected '(' after 'while'")
        
        condition = self.expression()
        
        if not self.match('SYMBOL') or self.previous().value != ')':
            raise Exception("Expected ')' after while condition")
        
        body = self.statement()
        
        return WhileStatement(condition, body)
    
    def do_while_statement(self):
        body = self.statement()
        
        if not self.match('CONTROL_FLOW') or self.previous().value != 'while':
            raise Exception("Expected 'while' after do statement body")
        
        if not self.match('SYMBOL') or self.previous().value != '(':
            raise Exception("Expected '(' after 'while'")
        
        condition = self.expression()
        
        if not self.match('SYMBOL') or self.previous().value != ')':
            raise Exception("Expected ')' after while condition")
        
        if not self.match('SYMBOL') or self.previous().value != ';':
            raise Exception("Expected ';' after do-while statement")
        
        return DoWhileStatement(body, condition)
    
    def for_statement(self):
        if not self.match('SYMBOL') or self.previous().value != '(':
            raise Exception("Expected '(' after 'for'")
        
        # Initializer
        init = None
        if not self.check('SYMBOL') or self.peek().value != ';':
            if self.check('KEYWORD'):
                # It's a variable declaration
                init = self.declaration()
            else:
                # It's an expression
                init = ExpressionStatement(self.expression())
                if not self.match('SYMBOL') or self.previous().value != ';':
                    raise Exception("Expected ';' after for initializer")
        else:
            self.advance()  # consume the semicolon
        
        # Condition
        condition = None
        if not self.check('SYMBOL') or self.peek().value != ';':
            condition = self.expression()
        
        if not self.match('SYMBOL') or self.previous().value != ';':
            raise Exception("Expected ';' after for condition")
        
        # Increment
        update = None
        if not self.check('SYMBOL') or self.peek().value != ')':
            update = self.expression()
        
        if not self.match('SYMBOL') or self.previous().value != ')':
            raise Exception("Expected ')' after for clauses")
        
        # Body
        body = self.statement()
        
        return ForStatement(init, condition, update, body)
    
    def switch_statement(self):
        if not self.match('SYMBOL') or self.previous().value != '(':
            raise Exception("Expected '(' after 'switch'")
        
        expression = self.expression()
        
        if not self.match('SYMBOL') or self.previous().value != ')':
            raise Exception("Expected ')' after switch expression")
        
        if not self.match('SYMBOL') or self.previous().value != '{':
            raise Exception("Expected '{' before switch body")
        
        cases = []
        while not self.check('SYMBOL') or self.peek().value != '}':
            if self.is_at_end():
                raise Exception("Unterminated switch statement")
            
            if self.match('CONTROL_FLOW'):
                if self.previous().value == 'case':
                    value = self.expression()
                    
                    if not self.match('SYMBOL') or self.previous().value != ':':
                        raise Exception("Expected ':' after case value")
                    
                    statements = []
                    while (not self.check('CONTROL_FLOW') or (self.peek().value != 'case' and self.peek().value != 'default')) and (not self.check('SYMBOL') or self.peek().value != '}'):
                        if self.is_at_end():
                            raise Exception("Unterminated case statement")
                        
                        statements.append(self.statement())
                    
                    cases.append(CaseStatement(value, statements))
                
                elif self.previous().value == 'default':
                    if not self.match('SYMBOL') or self.previous().value != ':':
                        raise Exception("Expected ':' after default")
                    
                    statements = []
                    while (not self.check('CONTROL_FLOW') or (self.peek().value != 'case' and self.peek().value != 'default')) and (not self.check('SYMBOL') or self.peek().value != '}'):
                        if self.is_at_end():
                            raise Exception("Unterminated default statement")
                        
                        statements.append(self.statement())
                    
                    cases.append(CaseStatement(None, statements))
            else:
                raise Exception("Expected 'case' or 'default' in switch statement")
        
        if not self.match('SYMBOL') or self.previous().value != '}':
            raise Exception("Expected '}' after switch body")
        
        return SwitchStatement(expression, cases)
    
    def expression(self):
        return self.conditional_expression()
    
    def conditional_expression(self):
        expr = self.assignment()
        
        # Handle ternary conditional expression: condition ? then_expr : else_expr
        if self.match('OPERATOR') and self.previous().value == '?':
            then_expr = self.expression()
            
            if not self.match('SYMBOL') or self.previous().value != ':':
                raise Exception("Expected ':' in conditional expression")
            
            else_expr = self.conditional_expression()
            return ConditionalExpression(expr, then_expr, else_expr)
        
        return expr
    
    def assignment(self):
        expr = self.logical_or()
        
        # Handle assignment expressions (=, +=, -=, etc.)
        if self.match('OPERATOR') and self.previous().value in ['=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '&=', '^=', '|=']:
            operator = self.previous().value
            right = self.assignment()  # Assignment is right-associative
            
            # Make sure the left-hand side is a valid assignment target
            if isinstance(expr, (Identifier, ArrayAccess, StructAccess)):
                return AssignmentExpression(expr, operator, right)
            else:
                raise Exception("Invalid assignment target")
        
        return expr
    
    def logical_or(self):
        expr = self.logical_and()
        
        while self.match('OPERATOR') and self.previous().value == '||':
            operator = self.previous().value
            right = self.logical_and()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def logical_and(self):
        expr = self.bitwise_or()
        
        while self.match('OPERATOR') and self.previous().value == '&&':
            operator = self.previous().value
            right = self.bitwise_or()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def bitwise_or(self):
        expr = self.bitwise_xor()
        
        while self.match('OPERATOR') and self.previous().value == '|':
            operator = self.previous().value
            right = self.bitwise_xor()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def bitwise_xor(self):
        expr = self.bitwise_and()
        
        while self.match('OPERATOR') and self.previous().value == '^':
            operator = self.previous().value
            right = self.bitwise_and()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def bitwise_and(self):
        expr = self.equality()
        
        while self.match('OPERATOR') and self.previous().value == '&':
            operator = self.previous().value
            right = self.equality()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def equality(self):
        expr = self.comparison()
        
        while self.match('OPERATOR') and self.previous().value in ['==', '!=']:
            operator = self.previous().value
            right = self.comparison()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def comparison(self):
        expr = self.shift()
        
        while self.match('OPERATOR') and self.previous().value in ['<', '>', '<=', '>=']:
            operator = self.previous().value
            right = self.shift()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def shift(self):
        expr = self.term()
        
        while self.match('OPERATOR') and self.previous().value in ['<<', '>>']:
            operator = self.previous().value
            right = self.term()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def term(self):
        expr = self.factor()
        
        while self.match('OPERATOR') and self.previous().value in ['+', '-']:
            operator = self.previous().value
            right = self.factor()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def factor(self):
        expr = self.unary()
        
        while self.match('OPERATOR') and self.previous().value in ['*', '/', '%']:
            operator = self.previous().value
            right = self.unary()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def unary(self):
        # Handle sizeof operator
        if self.match('KEYWORD') and self.previous().value == 'sizeof':
            if self.match('SYMBOL') and self.previous().value == '(':
                # Check if it's a type name or an expression
                if self.check('KEYWORD'):
                    type_name = self.advance().value
                    
                    # Check for pointer types
                    pointer_count = 0
                    while self.match('OPERATOR') and self.previous().value == '*':
                        pointer_count += 1
                    
                    if pointer_count > 0:
                        type_name = type_name + '*' * pointer_count
                    
                    if not self.match('SYMBOL') or self.previous().value != ')':
                        raise Exception("Expected ')' after sizeof type")
                    
                    return SizeofExpression(type_name, is_type=True)
                else:
                    expr = self.expression()
                    
                    if not self.match('SYMBOL') or self.previous().value != ')':
                        raise Exception("Expected ')' after sizeof expression")
                    
                    return SizeofExpression(expr, is_type=False)
            else:
                # sizeof applied to a primary expression without parentheses
                expr = self.primary()
                return SizeofExpression(expr, is_type=False)
        
        # Handle type casting
        if self.match('SYMBOL') and self.previous().value == '(':
            if self.check('KEYWORD'):
                type_name = self.advance().value
                
                # Check for pointer types
                pointer_count = 0
                while self.match('OPERATOR') and self.previous().value == '*':
                    pointer_count += 1
                
                if pointer_count > 0:
                    type_name = type_name + '*' * pointer_count
                
                if self.match('SYMBOL') and self.previous().value == ')':
                    expr = self.unary()  # Cast has same precedence as unary operators
                    return TypeCastExpression(type_name, expr)
                else:
                    # Not a type cast, restore position and treat as a grouped expression
                    self.current -= 2 + pointer_count
            else:
                # Not a type cast, restore position
                self.current -= 1
        
        # Handle prefix operators
        if self.match('OPERATOR') and self.previous().value in ['!', '-', '+', '++', '--', '~', '&', '*']:
            operator = self.previous().value
            right = self.unary()
            return UnaryExpression(operator, right, is_prefix=True)
        
        expr = self.postfix()
        return expr
    
    def postfix(self):
        expr = self.primary()
        
        while True:
            # Handle postfix operators
            if self.match('OPERATOR') and self.previous().value in ['++', '--']:
                operator = self.previous().value
                expr = UnaryExpression(operator, expr, is_prefix=False)
            
            # Handle array access
            elif self.match('SYMBOL') and self.previous().value == '[':
                index = self.expression()
                
                if not self.match('SYMBOL') or self.previous().value != ']':
                    raise Exception("Expected ']' after array index")
                
                expr = ArrayAccess(expr, index)
            
            # Handle struct/union member access
            elif self.match('OPERATOR') and self.previous().value in ['.', '->']:
                operator = self.previous().value
                
                if not self.check('STANDARD_IDENTIFIER') and not self.check('FUNCTION_CALL'):
                    raise Exception("Expected field name after '.' or '->'")
                
                field = self.advance().value
                expr = StructAccess(expr, operator, field)
            
            # Handle function call
            elif self.match('SYMBOL') and self.previous().value == '(':
                arguments = []
                if not self.check('SYMBOL') or self.peek().value != ')':
                    arguments.append(self.expression())
                    
                    while self.match('SYMBOL') and self.previous().value == ',':
                        arguments.append(self.expression())
                
                if not self.match('SYMBOL') or self.previous().value != ')':
                    raise Exception("Expected ')' after function arguments")
                
                # If expr is an identifier, create a FunctionCall directly
                if isinstance(expr, Identifier):
                    expr = FunctionCall(expr.name, arguments)
                else:
                    # Otherwise, it's a function pointer call
                    expr = FunctionCall(expr, arguments, is_ptr_call=True)
            else:
                break
        
        return expr
    
    def primary(self):
        if self.match('NUMBER'):
            return Literal(self.previous().value, "NUMBER")
        
        if self.match('STRING'):
            return Literal(self.previous().value, "STRING")
        
        if self.match('CHAR_LITERAL'):
            return Literal(self.previous().value, "CHAR_LITERAL")
        
        if self.match('STANDARD_IDENTIFIER'):
            return Identifier(self.previous().value)
        
        if self.match('FUNCTION_CALL'):
            return Identifier(self.previous().value)
        
        if self.match('SYMBOL') and self.previous().value == '(':
            expr = self.expression()
            
            if not self.match('SYMBOL') or self.previous().value != ')':
                raise Exception("Expected ')' after expression")
            
            return expr
        
        raise Exception(f"Unexpected token: {self.peek().value if not self.is_at_end() else 'EOF'}")
    
    def match(self, token_type):
        if self.check(token_type):
            self.advance()
            return True
        return False
    
    def check(self, token_type):
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self):
        return self.current >= len(self.tokens)
    
    def peek(self):
        return self.tokens[self.current]
    
    def previous(self):
        return self.tokens[self.current - 1]
    
    def synchronize(self):
        self.advance()
        
        while not self.is_at_end():
            if self.previous().value == ';':
                return
            
            if self.peek().type in ['KEYWORD', 'CONTROL_FLOW']:
                if self.peek().value in ['if', 'while', 'for', 'return', 'break', 'continue', 'int', 'char', 'float', 'double', 'void', 'struct']:
                    return
            
            self.advance()

# Example usage
if __name__ == "__main__":
    print("Enter C code (press Enter twice to finish input):")
    user_input = ''
    while True:
        line = input()
        if line == '':
            break
        user_input += line + '\n'

    # Create a lexer instance using the provided Lexical class
    lexer = Lexical(user_input)
    tokens, lex_errors = lexer.get_tokens()

    print(f"\n{'TOKEN VALUE':<30} {'TOKEN TYPE':<20} LINE")
    print('-' * 70)
    for token in tokens:
        print(token)

    # Display lexical error messages
    if lex_errors:
        print("\nLexical Errors:")
        for error in lex_errors:
            print(error)
    
    # Parse the tokens to create an AST
    parser = Parser(tokens)
    ast, parse_errors = parser.parse()
    
    # Display parse error messages
    if parse_errors:
        print("\nParse Errors:")
        for error in parse_errors:
            print(error)
    
    print("\nAbstract Syntax Tree:")
    print(ast)
