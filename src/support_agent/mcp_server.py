"""把设备的只读能力以 MCP Server 的形式暴露出去（第 5 周 Day 5）。

MCP 里三个角色在这里的分工：

- Server：本模块，对外提供 Tools / Resources / Prompts
- Client：连上 Server 的那一端，一个 Client 只连一个 Server
- Host：承载模型、决定要不要调用工具的那一端，也就是本项目的 Agent 服务

三样东西最容易被混成一件事，区别在于「谁发起」和「有没有副作用」：

- Tools 是可执行动作，由模型申请、Host 批准，可能有副作用（本项目只暴露只读工具）
- Resources 是只读数据，用 URI 标识，像 HTTP 的 GET，读多少次结果都该一样
- Prompts 是给人选的提示模板，由用户显式选择，不该由模型自己偷偷套用

运行方式（stdio 传输，由 Client 拉起这个子进程）：

    python -m support_agent.mcp_server
"""

import json
from dataclasses import asdict

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError as MCPToolError

from . import __version__
from .services.tools import MOCK_DEVICES, ToolError, query_device

DEVICE_CATALOG_URI = "device://catalog"

server = MCPServer(
    name="smartpv-device",
    version=__version__,
    description="光伏电站设备档案查询",
    instructions="按设备序列号查询逆变器档案。只提供只读能力，不提供任何写操作。",
)


@server.tool(
    name="query_device",
    description="按设备序列号查询逆变器型号、额定功率、运行状态、固件版本和并网情况。",
)
def query_device_tool(sn: str) -> str:
    """复用项目里已有的设备查询，不另写一份数据源。

    业务失败要按协议报成 `isError`，同时保留可读的错误文本：协议层给 Host 一个
    「这次调用失败了」的确定信号（可据此统计失败率、告警），文本层让模型知道
    到底哪儿不对。两者都要——只返回一段像正常结果的错误描述，Host 就分不出来。
    """
    try:
        device = query_device(sn)
    except ToolError as exc:
        raise MCPToolError(str(exc)) from exc
    return json.dumps(asdict(device), ensure_ascii=False)


@server.resource(
    DEVICE_CATALOG_URI,
    name="设备清单",
    description="当前环境里登记在册的设备序列号与对应型号",
    mime_type="application/json",
)
def device_catalog() -> str:
    """只读资源：读一次和读十次结果相同，不产生任何副作用。"""
    return json.dumps(
        [{"sn": device.sn, "model": device.model} for device in MOCK_DEVICES.values()],
        ensure_ascii=False,
    )


@server.prompt(
    name="fault_report",
    description="故障上报模板：把现象、时间、设备型号和现场条件分开写清楚",
)
def fault_report_prompt(device_sn: str = "", symptom: str = "", since: str = "") -> str:
    """提示模板：由用户显式选用，Server 只负责渲染，不替用户决定用不用。"""
    lines = [
        "请按下面的结构描述问题，信息越具体，定位越快：",
        "1. 现象：告警代码，或你实际看到、听到的异常",
        "2. 时间：什么时候开始、是否持续、是否与天气或负载有关",
        "3. 设备：型号与序列号（例如 SUN2000-100KTL-M1 / SN-2024-000123）",
        "4. 现场：已经做过的操作，以及当时的辐照、温度和电网情况",
    ]
    if device_sn:
        lines.append(f"已知设备序列号：{device_sn}")
    if symptom:
        lines.append(f"已知现象：{symptom}")
    if since:
        lines.append(f"开始时间：{since}")
    return "\n".join(lines)


def main() -> None:
    """stdio 传输的入口；由 Client 拉起，不直接给人用。"""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
