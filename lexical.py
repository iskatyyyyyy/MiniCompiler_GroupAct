# Tokens class
class Tokens:
    def __init__(self, token_type, token_value, line):
        self.type = token_type
        self.value = token_value
        self.line = line

    def __repr__(self):
        return f'{self.value:<15} {self.type:<15} {self.line}'

class Lexical:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.line = 1
        self.current_char = None
        self.advanceNextChar()
    def advanceNextChar(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
            if self.current_char == '\n':
                self.line += 1
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
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
        else:
            token_type = 'IDENTIFIER'

        return Tokens(token_type, result, line_num)

    def collect_number(self):
        result = ''
        line_num = self.line
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advanceNextChar()
        return Tokens('NUMBER', result, line_num)

    def get_tokens(self):
        tokens = []

        self.keywords = {
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
            'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'int',
            'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static',
            'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while'
        }

        self.control_flow = {'if', 'else', 'switch', 'case', 'for', 'while', 'do'}

        self.operators = {
            '++', '--', '+=', '-=', '*=', '/=', '%=', '==', '!=', '<=', '>=', '&&', '||',
            '+', '-', '*', '/', '%', '=', '<', '>', '!'
        }

        self.symbols = {';', ',', '(', ')', '{', '}', '[', ']'}

        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.collect_identifier_or_keyword())
                continue

            if self.current_char.isdigit():
                tokens.append(self.collect_number())
                continue

            two_chars = self.current_char
            next_char = self.text[self.pos + 1] if self.pos + 1 < len(self.text) else ''
            combined = two_chars + next_char

            if combined in self.operators:
                tokens.append(Tokens('OPERATOR', combined, self.line))
                self.advanceNextChar()
                self.advanceNextChar()
                continue

            if self.current_char in self.operators:
                tokens.append(Tokens('OPERATOR', self.current_char, self.line))
                self.advanceNextChar()
                continue

            if self.current_char in self.symbols:
                tokens.append(Tokens('SYMBOL', self.current_char, self.line))
                self.advanceNextChar()
                continue

            tokens.append(Tokens('UNKNOWN', self.current_char, self.line))
            self.advanceNextChar()

        return tokens

# Example usage
if __name__ == "__main__":
    print("Enter C code (press Enter twice to finish input):")
    user_input = ''
    while True:
        line = input()
        if line == '':
            break
        user_input += line + '\n'

    lexer = Lexical(user_input)
    tokens = lexer.get_tokens()

    print(f"\n{'TOKEN VALUE':<15} {'TOKEN TYPE':<15} LINE")
    print('-' * 45)
    for token in tokens:
        print(token)
