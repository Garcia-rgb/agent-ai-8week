import base64
import hashlib
import hmac
import json

import pytest

from support_agent.services.security import create_confirmation_token, verify_confirmation_token


def encode_body(body: object) -> str:
    """按服务端同样的编码方式把正文编成令牌的前半段。"""
    raw = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def sign(body: object, secret: str = "secret") -> str:
    """签出一份签名正确的令牌，用来构造「签名对但内容不正常」的输入。"""
    encoded = encode_body(body)
    signature = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def test_confirmation_token_round_trip() -> None:
    token = create_confirmation_token({"action": "create_ticket", "user_id": "u1"}, "secret")
    payload = verify_confirmation_token(token, "secret")
    assert payload["action"] == "create_ticket"
    assert payload["user_id"] == "u1"


def test_confirmation_token_detects_tampering() -> None:
    token = create_confirmation_token({"action": "create_ticket"}, "secret")
    with pytest.raises(ValueError, match="签名无效"):
        verify_confirmation_token(token + "broken", "secret")


def test_confirmation_token_rejects_an_edited_payload() -> None:
    """改内容、不动签名，是最自然的攻击方式。

    上面那条只弄坏了签名那一半；这条真的把 payload 里的 user_id 换成别人再拼回原签名，
    验签必须照样失败。
    """
    token = create_confirmation_token({"action": "create_ticket", "user_id": "u1"}, "secret")
    encoded, signature = token.split(".", 1)
    body = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
    body["user_id"] = "u2"
    with pytest.raises(ValueError, match="签名无效"):
        verify_confirmation_token(f"{encode_body(body)}.{signature}", "secret")


def test_confirmation_token_expires() -> None:
    """签名对但放太久，同样不能用。"""
    token = create_confirmation_token({"action": "create_ticket"}, "secret", ttl_seconds=-1)
    with pytest.raises(ValueError, match="已过期"):
        verify_confirmation_token(token, "secret")


def test_confirmation_token_is_bound_to_the_secret() -> None:
    """换密钥就验不过：令牌不能跨环境、跨部署直接复用。"""
    token = create_confirmation_token({"action": "create_ticket"}, "secret")
    with pytest.raises(ValueError, match="签名无效"):
        verify_confirmation_token(token, "another-secret")


def test_confirmation_token_reports_a_missing_separator_as_malformed() -> None:
    """没有 `签名` 分隔符时要说「格式无效」，不能笼统地报「无效」。"""
    with pytest.raises(ValueError, match="格式无效"):
        verify_confirmation_token("no-separator-here", "secret")


def test_confirmation_token_rejects_structurally_unusable_payloads() -> None:
    """签名正确但内容用不了，也要抛 ValueError（而不是 AttributeError / TypeError）。

    这两种情况只有签名方自己造得出来，所以它们是防御性分支；但正因为平时走不到，
    一旦少了守卫就会变成 500——调用方只接 ValueError。
    """
    with pytest.raises(ValueError, match="内容无效"):
        verify_confirmation_token(sign(123), "secret")
    with pytest.raises(ValueError, match="内容无效"):
        verify_confirmation_token(sign({"action": "create_ticket", "exp": "soon"}), "secret")
