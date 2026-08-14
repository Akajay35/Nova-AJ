from __future__ import annotations
import ast
import operator as op
import re
from core.base_skill import BaseSkill

OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod}
UNARY = {ast.UAdd: op.pos, ast.USub: op.neg}


def safe_eval(expression: str) -> float:
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression): return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)): return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 20: raise ValueError("power too large")
            return OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY: return UNARY[type(node.op)](visit(node.operand))
        raise ValueError("unsupported expression")

    value = visit(tree)
    if abs(value) > 10**15: raise ValueError("result too large")
    return value


class CalculatorSkill(BaseSkill):
    name = "calculator"
    description = "Safely evaluates basic arithmetic expressions."

    def matches(self, query: str) -> bool:
        q = query.lower().strip()
        return q.startswith(("calculate ", "what is ", "compute ")) and bool(re.search(r"[0-9][0-9+*/().%\- ]*", q))

    def handle(self, query: str, context: dict) -> str:
        expression = re.sub(r"^(calculate|compute|what is)\s+", "", query.strip(), flags=re.I)
        try:
            result = safe_eval(expression)
            return f"The answer is {result:g}."
        except Exception:
            return "I can calculate basic arithmetic, but I couldn't safely evaluate that expression."
