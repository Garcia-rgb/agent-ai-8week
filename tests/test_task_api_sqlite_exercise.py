from pathlib import Path

from fastapi.testclient import TestClient

from exercises.week02 import task_api_sqlite


def test_sqlite_task_crud(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "tasks.db"
    monkeypatch.setattr(task_api_sqlite, "DATABASE_PATH", database_path)
    task_api_sqlite.create_table()
    client = TestClient(task_api_sqlite.app)

    created = client.post("/tasks", json={"title": "学习 SQLite"})
    assert created.status_code == 201
    task_id = created.json()["id"]

    completed = client.patch(f"/tasks/{task_id}")
    assert completed.status_code == 200
    assert completed.json()["done"] is True

    listed = client.get("/tasks")
    assert listed.json() == [completed.json()]

    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 200
    assert client.get("/tasks").json() == []
    assert client.delete(f"/tasks/{task_id}").status_code == 404

