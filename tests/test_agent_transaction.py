from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from support_agent.config import Settings
from support_agent.models import Conversation, Message
from support_agent.services.agent import SupportAgent


async def test_respond_rolls_back_when_commit_fails(db_session: AsyncSession) -> None:
    agent = SupportAgent(
        db_session,
        Settings(
            database_url="sqlite+aiosqlite:///unused.db",
            confirmation_secret="test-secret",
        ),
    )
    failed_commit = AsyncMock(side_effect=RuntimeError("数据库提交失败"))
    rollback = AsyncMock(wraps=db_session.rollback)

    with (
        patch.object(db_session, "commit", failed_commit),
        patch.object(db_session, "rollback", rollback),
        pytest.raises(RuntimeError, match="数据库提交失败"),
    ):
        await agent.respond("2 + 2", None, "u1")

    rollback.assert_awaited_once()
    conversation_count = await db_session.scalar(
        select(func.count()).select_from(Conversation)
    )
    message_count = await db_session.scalar(select(func.count()).select_from(Message))
    assert conversation_count == 0
    assert message_count == 0
