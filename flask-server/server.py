# server.py (No changes needed, already correct)
from flask import Flask, request, jsonify
from lexical import Lexical
from parser import Parser
from semantic import SemanticAnalyzer
from ast_utils import expression_to_str

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    source_code = data.get("code", "")

    try:
        # Lexical analysis
        lexer = Lexical(source_code)
        tokens, lexical_errors = lexer.get_tokens()

        # Convert token objects to dicts for JSON serialization
        tokens_list = [{
            "type": token.type,
            "value": token.value,
            "line": token.line
        } for token in tokens]

        # Parsing step
        parser = Parser(tokens)
        ast = parser.parse() # This might need error handling for parser errors

        semantic_output = []
        ast_str = ""
        parser_errors = parser.errors # Assuming your Parser class has an 'errors' attribute

        if ast:
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            semantic_output = analyzer.errors
            ast_str = expression_to_str(ast)

        # Return all analysis results as JSON
        return jsonify({
            "tokens": tokens_list,
            "lexicalErrors": lexical_errors,
            "parserErrors": parser_errors, # Added parser errors
            "astString": ast_str,
            "semanticOutput": semantic_output
        })

    except Exception as e:
        # Return error info on failure
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)