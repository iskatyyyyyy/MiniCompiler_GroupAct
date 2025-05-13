from lexical import Lexical
from parser import Parser, ASTPrinter

def main():
    print("C Mini-Compiler")
    print("===============")
    print("Enter C code (press Enter twice to finish input):")
    
    user_input = ''
    while True:
        line = input()
        if line == '':
            break
        user_input += line + '\n'
    
    # Step 1: Lexical Analysis
    print("\n=== LEXICAL ANALYSIS ===")
    lexer = Lexical(user_input)
    tokens, lexer_errors = lexer.get_tokens()
    
    print(f"\n{'TOKEN VALUE':<30} {'TOKEN TYPE':<20} LINE")
    print('-' * 70)
    for token in tokens:
        print(token)
    
    # Display lexer error messages
    if lexer_errors:
        print("\nLexer Error Messages:")
        for error in lexer_errors:
            print(f"  {error}")
    
    # Step 2: Parsing
    print("\n=== PARSER ANALYSIS ===")
    parser = Parser(tokens)
    ast, parser_errors = parser.parse()
    
    # Print AST
    print("\nAbstract Syntax Tree:")
    print("====================")
    if ast:
        printer = ASTPrinter()
        print(printer.print_ast(ast))
    else:
        print("No AST generated.")
    
    # Display parser error messages
    if parser_errors:
        print("\nParser Error Messages:")
        print("====================")
        for error in parser_errors:
            print(f"  {error}")
    
    # Step 3: Compiler Status
    total_errors = len(lexer_errors) + len(parser_errors)
    if total_errors > 0:
        print(f"\nCompilation failed with {total_errors} error(s).")
    else:
        print("\nCompilation successful!")

if __name__ == "__main__":
    main()
