
import json
import ast
import operator
from datetime import datetime, timezone

from app.llm import openai_client
from app.config import settings


# Safe calculator operations
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate(expression: str):
    """Safely evaluate basic mathematical expressions."""

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Exponent is too large")

            result = OPERATORS[type(node.op)](left, right)

            if abs(result) > 1e100:
                raise ValueError("Result is too large")

            return result

        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](evaluate(node.operand))

        raise ValueError("Invalid mathematical expression")

    try:
        tree = ast.parse(expression, mode="eval")
        result = evaluate(tree.body)
        return {"result": result}

    except (SyntaxError, TypeError, ValueError, ZeroDivisionError, OverflowError) as e:
        return {"error": str(e)}


def get_current_time():
    """Return current UTC date and time."""

    return {
        "current_time": datetime.now(timezone.utc).isoformat(),
        "timezone": "UTC"
    }


# Available tools
TOOLS = [
    {
        "type": "function",
       