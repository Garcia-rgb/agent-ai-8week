import os
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from support_agent.config import EMBEDDING_DIMENSIONS, Settings
from support_agent.models import DocumentChunk, SourceDocument
from support_agent.services.embeddings import local_embedding
from support_agent.services.rag import RAGService
from support_agent.services.semantic import (
    EmbeddingBackend,
    EmbeddingUnavailableError,
    HashEmbeddingBackend,
    build_embedding_backend,
    get_embedding_backend,
    reset_embedding_backends,
)

# 语义模型不进仓库，CI 上也没有。需要覆盖 ONNX 路径时显式给路径：
#   SEMANTIC_MODEL_PATH=D:\...\models\bge-small-zh-v1.5 pytest tests/test_semantic.py
SEMANTIC_MODEL_PATH = os.environ.get("SEMANTIC_MODEL_PATH")


class _ConstantBackend(EmbeddingBackend):
    """每条文本都返回同一个向量，用来把「语义分」钉成一个已知值。"""

    def __init__(self, dimension: int):
        self.name = "constant"
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts):
        vector = [1.0] + [0.0] * (self._dimension - 1)
        return [list(vector) for _ in texts]


def test_hash_backend_dimension_and_normalization() -> None:
    backend = HashEmbeddingBackend(384)
    vector = backend.embed(["储能电池的容量怎么算"])[0]
    assert backend.dimension == 384
    assert len(vector) == 384
    # 归一化后点积才等于余弦相似度，这是检索侧比较向量的前提。
    assert sum(value * value for value in vector) == pytest.approx(1.0)
    assert backend.signature == "hash:384"


def test_hash_backend_returns_stable_vectors() -> None:
    """同一个后端两次算同一条文本必须一致，否则库里存的向量第二天就失效了。"""
    backend = HashEmbeddingBackend(384)
    assert backend.embed(["合母和控母的区别"]) == backend.embed(["合母和控母的区别"])


def test_backends_handle_empty_input() -> None:
    assert HashEmbeddingBackend(384).embed([]) == []


def test_default_backend_does_not_trust_semantic_channel() -> None:
    """哈希向量必须打折：字符碰撞出来的「相似」不能当语义分用。"""
    assert HashEmbeddingBackend(384).semantic_trust_floor < 1.0
    assert EmbeddingBackend.semantic_trust_floor == 1.0


def test_unknown_backend_raises() -> None:
    with pytest.raises(EmbeddingUnavailableError, match="未知的 embedding 后端"):
        build_embedding_backend(Settings(embedding_backend="magic"))


def test_onnx_backend_requires_model_path() -> None:
    with pytest.raises(EmbeddingUnavailableError, match="EMBEDDING_MODEL_PATH"):
        build_embedding_backend(Settings(embedding_backend="onnx", embedding_model_path=None))


def test_onnx_backend_reports_incomplete_model_dir(tmp_path: Path) -> None:
    """配置写了 onnx 就该按 onnx 跑，文件不全要报错，不能悄悄退回哈希向量。"""
    with pytest.raises(EmbeddingUnavailableError, match="模型目录不完整"):
        build_embedding_backend(
            Settings(embedding_backend="onnx", embedding_model_path=str(tmp_path))
        )


@pytest.mark.skipif(not SEMANTIC_MODEL_PATH, reason="未提供 SEMANTIC_MODEL_PATH，跳过真实模型")
def test_onnx_backend_loads_real_model() -> None:
    backend = build_embedding_backend(
        Settings(embedding_backend="onnx", embedding_model_path=SEMANTIC_MODEL_PATH)
    )
    assert backend.dimension == EMBEDDING_DIMENSIONS["onnx"]
    assert backend.signature == "onnx:512"

    query = backend.embed(["逆变器 RS485 通讯异常怎么排查"])[0]
    related = backend.embed(["检查通讯地址、波特率与校验位是否与后台一致"])[0]
    unrelated = backend.embed(["组件热斑会导致输出功率下降"])[0]

    def dot(left: list[float], right: list[float]) -> float:
        return sum(x * y for x, y in zip(left, right, strict=True))

    # 语义模型的判断标准不是分数高低，而是「相关 > 无关」这个顺序。
    assert dot(query, related) > dot(query, unrelated)


def test_vector_dimension_follows_backend() -> None:
    assert Settings(embedding_backend="hash").vector_dimension == 384
    assert Settings(embedding_backend="onnx").vector_dimension == 512
    # 显式配置优先，便于换用别的模型。
    assert Settings(embedding_backend="onnx", embedding_dimension=768).vector_dimension == 768


def test_backend_is_cached_per_configuration() -> None:
    """模型加载要几百毫秒，同一种配置不能每次请求都重新加载。"""
    reset_embedding_backends()
    first = get_embedding_backend(Settings(embedding_backend="hash"))
    assert get_embedding_backend(Settings(embedding_backend="hash")) is first
    # 换个维度就是另一种配置，必须换实例——否则会拿到维度不对的后端。
    other = get_embedding_backend(Settings(embedding_backend="hash", embedding_dimension=64))
    assert other is not first
    reset_embedding_backends()


async def _add_vector_chunk(db: AsyncSession, content: str) -> None:
    """落一条向量已知的片段：与 `_ConstantBackend` 的向量点积正好是 1。"""
    document = SourceDocument(filename="modbus.md", content_type="text/markdown", checksum=content)
    db.add(document)
    await db.flush()
    db.add(
        DocumentChunk(
            document_id=document.id,
            position=0,
            content=content,
            chunk_metadata={},
            embedding=[1.0] + [0.0] * (EMBEDDING_DIMENSIONS["hash"] - 1),
        )
    )
    await db.commit()


async def test_search_ignores_stored_vectors_of_other_dimension(
    db_session: AsyncSession,
) -> None:
    """库里的向量和当前后端维度不一致时，语义那一路必须记 0。

    余弦相似度按较短的向量截断，384 维的旧向量遇到 512 维的查询会静默算出一个
    看着正常的假分数——宁可不用这一路，也不能拿假分数排序。
    """
    await _add_vector_chunk(db_session, "合母与控母分别给不同母线供电。")

    matched = RAGService(db_session, backend=_ConstantBackend(384))
    mismatched = RAGService(db_session, backend=_ConstantBackend(64))
    same = await matched.search("控母是什么")
    other = await mismatched.search("控母是什么")

    assert same and other
    assert same[0].score > other[0].score


async def test_ingest_records_backend_signature(db_session: AsyncSession) -> None:
    """片段记下建库用的后端，换后端后能不能查得出来全靠它。"""
    rag = RAGService(db_session, backend=HashEmbeddingBackend(384))
    document, _, _ = await rag.ingest("alarm.md", "text/markdown", "绝缘阻抗低告警 2062。".encode())
    chunk = await db_session.scalar(
        select(DocumentChunk).where(DocumentChunk.document_id == document.id)
    )
    assert chunk is not None
    assert chunk.chunk_metadata["embedding_signature"] == "hash:384"
    assert len(chunk.embedding) == 384


async def test_ingested_vectors_come_from_the_backend(db_session: AsyncSession) -> None:
    """入库必须用注入的后端，而不是写死哈希向量。"""
    rag = RAGService(db_session, backend=_ConstantBackend(16))
    document, _, _ = await rag.ingest("tiny.md", "text/markdown", "合母电压。"[:8].encode())
    chunk = await db_session.scalar(
        select(DocumentChunk).where(DocumentChunk.document_id == document.id)
    )
    assert chunk is not None
    assert len(chunk.embedding) == 16


def test_local_embedding_still_available_for_compatibility() -> None:
    """哈希向量仍在原处：库里 384 维的旧数据还要靠它读得懂。"""
    assert len(local_embedding("合母")) == EMBEDDING_DIMENSIONS["hash"]
