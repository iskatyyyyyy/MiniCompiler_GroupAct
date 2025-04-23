# parser.py

from ast_1 import ASTNode

class SyntaxError(Exception):
    def __init__(self, message, line, col):
        super().__init__(f"[Line {line}, Col {col}] SyntaxError: {message}")


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def current_token(self):
        return self.tokens[self.current] if self.current < len(self.tokens) else None

    def match(self, type_, value=None):
        token = self.current_token()
        if token and token.type == type_ and (value is None or token.value == value):
            self.current += 1
            return token
        expected = f"{type_}('{value}')" if value else type_
        actual = f"{token.type}('{token.value}')" if token else "EOF"
        line = token.line if token else 0
        raise SyntaxError(f"Expected {expected}, got {actual}", line, 0)

    def accept(self, type_, value=None):
        token = self.current_token()
        if token and token.type == type_ and (value is None or token.value == value):
            self.current += 1
            return token
        return None

    def parse(self):
        return self.parse_translation_unit()

    def parse_translation_unit(self):
        children = []
        while self.current_token():
            children.append(self.parse_external_declaration())
        return ASTNode("TranslationUnit", children=children)

    def parse_external_declaration(self):
        if self.peek_function_definition():
            return self.parse_function_definition()
        return self.parse_declaration()

    def peek_function_definition(self):
        pos = self.current
        if self.accept('KEYWORD') and self.accept('IDENTIFIER') and self.accept('SYMBOL', '('):
            self.current = pos
            return True
        self.current = pos
        return False

    def parse_declaration(self):
        type_token = self.match('KEYWORD')  # int, float, char, etc.
        declarators = []

        while True:
            # Parse pointer level (e.g., *, **, etc.)
            pointer_level = 0
            while self.accept('OPERATOR', '*'):
                pointer_level += 1

            id_token = self.match('IDENTIFIER')

            # Optional array size: [NUMBER]
            array_size = None
            if self.accept('SYMBOL', '['):
                size_token = self.match('NUMBER')
                self.match('SYMBOL', ']')
                array_size = size_token.value

            # Build AST for this declarator
            children = [
                ASTNode("Type", value=type_token.value, line=type_token.line),
            ]

            if pointer_level > 0:
                children.append(ASTNode("Pointer", value=pointer_level, line=id_token.line))

            children.append(ASTNode("Identifier", value=id_token.value, line=id_token.line))

            if array_size is not None:
                children.append(ASTNode("ArraySize", value=array_size, line=id_token.line))

            declarators.append(ASTNode("Declarator", children=children, line=id_token.line))

            if not self.accept('SYMBOL', ','):
                break

        self.match('SYMBOL', ';')
        return ASTNode("VariableDeclarationList", children=declarators, line=type_token.line)


    def parse_function_definition(self):
        type_token = self.match('KEYWORD')
        id_token = self.match('IDENTIFIER')
        self.match('SYMBOL', '(')
        params = self.parse_parameter_list()
        self.match('SYMBOL', ')')
        body = self.parse_compound_statement()

        return ASTNode("FunctionDefinition", value=id_token.value, line=type_token.line, children=[
            ASTNode("ReturnType", value=type_token.value),
            ASTNode("Parameters", children=params),
            body
        ])

    def parse_parameter_list(self):
        params = []
        if self.accept('KEYWORD'):  # single param or start of list
            self.current -= 1
            while True:
                type_token = self.match('KEYWORD')
                id_token = self.match('IDENTIFIER')
                params.append(ASTNode("Parameter", children=[
                    ASTNode("Type", value=type_token.value),
                    ASTNode("Identifier", value=id_token.value)
                ]))
                if not self.accept('SYMBOL', ','):
                    break
        return params

    def parse_compound_statement(self):
        self.match('SYMBOL', '{')
        stmts = []
        while not self.accept('SYMBOL', '}'):
            stmts.append(self.parse_statement())
        return ASTNode("CompoundStatement", children=stmts)

    def parse_statement(self):
        token = self.current_token()

        if token.type == 'KEYWORD':
            if token.value in {'int', 'float', 'char', 'void'}:
                return self.parse_declaration()
            elif token.value == 'return':
                return self.parse_return_statement()
            elif token.value == 'if':
                return self.parse_if_statement()
            elif token.value == 'while':
                return self.parse_while_statement()
            elif token.value == 'for':
                return self.parse_for_statement()
            elif token.value == 'break':
                return self.parse_break_statement()
            elif token.value == 'continue':
                return self.parse_continue_statement()

        if token.type == 'SYMBOL' and token.value == '{':
            return self.parse_compound_statement()

        return self.parse_expression_statement()


    def parse_expression_statement(self):
        expr = self.parse_expression()
        self.match('SYMBOL', ';')
        return ASTNode("ExpressionStatement", children=[expr])

    def parse_return_statement(self):
        token = self.match('KEYWORD', 'return')
        expr = self.parse_expression()
        self.match('SYMBOL', ';')
        return ASTNode("ReturnStatement", children=[expr], line=token.line)

    def parse_if_statement(self):
        token = self.match('KEYWORD', 'if')
        self.match('SYMBOL', '(')
        cond = self.parse_expression()
        self.match('SYMBOL', ')')
        then_stmt = self.parse_statement()
        else_stmt = None
        if self.accept('KEYWORD', 'else'):
            else_stmt = self.parse_statement()
        children = [cond, then_stmt]
        if else_stmt:
            children.append(else_stmt)
        return ASTNode("IfStatement", children=children, line=token.line)

    def parse_while_statement(self):
        token = self.match('KEYWORD', 'while')
        self.match('SYMBOL', '(')
        cond = self.parse_expression()
        self.match('SYMBOL', ')')
        body = self.parse_statement()
        return ASTNode("WhileStatement", children=[cond, body], line=token.line)

    def parse_for_statement(self):
        token = self.match('KEYWORD', 'for')
        self.match('SYMBOL', '(')
        init = self.parse_expression_statement()
        cond = self.parse_expression_statement()
        post = self.parse_expression()
        self.match('SYMBOL', ')')
        body = self.parse_statement()
        return ASTNode("ForStatement", children=[init, cond, post, body], line=token.line)

    def parse_break_statement(self):
        token = self.match('KEYWORD', 'break')
        self.match('SYMBOL', ';')
        return ASTNode("BreakStatement", line=token.line)

    def parse_continue_statement(self):
        token = self.match('KEYWORD', 'continue')
        self.match('SYMBOL', ';')
        return ASTNode("ContinueStatement", line=token.line)

    # --- Expression Parsing with Precedence ---
    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        node = self.parse_logical_or()
        if self.accept('OPERATOR', '='):
            rhs = self.parse_assignment()
            return ASTNode("Assign", children=[node, rhs])
        return node

    def parse_logical_or(self):
        node = self.parse_logical_and()
        while self.accept('OPERATOR', '||'):
            rhs = self.parse_logical_and()
            node = ASTNode("LogicalOr", children=[node, rhs])
        return node

    def parse_logical_and(self):
        node = self.parse_equality()
        while self.accept('OPERATOR', '&&'):
            rhs = self.parse_equality()
            node = ASTNode("LogicalAnd", children=[node, rhs])
        return node

    def parse_equality(self):
        node = self.parse_relational()
        while True:
            if self.accept('OPERATOR', '=='):
                rhs = self.parse_relational()
                node = ASTNode("Equal", children=[node, rhs])
            elif self.accept('OPERATOR', '!='):
                rhs = self.parse_relational()
                node = ASTNode("NotEqual", children=[node, rhs])
            else:
                break
        return node

    def parse_relational(self):
        node = self.parse_additive()
        while True:
            if self.accept('OPERATOR', '<'):
                rhs = self.parse_additive()
                node = ASTNode("Less", children=[node, rhs])
            elif self.accept('OPERATOR', '>'):
                rhs = self.parse_additive()
                node = ASTNode("Greater", children=[node, rhs])
            elif self.accept('OPERATOR', '<='):
                rhs = self.parse_additive()
                node = ASTNode("LessEqual", children=[node, rhs])
            elif self.accept('OPERATOR', '>='):
                rhs = self.parse_additive()
                node = ASTNode("GreaterEqual", children=[node, rhs])
            else:
                break
        return node

    def parse_additive(self):
        node = self.parse_term()
        while True:
            if self.accept('OPERATOR', '+'):
                rhs = self.parse_term()
                node = ASTNode("Add", children=[node, rhs])
            elif self.accept('OPERATOR', '-'):
                rhs = self.parse_term()
                node = ASTNode("Subtract", children=[node, rhs])
            else:
                break
        return node

    def parse_term(self):
        node = self.parse_factor()
        while True:
            if self.accept('OPERATOR', '*'):
                rhs = self.parse_factor()
                node = ASTNode("Multiply", children=[node, rhs])
            elif self.accept('OPERATOR', '/'):
                rhs = self.parse_factor()
                node = ASTNode("Divide", children=[node, rhs])
            elif self.accept('OPERATOR', '%'):
                rhs = self.parse_factor()
                node = ASTNode("Modulo", children=[node, rhs])
            else:
                break
        return node

    def parse_factor(self):
        token = self.current_token()

        if token.type == 'NUMBER':
            self.current += 1
            return ASTNode("Number", value=token.value, line=token.line)

        if token.type == 'IDENTIFIER':
            self.current += 1
            return ASTNode("Identifier", value=token.value, line=token.line)

        if token.type == 'SYMBOL' and token.value == '(':
            self.current += 1
            expr = self.parse_expression()
            self.match('SYMBOL', ')')
            return expr

        raise SyntaxError(f"Unexpected token: {token.value}", token.line, 0)
