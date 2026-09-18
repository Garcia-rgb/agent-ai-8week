"""离线评测：把评测从「只看检索」扩成三层——检索、工具选择、最终回答。

评测集每行一条 JSON 样本，字段全部可选；**声明了哪几层就评哪几层**，
没声明的层不计入分母，因此不会出现「拿没声明期望的样本来拉低某层分数」。

    {
      "id": "kv-001",
      "question": "啥是合母",
      "retrieval": {"expected_keywords": ["合母"]},
      "tools": {"expected": ["search_knowledge_base"], "forbidden": ["calculator"]},
      "answer": {"status": "completed", "answer_source": "knowledge",
                 "must_contain": ["合母"], "must_not_contain": ["无法回答"]}
    }

向后兼容：顶层直接写 `"expected_keywords"` 等价于 `retrieval.expected_keywords`，
旧的检索评测集不用改就能继续跑。

两层判定都不自己实现，而是复用线上链路：检索层调 `SupportAgent.retrieve`，
工具层和回答层调 `SupportAgent.run_turn`。这样「评测通过」和「线上行为正确」
说的是同一件事；自己抄一份判定逻辑，两边迟早会各自漂移。

只声明检索层的样本不调用模型（旧评测集仍是零模型开销）；一旦声明了工具层或
回答层就会真的跑一轮 Agent Loop，所以配置了远程模型时评测会真的产生模型调用。
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from ..config import Settings
from ..models import EvaluationRun
from .agent import SupportAgent, TurnOutcome
from .agent_loop import LoopResult
from .rag import SearchHit

# 三层的固定顺序，汇总时按它输出，避免调用方依赖字典顺序。
LAYER_NAMES = ("retrieval", "tool", "answer")


@dataclass
class Sample:
    """一条评测样本解析后的形态；空列表表示「这一层没有声明期望」。"""

    id: str
    question: str
    # 检索层
    retrieval_keywords: list[str] = field(default_factory=list)
    # 工具选择层
    expected_tools: list[str] = field(default_factory=list)
    forbidden_tools: list[str] = field(default_factory=list)
    # 最终回答层
    expected_status: str | None = None
    expected_sources: list[str] = field(default_factory=list)
    must_contain: list[str] = field(default_factory=list)
    must_not_contain: list[str] = field(default_factory=list)

    @property
    def answer_declared(self) -> bool:
        return bool(
            self.expected_status
            or self.expected_sources
            or self.must_contain
            or self.must_not_contain
        )

    @property
    def needs_agent(self) -> bool:
        """工具层或回答层有期望时才跑 Agent Loop——跑一次就是一次模型调用。"""
        return bool(self.expected_tools or self.forbidden_tools or self.answer_declared)


def parse_sample(raw: dict) -> Sample:
    """把一行样本字典解析成 `Sample`，同时兼容旧版的顶层 expected_keywords。"""
    retrieval = raw.get("retrieval") or {}
    tools = raw.get("tools") or {}
    answer = raw.get("answer") or {}
    return Sample(
        id=str(raw.get("id") or raw.get("question") or "sample"),
        question=raw["question"],
        retrieval_keywords=list(
            retrieval.get("expected_keywords") or raw.get("expected_keywords") or []
        ),
        expected_tools=list(tools.get("expected") or []),
        forbidden_tools=list(tools.get("forbidden") or []),
        expected_status=answer.get("status"),
        expected_sources=list(answer.get("answer_source") or []),
        must_contain=list(answer.get("must_contain") or []),
        must_not_contain=list(answer.get("must_not_contain") or []),
    )


def _judge_retrieval(sample: Sample, hits: list[SearchHit]) -> dict:
    if not sample.retrieval_keywords:
        return {"applicable": False, "passed": False}
    retrieved = "\n".join(hit.chunk.content for hit in hits).lower()
    missing = [word for word in sample.retrieval_keywords if word.lower() not in retrieved]
    return {
        "applicable": True,
        "passed": not missing,
        "missing_keywords": missing,
        "hit_count": len(hits),
        "top_score": round(hits[0].score, 4) if hits else 0.0,
    }


def _judge_tools(sample: Sample, loop: LoopResult | None) -> dict:
    """统计模型**选对工具**的调用，两种失败要分开看：

    - 参数校验没过 / 工具报错：模型选错了，不算数；
    - 写操作被拦下待人工确认（`ok=False` 但带 `requires_confirmation`）：
      这正是设计要的行为，算选对。
    """
    if not (sample.expected_tools or sample.forbidden_tools):
        return {"applicable": False, "passed": False}
    called = [
        record.name
        for record in (loop.tool_calls if loop else [])
        if record.ok or record.requires_confirmation
    ]
    missing = [name for name in sample.expected_tools if name not in called]
    violated = [name for name in sample.forbidden_tools if name in called]
    return {
        "applicable": True,
        "passed": not missing and not violated,
        "called": sorted(set(called)),
        "missing_tools": missing,
        "forbidden_hit": violated,
    }


def _judge_answer(sample: Sample, outcome: TurnOutcome | None) -> dict:
    if outcome is None or not sample.answer_declared:
        return {"applicable": False, "passed": False}
    reasons: list[str] = []
    if sample.expected_status and outcome.status != sample.expected_status:
        reasons.append(f"status={outcome.status}，期望 {sample.expected_status}")
    if sample.expected_sources and outcome.answer_source not in sample.expected_sources:
        reasons.append(
            f"answer_source={outcome.answer_source}，期望 {'/'.join(sample.expected_sources)}"
        )
    answer = outcome.answer.lower()
    missing = [word for word in sample.must_contain if word.lower() not in answer]
    if missing:
        reasons.append("回答缺少：" + "、".join(missing))
    unexpected = [word for word in sample.must_not_contain if word.lower() in answer]
    if unexpected:
        reasons.append("回答不该出现：" + "、".join(unexpected))
    return {
        "applicable": True,
        "passed": not reasons,
        "status": outcome.status,
        "answer_source": outcome.answer_source,
        "reasons": reasons,
    }


def summarize_layers(details: list[dict]) -> dict:
    """按层汇总通过率；没声明该层的样本不进分母。"""
    summary = {}
    for name in LAYER_NAMES:
        applicable = [item for item in details if item["layers"][name]["applicable"]]
        passed = sum(1 for item in applicable if item["layers"][name]["passed"])
        summary[name] = {
            "total": len(applicable),
            "passed": passed,
            "score": round(passed / len(applicable), 4) if applicable else 0.0,
        }
    return summary


def describe_model(settings: Settings, model: object | None) -> str:
    """记录这次评测用的是哪个模型——不同模型跑出来的分数本身不可比。"""
    if model is not None:
        return getattr(model, "name", type(model).__name__)
    return settings.llm_model if settings.llm_enabled else "rule-based-local"


async def run_evaluation(
    db: AsyncSession,
    dataset_path: Path,
    settings: Settings | None = None,
    model: object | None = None,
) -> EvaluationRun:
    """跑一次分层评测，把逐条明细和总体结果保存到数据库。

    `total/passed/score` 仍是样本口径：**三层全部通过**才算这条样本通过，
    所以只有检索层的旧评测集跑出来的数字与升级前完全一致。
    """
    if not dataset_path.exists():
        raise FileNotFoundError("评测集不存在")
    samples = [
        parse_sample(json.loads(line))
        for line in dataset_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    settings = settings or Settings()
    agent = SupportAgent(db, settings, model=model)

    details = []
    passed = 0
    for sample in samples:
        # 检索层始终评：它就是线上第一次检索的结果（同语料、同阈值、同去重）。
        hits = await agent.retrieve(sample.question)
        outcome = await agent.run_turn(sample.question, []) if sample.needs_agent else None
        layers = {
            "retrieval": _judge_retrieval(sample, hits),
            "tool": _judge_tools(sample, outcome.loop if outcome else None),
            "answer": _judge_answer(sample, outcome),
        }
        ok = all(not layer["applicable"] or layer["passed"] for layer in layers.values())
        passed += int(ok)
        details.append(
            {"id": sample.id, "question": sample.question, "passed": ok, "layers": layers}
        )

    total = len(samples)
    run = EvaluationRun(
        total=total,
        passed=passed,
        score=passed / total if total else 0.0,
        details=details,
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run
