from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import Settings
from ..graph import build_route_graph
from ..models import AuditLog, Conversation, Message
from ..schemas import ChatResponse, PendingAction
from .llm import LLMError, OpenAICompatibleClient
from .rag import RAGService
from .security import create_confirmation_token
from .tools import ToolError, query_order, safe_calculate


class SupportAgent:
    """协调会话、路由、工具、RAG、模型调用和消息持久化。"""
    def __init__(self, db: AsyncSession, settings: Settings):
        self.db = db
        self.settings = settings
        self.rag = RAGService(db, settings.chunk_size, settings.chunk_overlap)
        self.llm = OpenAICompatibleClient(settings)
        self.graph = build_route_graph()

    async def _conversation(self, session_id: str | None, user_id: str) -> Conversation:
        """读取已有会话或创建新会话，同时检查会话归属。"""
        conversation = await self.db.get(Conversation, session_id) if session_id else None
        if conversation and conversation.user_id != user_id:
            raise PermissionError("无权访问该会话")
        if session_id and not conversation:
            raise LookupError("会话不存在")
        if not conversation:
            conversation = Conversation(user_id=user_id)
            self.db.add(conversation)
            await self.db.flush()
        return conversation

    async def _save_message(
        self, session_id: str, role: str, content: str, citations: list[dict] | None = None
    ) -> Message:
        message = Message(
            session_id=session_id, role=role, content=content, citations=citations or []
        )
        self.db.add(message)
        await self.db.flush()
        return message

    async def respond(self, text: str, session_id: str | None, user_id: str) -> ChatResponse:
        """处理一轮用户消息，并将用户消息和助手回答一起保存。"""
        conversation = await self._conversation(session_id, user_id)
        await self._save_message(conversation.id, "user", text)
        # 图只负责判断“该走哪条路”，真正的工具执行仍由 Python 代码控制。
        state = await self.graph.ainvoke({"message": text})
        route = state["route"]
        answer: str
        citations = []
        pending_action = None

        if route == "blocked":
            answer = "该请求可能试图绕过系统规则，我不能执行。你可以继续咨询公开的业务信息。"
            self.db.add(
                AuditLog(actor=user_id, action="prompt_injection_blocked", resource=conversation.id)
            )
        elif route == "calculator":
            try:
                result = safe_calculate(state.get("expression") or "")
                answer = f"计算结果：{result:g}"
            except ToolError as exc:
                answer = f"计算失败：{exc}"
        elif route == "order":
            try:
                order = query_order(state["order_id"] or "")
                answer = (
                    f"订单 {order.id} 当前状态为“{order.status}”，金额 ¥{order.amount:.2f}，"
                    f"{'支持' if order.refundable else '暂不支持'}退款。"
                )
            except ToolError as exc:
                answer = str(exc)
        elif route == "ticket":
            order_id = state.get("order_id")
            token = create_confirmation_token(
                {
                    "action": "create_ticket",
                    "session_id": conversation.id,
                    "user_id": user_id,
                    "order_id": order_id,
                    "reason": text,
                },
                self.settings.confirmation_secret,
            )
            # 创建工单会写入数据，因此这里只返回确认令牌，不立即执行。
            answer = "创建工单会产生写操作，请确认后再提交。"
            pending_action = PendingAction(
                action="create_ticket", confirmation_token=token, summary=f"创建工单：{text[:80]}"
            )
        else:
            # 知识问答先检索相关片段，再让模型依据片段组织答案。
            hits = await self.rag.search(
                text,
                self.settings.retrieval_top_k,
                corpus_id=self.settings.retrieval_corpus_id,
                min_score=self.settings.retrieval_min_score,
            )
            citations = self.rag.citations(hits)
            if not hits:
                answer = "当前知识库没有找到足够可靠的依据，请补充问题信息或转人工确认。"
            else:
                try:
                    answer = await self.llm.answer(text, [hit.chunk.content for hit in hits])
                except LLMError:
                    answer = "模型服务暂时不可用，已保留会话，请稍后重试。"

        assistant_message = await self._save_message(
            conversation.id,
            "assistant",
            answer,
            [citation.model_dump() for citation in citations],
        )
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
        return ChatResponse(
            session_id=conversation.id,
            message_id=assistant_message.id,
            answer=answer,
            citations=citations,
            pending_action=pending_action,
        )


async def get_conversation(db: AsyncSession, session_id: str, user_id: str) -> Conversation:
    conversation = await db.scalar(
        select(Conversation).where(Conversation.id == session_id, Conversation.user_id == user_id)
    )
    if not conversation:
        raise LookupError("会话不存在")
    return conversation
