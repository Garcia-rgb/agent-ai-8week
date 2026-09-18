import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .industry import build_chunk_metadata, extract_document_version

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
STRONG_HEADING_PATTERN = re.compile(r"^\*\*(.+?)\*\*(?:\s+★+)?\s*$")
PAGE_RANGE_PATTERN = re.compile(r"p(\d+)[–-](\d+)")
RESTRICTED_SECTION_TERMS = ("账号、密码与默认值", "密码重置")
SMARTPV_CORPUS_ID = "smartpv_v2"


@dataclass(frozen=True)
class KnowledgeChunk:
    """从一份知识库分卷中提取出的、带来源信息的章节。"""

    document_id: str
    document_title: str
    section_title: str
    page_start: int | None
    page_end: int | None
    source_path: Path
    content: str
    visibility: str = "local_only"
    restricted: bool = False
    # 这份分卷出自哪一版教材。标题和文件名里常常没有版本号（例如 M1 分卷），
    # 所以由导入侧从索引里读出来显式传入，避免版本冲突检测失去依据。
    document_version: str | None = None

    @property
    def metadata(self) -> dict[str, Any]:
        return build_chunk_metadata(
            document_id=self.document_id,
            document_title=self.document_title,
            section_title=self.section_title,
            source_file=self.source_path.name,
            corpus_id=SMARTPV_CORPUS_ID,
            content=self.content,
            extra={
                "page_start": self.page_start,
                "page_end": self.page_end,
                "visibility": self.visibility,
                "restricted": self.restricted,
            },
            document_version=self.document_version,
        )


def _parse_page_range(value: str | None) -> tuple[int | None, int | None]:
    match = PAGE_RANGE_PATTERN.search(value or "")
    if not match:
        return None, None
    return int(match.group(1)), int(match.group(2))


def _standalone_heading(line: str) -> str | None:
    """识别 M9/M12 中用独立粗体表示、但没有使用 ## 的小节标题。"""
    match = STRONG_HEADING_PATTERN.match(line.strip())
    return match.group(1).strip() if match else None


def split_markdown_sections(text: str) -> list[tuple[str, str]]:
    """优先按 Markdown 二级标题切分，并兼容独立粗体小节标题。"""
    lines = text.splitlines()
    has_h2 = any(
        (match := HEADING_PATTERN.match(line)) and len(match.group(1)) == 2 for line in lines
    )
    document_title = "未命名章节"
    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_lines
        content = "\n".join(current_lines).strip()
        if current_title and content:
            sections.append((current_title, current_lines.copy()))
        current_lines = []

    for line in lines:
        heading = HEADING_PATTERN.match(line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            if level == 1:
                document_title = title
                continue
            if level == 2:
                flush()
                current_title = title
                current_lines = [line]
                continue

        strong_title = _standalone_heading(line)
        if strong_title and not has_h2:
            flush()
            current_title = strong_title
            current_lines = [line]
            continue

        if current_title is not None:
            current_lines.append(line)

    flush()
    if not sections:
        body = "\n".join(lines[1:]).strip()
        return [(document_title, body)] if body else []
    return [(title, "\n".join(content).strip()) for title, content in sections]


def _load_index(index_path: Path) -> dict[str, Any]:
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"知识库索引不存在：{index_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"知识库索引不是有效 JSON：{index_path}") from exc
    if not isinstance(index.get("modules"), list) or not isinstance(index.get("appendices"), list):
        raise ValueError("知识库索引缺少 modules 或 appendices")
    return index


def load_smartpv_corpus(root: Path, *, include_restricted: bool = False) -> list[KnowledgeChunk]:
    """读取本地 SmartPV 分卷；默认排除账号密码等受限章节。"""
    index = _load_index(root / "HCSA-SmartPV-V2.0-index.json")
    split_dir = root / "HCSA-SmartPV-V2.0-知识库分卷"
    if not split_dir.is_dir():
        raise ValueError(f"知识库分卷目录不存在：{split_dir}")

    entries = [*index["modules"], *index["appendices"]]
    # 教材版本只在索引里（source / title），分卷标题和文件名都没有版本号，
    # 所以在这里抽一次，传给它下面每个章节。
    corpus_version = extract_document_version(
        str(index.get("source", "")), str(index.get("title", ""))
    )
    chunks: list[KnowledgeChunk] = []
    for entry in entries:
        document_id = str(entry.get("id", "")).strip()
        title = str(entry.get("title", "")).strip()
        if not document_id or not title:
            raise ValueError("知识库索引存在缺少 id 或 title 的条目")

        file_prefix = document_id if document_id.startswith("M") else f"附录{document_id}"
        matches = sorted(split_dir.glob(f"{file_prefix}-*.md"))
        if len(matches) != 1:
            raise ValueError(f"{document_id} 应对应一份分卷，实际找到 {len(matches)} 份")
        source_path = matches[0]
        page_start, page_end = _parse_page_range(entry.get("pages"))

        for section_title, content in split_markdown_sections(
            source_path.read_text(encoding="utf-8")
        ):
            restricted = any(term in section_title for term in RESTRICTED_SECTION_TERMS)
            if restricted and not include_restricted:
                continue
            chunks.append(
                KnowledgeChunk(
                    document_id=document_id,
                    document_title=title,
                    section_title=section_title,
                    page_start=page_start,
                    page_end=page_end,
                    source_path=source_path,
                    content=content,
                    restricted=restricted,
                    document_version=corpus_version,
                )
            )

    if not chunks:
        raise ValueError("知识库中没有可读取的章节")
    return chunks
