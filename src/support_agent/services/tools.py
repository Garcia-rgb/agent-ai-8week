import ast
import operator
import re
from dataclasses import dataclass


class ToolError(ValueError):
    pass


_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_calculate(expression: str) -> float:
    """Evaluate arithmetic only; names, calls and attribute access are rejected."""
    if len(expression) > 100:
        raise ToolError("表达式过长")

    def evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
            left, right = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ToolError("指数过大")
            return _OPERATORS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](evaluate(node.operand))
        raise ToolError("表达式包含不允许的内容")

    try:
        result = evaluate(ast.parse(expression, mode="eval"))
    except (SyntaxError, ZeroDivisionError, OverflowError) as exc:
        raise ToolError("无法计算该表达式") from exc
    if abs(result) > 1e100:
        raise ToolError("计算结果过大")
    return result


@dataclass(frozen=True)
class Order:
    id: str
    status: str
    amount: float
    refundable: bool


MOCK_ORDERS = {
    "A1001": Order("A1001", "已发货", 199.0, True),
    "A1002": Order("A1002", "已退款", 89.0, False),
    "A1003": Order("A1003", "待支付", 399.0, False),
}


def find_order_id(text: str) -> str | None:
    match = re.search(r"\bA\d{4,10}\b", text.upper())
    return match.group(0) if match else None


def query_order(order_id: str) -> Order:
    try:
        return MOCK_ORDERS[order_id.upper()]
    except KeyError as exc:
        raise ToolError(f"未找到订单 {order_id}") from exc
