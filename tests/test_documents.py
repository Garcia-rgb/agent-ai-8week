import pytest

from support_agent.services.documents import PageText, chunk_pages, extract_pages


def test_extract_utf8_text() -> None:
    pages = extract_pages("manual.md", "告警处理".encode())
    assert pages == [PageText(page=None, text="告警处理")]


def test_reject_unsupported_file() -> None:
    with pytest.raises(ValueError, match="仅支持"):
        extract_pages("data.csv", b"a,b")


def test_chunks_overlap() -> None:
    chunks = chunk_pages([PageText(page=1, text="abcdefghij")], chunk_size=6, overlap=2)
    assert [chunk.text for chunk in chunks] == ["abcdef", "efghij"]
