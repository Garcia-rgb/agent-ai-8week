import re
from typing import Literal, TypedDict

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from .services.security import looks_like_prompt_injection
from .services.tools import find_device_sn

Route = Literal["blocked", "calculator", "device", "ticket", "knowledge"]

#: 条件路由的全部分支；节点注册与条件边都从这里取，避免两处各写一份。
ROUTES: tuple[Route, ...] = ("blocked", "calculator", "device", "ticket", "knowledge")


class AgentState(TypedDict, total=False):
    """节点之间传递的 Agent 状态；字段可由不同节点逐步补充。"""
    message: str
    route: Route
    device_sn: str | None
    expression: str | None


def classify(state: AgentState) -> AgentState:
    """使用固定规则识别意图，决定下一步进入哪个处理节点。"""
    message = state["message"].strip()
    lowered = message.lower()
    if looks_like_prompt_injection(message):
        route: Route = "blocked"
    elif re.match(r"^(计算|calc[:：]?)", lowered):
        route = "calculator"
    elif any(word in message for word in ("工单", "投诉", "转人工")):
        route = "ticket"
    elif find_device_sn(message):
        route = "device"
    else:
        route = "knowledge"
    expression = re.sub(r"^(计算|calc[:：]?)\s*", "", message, flags=re.IGNORECASE)
    return {
        "route": route,
        "device_sn": find_device_sn(message),
        "expression": expression if route == "calculator" else None,
    }


def passthrough(state: AgentState) -> AgentState:
    """当前各路由的占位节点，原样传递状态供业务层处理。"""
    return state


def build_route_graph(
    checkpointer: BaseCheckpointSaver | None = None,
    interrupt_after: list[str] | None = None,
):
    """构建并编译“分类后分流”的 LangGraph 工作流。

    默认不传 `checkpointer`，此时图是一次性的纯计算：跑完状态就没了，
    与加入检查点之前的行为完全一致。传入检查点后每一步状态都会落盘，
    可以用同一个 `thread_id` 续跑，也可以回放走过的路径。

    `interrupt_after` 指定在哪些节点之后停下，供人工介入；必须与检查点一起使用，
    因为“停下来”意味着状态得先有个地方存，否则下次请求接不上。
    """
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify)
    for route in ROUTES:
        graph.add_node(route, passthrough)
        graph.add_edge(route, END)
    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", lambda state: state["route"])
    return graph.compile(checkpointer=checkpointer, interrupt_after=interrupt_after)
