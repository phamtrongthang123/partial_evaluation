import ast

class IfElseEvaluator(ast.NodeTransformer):
    def __init__(self, flag_value):
        self.flag_value = flag_value

    def visit_If(self, node):
        if isinstance(node.test, ast.Compare):
            left = node.test.left
            op = node.test.ops[0]
            right = node.test.comparators[0]
            
            if (isinstance(left, ast.Name) and left.id == 'flag' and 
                isinstance(op, ast.Eq) and 
                isinstance(right, ast.Str) and right.s == self.flag_value):
                return node.body
            elif (isinstance(right, ast.Name) and right.id == 'flag' and 
                  isinstance(op, ast.Eq) and 
                  isinstance(left, ast.Str) and left.s == self.flag_value):
                return node.body
        
        return node.orelse

class SourceGenerator(ast.NodeVisitor):
    def __init__(self):
        self.code = []

    def visit_FunctionDef(self, node):
        self.code.append(f"def {node.name}():")
        self.generic_visit(node)

    def visit_Assign(self, node):
        target = node.targets[0].id if isinstance(node.targets[0], ast.Name) else '...'
        value = self.get_value(node.value)
        self.code.append(f"{target} = {value}")

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            func = node.value.func.id if isinstance(node.value.func, ast.Name) else '...'
            self.code.append(f"{func}()")
        else:
            self.code.append(self.get_value(node.value))

    def get_value(self, node):
        if isinstance(node, ast.Str):
            return f"'{node.s}'"
        elif isinstance(node, ast.Num):
            return str(node.n)
        elif isinstance(node, ast.Name):
            return node.id
        else:
            return '...'

    def to_source(self):
        return '\n'.join(self.code)

def partial_evaluate(code, flag_value):
    tree = ast.parse(code)
    transformer = IfElseEvaluator(flag_value)
    new_tree = transformer.visit(tree)
    generator = SourceGenerator()
    generator.visit(new_tree)
    return generator.to_source()

# Example usage
code = """
x = 2
if flag == 'a':
    do_something()
    z = 4
else:
    do_other_thing()
    r = 5
y = 3 
"""

result = partial_evaluate(code, 'a')
print(result)