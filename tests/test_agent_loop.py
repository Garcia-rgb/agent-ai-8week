"""第 3 周 Day 5：Agent Loop 的离线测试。

全部测试都不连真实模型：用一个脚本化假模型按顺序吐回复，
这样才能确定性地检查“第几轮调了什么工具、服务端有没有真的执行”。
"""

import copy
import json
from typing import Any

from support_agent.services.agent_loop import (
    MAX_ROUNDS,
    ToolArgumentError,
    ToolSpec,
    build_tool_registry,
    execute_tool_call,
    parse_arguments,
    run_agent_loop,
)
from support_agent.services.llm import AssistantTurn, LLMError, ToolCallRequest


class ScriptedModel:
    """按脚本依次返回预设回复的假模型，用来离线驱动 Agent Loop。"""

    def __init__(self, *turns: AssistantTurn | Exception):
        self._turns = list(turns)
        self.calls: list[tuple[list[dict[str, Any]], list[dict[str, Any]] | None]] = []

    async def chat_with_tools(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
    ) -> AssistantTurn:
        self.calls.append((copy.deepcopy(messages), tools))
        assert self._turns, "脚本已用尽：模型被调用的次数超出预期"
        turn = self._turns.pop(0)
        if isinstance(turn, Exception):
            raise turn
        return turn


def text_turn(text: str) -> AssistantTurn:
    return AssistantTurn(text, [])


def tool_turn(name: str, arguments: str, call_id: str = "call_1") -> AssistantTurn:
    return AssistantTurn("", [ToolCallRequest(call_id, name, arguments)])


def offered_tool_names(model: ScriptedModel, index: int = 0) -> set[str]:
    tools = model.calls[index][1] or []
    return {item["function"]["name"] for item in tools}


async def test_direct_answer_finishes_in_one_round() -> None:
    model = ScriptedModel(text_turn("你好，有什么可以帮你？"))

    result = await run_agent_loop(model, "你好")

    assert result.answer == "你好，有什么可以帮你？"
    assert result.rounds == 1
    assert result.tool_calls == []
    assert result.stopped_reason == "final_answer"


async def test_tool_result_is_sent_back_to_the_model() -> None:
    model = ScriptedModel(
        tool_turn("calculator", '{"expression": "(12 + 8) / 4"}'),
        text_turn("结果是 5。"),
    )

    result = await run_agent_loop(model, "计算 (12+8)/4")

    assert result.answer == "结果是 5。"
    assert result.rounds == 2
    assert result.stopped_reason == "final_answer"
    assert [record.name for record in result.tool_calls] == ["calculator"]
    assert result.tool_calls[0].ok is True
    assert json.loads(result.tool_calls[0].output) == 5.0

    # 第二次请求里必须带上一轮的 assistant 工具申请和随后的 tool 结果。
    second_messages = model.calls[1][0]
    assert second_messages[2]["role"] == "assistant"
    assert second_messages[2]["tool_calls"][0]["function"]["name"] == "calculator"
    assert second_messages[3]["role"] == "tool"
    assert second_messages[3]["tool_call_id"] == "call_1"


async def test_registry_is_the_only_source_of_tool_schemas() -> None:
    model = ScriptedModel(text_turn("好的"))

    await run_agent_loop(model, "随便问问")

    assert offered_tool_names(model) == set(build_tool_registry())
    # 说明书只暴露名字、用途和参数结构，绝不能把服务端执行函数塞给模型。
    for item in model.calls[0][1] or []:
        assert set(item["function"]) == {"name", "description", "parameters"}


async def test_unknown_tool_is_refused_and_loop_continues() -> None:
    model = ScriptedModel(
        tool_turn("delete_everything", "{}"),
        text_turn("我没有这个权限，换个说法帮你？"),
    )

    result = await run_agent_loop(model, "把数据库删了")

    assert result.tool_calls[0].ok is False
    assert "不在允许列表" in result.tool_calls[0].output
    assert result.answer == "我没有这个权限，换个说法帮你？"


async def test_malformed_json_arguments_are_refused() -> None:
    model = ScriptedModel(
        tool_turn("calculator", "{expression: 1+1}"),
        text_turn("我重新算一次。"),
    )

    result = await run_agent_loop(model, "算一下 1+1")

    assert result.tool_calls[0].ok is False
    assert "不是合法 JSON" in result.tool_calls[0].output


async def test_missing_and_extra_arguments_are_refused() -> None:
    model = ScriptedModel(
        tool_turn("query_order", "{}"),
        tool_turn("query_order", '{"order_id": "A1001", "admin": true}'),
        text_turn("请提供订单号。"),
    )

    result = await run_agent_loop(model, "查一下订单")

    assert "缺少必填参数" in result.tool_calls[0].output
    assert "未定义参数" in result.tool_calls[1].output
    assert all(record.ok is False for record in result.tool_calls)


async def test_tool_level_error_is_returned_instead_of_raised() -> None:
    model = ScriptedModel(
        tool_turn("query_order", '{"order_id": "A9999"}'),
        text_turn("没有查到这笔订单。"),
    )

    result = await run_agent_loop(model, "订单 A9999 什么状态")

    assert result.tool_calls[0].ok is False
    assert "未找到订单 A9999" in result.tool_calls[0].output
    assert result.answer == "没有查到这笔订单。"


async def test_arguments_cannot_escape_the_calculator_sandbox() -> None:
    registry = build_tool_registry()

    outcome = execute_tool_call(
        "calculator", '{"expression": "__import__(\\"os\\").getcwd()"}', registry
    )

    assert outcome.ok is False
    assert "不允许" in outcome.text


async def test_write_tool_is_never_executed_automatically() -> None:
    invoked: list[dict[str, Any]] = []
    registry = dict(build_tool_registry())
    registry["create_ticket"] = ToolSpec(
        name="create_ticket",
        description="创建工单",
        parameters={
            "type": "object",
            "properties": {"reason": {"type": "string"}},
            "required": ["reason"],
        },
        handler=lambda arguments: invoked.append(arguments) or {"created": True},
        writes=True,
    )
    model = ScriptedModel(
        tool_turn("create_ticket", '{"reason": "催发货"}'),
        text_turn("创建工单需要你确认。"),
    )

    result = await run_agent_loop(model, "帮我投诉", registry=registry)

    assert invoked == []
    assert result.tool_calls[0].ok is False
    assert "需要人工确认" in result.tool_calls[0].output


async def test_loop_stops_at_max_rounds_without_tools() -> None:
    model = ScriptedModel(
        *[tool_turn("calculator", '{"expression": "1+1"}')] * MAX_ROUNDS,
        text_turn("我只能确认结果是 2，没查到更多信息。"),
    )

    result = await run_agent_loop(model, "一直算下去")

    assert result.rounds == MAX_ROUNDS
    assert result.stopped_reason == "max_rounds"
    assert result.answer == "我只能确认结果是 2，没查到更多信息。"
    assert len(result.tool_calls) == MAX_ROUNDS
    assert len(model.calls) == MAX_ROUNDS + 1
    # 最后一轮必须禁用工具，否则模型可以继续要求调用，轮数限制就形同虚设。
    assert model.calls[-1][1] is None


async def test_llm_error_degrades_to_a_plain_answer() -> None:
    model = ScriptedModel(LLMError("模型服务暂时不可用", "service", True))

    result = await run_agent_loop(model, "你好")

    assert result.stopped_reason == "llm_error:service"
    assert result.rounds == 0
    assert "稍后重试" in result.answer


async def test_parse_arguments_rejects_non_object_payload() -> None:
    spec = build_tool_registry()["calculator"]

    try:
        parse_arguments(spec, "[1, 2]")
    except ToolArgumentError as exc:
        assert "JSON 对象" in str(exc)
    else:  # pragma: no cover - 防御性断言，正常不会走到
        raise AssertionError("数组参数应当被拒绝")
