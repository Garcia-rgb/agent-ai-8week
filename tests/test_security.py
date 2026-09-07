import pytest

from support_agent.services.security import create_confirmation_token, verify_confirmation_token


def test_confirmation_token_round_trip() -> None:
    token = create_confirmation_token({"action": "create_ticket", "user_id": "u1"}, "secret")
    payload = verify_confirmation_token(token, "secret")
    assert payload["action"] == "create_ticket"
    assert payload["user_id"] == "u1"


def test_confirmation_token_detects_tampering() -> None:
    token = create_confirmation_token({"action": "create_ticket"}, "secret")
    with pytest.raises(ValueError, match="无效"):
        verify_confirmation_token(token + "broken", "secret")
