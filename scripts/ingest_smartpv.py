import argparse
import asyncio
import os
from pathlib import Path

from support_agent.db import SessionFactory, create_schema
from support_agent.services.rag import RAGService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导入本地 SmartPV Markdown 知识库")
    parser.add_argument(
        "--source",
        type=Path,
        default=os.getenv("SMARTPV_KB_PATH"),
        help="包含 index.json 和知识库分卷目录的本地路径",
    )
    parser.add_argument(
        "--include-restricted",
        action="store_true",
        help="显式导入账号密码、密码重置等受限章节",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    if args.source is None:
        raise SystemExit("请使用 --source 指定本地知识库路径")

    await create_schema()
    async with SessionFactory() as db:
        report = await RAGService(db).ingest_smartpv_corpus(
            args.source,
            include_restricted=args.include_restricted,
        )
    print(
        "导入完成："
        f"新文档 {report.documents_created}，"
        f"跳过 {report.documents_skipped}，"
        f"章节 {report.sections}，"
        f"检索片段 {report.chunks_created}"
    )


if __name__ == "__main__":
    asyncio.run(main())
