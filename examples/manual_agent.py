"""不使用 Agent 框架，手写清晰的工具调用边界。

运行方式：python examples/manual_agent.py
"""

import json

from support_agent.services.tools import ToolError, query_device, safe_calculate

TOOLS = {
    "calculator": lambda args: safe_calculate(args["expression"]),
    "query_device": lambda args: query_device(args["sn"]).__dict__,
}


def execute_tool_call(name: str, arguments_json: str):
    """校验工具名称和 JSON 参数后，才允许执行已注册的工具。"""
    if name not in TOOLS:
        raise ToolError(f"未知工具：{name}")
    try:
        arguments = json.loads(arguments_json)
    except json.JSONDecodeError as exc:
        raise ToolError("工具参数不是合法 JSON") from exc
    return TOOLS[name](arguments)


if __name__ == "__main__":
    print(execute_tool_call("calculator", '{"expression": "(12 + 8) / 4"}'))
    print(execute_tool_call("query_device", '{"sn": "SN-2024-000123"}'))
