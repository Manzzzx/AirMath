import re

def evaluate_expr(expr: str) -> str:
    try:
        expr = expr.replace("x", "*").replace("X", "*").replace("÷", "/")

        if not re.fullmatch(r"[\d\+\-\*/\(\) ]+", expr):
            return "Invalid input"

        result = eval(expr)
        return str(result)
    except Exception:
        return "Error"
