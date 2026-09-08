"""无需启动网络端口，直接对 ASGI 应用运行一遍主要用户流程。"""

from fastapi.testclient import TestClient

from support_agent.main import app


def main() -> None:
    """依次验证健康检查、知识问答、工单确认、防重放和离线评测。"""
    with TestClient(app) as client:
        health = client.get("/health")
        health.raise_for_status()

        chat = client.post(
            "/chat", json={"message": "退货后多久到账？", "user_id": "smoke-user"}
        )
        chat.raise_for_status()
        assert chat.json()["citations"], "knowledge query must return citations"

        pending = client.post(
            "/chat",
            json={"message": "物流一直没更新，请创建工单", "user_id": "smoke-user"},
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

        evaluation = client.post("/evaluations/run")
        evaluation.raise_for_status()
        result = evaluation.json()
        print(
            {
                "health": health.json(),
                "answer_has_citations": True,
                "ticket_id": ticket.json()["id"],
                "replay_status": replay.status_code,
                "evaluation": {
                    "passed": result["passed"],
                    "total": result["total"],
                    "score": result["score"],
                },
            }
        )


if __name__ == "__main__":
    main()
