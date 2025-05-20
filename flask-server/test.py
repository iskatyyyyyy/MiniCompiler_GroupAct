from lexical import Lexical  # Your lexer
from parser import Parser  # Your parser
from ast_utils import pretty_print  # Import the pretty_print function

source_code = """
int add(int a, int b) {
    return a + b;
}

int main() {
    int x = 10;
    if (x > 5) {
        x = x - 1;
    } else {
        x = x + 1;
    }

    for (int i = 0; i < 3; i++) {
        int y = i * 2;
    }

    while (x < 20) {
        x++;
    }

    switch (x) {
        case 5:
            x += 1;
            break;
        case 10:
            x += 2;
            break;
        default:
            x = 0;
    }

    return 0;
}
"""

print("=== LEXER OUTPUT ===")
lexer = Lexical(source_code)
tokens, lexer_errors = lexer.get_tokens()

for t in tokens:
    print(f"{t.type:<10} {t.value:<10} (line {t.line})")

if lexer_errors:
    print("\n=== LEXER ERRORS ===")
    for err in lexer_errors:
        print("Lexer error:", err)

print("\n=== PARSER ERRORS ===")
parser = Parser(tokens)
ast = parser.parse()


print("\n=== AST ===")
pretty_print(ast)
