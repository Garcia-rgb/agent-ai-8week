from sqlalchemy.ext.asyncio import AsyncSession

from support_agent.services.rag import RAGService


async def test_ingest_deduplicate_and_search(db_session: AsyncSession) -> None:
    rag = RAGService(db_session, chunk_size=40, overlap=5)
    data = "七天无理由退款。已发货订单需要先拒收，退款在三个工作日内到账。".encode()
    document, count, duplicate = await rag.ingest("refund.md", "text/markdown", data)
    assert count > 0
    assert duplicate is False

    same_document, same_count, duplicate = await rag.ingest("refund.md", "text/markdown", data)
    assert same_document.id == document.id
    assert same_count == count
    assert duplicate is True

    hits = await rag.search("退款多久到账")
    assert hits
    assert "三个工作日" in hits[0].chunk.content
