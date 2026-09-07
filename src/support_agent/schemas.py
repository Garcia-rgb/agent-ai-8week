from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    document_id: str
    filename: str
    chunk_id: str
    page: int | None = None
    excerpt: str
    score: float


class DocumentResponse(BaseModel):
    id: str
    filename: str
    chunks: int
    duplicate: bool = False


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = None
    user_id: str = Field(default="demo-user", min_length=1, max_length=64)


class PendingAction(BaseModel):
    action: Literal["create_ticket"]
    confirmation_token: str
    summary: str


class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    answer: str
    citations: list[Citation] = []
    pending_action: PendingAction | None = None


class MessageView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    role: str
    content: str
    citations: list[dict]
    created_at: datetime


class SessionResponse(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    messages: list[MessageView]


class FeedbackRequest(BaseModel):
    message_id: str
    rating: int = Field(ge=-1, le=1)
    comment: str | None = Field(default=None, max_length=1000)


class TicketCreateRequest(BaseModel):
    confirmation_token: str
    user_id: str = "demo-user"


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    session_id: str
    order_id: str | None
    reason: str
    status: str


class EvaluationResponse(BaseModel):
    run_id: str
    total: int
    passed: int
    score: float
    details: list[dict]
