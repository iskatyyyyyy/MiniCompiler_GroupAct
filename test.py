from lexical import Lexical  # Your lexer
from parser import Parser    # Your parser
from ast_utils import pretty_print  # Import the pretty_print function

source_code = """

int a = 5;
a += 3 * 2;
a--;

"""

lexer = Lexical(source_code)
tokens, errors = lexer.get_tokens()

for t in tokens:
    print(f"{t.type} {t.value} (line {t.line})")

if errors:
    for err in errors:
        print("Lexer error:", err)
else:
    parser = Parser(tokens)
    ast = parser.parse()
    pretty_print(ast)
