import hashlib
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import Settings, get_settings
from .db import create_schema, get_db
from .models import AuditLog, Conversation, Feedback, Message, Ticket
from .observability import request_observability
from .schemas import (
    ChatRequest,
    ChatResponse,
    DocumentResponse,
    EvaluationResponse,
    FeedbackRequest,
    SessionResponse,
    TicketCreateRequest,
    TicketResponse,
)
from .services.agent import SupportAgent
from .services.evaluation import run_evaluation
from .services.rag import RAGService
from .services.security import verify_confirmation_token


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用启动时创建数据库表，关闭时结束生命周期。"""
    await create_schema()
    yield


app = FastAPI(
    title="企业知识库客服 Agent",
    version="0.1.0",
    description="RAG、工具调用、人工确认、评测与审计的求职作品项目",
    lifespan=lifespan,
)
app.middleware("http")(request_observability)

DbDep = Annotated[AsyncSession, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
UploadDep = Annotated[UploadFile, File()]
UserHeader = Annotated[str, Header()]

# 上面的类型别名同时描述参数类型和 FastAPI 的依赖来源，减少接口中的重复代码。


@app.get("/health")
async def health(settings: SettingsDep) -> dict:
    return {"status": "ok", "environment": settings.app_env, "llm_enabled": settings.llm_enabled}


@app.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadDep,
    db: DbDep,
    settings: SettingsDep,
) -> DocumentResponse:
    filename = Path(file.filename or "").name
    if not filename:
        raise HTTPException(400, "文件名不能为空")
    data = await file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(413, "文件超过大小限制")
    try:
        document, chunks, duplicate = await RAGService(
            db, settings.chunk_size, settings.chunk_overlap
        ).ingest(filename, file.content_type or "application/octet-stream", data)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return DocumentResponse(
        id=document.id, filename=document.filename, chunks=chunks, duplicate=duplicate
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: DbDep,
    settings: SettingsDep,
) -> ChatResponse:
    try:
        return await SupportAgent(db, settings).respond(
            request.message, request.session_id, request.user_id
        )
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: DbDep,
    x_user_id: UserHeader = "demo-user",
) -> SessionResponse:
    conversation = await db.scalar(
        select(Conversation).where(Conversation.id == session_id, Conversation.user_id == x_user_id)
    )
    if not conversation:
        raise HTTPException(404, "会话不存在")
    messages = (
        await db.scalars(
            select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
        )
    ).all()
    return SessionResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        created_at=conversation.created_at,
        messages=messages,
    )


@app.post("/feedback", status_code=status.HTTP_201_CREATED)
async def create_feedback(request: FeedbackRequest, db: DbDep) -> dict:
    if not await db.get(Message, request.message_id):
        raise HTTPException(404, "消息不存在")
    feedback = Feedback(**request.model_dump())
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return {"id": feedback.id}


@app.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    request: TicketCreateRequest,
    db: DbDep,
    settings: SettingsDep,
) -> TicketResponse:
    try:
        payload = verify_confirmation_token(
            request.confirmation_token, settings.confirmation_secret
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if payload.get("action") != "create_ticket" or payload.get("user_id") != request.user_id:
        raise HTTPException(403, "确认令牌与当前操作或用户不匹配")
    token_hash = hashlib.sha256(request.confirmation_token.encode()).hexdigest()
    # 只保存令牌哈希并检查审计记录，防止同一个确认令牌被重复使用。
    replay = await db.scalar(
        select(AuditLog).where(
            AuditLog.action == "confirmation_consumed", AuditLog.resource == token_hash
        )
    )
    if replay:
        raise HTTPException(409, "确认令牌已经使用")
    ticket = Ticket(
        session_id=payload["session_id"],
        order_id=payload.get("order_id"),
        reason=payload["reason"],
    )
    db.add(ticket)
    await db.flush()
    db.add(
        AuditLog(
            actor=request.user_id,
            action="confirmation_consumed",
            resource=token_hash,
            detail={"ticket_id": ticket.id},
        )
    )
    await db.commit()
    await db.refresh(ticket)
    return ticket


@app.post("/evaluations/run", response_model=EvaluationResponse)
async def evaluation(db: DbDep) -> EvaluationResponse:
    try:
        run = await run_evaluation(db, Path("evals/dataset.jsonl"))
    except FileNotFoundError as exc:
        raise HTTPException(500, str(exc)) from exc
    return EvaluationResponse(
        run_id=run.id,
        total=run.total,
        passed=run.passed,
        score=run.score,
        details=run.details,
    )
