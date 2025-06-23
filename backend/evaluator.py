def evaluate_expr(expr: str) -> str:
    try:
        return str(eval(expr))  # TODO: sanitize input!
    except:
        return "error"
