from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from exercises.week02 import task_api_sqlalchemy


def test_sqlalchemy_task_crud(tmp_path: Path, monkeypatch) -> None:
    database_url = f"sqlite+aiosqlite:///{(tmp_path / 'tasks.db').as_posix()}"
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(task_api_sqlalchemy, "engine", engine)
    monkeypatch.setattr(task_api_sqlalchemy, "SessionFactory", session_factory)

    with TestClient(task_api_sqlalchemy.app) as client:
        created = client.post("/tasks", json={"title": "学习 SQLAlchemy"})
        assert created.status_code == 201
        task_id = created.json()["id"]

        completed = client.patch(f"/tasks/{task_id}")
        assert completed.status_code == 200
        assert completed.json()["done"] is True

        assert client.get("/tasks").json() == [completed.json()]
        assert client.delete(f"/tasks/{task_id}").status_code == 200
        assert client.get("/tasks").json() == []
        assert client.delete(f"/tasks/{task_id}").status_code == 404

