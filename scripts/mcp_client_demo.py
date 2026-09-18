"""演示：以 Client 身份连上本项目的 MCP Server。

运行方式：python scripts/mcp_client_demo.py

关键在这一点：Client 通过 stdio 启动 Server 子进程，两边只用 JSON-RPC 通信，
不共享任何 Python 对象。工具的执行权完全在 Server 进程里，Host 拿到的是文本结果——
它和「在本进程里调一个函数」是两回事，这一点决定了 MCP 工具的结果必须当成不可信输入。
"""

import asyncio
import sys

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

SERVER = StdioServerParameters(command=sys.executable, args=["-m", "support_agent.mcp_server"])


def shorten(text: str, limit: int = 96) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else f"{text[:limit]}…"


async def main() -> None:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            info = await session.initialize()
            server_info = info.server_info
            print(f"[握手] 连上 {server_info.name} {server_info.version}")

            print("\n[Tools] 可执行动作（由模型申请、Host 批准）")
            for tool in (await session.list_tools()).tools:
                print(f"  - {tool.name}：{shorten(tool.description or '')}")

            hit = await session.call_tool("query_device", {"sn": "SN-2024-000123"})
            print(f"\n[调用 query_device] isError={hit.is_error}")
            print(f"  {hit.content[0].text}")

            miss = await session.call_tool("query_device", {"sn": "SN-2024-000999"})
            print(f"\n[调用不存在的设备] isError={miss.is_error}")
            print(f"  {miss.content[0].text}")

            print("\n[Resources] 只读数据（用 URI 标识，像 GET）")
            for item in (await session.list_resources()).resources:
                print(f"  - {item.uri}：{item.name}")
            catalog = await session.read_resource("device://catalog")
            print(f"  读取 {catalog.contents[0].text}")

            print("\n[Prompts] 提示模板（由用户显式选择）")
            for item in (await session.list_prompts()).prompts:
                print(f"  - {item.name}：{shorten(item.description or '')}")
            rendered = await session.get_prompt("fault_report", {"device_sn": "SN-2024-000123"})
            print("  渲染结果：")
            for line in rendered.messages[0].content.text.splitlines():
                print(f"    {line}")


if __name__ == "__main__":
    asyncio.run(main())
