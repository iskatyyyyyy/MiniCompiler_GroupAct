import difflib

class Tokens:
    def __init__(self, token_type, token_value, line):
        self.type = token_type
        self.value = token_value
        self.line = line

    def __repr__(self):
        return f'{self.value:<30} {self.type:<20} {self.line}'

class Lexical:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.line = 1
        self.current_char = None
        self.errors = []
        self.advanceNextChar()

    def advanceNextChar(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
            if self.current_char == '\n':
                self.line += 1
        else:
            self.current_char = None

    def peek(self):
        return self.text[self.pos + 1] if self.pos + 1 < len(self.text) else ''

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advanceNextChar()

    def skip_comment(self):
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char is not None and self.current_char != '\n':
                self.advanceNextChar()
        elif self.current_char == '/' and self.peek() == '*':
            self.advanceNextChar()
            self.advanceNextChar()
            while self.current_char is not None:
                if self.current_char == '*' and self.peek() == '/':
                    self.advanceNextChar()
                    self.advanceNextChar()
                    break
                self.advanceNextChar()

    def collect_identifier_or_keyword(self):
        result = ''
        line_num = self.line

        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advanceNextChar()

        if result in self.keywords:
            token_type = 'KEYWORD'
        elif result in self.control_flow:
            token_type = 'CONTROL_FLOW'
        elif result in self.standard_identifiers:
            token_type = 'STANDARD_IDENTIFIER'
        else:
            possible_syntax = self.keywords.union(self.standard_identifiers, self.control_flow)
            close = difflib.get_close_matches(result, possible_syntax, n=1, cutoff=0.75)
            if close:
                token_type = 'ERROR'
            else:
                token_type = 'IDENTIFIER'

        return Tokens(token_type, result, line_num)

    def collect_number(self):
        result = ''
        line_num = self.line
        dot_count = 0

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            result += self.current_char
            self.advanceNextChar()

        return Tokens('NUMBER', result, line_num)

    def collect_string(self):
        result = ''
        line_num = self.line
        self.advanceNextChar()

        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\' and self.peek() == '"':
                result += '"'
                self.advanceNextChar()
            else:
                result += self.current_char
            self.advanceNextChar()

        self.advanceNextChar()
        return Tokens('STRING', result, line_num)

    def collect_char(self):
        result = ''
        line_num = self.line
        self.advanceNextChar()

        if self.current_char == '\\':
            result += self.current_char
            self.advanceNextChar()
            if self.current_char is not None:
                result += self.current_char
                self.advanceNextChar()
        elif self.current_char is not None:
            result += self.current_char
            self.advanceNextChar()

        if self.current_char == "'":
            self.advanceNextChar()
        else:
            return Tokens('ERROR', result, line_num)

        return Tokens('CHAR_LITERAL', result, line_num)

    def collect_preprocessor_directive(self):
        result = '#'
        line_num = self.line
        self.advanceNextChar()

        while self.current_char is not None and self.current_char != '\n':
            result += self.current_char
            self.advanceNextChar()

        return Tokens('PREPROCESSOR_DIRECTIVE', result.strip(), line_num)

    def get_tokens(self):
        tokens = []
        errors = []

        self.keywords = {
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
            'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'int',
            'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static',
            'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while'
        }

        self.control_flow = {'if', 'else', 'switch', 'case', 'for', 'while', 'do'}

        self.standard_identifiers = {
            'main', 'printf', 'scanf', 'puts', 'gets', 'malloc', 'calloc', 'free', 'exit',
            'strlen', 'strcpy', 'strncpy', 'strcmp', 'strcat', 'fopen', 'fclose', 'fread',
            'fwrite', 'fseek', 'ftell', 'rewind', 'feof', 'fgetc', 'fputc', 'fgets', 'fputs',
            'getchar', 'putchar', 'perror', 'atoi', 'atof', 'atol', 'toupper', 'tolower'
        }

        self.operators = {
            '++', '--', '+=', '-=', '*=', '/=', '%=', '==', '!=', '<=', '>=', '&&', '||',
            '+', '-', '*', '/', '%', '=', '<', '>', '!', '&'
        }

        self.symbols = {';', ',', '(', ')', '{', '}', '[', ']', ':'}

        prev_token = None

        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/' and (self.peek() == '/' or self.peek() == '*'):
                self.skip_comment()
                continue

            if self.current_char == '#':
                token = self.collect_preprocessor_directive()
                tokens.append(token)
                prev_token = token
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                token = self.collect_identifier_or_keyword()

                if token.type == 'ERROR':
                    errors.append(f"Error: '{token.value}' is not a valid keyword or identifier (possible typo?).")
                else:
                    # If the previous token was a known data type, treat this as variable name
                    if prev_token and prev_token.type == 'KEYWORD' and prev_token.value in self.keywords:
                        token.type = 'IDENTIFIER'

                tokens.append(token)
                prev_token = token
                continue

            if self.current_char.isdigit():
                token = self.collect_number()
                tokens.append(token)
                prev_token = token
                continue

            if self.current_char == '"':
                token = self.collect_string()
                tokens.append(token)
                prev_token = token
                continue

            if self.current_char == "'":
                token = self.collect_char()
                tokens.append(token)
                prev_token = token
                continue

            two_char = self.current_char + self.peek()
            if two_char in self.operators:
                token = Tokens('OPERATOR', two_char, self.line)
                tokens.append(token)
                self.advanceNextChar()
                self.advanceNextChar()
                prev_token = token
                continue

            if self.current_char in self.operators:
                token = Tokens('OPERATOR', self.current_char, self.line)
                tokens.append(token)
                self.advanceNextChar()
                prev_token = token
                continue

            if self.current_char in self.symbols:
                token = Tokens('SYMBOL', self.current_char, self.line)
                tokens.append(token)
                self.advanceNextChar()
                prev_token = token
                continue

            token = Tokens('ERROR', self.current_char, self.line)
            tokens.append(token)
            errors.append(f"Error: Invalid token '{self.current_char}' found at line {self.line}.")
            self.advanceNextChar()
            prev_token = token

        return tokens, errors
