"""Week 3 exercise: a framework-free tool boundary.

Run: python examples/manual_agent.py
"""

import json

from support_agent.services.tools import ToolError, query_order, safe_calculate

TOOLS = {
    "calculator": lambda args: safe_calculate(args["expression"]),
    "query_order": lambda args: query_order(args["order_id"]).__dict__,
}


def execute_tool_call(name: str, arguments_json: str):
    if name not in TOOLS:
        raise ToolError(f"未知工具：{name}")
    try:
        arguments = json.loads(arguments_json)
    except json.JSONDecodeError as exc:
        raise ToolError("工具参数不是合法 JSON") from exc
    return TOOLS[name](arguments)


if __name__ == "__main__":
    print(execute_tool_call("calculator", '{"expression": "(12 + 8) / 4"}'))
    print(execute_tool_call("query_order", '{"order_id": "A1001"}'))
