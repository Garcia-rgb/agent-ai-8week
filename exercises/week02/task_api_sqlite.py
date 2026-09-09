import sqlite3
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

DATABASE_PATH = Path(__file__).with_name("tasks.db")


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class Task(BaseModel):
    id: str
    title: str
    done: bool = False


app = FastAPI(title="SQLite 任务管理器练习")


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_table() -> None:
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )


create_table()


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    task = Task(id=str(uuid4())[:8], title=payload.title)
    with connect() as connection:
        connection.execute(
            "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
            (task.id, task.title, task.done),
        )
    return task


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    with connect() as connection:
        rows = connection.execute(
            "SELECT id, title, done FROM tasks ORDER BY rowid"
        ).fetchall()
    return [Task(**dict(row)) for row in rows]


@app.patch("/tasks/{task_id}", response_model=Task)
def complete_task(task_id: str) -> Task:
    with connect() as connection:
        result = connection.execute(
            "UPDATE tasks SET done = 1 WHERE id = ?",
            (task_id,),
        )

        if result.rowcount == 0:
            raise HTTPException(404, "任务不存在")

        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return Task(**dict(row))


@app.delete("/tasks/{task_id}", response_model=Task)
def delete_task(task_id: str) -> Task:
    with connect() as connection:
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(404, "任务不存在")

        connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

    return Task(**dict(row))
