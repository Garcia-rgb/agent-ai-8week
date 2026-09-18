"""第 3 周 Day 5 演示：不接真实模型，观察 Agent Loop 每一轮到底发生了什么。

运行方式：python examples/agent_loop_demo.py

这里用脚本化假模型替代真实模型，好处是每一轮的“模型意图”都是确定的，
可以把注意力放在循环本身：谁提出工具、谁执行、结果怎么回到模型手里。
"""

import asyncio

from support_agent.services.agent_loop import run_agent_loop
from support_agent.services.llm import AssistantTurn, ToolCallRequest


class ScriptedModel:
    """按剧本依次返回回复的假模型。真实模型换成 OpenAICompatibleClient 即可。"""

    def __init__(self, *turns: AssistantTurn):
        self._turns = list(turns)

    async def chat_with_tools(self, messages, tools=None):
        print(f"  [模型输入] 共 {len(messages)} 条消息，本轮提供 {len(tools or [])} 个工具")
        turn = self._turns.pop(0)
        if turn.tool_calls:
            for call in turn.tool_calls:
                print(f"  [模型意图] 申请调用 {call.name}，参数 {call.arguments}")
        else:
            print(f"  [模型意图] 直接给出最终回答：{turn.content}")
        return turn


def ask(name: str, arguments: str) -> AssistantTurn:
    return AssistantTurn("", [ToolCallRequest("call", name, arguments)])


def say(text: str) -> AssistantTurn:
    return AssistantTurn(text, [])


async def main() -> None:
    model = ScriptedModel(
        ask("calculator", '{"expression": "(12 + 8) / 4"}'),
        ask("query_device", '{"sn": "SN-2024-000123"}'),
        say("计算结果是 5。设备 SN-2024-000123 型号 SUN2000-100KTL-M1，当前并网发电。"),
    )

    result = await run_agent_loop(
        model, "帮我算 (12+8)/4，再看看设备 SN-2024-000123 现在什么状态"
    )

    print("\n===== 执行轨迹 =====")
    for record in result.tool_calls:
        flag = "成功" if record.ok else "失败"
        print(f"第 {record.round} 轮 | {record.name} | {flag} | {record.output}")
    print("\n===== 最终结果 =====")
    print(f"轮数：{result.rounds}，停止原因：{result.stopped_reason}")
    print(f"回答：{result.answer}")


if __name__ == "__main__":
    asyncio.run(main())
