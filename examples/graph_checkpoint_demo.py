"""演示：给路由图加检查点，对比「无状态」与「可回放」。

运行方式：python examples/graph_checkpoint_demo.py

同一个 `classify` 函数，编译时传不传 checkpointer 决定了它是一次性纯计算还是有记忆：

- 不传：每次 `invoke` 都从零开始，跑完只拿到返回值，状态随即消失。
- 传了：每一步状态都落成 checkpoint。`get_state` 取回最新状态，
  `get_state_history` 按时间倒序列出走过的每一步——这就是 replay 的原料。

需要注意：加了检查点之后，`invoke` 必须带 `thread_id`，否则图不知道该往哪个
线程里写状态，会直接报错。这不是麻烦，而是提醒你「持久化是有归属的」。
"""

from langgraph.checkpoint.memory import InMemorySaver

from support_agent.graph import build_route_graph

QUESTIONS = (
    "SN-2024-000123 这台设备现在什么状态",
    "计算 100*0.986",
    "组串逆变器绝缘阻抗低怎么排查",
)


def without_checkpoint() -> None:
    """不传检查点：图是无状态的，调用之间互不记忆。"""
    graph = build_route_graph()
    print("[无检查点] 图是一次性纯计算，返回值之外什么都不留")
    for question in QUESTIONS:
        state = graph.invoke({"message": question})
        print(f"  route={state['route']:<11} ← {question}")
    print(f"  checkpointer 属性：{graph.checkpointer}（没有检查点，也就无从回放）\n")


def with_checkpoint() -> None:
    """传检查点：同一个 thread_id 连问三句，每一步都留下来。"""
    graph = build_route_graph(checkpointer=InMemorySaver())
    first = {"configurable": {"thread_id": "demo-thread-1"}}

    print("[有检查点] 同一个 thread_id 连问三句")
    for question in QUESTIONS:
        graph.invoke({"message": question}, first)
        snapshot = graph.get_state(first)
        print(f"  最新 route={snapshot.values['route']:<11} 待执行节点={snapshot.next}")

    print("\n  这个线程的 checkpoint 历史（新的在前）：")
    for index, snapshot in enumerate(graph.get_state_history(first)):
        checkpoint_id = snapshot.config["configurable"]["checkpoint_id"][-6:]
        route = snapshot.values.get("route") or "-"
        print(f"    #{index} route={route:<11} 下一步={str(snapshot.next):<14} id=…{checkpoint_id}")

    print("\n  换个 thread_id，历史彼此独立：")
    second = {"configurable": {"thread_id": "demo-thread-2"}}
    graph.invoke({"message": "帮我建个工单"}, second)
    print(f"    demo-thread-2 最新 route={graph.get_state(second).values['route']}")
    print(f"    demo-thread-1 仍停在 route={graph.get_state(first).values['route']}\n")


def pause_and_resume() -> None:
    """让图停在 classify 之后，取出状态，人工确认后再放行。

    这一段才是检查点真正的用途：不是「留个记录」，而是让一次执行可以跨请求暂停和继续。
    停在半路时进程可以退出，状态已经落在检查点里；下一个请求带着同一个 thread_id 回来，
    用 `invoke(None, config)` 就能从断点接着走。
    """
    graph = build_route_graph(checkpointer=InMemorySaver(), interrupt_after=["classify"])
    config = {"configurable": {"thread_id": "demo-thread-3"}}

    print("[中断与恢复] 在 classify 之后停下，等人工确认")
    graph.invoke({"message": "SN-2024-000123 这台设备有问题，帮我建个工单"}, config)
    snapshot = graph.get_state(config)
    print(f"  第一次请求结束：route={snapshot.values['route']} 下一步={snapshot.next}")
    print("  此时进程可以退出，状态已经落在检查点里，不需要重新分类")

    graph.invoke(None, config)
    snapshot = graph.get_state(config)
    print(f"  带同一个 thread_id 回来续跑：route={snapshot.values['route']} 下一步={snapshot.next}")
    print("  停下的位置由 next 决定，恢复时从那里继续，前面的 classify 不会重跑")


if __name__ == "__main__":
    without_checkpoint()
    with_checkpoint()
    pause_and_resume()
