from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class Task(BaseModel):
    id: str
    title: str
    done: bool = False


app = FastAPI(title="任务管理器练习")
tasks: list[Task] = []


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    task = Task(id=str(uuid4())[:8], title=payload.title)
    tasks.append(task)
    return task


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    return tasks


@app.patch("/tasks/{task_id}", response_model=Task)
def complete_task(task_id: str) -> Task:
    # TODO：找到 ID 相同的任务，把 done 改为 True 并返回。
    for task in tasks:
        if task.id == task_id:
            task.done = True
            return task
    raise HTTPException(404, "任务不存在")


@app.delete("/tasks/{task_id}", response_model=Task)
def delete_task(task_id: str) -> Task:
    # TODO：找到 ID 相同的任务，从列表删除并返回。
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return task
    raise HTTPException(404, "任务不存在")

