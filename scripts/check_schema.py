"""对比「代码里的表定义」与「数据库里实际的表结构」。

为什么需要它：`create_all` 只会补建缺失的表，**不会修改已存在表的列名**。
把某个列改名（例如 `tickets.order_id` → `tickets.device_sn`）之后，SQLite 那边
重建过库就没事，而 PostgreSQL 走的是命名卷 `postgres_data`，表结构会一直停在
旧版本，直到某次写入才炸出一个 500。这个脚本把那种漂移提前暴露出来。

用法：

    python scripts/check_schema.py                  # 检查当前 DATABASE_URL
    docker exec -i agent-ai-8week-api-1 python - < scripts/check_schema.py

有漂移时退出码为 1，可以直接串进 CI 或部署前检查。
"""

import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import inspect  # noqa: E402

from support_agent import models  # noqa: E402,F401  导入才会把表登记进 metadata
from support_agent.db import Base, engine  # noqa: E402


async def main() -> int:
    async with engine.connect() as conn:

        def check(sync_conn):
            insp = inspect(sync_conn)
            db_tables = set(insp.get_table_names())
            declared = {t.name for t in Base.metadata.sorted_tables}
            problems: list[str] = []

            for table in Base.metadata.sorted_tables:
                if table.name not in db_tables:
                    problems.append(f"[缺表  ] {table.name}")
                    continue
                db_cols = {c["name"] for c in insp.get_columns(table.name)}
                md_cols = {c.name for c in table.columns}
                missing = sorted(md_cols - db_cols)
                extra = sorted(db_cols - md_cols)
                if missing or extra:
                    problems.append(f"[列漂移] {table.name}: 库里缺 {missing}｜库里多 {extra}")
                    for col in missing:
                        for cand in extra:
                            problems.append(
                                f"         可能的重命名（确认后再执行）："
                                f"ALTER TABLE {table.name} RENAME COLUMN {cand} TO {col};"
                            )

            extra_tables = sorted(db_tables - declared)
            if extra_tables:
                problems.append(f"[多余表] {extra_tables}（代码里已无对应模型）")

            print(f"声明表 {len(declared)} 张，库内表 {len(db_tables)} 张")
            if problems:
                print("\n".join(problems))
                print(f"\n发现 {len(problems)} 个问题：列名变更不会由 create_all 自动应用。")
                return 1
            print("表结构一致，无漂移。")
            return 0

        return await conn.run_sync(check)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
