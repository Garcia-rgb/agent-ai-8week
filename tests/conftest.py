from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from support_agent.config import Settings, get_settings
from support_agent.db import Base, get_db
from support_agent.main import app


@pytest.fixture(autouse=True)
def hermetic_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """让测试不读开发者本机的 .env。

    否则一旦在 .env 里填了真实模型配置，``llm_enabled`` 就会变真，
    同一份代码在本机跑 pytest 和在 CI（没有 .env）跑会得到不同结果。
    所以测试期间一律不加载 .env，配置只能由用例显式传进来。
    """
    monkeypatch.setitem(Settings.model_config, "env_file", None)


@pytest_asyncio.fixture
async def db_session(tmp_path) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[httpx.AsyncClient]:
    settings = Settings(
        database_url="sqlite+aiosqlite:///unused.db",
        confirmation_secret="test-secret",
        max_upload_bytes=1024 * 1024,
    )

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
