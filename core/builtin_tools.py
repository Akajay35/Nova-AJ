from __future__ import annotations

import ast
import operator
from datetime import datetime, timezone
from typing import Any


_ALLOWED_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def current_time() -> str:
    """Return a compact UTC timestamp."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _calculate_node(node: ast.AST) -> float | int:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_calculate_node(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINARY:
        left = _calculate_node(node.left)
        right = _calculate_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent is too large")
        return _ALLOWED_BINARY[type(node.op)](left, right)
    raise ValueError("Only basic arithmetic is allowed")


def calculate(expression: str) -> str:
    """Safely evaluate basic arithmetic without using eval()."""
    text = expression.strip()
    if not text:
        raise ValueError("Expression cannot be empty")
    if len(text) > 200:
        raise ValueError("Expression is too long")
    try:
        tree = ast.parse(text, mode="eval")
        value = _calculate_node(tree.body)
    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(f"Cannot calculate expression safely: {exc}") from exc
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def builtin_handlers() -> dict[str, Any]:
    return {"current_time": current_time, "calculate": calculate}
