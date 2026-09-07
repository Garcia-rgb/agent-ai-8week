import json

from sqlalchemy.ext.asyncio import AsyncSession

from support_agent.services.evaluation import run_evaluation
from support_agent.services.rag import RAGService


async def test_evaluation_run(db_session: AsyncSession, tmp_path) -> None:
    await RAGService(db_session).ingest(
        "policy.md", "text/markdown", "退款将在三个工作日到账。".encode()
    )
    dataset = tmp_path / "dataset.jsonl"
    dataset.write_text(
        json.dumps(
            {"id": "refund-01", "question": "退款多久到账", "expected_keywords": ["三个工作日"]},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    run = await run_evaluation(db_session, dataset)
    assert run.total == 1
    assert run.passed == 1
    assert run.score == 1.0
