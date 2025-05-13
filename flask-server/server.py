from flask import Flask, request, jsonify
from lexical import Lexical
from parser import Parser, ASTPrinter
from semantic import Semantic

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze_code():
    data = request.get_json()
    user_code = data.get("code", "")
    
    if not user_code:
        return jsonify({"error": "No code provided"}), 400

    user_code_lines = user_code.splitlines()

    # Lexical Analysis
    lexer = Lexical(user_code)
    tokens, lexer_errors = lexer.get_tokens()

    # Parser Analysis
    parser = Parser(tokens)
    ast, parser_errors = parser.parse()

    ast_output = ""
    if ast:
        printer = ASTPrinter()
        ast_output = printer.print_ast(ast)

    # Semantic Analysis (output is printed, you might want to capture it differently)
    semantic_output = Semantic.analyze_code(user_code_lines)

    # Count errors
    total_errors = len(lexer_errors) + len(parser_errors) + len(semantic_output)

    return jsonify({
        "tokens": [str(t) for t in tokens],
        "lexerErrors": lexer_errors,
        "parserErrors": parser_errors,
        "ast": ast_output,
        "semanticOutput": semantic_output,  # Change if Semantic returns structured data
        "success": total_errors == 0
    })

if __name__ == "__main__":
    app.run(debug=True)
