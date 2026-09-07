# 企业知识库客服 Agent｜8 周转型项目

这是一个同时用于学习、作品集和面试讲解的仓库。项目覆盖 FastAPI、数据库、RAG、LangGraph、工具调用、人工确认、安全审计、离线评测、测试和 Docker。

默认模式不需要模型 API、PostgreSQL 或 Redis：SQLite 保存数据，确定性本地模型展示检索结果。接入 OpenAI 兼容接口后，系统会基于检索资料生成回答。

## 快速开始（Windows PowerShell）

```powershell
cd D:\agent1\projects\agent-ai-8week
conda env create -f environment.yml
conda activate agent-ai-8week
Copy-Item .env.example .env
python scripts/seed.py
uvicorn support_agent.main:app --reload
```

环境已存在时，用下面的命令同步依赖：

```powershell
conda env update -f environment.yml --prune
conda activate agent-ai-8week
```

打开 <http://127.0.0.1:8000/docs> 使用 Swagger。运行测试：

```powershell
pytest -q
ruff check .
```

完整基础设施模式：

```powershell
docker compose up --build
```

## 模型配置

在 `.env` 中填写任意 OpenAI 兼容服务。不要提交真实密钥。

```dotenv
LLM_BASE_URL=https://your-provider.example/v1
LLM_API_KEY=replace-me
LLM_MODEL=your-chat-model
```

未配置这些变量时，`/chat` 会返回检索片段，适合免费开发和自动化测试。

## 架构

```mermaid
flowchart LR
    U[用户 / Swagger] --> API[FastAPI]
    API --> G[LangGraph 路由]
    G --> SAFE[安全检查]
    G --> RAG[混合检索]
    G --> TOOLS[订单/计算/工单工具]
    RAG --> PG[(PostgreSQL + pgvector)]
    RAG --> LLM[OpenAI 兼容模型]
    TOOLS --> CONFIRM[人工确认]
    CONFIRM --> AUDIT[(审计日志)]
    API --> SESSION[(会话与反馈)]
    EVAL[40 条离线评测] --> RAG
```

详细设计见 [docs/architecture.md](docs/architecture.md)。

## API

| 接口 | 用途 | 关键行为 |
|---|---|---|
| `POST /documents` | 导入 TXT、Markdown、PDF | 限制大小、校验类型、按 SHA-256 去重 |
| `POST /chat` | 会话和 Agent 工作流 | RAG、计算器、订单查询、工单意图、安全拦截 |
| `GET /sessions/{id}` | 查看会话 | 通过 `X-User-Id` 做所有权校验 |
| `POST /feedback` | 回答反馈 | 保存评分和备注 |
| `POST /tickets` | 创建模拟工单 | 必须提供十分钟内有效且未使用的确认令牌 |
| `POST /evaluations/run` | 运行离线检索评测 | 输出逐条结果和总体通过率 |

请求示例见 [docs/api_examples.http](docs/api_examples.http)。

## 仓库导航

- `course/`：8 周日程、验收与复盘问题
- `src/support_agent/`：应用代码
- `sample_data/`：可导入的演示知识库
- `evals/dataset.jsonl`：40 条固定评测样本
- `tests/`：安全、RAG、API 和工作流测试
- `docs/`：架构、简历、面试和求职追踪材料
- `examples/manual_agent.py`：不依赖 Agent 框架的工具调用边界示例

最新资源选择和框架比较见 [course/resources_2026.md](course/resources_2026.md)，第一次学习直接从 [course/tomorrow_start.md](course/tomorrow_start.md) 开始。

## 8 周总验收

- 能在不看 AI 输出的情况下解释关键代码、数据库表和每条安全边界。
- 能从零写出一个 FastAPI CRUD、SQL 查询和受控工具调用。
- 能演示文档导入、知识问答、引用、订单查询、工单确认和令牌防重放。
- 能展示 40 条评测集、失败样本和至少一次可量化优化。
- 能用 Docker Compose 启动，并清楚说明 SQLite 演示模式与 PostgreSQL 模式的差异。

本仓库是求职作品，不应直接处理真实客户数据或真实支付/退款操作。
