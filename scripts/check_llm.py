"""连真实模型的一键自检：读 .env，先问答一次，再跑一次工具调用循环。

用法（在仓库根目录执行）：

    python scripts/check_llm.py

第 2 步会真的走一遍「模型选工具 → 服务端执行 → 结果回传模型」，
所以它能同时验证鉴权、模型名、以及思考模式下思维链是否正确回传。
不产生任何写操作，也不写数据库。
"""

import asyncio
from pathlib import Path

from support_agent.config import Settings
from support_agent.services.agent_loop import build_tool_registry, run_agent_loop
from support_agent.services.llm import LLMError, OpenAICompatibleClient

REPO_ROOT = Path(__file__).resolve().parents[1]
QUESTION = "帮我算一下 (12+8)/4 是多少"
# 问答自检用的资料片段：随手给一段光伏运维文本，验证模型是否会按指令只依据它作答。
CONTEXT = "绝缘阻抗低（告警 2062）处理：检查阵列对地阻抗，并确认保护地线连接可靠。"


def mask(secret: str | None) -> str:
    """只显示密钥的前几位，避免把密钥打进日志。"""
    if not secret:
        return "(未配置)"
    return f"{secret[:4]}{'*' * 8}（长度 {len(secret)}）"


async def main() -> int:
    settings = Settings(_env_file=REPO_ROOT / ".env")
    print(f"base_url : {settings.llm_base_url or '(未配置)'}")
    print(f"model    : {settings.llm_model or '(未配置)'}")
    print(f"api_key  : {mask(settings.llm_api_key)}")
    if not settings.llm_enabled:
        print("\n三项配置没齐，/chat 会退回本地规则模型。请把 .env 里的 LLM_API_KEY 填上。")
        return 1

    client = OpenAICompatibleClient(settings)

    print("\n[1/2] 单轮问答（不带工具）……")
    try:
        answer = await client.answer("绝缘阻抗低应该先查什么？", [CONTEXT])
    except LLMError as exc:
        print(f"  失败：category={exc.category} retryable={exc.retryable} 原因={exc}")
        return 1
    print(f"  回答：{answer[:160]}")

    print("\n[2/2] 工具调用循环（两轮以上，会校验思维链回传）……")
    try:
        result = await run_agent_loop(
            client,
            QUESTION,
            registry=build_tool_registry(),
            max_rounds=settings.agent_max_rounds,
        )
    except LLMError as exc:
        print(f"  失败：category={exc.category} retryable={exc.retryable} 原因={exc}")
        return 1

    print(f"  轮数={result.rounds} 结束原因={result.stopped_reason}")
    for record in result.tool_calls:
        print(f"  第 {record.round} 轮 {record.name} ok={record.ok} → {record.output[:80]}")
    print(f"  最终回答：{result.answer[:160]}")

    if result.stopped_reason.startswith("llm_error"):
        print("\n模型在循环中失败；上面两行指出了具体类别。")
        return 1
    print("\n通过：真实模型已经跑通完整 Agent Loop。")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
