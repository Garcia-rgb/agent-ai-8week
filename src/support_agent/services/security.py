import base64
import hashlib
import hmac
import json
import time
from typing import Any


def create_confirmation_token(payload: dict[str, Any], secret: str, ttl_seconds: int = 600) -> str:
    body = {**payload, "exp": int(time.time()) + ttl_seconds}
    encoded = (
        base64.urlsafe_b64encode(
            json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()
        )
        .decode()
        .rstrip("=")
    )
    signature = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def verify_confirmation_token(token: str, secret: str) -> dict[str, Any]:
    try:
        encoded, supplied_signature = token.split(".", 1)
        expected = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(supplied_signature, expected):
            raise ValueError("确认令牌签名无效")
        padded = encoded + "=" * (-len(encoded) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded).decode())
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("确认令牌无效") from exc
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("确认令牌已过期")
    return payload


SUSPICIOUS_PATTERNS = (
    "忽略之前的指令",
    "ignore previous instructions",
    "system prompt",
    "泄露密钥",
    "api key",
)


def looks_like_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in SUSPICIOUS_PATTERNS)
