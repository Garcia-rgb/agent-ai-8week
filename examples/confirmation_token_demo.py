"""演示工单确认令牌的四道闸：能用、防篡改、防重放、防过期。

直接对 ASGI 应用发请求，不用起端口。数据落在临时目录，跑多少遍都不会碰到
开发库，也不连模型、不加载 ONNX 模型，所以结果是确定的：

    python examples/confirmation_token_demo.py
"""

import logging
import os
import tempfile
from pathlib import Path

# 必须在导入应用之前改环境变量：配置是 lru_cache 的，导入之后再改就晚了。
# 清掉 API key 是为了让演示走本地规则模型，不去连远程；换回哈希向量是为了
# 不触发 90MB 模型加载——演示的重点是令牌，不该被这两件事干扰。
_DEMO_DIR = Path(tempfile.mkdtemp(prefix="smartpv-confirm-demo-"))
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{(_DEMO_DIR / 'demo.db').as_posix()}"
os.environ["LLM_API_KEY"] = ""
os.environ["EMBEDDING_BACKEND"] = "hash"

from fastapi.testclient import TestClient  # noqa: E402

from support_agent.config import get_settings  # noqa: E402
from support_agent.main import app  # noqa: E402
from support_agent.services.security import create_confirmation_token  # noqa: E402

# 写操作必须由模型先提出申请，服务端再把申请转成一次人工确认。
WRITE_INTENT = (
    "SN-2024-000789 故障停机了，请创建工单，标题写逆变器故障停机，描述写现场已确认断电"
)
USER = "demo-user"

# 请求日志本身没问题，但一屏 JSON 会把演示输出冲散，这里只保留警告及以上。
# 用全局 disable 而不是按名字压级别：TestClient 用的日志器名不一定叫 httpx
#（本机上是 httpx2），按名字压会静默失效。
logging.disable(logging.INFO)


def issue_token(client: TestClient) -> str:
    """走一次真实链路拿到待确认令牌。"""
    response = client.post("/chat", json={"message": WRITE_INTENT, "user_id": USER})
    body = response.json()
    pending = body.get("pending_action")
    if pending is None:
        raise SystemExit(f"没有拿到待确认动作：status={body.get('status')}\n{body.get('answer')}")
    print(f"   会话 status={body['status']}，待确认动作={pending['action']}")
    print(f"   摘要：{pending['summary']}")
    return pending["confirmation_token"]


def submit(client: TestClient, token: str) -> tuple[int, str]:
    response = client.post("/tickets", json={"confirmation_token": token, "user_id": USER})
    detail = response.json().get("detail") if response.status_code >= 400 else response.json()["id"]
    return response.status_code, detail


def main() -> None:
    with TestClient(app) as client:
        health = client.get("/health").json()
        print(f"[环境] 临时库 {_DEMO_DIR / 'demo.db'}")
        print(f"       模型启用={health['llm_enabled']}（演示只走本地规则模型）")

        print("\n[1/4] 能用：正常令牌确认后建单")
        token = issue_token(client)
        status_code, detail = submit(client, token)
        print(f"   HTTP {status_code}，工单 id={detail}")
        assert status_code == 201, detail

        print("\n[2/4] 防重放：拿同一张令牌再提交一次")
        status_code, detail = submit(client, token)
        print(f"   HTTP {status_code}，{detail}")
        print("   工单只有一条——令牌消费记录的主键挡住了第二次")
        assert status_code == 409, detail

        print("\n[3/4] 防篡改：把令牌正文改一个字符（签名不动）")
        encoded, signature = token.split(".", 1)
        flipped = "A" if encoded[-1] != "A" else "B"
        status_code, detail = submit(client, f"{encoded[:-1]}{flipped}.{signature}")
        print(f"   HTTP {status_code}，{detail}")
        print("   注意这里是 400 不是 409：验签排在判重之前，")
        print("   所以改过的令牌不会被判成「已使用」，也就不会泄露它是否存在")
        assert status_code == 400, detail

        print("\n[4/4] 防过期：用同一密钥签一张已经过期的令牌")
        expired = create_confirmation_token(
            {
                "action": "create_ticket",
                "session_id": "demo-session",
                "user_id": USER,
                "device_sn": "SN-2024-000789",
                "reason": "逆变器故障停机",
            },
            get_settings().confirmation_secret,
            ttl_seconds=-1,
        )
        status_code, detail = submit(client, expired)
        print(f"   HTTP {status_code}，{detail}")
        print("   签名是对的——它只是放太久了，所以过期是独立的一道闸")
        assert status_code == 400, detail

        print("\n四道闸：签名挡篡改，有效期挡久放，消费记录挡重放，写操作本身由人工确认放行。")


if __name__ == "__main__":
    main()
