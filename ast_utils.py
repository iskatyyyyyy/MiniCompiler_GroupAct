def expression_to_str(expr):
    if expr is None:
        return "None"
    t = type(expr).__name__
    if t == 'Number':
        return str(expr.value)
    elif t == 'VariableNode':
        return expr.name
    elif t == 'BinaryOperation':
        return f"({expression_to_str(expr.left)} {expr.operator} {expression_to_str(expr.right)})"
    elif t == 'FunctionCallNode':  # fixed name
        args = ', '.join(expression_to_str(arg) for arg in expr.args)
        return f"{expr.name}({args})"
    elif t == 'UnaryOperation':
        if getattr(expr, 'postfix', False):
            return f"({expression_to_str(expr.operand)}{expr.operator})"
        else:
            return f"({expr.operator}{expression_to_str(expr.operand)})"
    elif t == 'StringNode':
        return f'"{expr.value}"'
    elif t == 'CharNode':
        return f"'{expr.value}'"
    elif t == 'AssignmentExpression':
        return f"{expression_to_str(expr.left)} {expr.operator} {expression_to_str(expr.right)}"
    return f"<UnknownExpr:{t}>"


def pretty_print(node, indent=0):
    indent_str = '  ' * indent

    if node is None:
        print(f"{indent_str}None")
        return

    # Handle list of nodes (e.g., Block statements, parameters)
    if isinstance(node, list):
        for item in node:
            pretty_print(item, indent)
        return

    t = type(node).__name__

    if t == 'FunctionDeclaration':
        print(f"{indent_str}FunctionDefinition: {node.name}")
        print(f"{indent_str}  ReturnType: {node.return_type}")
        print(f"{indent_str}  Parameters: [{', '.join(f'{ptype} {pname}' for ptype, pname in node.parameters)}]")
        print(f"{indent_str}  Body:")
        pretty_print(node.body, indent + 2)

    elif t == 'Block':
        print(f"{indent_str}Block {{")
        for stmt in node.statements:
            pretty_print(stmt, indent + 1)
        print(f"{indent_str}}}")

    elif t == 'VariableDeclaration':
        if node.initializer:
            init_str = expression_to_str(node.initializer)
            print(f"{indent_str}Declaration: {node.var_type} {node.name} = {init_str}")
        else:
            print(f"{indent_str}Declaration: {node.var_type} {node.name}")

    elif t == 'AssignmentExpression':
        print(f"{indent_str}AssignmentExpression:")
        print(f"{indent_str}  operator: {node.operator}")
        print(f"{indent_str}  left:")
        pretty_print(node.left, indent + 2)
        print(f"{indent_str}  right:")
        pretty_print(node.right, indent + 2)

    elif t == 'IfStatement':
        print(f"{indent_str}IfStatement:")
        print(f"{indent_str}  Condition:")
        pretty_print(node.condition, indent + 2)
        print(f"{indent_str}  ThenBlock:")
        pretty_print(node.then_branch, indent + 2)
        if node.else_branch:
            print(f"{indent_str}  ElseBlock:")
            pretty_print(node.else_branch, indent + 2)

    elif t == 'WhileStatement':
        print(f"{indent_str}WhileStatement:")
        print(f"{indent_str}  Condition:")
        pretty_print(node.condition, indent + 2)
        print(f"{indent_str}  Body:")
        pretty_print(node.body, indent + 2)

    elif t == 'ForStatement':
        print(f"{indent_str}ForStatement:")
        print(f"{indent_str}  Init:")
        pretty_print(node.init, indent + 2)
        print(f"{indent_str}  Condition:")
        pretty_print(node.condition, indent + 2)
        print(f"{indent_str}  Increment:")
        pretty_print(node.increment, indent + 2)
        print(f"{indent_str}  Body:")
        pretty_print(node.body, indent + 2)

    elif t == 'ReturnStatement':
        print(f"{indent_str}ReturnStatement:")
        pretty_print(node.value, indent + 1)

    elif t == 'ExpressionStatement':
        print(f"{indent_str}ExpressionStatement:")
        pretty_print(node.expression, indent + 1)

    elif t == 'BinaryOperation':
        print(f"{indent_str}BinaryExpression: {node.operator}")
        print(f"{indent_str}  Left:")
        pretty_print(node.left, indent + 2)
        print(f"{indent_str}  Right:")
        pretty_print(node.right, indent + 2)

    elif t == 'UnaryOperation':
        postfix = " (postfix)" if getattr(node, 'postfix', False) else ""
        print(f"{indent_str}UnaryOperation: {node.operator}{postfix}")
        print(f"{indent_str}  Operand:")
        pretty_print(node.operand, indent + 2)

    elif t == 'FunctionCallNode':
        print(f"{indent_str}FunctionCall: {node.name}(")
        for arg in node.args:
            pretty_print(arg, indent + 2)
        print(f"{indent_str})")

    elif t == 'VariableNode':
        print(f"{indent_str}Identifier({node.name})")

    elif t == 'Number':
        print(f"{indent_str}IntegerLiteral({node.value})")

    elif t == 'StringNode':
        print(f'{indent_str}StringLiteral("{node.value}")')

    elif t == 'CharNode':
        print(f"{indent_str}CharLiteral('{node.value}')")

    else:
        print(f"{indent_str}{t}: (unknown node)")
        if hasattr(node, '__dict__'):
            for attr, val in vars(node).items():
                print(f"{indent_str}  {attr}: {val}")
        else:
            print(f"{indent_str}  {node} (no attributes)")
