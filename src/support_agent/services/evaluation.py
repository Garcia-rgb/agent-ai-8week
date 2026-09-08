import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import EvaluationRun
from .rag import RAGService


async def run_evaluation(db: AsyncSession, dataset_path: Path) -> EvaluationRun:
    """运行离线检索评测，并把每条样本和总体结果保存到数据库。"""
    if not dataset_path.exists():
        raise FileNotFoundError("评测集不存在")
    samples = [
        json.loads(line)
        for line in dataset_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    rag = RAGService(db)
    details = []
    passed = 0
    for sample in samples:
        hits = await rag.search(sample["question"], top_k=5)
        retrieved = "\n".join(hit.chunk.content for hit in hits).lower()
        keywords = [word.lower() for word in sample["expected_keywords"]]
        # 当前使用“预期关键词是否全部被检索到”作为最小可重复的通过标准。
        ok = all(word in retrieved for word in keywords)
        passed += int(ok)
        details.append(
            {
                "id": sample["id"],
                "passed": ok,
                "expected_keywords": keywords,
                "top_score": round(hits[0].score, 4) if hits else 0.0,
            }
        )
    total = len(samples)
    run = EvaluationRun(
        total=total, passed=passed, score=passed / total if total else 0.0, details=details
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run
