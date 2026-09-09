from fastapi.testclient import TestClient

from exercises.week01.task_api import app, tasks


def test_task_crud() -> None:
    tasks.clear()
    client = TestClient(app)

    created = client.post("/tasks", json={"title": "学习 FastAPI"})
    assert created.status_code == 201
    task_id = created.json()["id"]

    listed = client.get("/tasks")
    assert listed.json() == [created.json()]

    completed = client.patch(f"/tasks/{task_id}")
    assert completed.status_code == 200
    assert completed.json()["done"] is True

    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 200
    assert client.get("/tasks").json() == []

    missing = client.delete(f"/tasks/{task_id}")
    assert missing.status_code == 404


def test_task_title_cannot_be_empty() -> None:
    tasks.clear()
    client = TestClient(app)

    response = client.post("/tasks", json={"title": ""})

    assert response.status_code == 422

