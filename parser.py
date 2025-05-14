from lexical import Lexical, Tokens
from typing import List, Optional, Tuple, Union, Dict, Any

# AST Node classes
class ASTNode:
    def __init__(self, line: int):
        self.line = line
    
    def __str__(self):
        return self.__repr__()

class Program(ASTNode):
    def __init__(self, declarations: List[ASTNode], line: int):
        super().__init__(line)
        self.declarations = declarations
    
    def __repr__(self):
        return f"Program(declarations={len(self.declarations)})"

class Declaration(ASTNode):
    pass

class VarDeclaration(Declaration):
    def __init__(self, type_spec: str, var_name: str, initializer: Optional[ASTNode] = None, array_size: Optional[ASTNode] = None, line: int = 0):
        super().__init__(line)
        self.type_spec = type_spec
        self.var_name = var_name
        self.initializer = initializer  # Added initializer
        self.array_size = array_size

    def __repr__(self):
        array_suffix = f"[{self.array_size}]" if self.array_size else ""
        init_suffix = f" = {self.initializer}" if self.initializer else ""  # Include initializer in repr
        return f"VarDeclaration({self.type_spec} {self.var_name}{array_suffix}{init_suffix})"


class FunctionDeclaration(Declaration):
    def __init__(self, return_type: str, name: str, params: List[VarDeclaration], 
                 body: Optional['CompoundStatement'] = None, line: int = 0):
        super().__init__(line)
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body
    
    def __repr__(self):
        return f"FunctionDeclaration({self.return_type} {self.name}({len(self.params)} params))"

class Statement(ASTNode):
    pass

class ExpressionStatement(Statement):
    def __init__(self, expression: Optional['Expression'], line: int):
        super().__init__(line)
        self.expression = expression
    
    def __repr__(self):
        return f"ExpressionStatement({self.expression})"

class CompoundStatement(Statement):
    def __init__(self, local_declarations: List[VarDeclaration], statements: List[Statement], line: int):
        super().__init__(line)
        self.local_declarations = local_declarations
        self.statements = statements
    
    def __repr__(self):
        return f"CompoundStatement(locals={len(self.local_declarations)}, stmts={len(self.statements)})"

class IfStatement(Statement):
    def __init__(self, condition: 'Expression', if_body: Statement, 
                 else_body: Optional[Statement] = None, line: int = 0):
        super().__init__(line)
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body
    
    def __repr__(self):
        has_else = "with else" if self.else_body else "no else"
        return f"IfStatement({has_else})"

class WhileStatement(Statement):
    def __init__(self, condition: 'Expression', body: Statement, line: int):
        super().__init__(line)
        self.condition = condition
        self.body = body
    
    def __repr__(self):
        return f"WhileStatement()"

class DoWhileStatement(Statement):
    def __init__(self, body: Statement, condition: 'Expression', line: int):
        super().__init__(line)
        self.body = body
        self.condition = condition
    
    def __repr__(self):
        return f"DoWhileStatement()"

class ForStatement(Statement):
    def __init__(self, init: Optional['Expression'], condition: Optional['Expression'], 
                 update: Optional['Expression'], body: Statement, line: int):
        super().__init__(line)
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
    
    def __repr__(self):
        return f"ForStatement()"

class SwitchStatement(Statement):
    def __init__(self, expression: 'Expression', cases: List['CaseStatement'], 
                 default_case: Optional['DefaultStatement'], line: int):
        super().__init__(line)
        self.expression = expression
        self.cases = cases
        self.default_case = default_case
    
    def __repr__(self):
        return f"SwitchStatement(cases={len(self.cases)}, has_default={self.default_case is not None})"

class CaseStatement(Statement):
    def __init__(self, value: 'Expression', statements: List[Statement], line: int):
        super().__init__(line)
        self.value = value
        self.statements = statements
    
    def __repr__(self):
        return f"CaseStatement(value={self.value}, stmts={len(self.statements)})"

class DefaultStatement(Statement):
    def __init__(self, statements: List[Statement], line: int):
        super().__init__(line)
        self.statements = statements
    
    def __repr__(self):
        return f"DefaultStatement(stmts={len(self.statements)})"

class ReturnStatement(Statement):
    def __init__(self, expression: Optional['Expression'], line: int):
        super().__init__(line)
        self.expression = expression
    
    def __repr__(self):
        return f"ReturnStatement({self.expression})"

class BreakStatement(Statement):
    def __init__(self, line: int):
        super().__init__(line)
    
    def __repr__(self):
        return "BreakStatement()"

class ContinueStatement(Statement):
    def __init__(self, line: int):
        super().__init__(line)
    
    def __repr__(self):
        return "ContinueStatement()"

class Expression(ASTNode):
    pass

class LiteralExpression(Expression):
    def __init__(self, value: str, literal_type: str, line: int):
        super().__init__(line)
        self.value = value
        self.literal_type = literal_type  # number, string, char
    
    def __repr__(self):
        return f"LiteralExpression({self.literal_type}: {self.value})"

class IdentifierExpression(Expression):
    def __init__(self, name: str, line: int):
        super().__init__(line)
        self.name = name
    
    def __repr__(self):
        return f"IdentifierExpression({self.name})"

class ArrayAccessExpression(Expression):
    def __init__(self, array: Expression, index: Expression, line: int):
        super().__init__(line)
        self.array = array
        self.index = index
    
    def __repr__(self):
        return f"ArrayAccessExpression({self.array}[{self.index}])"

class FunctionCallExpression(Expression):
    def __init__(self, function: Expression, arguments: List[Expression], line: int):
        super().__init__(line)
        self.function = function
        self.arguments = arguments
    
    def __repr__(self):
        return f"FunctionCallExpression({self.function}, args={len(self.arguments)})"

class UnaryExpression(Expression):
    def __init__(self, operator: str, operand: Expression, line: int):
        super().__init__(line)
        self.operator = operator
        self.operand = operand
    
    def __repr__(self):
        return f"UnaryExpression({self.operator}{self.operand})"

class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression, line: int):
        super().__init__(line)
        self.left = left
        self.operator = operator
        self.right = right
    
    def __repr__(self):
        return f"BinaryExpression({self.left} {self.operator} {self.right})"

class AssignmentExpression(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression, line: int):
        super().__init__(line)
        self.left = left
        self.operator = operator
        self.right = right
    
    def __repr__(self):
        return f"AssignmentExpression({self.left} {self.operator} {self.right})"

class Parser:
    def __init__(self, tokens: List[Tokens]):
        self.tokens = tokens
        self.current = 0
        self.errors = []
        self.synchronization_tokens = {'if', 'else', 'while', 'for', 'do', 'return', 'switch', 'case', 'default', 'break', 'continue', ';', '{', '}'}
    
    def advance(self) -> Tokens:
        """Advance to the next token and return the previous token"""
        prev = self.current_token()
        self.current += 1
        return prev
    
    def current_token(self) -> Tokens:
        """Get the current token"""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None
    
    def peek(self, offset: int = 1) -> Tokens:
        """Look ahead at future tokens without advancing"""
        if self.current + offset < len(self.tokens):
            return self.tokens[self.current + offset]
        return None
    
    def check(self, token_type: str, token_value: str = None) -> bool:
        """Check if the current token matches the expected type/value"""
        if self.is_at_end():
            return False
        
        current = self.current_token()
        if token_value:
            return current.type == token_type and current.value == token_value
        else:
            return current.type == token_type
    
    def match(self, token_type: str, token_value: str = None) -> bool:
        """Check if current token matches, and advance if it does"""
        if self.check(token_type, token_value):
            self.advance()
            return True
        return False
    
    def consume(self, token_type: str, token_value: str = None, error_message: str = None) -> Optional[Tokens]:
        """Consume the expected token or report an error"""
        if self.check(token_type, token_value):
            return self.advance()
        
        token = self.current_token()
        message = error_message or f"Expected {token_type}"
        if token_value:
            message += f" '{token_value}'"
        
        if token:
            self.error(message, token.line)
            return token
        else:
            self.error(message, -1)  # End of file
            return None
    
    def error(self, message: str, line: int) -> None:
        """Report a parsing error"""
        error_msg = f"Error at line {line}: {message}"
        self.errors.append(error_msg)
    
    def is_at_end(self) -> bool:
        """Check if we've reached the end of input"""
        return self.current >= len(self.tokens)
    
    def synchronize(self) -> None:
        """Error recovery - skip tokens until a synchronization point"""
        self.advance()  # Skip the token that caused the error
        
        while not self.is_at_end():
            # Synchronize on statement boundaries
            token = self.current_token()
            
            # Reached end of statement or beginning of new block
            if token.value in self.synchronization_tokens or token.value == ';':
                return
            
            self.advance()
    
    def parse(self) -> Tuple[Program, List[str]]:
        """Parse the tokens into an AST"""
        try:
            ast = self.program()
            return ast, self.errors
        except Exception as e:
            self.error(f"Unexpected error: {str(e)}", -1)
            return None, self.errors
    
    # Recursive Descent Parsing Methods
    
    def program(self) -> Program:
        """Parse the entire program: program -> declaration*"""
        declarations = []
        
        while not self.is_at_end():
            try:
                declarations.append(self.declaration())
            except Exception as e:
                self.error(f"Error in declaration: {str(e)}", 
                          self.current_token().line if self.current_token() else -1)
                self.synchronize()
        
        return Program(declarations, 1)  # Start at line 1
    
    def declaration(self) -> Declaration:
        """Parse a declaration: declaration -> var_declaration | function_declaration"""
        # Parse type specifier
        if not self.check('KEYWORD'):
            self.error("Expected type specifier", self.current_token().line)
            self.synchronize()
            return None
        
        type_spec = self.current_token().value
        line = self.current_token().line
        self.advance()
        
        # Parse identifier
        if not (self.check('IDENTIFIER') or self.check('STANDARD_IDENTIFIER') or self.check('FUNCTION_CALL')):
            self.error("Expected identifier after type specifier", self.current_token().line)
            self.synchronize()
            return None
        
        identifier = self.current_token().value
        self.advance()
        
        # Check if this is a function declaration or variable declaration
        if self.check('SYMBOL', '('):
            # Function declaration
            return self.finish_function_declaration(type_spec, identifier, line)
        else:
            # Variable declaration
            return self.finish_var_declaration(type_spec, identifier, line)
    
    def variable_declaration(self):
        type_token = self.consume('KEYWORD', message="Expected type specifier")
        type_spec = type_token.value
        identifier_token = self.consume('IDENTIFIER', message="Expected identifier after type specifier")
        line = identifier_token.line

        initializer = None
        if self.match('SYMBOL', '='):
            initializer = self.expression()  # Parse initializer expression

        self.consume('SYMBOL', ';', "Expected ';' after local variable declaration")
        return VarDeclaration(type_spec, identifier_token.value, initializer, line)

    def finish_var_declaration(self, type_spec: str, var_name: str, line: int) -> VarDeclaration:
        """Finish parsing a variable declaration"""
        array_size = None
        
        # Check for array declaration
        if self.match('SYMBOL', '['):
            # Array declaration with size
            if self.check('NUMBER'):
                array_size = LiteralExpression(self.current_token().value, 'number', self.current_token().line)
                self.advance()
            else:
                self.error("Expected array size", self.current_token().line)
            
            self.consume('SYMBOL', ']', "Expected ']' after array size")
        
        # Expect semicolon
        self.consume('SYMBOL', ';', "Expected ';' after variable declaration")
        
        return VarDeclaration(type_spec, var_name, array_size, line)
    
    def finish_function_declaration(self, return_type: str, name: str, line: int) -> FunctionDeclaration:
        """Finish parsing a function declaration"""
        # Consume opening parenthesis
        self.advance()  # Consume '('
        
        # Parse parameters
        params = []
        if not self.check('SYMBOL', ')'):
            params = self.parameter_list()
        
        # Consume closing parenthesis
        self.consume('SYMBOL', ')', "Expected ')' after function parameters")
        
        # Function declaration (prototype) or definition?
        if self.match('SYMBOL', ';'):
            # Function prototype only
            return FunctionDeclaration(return_type, name, params, None, line)
        elif self.check('SYMBOL', '{'):
            # Function definition with body
            body = self.compound_statement()
            return FunctionDeclaration(return_type, name, params, body, line)
        else:
            self.error("Expected ';' or '{' after function declaration", self.current_token().line)
            self.synchronize()
            return FunctionDeclaration(return_type, name, params, None, line)  # Return what we have so far
    
    def match_type_specifier(self):
        return self.match('KEYWORD', 'int') or \
            self.match('KEYWORD', 'float') or \
            self.match('KEYWORD', 'char') or \
            self.match('KEYWORD', 'void')
    
    def consume_type_specifier(self):
        if self.check('KEYWORD', 'int') or self.check('KEYWORD', 'float') or self.check('KEYWORD', 'char') or self.check('KEYWORD', 'void'):
            return self.advance().value
        else:
            raise self.error(self.current_token(), "Expected type specifier")

    def parameter_list(self) -> List[VarDeclaration]:
        """Parse function parameters: param_list -> param (',' param)*"""
        params = []
        
        while True:
            # Parse parameter type
            if not self.check('KEYWORD'):
                self.error("Expected type specifier in parameter", self.current_token().line)
                break
            
            param_type = self.current_token().value
            line = self.current_token().line
            self.advance()
            
            # Parse parameter name
            if not self.check('IDENTIFIER') and not self.check('STANDARD_IDENTIFIER'):
                self.error("Expected parameter name", self.current_token().line)
                break
            
            param_name = self.current_token().value
            self.advance()
            
            # Check for array parameter
            array_size = None
            if self.match('SYMBOL', '['):
                self.consume('SYMBOL', ']', "Expected ']' after array parameter")
                array_size = LiteralExpression("0", 'number', line)  # Array params don't have size
            
            params.append(VarDeclaration(param_type, param_name, array_size, line))
            
            # Continue if there are more parameters
            if not self.match('SYMBOL', ','):
                break
        
        return params
    
    def compound_statement(self) -> CompoundStatement:
        """Parse compound statement: { local_declarations statement_list }"""
        self.consume('SYMBOL', '{', "Expected '{' at start of compound statement")
        line = self.current_token().line
        
        local_declarations = []
        statements = []
        
        # Parse local variable declarations
        while self.check('KEYWORD'):
            # This should be a type specifier for a local variable
            type_spec = self.current_token().value
            var_line = self.current_token().line
            self.advance()  # consume the type specifier
            
            # Must be followed by an identifier (the variable name)
            if not self.check('IDENTIFIER') and not self.check('STANDARD_IDENTIFIER'):
                self.error("Expected identifier after type specifier", self.current_token().line)
                self.synchronize()
                continue
            
            var_name = self.current_token().value
            self.advance()  # consume the variable name
            
            # Handle array size if applicable
            array_size = None
            if self.match('SYMBOL', '['):
                if self.check('NUMBER'):
                    array_size = LiteralExpression(self.current_token().value, 'number', self.current_token().line)
                    self.advance()
                self.consume('SYMBOL', ']', "Expected ']' after array size")
            
            # Check if there's an initializer (e.g., "int a = 5;")
            initializer = None
            if self.match('SYMBOL', '='):
                initializer = self.expression()  # Parse the initializer expression
            
            self.consume('SYMBOL', ';', "Expected ';' after local variable declaration")

            # Add the local variable declaration to the list
            local_declarations.append(VarDeclaration(type_spec, var_name, initializer, array_size, var_line))
        
        # Parse statements (normal statements after declarations)
        while not self.check('SYMBOL', '}') and not self.is_at_end():
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        
        self.consume('SYMBOL', '}', "Expected '}' at end of compound statement")
        
        return CompoundStatement(local_declarations, statements, line)



    def statement(self) -> Statement:
        """Parse a statement"""
        if self.check('KEYWORD'):
            keyword = self.current_token().value
            if keyword == 'return':
                self.advance()  # consume 'return'
                line = self.current_token().line
                
                # Handle return with no value
                if self.check('SYMBOL', ';'):
                    self.advance()  # consume semicolon
                    return ReturnStatement(None, line)
                
                # Handle return with value
                expr = None
                if self.check('NUMBER'):
                    value = self.current_token().value
                    expr = LiteralExpression(value, 'number', line)
                    self.advance()  # consume number
                else:
                    expr = self.expression()
                    
                self.consume('SYMBOL', ';', "Expected ';' after return value")
                return ReturnStatement(expr, line)
            elif keyword == 'if':
                self.advance()
                return self.if_statement()
            elif keyword == 'while':
                self.advance()
                return self.while_statement()
            elif keyword == 'do':
                self.advance()
                return self.do_while_statement()
            elif keyword == 'for':
                self.advance()
                return self.for_statement()
            elif keyword == 'switch':
                self.advance()
                return self.switch_statement()
            elif keyword == 'break':
                self.advance()
                stmt = BreakStatement(self.current_token().line)
                self.consume('SYMBOL', ';', "Expected ';' after 'break'")
                return stmt
            elif keyword == 'continue':
                self.advance()
                stmt = ContinueStatement(self.current_token().line)
                self.consume('SYMBOL', ';', "Expected ';' after 'continue'")
                return stmt
        
        if self.check('SYMBOL', '{'):
            return self.compound_statement()
        
        # Handle expression statements
        expr = self.expression_statement()
        return expr
    
    # method to handle function calls in expressions:
    def function_call(self) -> Expression:
        """Parse function call: identifier '(' arguments? ')'"""
        name = self.current_token().value
        line = self.current_token().line
        self.advance()  # consume function name
        
        self.consume('SYMBOL', '(', "Expected '(' after function name")
        arguments = []
        
        if not self.check('SYMBOL', ')'):
            arguments.append(self.expression())
            while self.match('SYMBOL', ','):
                arguments.append(self.expression())
        
        self.consume('SYMBOL', ')', "Expected ')' after arguments")
        
        return FunctionCallExpression(IdentifierExpression(name, line), arguments, line)


    
    def if_statement(self) -> IfStatement:
        """Parse if statement: if (expression) statement [else statement]"""
        line = self.current_token().line - 1  # Line of 'if' keyword
        
        self.consume('SYMBOL', '(', "Expected '(' after 'if'")
        condition = self.expression()
        self.consume('SYMBOL', ')', "Expected ')' after if condition")
        
        if_body = self.statement()
        else_body = None
        
        if self.match('KEYWORD', 'else'):
            else_body = self.statement()
        
        return IfStatement(condition, if_body, else_body, line)
    
    def while_statement(self) -> WhileStatement:
        """Parse while statement: while (expression) statement"""
        line = self.current_token().line - 1  # Line of 'while' keyword
        
        self.consume('SYMBOL', '(', "Expected '(' after 'while'")
        condition = self.expression()
        self.consume('SYMBOL', ')', "Expected ')' after while condition")
        
        body = self.statement()
        
        return WhileStatement(condition, body, line)
    
    def do_while_statement(self) -> DoWhileStatement:
        """Parse do-while statement: do statement while (expression);"""
        line = self.current_token().line - 1  # Line of 'do' keyword
        
        body = self.statement()
        
        self.consume('KEYWORD', 'while', "Expected 'while' after 'do' block")
        self.consume('SYMBOL', '(', "Expected '(' after 'while'")
        condition = self.expression()
        self.consume('SYMBOL', ')', "Expected ')' after do-while condition")
        self.consume('SYMBOL', ';', "Expected ';' after do-while statement")
        
        return DoWhileStatement(body, condition, line)
    
    def for_statement(self) -> ForStatement:
        """Parse for statement: for (init; condition; update) statement"""
        line = self.current_token().line - 1  # Line of 'for' keyword
        
        self.consume('SYMBOL', '(', "Expected '(' after 'for'")
        
        # Initialize clause
        init = None
        if not self.check('SYMBOL', ';'):
            init = self.expression()
        self.consume('SYMBOL', ';', "Expected ';' after for-loop initialization")
        
        # Condition clause
        condition = None
        if not self.check('SYMBOL', ';'):
            condition = self.expression()
        self.consume('SYMBOL', ';', "Expected ';' after for-loop condition")
        
        # Update clause
        update = None
        if not self.check('SYMBOL', ')'):
            update = self.expression()
        self.consume('SYMBOL', ')', "Expected ')' after for-loop clauses")
        
        # Body
        body = self.statement()
        
        return ForStatement(init, condition, update, body, line)
    
    def switch_statement(self) -> SwitchStatement:
        """Parse switch statement: switch (expression) { case_stmt* default_stmt? }"""
        line = self.current_token().line - 1  # Line of 'switch' keyword
        
        self.consume('SYMBOL', '(', "Expected '(' after 'switch'")
        expression = self.expression()
        self.consume('SYMBOL', ')', "Expected ')' after switch expression")
        
        self.consume('SYMBOL', '{', "Expected '{' after switch")
        
        cases = []
        default_case = None
        
        while not self.check('SYMBOL', '}') and not self.is_at_end():
            if self.match('KEYWORD', 'case'):
                case_line = self.current_token().line - 1
                value = self.expression()
                self.consume('SYMBOL', ':', "Expected ':' after case value")
                
                statements = []
                while not self.check('KEYWORD', 'case') and not self.check('KEYWORD', 'default') and \
                      not self.check('SYMBOL', '}') and not self.is_at_end():
                    statements.append(self.statement())
                
                cases.append(CaseStatement(value, statements, case_line))
            
            elif self.match('KEYWORD', 'default'):
                default_line = self.current_token().line - 1
                self.consume('SYMBOL', ':', "Expected ':' after 'default'")
                
                statements = []
                while not self.check('KEYWORD', 'case') and not self.check('KEYWORD', 'default') and \
                      not self.check('SYMBOL', '}') and not self.is_at_end():
                    statements.append(self.statement())
                
                default_case = DefaultStatement(statements, default_line)
            
            else:
                self.error("Expected 'case' or 'default' in switch statement", self.current_token().line)
                self.synchronize()
        
        self.consume('SYMBOL', '}', "Expected '}' after switch statement")
        
        return SwitchStatement(expression, cases, default_case, line)

    def expression_statement(self) -> ExpressionStatement:
        """Parse an expression statement"""
        line = self.current_token().line
        
        # Handle empty statements (just a semicolon)
        if self.check('SYMBOL', ';'):
            self.advance()
            return ExpressionStatement(None, line)
        
        # Parse the expression
        expr = self.expression()
        self.consume('SYMBOL', ';', "Expected ';' after expression")
        return ExpressionStatement(expr, line)

    def parse_binary_expression(self, parse_operand_func, operators):
        expr = parse_operand_func()
        while self.check('SYMBOL') and self.current_token().value in operators:
            op = self.current_token().value
            line = self.current_token().line
            self.advance()
            right = parse_operand_func()
            expr = BinaryExpression(expr, op, right, line)
        return expr
    
    def expression(self) -> Expression:
        """Parse an expression with binary operator support"""
        return self.parse_binary_expression(self.term, ['+', '-', '*', '/'])  # You can extend operators here
    
    def term(self) -> Expression:
        if self.check('NUMBER'):
            value = self.current_token().value
            line = self.current_token().line
            self.advance()
            return LiteralExpression(value, 'number', line)

        elif self.check('STRING'):
            value = self.current_token().value
            line = self.current_token().line
            self.advance()
            return LiteralExpression(value, 'string', line)

        elif self.check('IDENTIFIER') or self.check('STANDARD_IDENTIFIER'):
            name_token = self.current_token()
            name = name_token.value
            line = name_token.line
            self.advance()

            # Function call: IDENTIFIER '(' ...
            if self.check('SYMBOL', '('):
                self.advance()
                arguments = []
                if not self.check('SYMBOL', ')'):
                    arguments.append(self.expression())
                    while self.match('SYMBOL', ','):
                        arguments.append(self.expression())
                self.consume('SYMBOL', ')', "Expected ')' after arguments")
                return FunctionCallExpression(IdentifierExpression(name, line), arguments, line)
            else:
                return IdentifierExpression(name, line)

        elif self.check('SYMBOL', '('):
            self.advance()
            expr = self.expression()
            self.consume('SYMBOL', ')', "Expected ')' after expression")
            return expr

        else:
            raise self.error(self.current_token(), "Unexpected token in expression")

    def assignment(self) -> Expression:
        """Parse assignment: logical_or (assignment_op assignment)?"""
        expr = self.logical_or()
        
        # Check if this is an assignment
        if self.check('OPERATOR', '=') or self.check('OPERATOR', '+=') or \
           self.check('OPERATOR', '-=') or self.check('OPERATOR', '*=') or \
           self.check('OPERATOR', '/=') or self.check('OPERATOR', '%='):
            
            # Make sure left side is a valid target
            if not isinstance(expr, (IdentifierExpression, ArrayAccessExpression)):
                self.error("Invalid assignment target", self.current_token().line)
            
            operator = self.current_token().value
            line = self.current_token().line
            self.advance()
            
            right = self.assignment()  # Right-associative
            
            return AssignmentExpression(expr, operator, right, line)
        
        return expr
    
    def logical_or(self) -> Expression:
        """Parse logical OR: logical_and ('||' logical_and)*"""
        expr = self.logical_and()
        
        while self.match('OPERATOR', '||'):
            line = self.current_token().line - 1
            right = self.logical_and()
            expr = BinaryExpression(expr, '||', right, line)
        
        return expr
    
    def logical_and(self) -> Expression:
        """Parse logical AND: equality ('&&' equality)*"""
        expr = self.equality()
        
        while self.match('OPERATOR', '&&'):
            line = self.current_token().line - 1
            right = self.equality()
            expr = BinaryExpression(expr, '&&', right, line)
        
        return expr
    
    def equality(self) -> Expression:
        """Parse equality: relational ('==' | '!=' relational)*"""
        expr = self.relational()
        
        while self.match('OPERATOR', '==') or self.match('OPERATOR', '!='):
            operator = self.tokens[self.current - 1].value
            line = self.tokens[self.current - 1].line
            right = self.relational()
            expr = BinaryExpression(expr, operator, right, line)
        
        return expr
    
    def relational(self) -> Expression:
        """Parse relational: additive ('<' | '<=' | '>' | '>=' additive)*"""
        expr = self.additive()
        
        while self.match('OPERATOR', '<') or self.match('OPERATOR', '<=') or \
              self.match('OPERATOR', '>') or self.match('OPERATOR', '>='):
            operator = self.tokens[self.current - 1].value
            line = self.tokens[self.current - 1].line
            right = self.additive()
            expr = BinaryExpression(expr, operator, right, line)
        
        return expr
    
    def additive(self) -> Expression:
        """Parse additive: multiplicative ('+' | '-' multiplicative)*"""
        expr = self.multiplicative()
        
        while self.match('OPERATOR', '+') or self.match('OPERATOR', '-'):
            operator = self.tokens[self.current - 1].value
            line = self.tokens[self.current - 1].line
            right = self.multiplicative()
            expr = BinaryExpression(expr, operator, right, line)
        
        return expr
    
    def multiplicative(self) -> Expression:
        """Parse multiplicative: unary ('*' | '/' | '%' unary)*"""
        expr = self.unary()
        
        while self.match('OPERATOR', '*') or self.match('OPERATOR', '/') or self.match('OPERATOR', '%'):
            operator = self.tokens[self.current - 1].value
            line = self.tokens[self.current - 1].line
            right = self.unary()
            expr = BinaryExpression(expr, operator, right, line)
        
        return expr
    
    def unary(self) -> Expression:
        """Parse unary: ('!' | '-' | '+' | '++' | '--') unary | postfix"""
        if self.match('OPERATOR', '!') or self.match('OPERATOR', '-') or \
           self.match('OPERATOR', '+') or self.match('OPERATOR', '++') or \
           self.match('OPERATOR', '--'):
            operator = self.tokens[self.current - 1].value
            line = self.tokens[self.current - 1].line
            right = self.unary()
            return UnaryExpression(operator, right, line)
        
        return self.postfix()
    
    def postfix(self) -> Expression:
        """Parse postfix: primary ('++' | '--' | '[' expression ']' | '(' arguments ')')*"""
        expr = self.primary()
        
        while True:
            if self.match('OPERATOR', '++') or self.match('OPERATOR', '--'):
                operator = self.tokens[self.current - 1].value
                line = self.tokens[self.current - 1].line
                expr = UnaryExpression(operator + '_post', expr, line)  # Mark as postfix
            
            elif self.match('SYMBOL', '['):
                line = self.current_token().line - 1
                index = self.expression()
                self.consume('SYMBOL', ']', "Expected ']' after array index")
                expr = ArrayAccessExpression(expr, index, line)
            
            elif self.match('SYMBOL', '('):
                line = self.current_token().line - 1
                arguments = []
                
                # Parse arguments if any
                if not self.check('SYMBOL', ')'):
                    arguments.append(self.expression())
                    
                    while self.match('SYMBOL', ','):
                        arguments.append(self.expression())
                
                self.consume('SYMBOL', ')', "Expected ')' after function arguments")
                expr = FunctionCallExpression(expr, arguments, line)
            
            else:
                break
        
        return expr

# for Expression
    def primary(self) -> Expression:
        # Parse primary: NUMBER | STRING | CHAR | IDENTIFIER | FUNCTION_CALL | '(' expression ')'
        if self.match('NUMBER'):
            return LiteralExpression(self.tokens[self.current - 1].value, 'number', 
                                self.tokens[self.current - 1].line)
        
        elif self.match('STRING'):
            return LiteralExpression(self.tokens[self.current - 1].value, 'string', 
                                self.tokens[self.current - 1].line)
        
        elif self.match('CHAR_LITERAL'):
            return LiteralExpression(self.tokens[self.current - 1].value, 'char', 
                                self.tokens[self.current - 1].line)
        
        elif self.check('FUNCTION_CALL'):
            return self.function_call()
        
        elif self.match('IDENTIFIER') or self.match('STANDARD_IDENTIFIER'):
            return IdentifierExpression(self.tokens[self.current - 1].value, 
                                    self.tokens[self.current - 1].line)
        
        elif self.match('SYMBOL', '('):
            expr = self.expression()
            self.consume('SYMBOL', ')', "Expected ')' after expression")
            return expr
        
        self.error("Expected expression", self.current_token().line if self.current_token() else -1)
        return None

# AST Printer

# Add this class after all the existing code in parser.py

class ASTPrinter:
    def __init__(self):
        self.indent = 0

    def print_ast(self, node, indent=0) -> str:
        lines = []

        def _print(node, indent):
            if node is None:
                lines.append("  " * indent + "None")
                return

            lines.append("  " * indent + str(node))

            if isinstance(node, Program):
                for decl in node.declarations:
                    _print(decl, indent + 1)

            elif isinstance(node, FunctionDeclaration):
                for param in node.params:
                    _print(param, indent + 1)
                if node.body:
                    _print(node.body, indent + 1)

            elif isinstance(node, CompoundStatement):
                for decl in node.local_declarations:
                    _print(decl, indent + 1)
                for stmt in node.statements:
                    _print(stmt, indent + 1)

            elif isinstance(node, IfStatement):
                _print(node.condition, indent + 1)
                _print(node.if_body, indent + 1)
                if node.else_body:
                    _print(node.else_body, indent + 1)

            elif isinstance(node, WhileStatement):
                _print(node.condition, indent + 1)
                _print(node.body, indent + 1)

            elif isinstance(node, DoWhileStatement):
                _print(node.body, indent + 1)
                _print(node.condition, indent + 1)

            elif isinstance(node, ForStatement):
                if node.init:
                    _print(node.init, indent + 1)
                if node.condition:
                    _print(node.condition, indent + 1)
                if node.update:
                    _print(node.update, indent + 1)
                _print(node.body, indent + 1)

            elif isinstance(node, SwitchStatement):
                _print(node.expression, indent + 1)
                for case in node.cases:
                    _print(case, indent + 1)
                if node.default_case:
                    _print(node.default_case, indent + 1)

            elif isinstance(node, CaseStatement):
                _print(node.value, indent + 1)
                for stmt in node.statements:
                    _print(stmt, indent + 1)

            elif isinstance(node, DefaultStatement):
                for stmt in node.statements:
                    _print(stmt, indent + 1)

            elif isinstance(node, ReturnStatement):
                if node.expression:
                    _print(node.expression, indent + 1)

            elif isinstance(node, ExpressionStatement):
                if node.expression:
                    _print(node.expression, indent + 1)

            elif isinstance(node, BinaryExpression):
                _print(node.left, indent + 1)
                _print(node.right, indent + 1)

            elif isinstance(node, UnaryExpression):
                _print(node.operand, indent + 1)

            elif isinstance(node, AssignmentExpression):
                _print(node.left, indent + 1)
                _print(node.right, indent + 1)

            elif isinstance(node, FunctionCallExpression):
                _print(node.function, indent + 1)
                for arg in node.arguments:
                    _print(arg, indent + 1)

            elif isinstance(node, ArrayAccessExpression):
                _print(node.array, indent + 1)
                _print(node.index, indent + 1)

            elif isinstance(node, VarDeclaration):
                result += "  " * indent + f"VarDeclaration: {node.type_spec} {node.var_name}"
                if node.array_size:
                    result += f"[{node.array_size}]"
                if node.initializer:
                    result += f" = {self.print_ast(node.initializer, indent + 1)}"  # Print the initializer
                result += "\n"

        _print(node, indent)
        return "\n".join(lines)

