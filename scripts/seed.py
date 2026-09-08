import asyncio
import mimetypes
from pathlib import Path

from support_agent.db import SessionFactory, create_schema
from support_agent.services.rag import RAGService


async def main() -> None:
    """把 sample_data 目录中的示例文档批量导入知识库。"""
    await create_schema()
    async with SessionFactory() as db:
        for path in Path("sample_data").glob("*.*"):
            content_type = mimetypes.guess_type(path.name)[0] or "text/plain"
            document, chunks, duplicate = await RAGService(db).ingest(
                path.name, content_type, path.read_bytes()
            )
            print(document.id, path.name, chunks, "duplicate" if duplicate else "created")


if __name__ == "__main__":
    asyncio.run(main())
