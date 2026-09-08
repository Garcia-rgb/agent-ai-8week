import re
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from .services.security import looks_like_prompt_injection
from .services.tools import find_order_id

Route = Literal["blocked", "calculator", "order", "ticket", "knowledge"]


class AgentState(TypedDict, total=False):
    """节点之间传递的 Agent 状态；字段可由不同节点逐步补充。"""
    message: str
    route: Route
    order_id: str | None
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
    elif find_order_id(message):
        route = "order"
    else:
        route = "knowledge"
    expression = re.sub(r"^(计算|calc[:：]?)\s*", "", message, flags=re.IGNORECASE)
    return {
        "route": route,
        "order_id": find_order_id(message),
        "expression": expression if route == "calculator" else None,
    }


def passthrough(state: AgentState) -> AgentState:
    """当前各路由的占位节点，原样传递状态供业务层处理。"""
    return state


def build_route_graph():
    """构建并编译“分类后分流”的 LangGraph 工作流。"""
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify)
    for route in ("blocked", "calculator", "order", "ticket", "knowledge"):
        graph.add_node(route, passthrough)
        graph.add_edge(route, END)
    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", lambda state: state["route"])
    return graph.compile()
