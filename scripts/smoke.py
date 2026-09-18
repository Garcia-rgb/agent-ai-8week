"""无需启动网络端口，直接对 ASGI 应用运行一遍主要用户流程。"""

import os

from fastapi.testclient import TestClient

from support_agent.main import app

# 评测集不进仓库（它随知识库变化），所以这一步靠环境变量显式指定；没给就跳过。
DATASET_ENV = "SMOKE_DATASET_PATH"


def main() -> None:
    """依次验证健康检查、知识问答、工单确认、防重放和离线评测。"""
    with TestClient(app) as client:
        health = client.get("/health")
        health.raise_for_status()

        chat = client.post(
            "/chat", json={"message": "逆变器报绝缘阻抗低怎么排查？", "user_id": "smoke-user"}
        )
        chat.raise_for_status()
        assert chat.json()["citations"], "knowledge query must return citations"

        pending = client.post(
            "/chat",
            json={
                "message": (
                    "SN-2024-000789 故障停机了，请创建工单，"
                    "标题写逆变器故障停机，描述写现场已确认断电"
                ),
                "user_id": "smoke-user",
            },
        )
        pending.raise_for_status()
        token = pending.json()["pending_action"]["confirmation_token"]
        ticket = client.post(
            "/tickets", json={"confirmation_token": token, "user_id": "smoke-user"}
        )
        ticket.raise_for_status()
        replay = client.post(
            "/tickets", json={"confirmation_token": token, "user_id": "smoke-user"}
        )
        assert replay.status_code == 409

        summary: dict[str, object] = {
            "health": health.json(),
            "answer_has_citations": True,
            "ticket_id": ticket.json()["id"],
            "replay_status": replay.status_code,
        }

        dataset_path = os.environ.get(DATASET_ENV)
        if dataset_path:
            evaluation = client.post(
                "/evaluations/run", params={"dataset_path": dataset_path}
            )
            evaluation.raise_for_status()
            result = evaluation.json()
            summary["evaluation"] = {
                "passed": result["passed"],
                "total": result["total"],
                "score": result["score"],
            }
        else:
            summary["evaluation"] = f"skipped (set {DATASET_ENV} to run)"

        print(summary)


if __name__ == "__main__":
    main()
