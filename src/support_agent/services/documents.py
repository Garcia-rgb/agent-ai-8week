import hashlib
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class PageText:
    page: int | None
    text: str


SUPPORTED_SUFFIXES = {".txt", ".md", ".pdf"}


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_pages(filename: str, data: bytes) -> list[PageText]:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError("仅支持 .txt、.md 和 .pdf 文件")
    if suffix == ".pdf":
        reader = PdfReader(BytesIO(data))
        return [
            PageText(page=index + 1, text=page.extract_text() or "")
            for index, page in enumerate(reader.pages)
        ]
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("文本文件必须使用 UTF-8 编码") from exc
    return [PageText(page=None, text=text)]


def chunk_pages(pages: list[PageText], chunk_size: int = 700, overlap: int = 100) -> list[PageText]:
    if chunk_size <= overlap or overlap < 0:
        raise ValueError("chunk_size 必须大于 overlap")
    chunks: list[PageText] = []
    step = chunk_size - overlap
    for page in pages:
        normalized = "\n".join(line.strip() for line in page.text.splitlines() if line.strip())
        for start in range(0, len(normalized), step):
            content = normalized[start : start + chunk_size].strip()
            if content:
                chunks.append(PageText(page=page.page, text=content))
            if start + chunk_size >= len(normalized):
                break
    return chunks
