from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_PATH = Path(__file__).with_name("tasks_orm.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH.as_posix()}"


class Base(DeclarativeBase):
    pass


class TaskRow(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(8), primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(default=False)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    done: bool


engine = create_async_engine(DATABASE_URL)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionFactory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="SQLAlchemy 任务管理器练习", lifespan=lifespan)


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    session: SessionDep,
) -> TaskRow:
    task = TaskRow(id=str(uuid4())[:8], title=payload.title)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@app.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    session: SessionDep,
) -> list[TaskRow]:
    statement = select(TaskRow).order_by(TaskRow.id)
    return list((await session.scalars(statement)).all())


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    session: SessionDep,
) -> TaskRow:
    task = await session.get(TaskRow, task_id)

    if task is None:
        raise HTTPException(404, "任务不存在")

    task.done = True
    await session.commit()
    await session.refresh(task)
    return task


@app.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task(
    task_id: str,
    session: SessionDep,
) -> TaskRow:
    task = await session.get(TaskRow, task_id)

    if task is None:
        raise HTTPException(404, "任务不存在")

    await session.delete(task)
    await session.commit()
    return task
