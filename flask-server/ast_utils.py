from ast_nodes import *
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
    elif t == 'FunctionCallNode':
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
    elif t == 'VariableDeclaration':
        if expr.initializer:
            init_str = expression_to_str(expr.initializer)
            return f"{expr.var_type} {expr.name} = {init_str}"
        else:
            return f"{expr.var_type} {expr.name}"
    elif t == 'IfStatement':
        condition_str = expression_to_str(expr.condition)
        then_branch_str = expression_to_str(expr.then_branch)
        else_branch_str = expression_to_str(expr.else_branch) if expr.else_branch else ""
        return f"if ({condition_str}) {{ {then_branch_str} }} else {{ {else_branch_str} }}"
    elif t == 'WhileStatement':
        condition_str = expression_to_str(expr.condition)
        body_str = expression_to_str(expr.body)
        return f"while ({condition_str}) {{ {body_str} }}"
    elif t == 'ForStatement':
        init_str = expression_to_str(expr.init)
        condition_str = expression_to_str(expr.condition)
        increment_str = expression_to_str(expr.increment)
        body_str = expression_to_str(expr.body)
        return f"for ({init_str}; {condition_str}; {increment_str}) {{ {body_str} }}"
    elif t == 'SwitchStatement':
        expression_str = expression_to_str(expr.expression)
        cases_str = ' '.join(expression_to_str(case) for case in expr.cases)
        default_str = expression_to_str(expr.default) if expr.default else ""
        return f"switch ({expression_str}) {{ {cases_str} {default_str} }}"
    elif t == 'SwitchCase':
        if expr.value is None:
            # default case
            body_str = ' '.join(expression_to_str(stmt) for stmt in expr.body)
            return f"default: {{ {body_str} }}"
        else:
            case_str = expression_to_str(expr.value)
            body_str = ' '.join(expression_to_str(stmt) for stmt in expr.body)
            return f"case {case_str}: {{ {body_str} }}"
    elif t == 'BreakStatement':
        return "break;"
    elif t == 'ContinueStatement':
        return "continue;"
    elif t == 'ReturnStatement':
        return f"return {expression_to_str(expr.value)};"
    elif t == 'ExpressionStatement':
        return f"{expression_to_str(expr.expression)};"
    elif t == 'Block':
        statements_str = ' '.join(expression_to_str(stmt) for stmt in expr.statements)
        return f"{{ {statements_str} }}"
    return f"<UnknownExpr:{t}>"


def pretty_print(node, indent=0):
    indent_str = '  ' * indent

    if node is None:
        print(f"{indent_str}None")
        return

    #Root Program Node
    if isinstance(node, Program):
        print(f"{indent_str}Program:")
        for stmt in node.statements:
            pretty_print(stmt, indent + 1)
        return

    # Handle lists of nodes (used in things like BlockStatement, Switch cases, etc.)
    if isinstance(node, (list, tuple)):
        for stmt in node:
            pretty_print(stmt, indent)
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

    elif t == 'SwitchStatement':
        print(f"{indent_str}SwitchStatement:")
        print(f"{indent_str}  Expression:")
        pretty_print(node.expression, indent + 2)
        print(f"{indent_str}  Cases:")
        for case in node.cases:
            pretty_print(case, indent + 2)
        if node.default:
            print(f"{indent_str}  Default:")
            pretty_print(node.default, indent + 2)

    elif t == 'SwitchCase':
        if node.value is None:
            print(f"{indent_str}DefaultCase:")
        else:
            print(f"{indent_str}Case: {expression_to_str(node.value)}")
        
        # Check if node.body is a Block, then iterate its statements, else iterate directly
        if type(node.body).__name__ == 'Block':
            for stmt in node.body.statements:
                pretty_print(stmt, indent + 2)
        else:
            for stmt in node.body:
                pretty_print(stmt, indent + 2)


    elif t == 'BreakStatement':
        print(f"{indent_str}BreakStatement")

    elif t == 'ContinueStatement':
        print(f"{indent_str}ContinueStatement")

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