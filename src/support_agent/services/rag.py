from collections import Counter
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import DocumentChunk, SourceDocument
from ..schemas import Citation
from .documents import checksum, chunk_pages, extract_pages
from .embeddings import cosine_similarity, local_embedding, tokenize


@dataclass(frozen=True)
class SearchHit:
    chunk: DocumentChunk
    document: SourceDocument
    score: float


class RAGService:
    def __init__(self, db: AsyncSession, chunk_size: int = 700, overlap: int = 100):
        self.db = db
        self.chunk_size = chunk_size
        self.overlap = overlap

    async def ingest(
        self, filename: str, content_type: str, data: bytes
    ) -> tuple[SourceDocument, int, bool]:
        digest = checksum(data)
        existing = await self.db.scalar(
            select(SourceDocument).where(SourceDocument.checksum == digest)
        )
        if existing:
            count_result = await self.db.scalars(
                select(DocumentChunk).where(DocumentChunk.document_id == existing.id)
            )
            return existing, len(count_result.all()), True

        pages = extract_pages(filename, data)
        pieces = chunk_pages(pages, self.chunk_size, self.overlap)
        if not pieces:
            raise ValueError("文件中没有可索引的文本")
        document = SourceDocument(filename=filename, content_type=content_type, checksum=digest)
        self.db.add(document)
        await self.db.flush()
        for position, piece in enumerate(pieces):
            self.db.add(
                DocumentChunk(
                    document_id=document.id,
                    position=position,
                    page=piece.page,
                    content=piece.text,
                    chunk_metadata={"filename": filename},
                    embedding=local_embedding(piece.text),
                )
            )
        await self.db.commit()
        return document, len(pieces), False

    async def search(self, query: str, top_k: int = 5) -> list[SearchHit]:
        rows = (
            await self.db.execute(
                select(DocumentChunk, SourceDocument).join(
                    SourceDocument, SourceDocument.id == DocumentChunk.document_id
                )
            )
        ).all()
        query_embedding = local_embedding(query)
        query_terms = Counter(tokenize(query))
        hits: list[SearchHit] = []
        for chunk, document in rows:
            chunk_terms = Counter(tokenize(chunk.content))
            overlap = sum(
                min(count, chunk_terms.get(term, 0)) for term, count in query_terms.items()
            )
            lexical = overlap / max(sum(query_terms.values()), 1)
            semantic = max(cosine_similarity(query_embedding, list(chunk.embedding)), 0.0)
            score = 0.55 * lexical + 0.45 * semantic
            if score > 0:
                hits.append(SearchHit(chunk, document, score))
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:top_k]

    @staticmethod
    def citations(hits: list[SearchHit]) -> list[Citation]:
        return [
            Citation(
                document_id=hit.document.id,
                filename=hit.document.filename,
                chunk_id=hit.chunk.id,
                page=hit.chunk.page,
                excerpt=hit.chunk.content[:240],
                score=round(hit.score, 4),
            )
            for hit in hits
        ]
