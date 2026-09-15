"""把 Agent Loop 接进 /chat 的协调层。

Day 1～Day 5 时，/chat 走的是 `graph.py` 的规则路由：Python 用关键词判断用户
想干什么，再决定调哪个工具。Day 6 把这条路径换成了 Agent Loop——由「模型」提出
工具调用申请，服务端负责校验和执行。

这里有两个容易被混淆的概念，代码结构上是分开的：

- **模型**只提出申请。配置了远程模型就用真模型，没配置就用 `RuleBasedLocalModel`，
  两者实现同一个 `chat_with_tools` 接口，因此 Agent Loop 和测试都不必区分它们。
- **规则**仍然由服务端掌握。提示词注入拦截放在循环之外，因为安全判断不能交给模型。
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import Settings
from ..models import AuditLog, Conversation, Message
from ..schemas import ChatResponse, PendingAction
from .agent_loop import LoopResult, build_support_registry, run_agent_loop
from .llm import OpenAICompatibleClient
from .local_model import RuleBasedLocalModel
from .rag import RAGService, SearchHit
from .security import create_confirmation_token, looks_like_prompt_injection

INJECTION_ANSWER = "该请求可能试图绕过系统规则，我不能执行。你可以继续咨询公开的业务信息。"
NO_EVIDENCE_ANSWER = "当前知识库没有找到足够可靠的依据，请补充问题信息或转人工确认。"
CONFIRMATION_ANSWER = "创建工单会产生写操作，请确认后再提交。"
# 单条历史消息最多回填多少字符，避免一次长会话把提示词撑爆。
HISTORY_MESSAGE_CHARS = 2000
# 写进审计日志的参数原文长度上限。
AUDIT_ARGUMENT_CHARS = 500


def _dedupe_hits(hits: list[SearchHit], top_k: int) -> list[SearchHit]:
    """同一个片段可能被多轮检索命中，按片段去重并按相关度取前若干条。"""
    seen: set[str] = set()
    unique: list[SearchHit] = []
    for hit in hits:
        if hit.chunk.id in seen:
            continue
        seen.add(hit.chunk.id)
        unique.append(hit)
    return sorted(unique, key=lambda item: item.score, reverse=True)[:top_k]


class SupportAgent:
    """协调会话、Agent Loop、工具、RAG、模型调用和消息持久化。"""

    def __init__(
        self, db: AsyncSession, settings: Settings, model: object | None = None
    ) -> None:
        self.db = db
        self.settings = settings
        self.rag = RAGService(db, settings.chunk_size, settings.chunk_overlap)
        self.llm = OpenAICompatibleClient(settings)
        # 远程模型三项配置齐全时才用它，否则退回本地规则模型。
        self.model = model or (self.llm if settings.llm_enabled else RuleBasedLocalModel())

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

    async def _history(self, session_id: str) -> list[dict[str, str]]:
        """读取本会话此前的消息，按时间正序返回给模型当前轮。"""
        rows = (
            await self.db.scalars(
                select(Message)
                .where(Message.session_id == session_id)
                .order_by(Message.created_at.desc(), Message.id.desc())
                .limit(self.settings.chat_history_limit)
            )
        ).all()
        return [
            {"role": item.role, "content": item.content[:HISTORY_MESSAGE_CHARS]}
            for item in reversed(rows)
        ]

    def _knowledge_searcher(self, sink: list[SearchHit]):
        """构造知识库检索工具的执行函数，同时把命中收集起来用于生成引用。"""

        async def search(query: str) -> str:
            hits = await self.rag.search(
                query,
                self.settings.retrieval_top_k,
                corpus_id=self.settings.retrieval_corpus_id,
                min_score=self.settings.retrieval_min_score,
            )
            sink.extend(hits)
            if not hits:
                return "知识库中没有找到相关依据。请如实告知用户无法回答，不要编造内容。"
            return "\n\n".join(
                f"[资料{index + 1}] {hit.chunk.content}" for index, hit in enumerate(hits)
            )

        return search

    def _confirmation(
        self, result: LoopResult, session_id: str, user_id: str, text: str
    ) -> PendingAction | None:
        """把循环里被拦下的写操作转成一次人工确认请求。"""
        for record in result.tool_calls:
            if not record.requires_confirmation:
                continue
            arguments = record.parsed or {}
            reason = arguments.get("reason") or text
            token = create_confirmation_token(
                {
                    "action": "create_ticket",
                    "session_id": session_id,
                    "user_id": user_id,
                    "order_id": arguments.get("order_id"),
                    "reason": reason,
                },
                self.settings.confirmation_secret,
            )
            return PendingAction(
                action="create_ticket",
                confirmation_token=token,
                summary=f"创建工单：{reason[:80]}",
            )
        return None

    def _audit_tool_calls(self, user_id: str, session_id: str, result: LoopResult) -> None:
        """把工具轨迹写进审计日志；消息表只保留对用户可见的对话内容。"""
        if not result.tool_calls:
            return
        self.db.add(
            AuditLog(
                actor=user_id,
                action="agent_loop_tool_calls",
                resource=session_id,
                detail={
                    "rounds": result.rounds,
                    "stopped_reason": result.stopped_reason,
                    "tools": [
                        {
                            "name": record.name,
                            "ok": record.ok,
                            "arguments": record.arguments[:AUDIT_ARGUMENT_CHARS],
                        }
                        for record in result.tool_calls
                    ],
                },
            )
        )

    async def respond(self, text: str, session_id: str | None, user_id: str) -> ChatResponse:
        """处理一轮用户消息：跑 Agent Loop，并把用户消息和最终回答一起保存。"""
        conversation = await self._conversation(session_id, user_id)
        # 历史必须在写入本轮用户消息之前读取，否则本轮问题会在上下文里出现两次。
        history = await self._history(conversation.id)
        await self._save_message(conversation.id, "user", text)

        citations: list = []
        pending_action: PendingAction | None = None

        if looks_like_prompt_injection(text):
            # 安全判断不能交给模型：即使模型被说服，这里也必须先拦下来。
            answer = INJECTION_ANSWER
            self.db.add(
                AuditLog(
                    actor=user_id, action="prompt_injection_blocked", resource=conversation.id
                )
            )
        else:
            retrieved: list[SearchHit] = []
            registry = build_support_registry(self._knowledge_searcher(retrieved))
            result = await run_agent_loop(
                self.model,
                text,
                registry=registry,
                max_rounds=self.settings.agent_max_rounds,
                history=history,
            )
            answer = result.answer
            if result.stopped_reason == "needs_confirmation":
                # 写操作没有被执行，这里只是把它换成一张确认令牌交给用户。
                pending_action = self._confirmation(result, conversation.id, user_id, text)
                if pending_action is not None:
                    answer = CONFIRMATION_ANSWER
            hits = _dedupe_hits(retrieved, self.settings.retrieval_top_k)
            citations = self.rag.citations(hits)
            searched = any(
                record.name == "search_knowledge_base" for record in result.tool_calls
            )
            if searched and not hits:
                # 检索过但没有任何依据时，服务端覆盖模型的话术，避免它凭记忆作答。
                answer = NO_EVIDENCE_ANSWER
            self._audit_tool_calls(user_id, conversation.id, result)

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
