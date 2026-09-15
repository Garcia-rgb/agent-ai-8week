from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import DocumentChunk, SourceDocument
from ..schemas import Citation
from .documents import PageText, checksum, chunk_pages, extract_pages
from .embeddings import cosine_similarity, local_embedding, tokenize
from .knowledge_base import KnowledgeChunk, load_smartpv_corpus

QUERY_FILLERS = ("请问", "是什么", "是啥", "如何处理", "怎么处理", "怎么办", "怎么解决")


@dataclass(frozen=True)
class SearchHit:
    """一次检索命中，包含文本片段、来源文档和相关度分数。"""
    chunk: DocumentChunk
    document: SourceDocument
    score: float


@dataclass(frozen=True)
class CorpusIngestReport:
    """一次目录知识库导入的汇总结果。"""

    documents_created: int
    documents_skipped: int
    sections: int
    chunks_created: int


class RAGService:
    """负责文档入库、切块、向量生成、检索和引用格式转换。"""
    def __init__(self, db: AsyncSession, chunk_size: int = 700, overlap: int = 100):
        self.db = db
        self.chunk_size = chunk_size
        self.overlap = overlap

    async def ingest(
        self, filename: str, content_type: str, data: bytes
    ) -> tuple[SourceDocument, int, bool]:
        """导入文档；相同内容通过校验和去重，不重复生成文本片段。"""
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

    async def ingest_smartpv_corpus(
        self, root: Path, *, include_restricted: bool = False
    ) -> CorpusIngestReport:
        """把本地 SmartPV 分卷按章节导入数据库，并保留检索元数据。"""
        sections = load_smartpv_corpus(root, include_restricted=include_restricted)
        by_source: dict[Path, list[KnowledgeChunk]] = defaultdict(list)
        for section in sections:
            by_source[section.source_path].append(section)

        documents_created = 0
        documents_skipped = 0
        chunks_created = 0
        for source_path, source_sections in by_source.items():
            data = source_path.read_bytes()
            digest = checksum(data)
            existing = await self.db.scalar(
                select(SourceDocument).where(SourceDocument.checksum == digest)
            )
            if existing:
                documents_skipped += 1
                continue

            document = SourceDocument(
                filename=source_path.name,
                content_type="text/markdown",
                checksum=digest,
            )
            self.db.add(document)
            await self.db.flush()
            documents_created += 1

            position = 0
            for section in source_sections:
                pieces = chunk_pages(
                    [PageText(page=section.page_start, text=section.content)],
                    self.chunk_size,
                    self.overlap,
                )
                for piece in pieces:
                    self.db.add(
                        DocumentChunk(
                            document_id=document.id,
                            position=position,
                            page=piece.page,
                            content=piece.text,
                            chunk_metadata=section.metadata,
                            embedding=local_embedding(piece.text),
                        )
                    )
                    position += 1
                    chunks_created += 1

        await self.db.commit()
        return CorpusIngestReport(
            documents_created=documents_created,
            documents_skipped=documents_skipped,
            sections=len(sections),
            chunks_created=chunks_created,
        )

    async def search(
        self,
        query: str,
        top_k: int = 5,
        *,
        corpus_id: str | None = None,
        include_restricted: bool = False,
        min_score: float = 0.0,
    ) -> list[SearchHit]:
        """在指定语料库和权限范围内进行混合检索。"""
        rows = (
            await self.db.execute(
                select(DocumentChunk, SourceDocument).join(
                    SourceDocument, SourceDocument.id == DocumentChunk.document_id
                )
            )
        ).all()
        normalized_query = query
        for filler in QUERY_FILLERS:
            normalized_query = normalized_query.replace(filler, "")
        normalized_query = normalized_query.strip() or query
        query_embedding = local_embedding(normalized_query)
        query_terms = Counter(tokenize(normalized_query))
        hits: list[SearchHit] = []
        for chunk, document in rows:
            metadata = chunk.chunk_metadata or {}
            if corpus_id and metadata.get("corpus_id") != corpus_id:
                continue
            if not include_restricted and metadata.get("restricted") is True:
                continue
            chunk_terms = Counter(tokenize(chunk.content))
            overlap = sum(
                min(count, chunk_terms.get(term, 0)) for term, count in query_terms.items()
            )
            lexical = overlap / max(sum(query_terms.values()), 1)
            semantic = max(cosine_similarity(query_embedding, list(chunk.embedding)), 0.0)
            # 当前权重用于教学演示；生产环境应通过评测集调参，并设置最低分阈值。
            score = 0.55 * lexical + 0.45 * semantic
            if score > 0 and score >= min_score:
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
