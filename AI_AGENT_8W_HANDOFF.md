# AI Agent / AI 应用开发 8 周转型计划｜跨主机交接

## 1. 学员背景与目标

- 26 届浙江理工大学软件工程硕士，目前在品联科技工作。
- 当前工作偏测试/实施，研发经历的说服力不足；能借助 AI 做项目，但脱离 AI 后编码基本功需要加强。
- 地点优先杭州及周边，优先中小型 AI 团队，不裸辞。
- 每周可投入 20–25 小时，模型与部署预算约 100–300 元/月。
- 目标是在 8 周内达到初级 Agent / AI 应用开发岗位“可投、能面、有完整作品”的程度，不把目标设为预训练、强化学习或基础模型研究岗。

目标职业定位：

> 软件工程硕士，具备 Python 后端、大模型 API、RAG、Agent 工作流、评测与部署能力，可独立完成 AI 应用 MVP。

投递比例：

- 60%：大模型应用开发、Agent/智能体研发、生成式 AI 工程师。
- 25%：AI 后端、RAG/知识库研发、企业智能化研发。
- 15%：要求相对宽松的 LLM 应用算法岗位。

## 2. 固定技术路线

主技术栈：

`Python 3.12 + FastAPI + Pydantic + PostgreSQL/pgvector + Redis + LangGraph + pytest + Docker`

学习原则：

1. 先补 Python、SQL、HTTP、Git、Linux、数据结构，再进入 Agent 框架。
2. 先用模型 SDK 手写最小 Agent Loop，再学习 LangGraph。
3. LangGraph 是唯一要求熟练的 Agent 编排框架。
4. LlamaIndex 只吸收文档处理、检索和评测思路。
5. OpenAI Agents SDK 做最小实验并理解与 Responses API 的边界，作品项目保持模型厂商中立。
6. CrewAI、Google ADK、Microsoft Agent Framework、PydanticAI、Dify 只了解定位，不同时主修。
7. MCP 至少完成一个最小 Client/Server，并理解授权与信任边界。
8. 暂不投入微调、本地大模型部署和多 Agent 炫技，除非目标岗位明确要求。

## 3. 8 周执行计划

每周固定分配：课程/文档 4–5 小时，主项目 10–12 小时，无 AI 编码和基础题 4–5 小时，复盘/简历/面试 2–3 小时。

### 第 1 周：Python 与 HTTP

- 学习数据结构、函数、类、异常、文件、类型提示、Pydantic、HTTP/JSON、REST、Git。
- 无 AI 完成命令行任务管理器和 FastAPI CRUD。
- 验收：能独立写基础增删改查并解释数据模型。

### 第 2 周：数据库、测试与部署底座

- 学习 PostgreSQL、SQLAlchemy、事务、索引、分层设计、配置、异常处理、pytest、Mock、Docker Compose。
- 完成用户、会话、消息服务和接口测试。
- 验收：能解释事务、索引、依赖注入，并一键启动服务。

### 第 3 周：LLM 与工具调用

- 学习 Token、上下文、采样、幻觉、成本/延迟、Prompt、结构化输出、流式响应、Tool Calling、重试与限流。
- 不使用 Agent 框架，手写可调用计算器、模拟搜索、工单工具的 Agent Loop。
- 验收：工具参数经过校验，失败可重试，模型接口可替换。

### 第 4 周：RAG

- 学习解析、清洗、切块、Metadata、Embedding、BM25/混合检索、Rerank、Query Rewrite、引用和评测。
- 支持 Markdown/TXT/PDF 导入、pgvector 检索、引用回溯。
- 建立至少 40 条固定评测样本，比较切块和检索配置。

### 第 5 周：LangGraph 与 MCP

- 学习 State、Node、Edge、Checkpoint、Persistence、Interrupt、工具路由、人工确认、失败恢复。
- 把手写 Agent 改为 LangGraph 工作流，接入知识库、订单和工单工具。
- 完成最小 MCP Server/Client；高风险写操作必须人工确认。

### 第 6 周：生产化、评测与安全

- 增加 Trace、日志、Token/成本记录、Prompt/模型版本、缓存、并发、限流、权限、审计。
- 覆盖 Prompt Injection、越权工具调用和敏感信息处理。
- 接入 Phoenix、LangSmith 或同类观测方案；完成 Docker 部署和基础 CI。
- 从本周开始，每周 15–20 次针对性投递。

### 第 7 周：作品集打磨

- 完善 README、架构图、启动脚本、测试、评测报告、成本与已知限制。
- 准备 3–5 分钟演示视频。
- 验收：陌生人能在 10 分钟内启动并理解项目价值。

### 第 8 周：面试与投递

- 完成中文简历、项目深挖题、故障排查案例、Python/数据库/网络/Redis/Docker 复习。
- 完成约 30 道高频简单/中等算法题。
- 项目表达按“业务问题—架构—关键难点—评测—结果”组织。

## 4. 主项目与当前资产

主项目固定为“企业知识库客服 Agent”。原目录：`D:\202609`。

已有内容：

- 完整 8 周课程：`course/week01.md` 至 `course/week08.md`。
- 第一天执行单：`course/tomorrow_start.md`。
- 2026 年课程与框架核对：`course/resources_2026.md`。
- FastAPI 项目骨架与服务代码：`src/support_agent/`。
- SQLite 免费演示模式；可切换 PostgreSQL/pgvector、Redis。
- 文档导入、RAG、Agent、工具、安全、评测和观测模块。
- 40 条评测数据：`evals/dataset.jsonl`。
- 测试目录：`tests/`；原对话记录的基线为 15 个测试通过。
- Dockerfile、Docker Compose、种子脚本、示例文档。
- 架构、简历模板、面试题库、错误日志、项目复盘、投递追踪表。

核心接口：

- `POST /documents`：上传并索引文档。
- `POST /chat`：运行对话或 Agent 工作流。
- `GET /sessions/{id}`：查询会话与历史。
- `POST /feedback`：保存反馈。
- `POST /evaluations/run`：运行离线评测。
- `POST /tickets`：经确认令牌后创建模拟工单。

注意：当前仓库 `main` 分支还没有任何提交，所有文件处于未跟踪状态。迁移后应先检查内容，再做一次初始提交。

## 5. 新主机恢复步骤

1. 解压迁移包，并进入其中的 `202609` 目录。
2. 安装 Python 3.12、Git；如需完整基础设施，再安装 Docker Desktop。
3. 创建环境并安装依赖：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python scripts/seed.py
pytest -q
ruff check .
uvicorn support_agent.main:app --reload
```

4. 打开 `http://127.0.0.1:8000/docs` 验证 Swagger。
5. 不配置模型密钥时使用 SQLite + 本地确定性回答模式；需要真实模型时，在 `.env` 填写 OpenAI 兼容服务的 `LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL`。不要提交密钥。
6. 阅读 `README.md`、`course/README.md`、`course/tomorrow_start.md`，从 Day 1 开始。
7. 确认测试和静态检查通过后执行初始提交，例如：`git add .`、`git commit -m "chore: import 8-week agent learning project"`。

## 6. Day 1 立即执行

总时长约 2 小时 20 分钟；第一天不接模型 API、不学 LangGraph。

1. 15 分钟：确认 Python 3.12 和测试基线。
2. 45 分钟，完全禁用 AI：实现字符串稳定去重、中英文词/字频、JSON 任务保存/读取、文件不存在和 JSON 损坏处理。
3. 35 分钟：针对暴露的短板阅读 Python 官方教程中的列表、字典、函数和异常。
4. 30 分钟：阅读 `exercises/week01/task_cli.py` 与 `src/support_agent/schemas.py`，回答 dataclass 与 Pydantic 的使用差异。
5. 15 分钟：更新 `docs/error_log.md` 和 `docs/project_review.md`，口述代码 3 分钟。

每天必须保持 45–60 分钟无 AI 编码；AI 生成的代码必须能逐行解释。每周随机抽一个已完成功能，在无 AI 条件下重写核心部分。

## 7. 给另一台主机上 Codex 的接手提示词

将下列内容作为新任务的第一条消息，并同时提供本文件和解压后的项目目录：

> 请接手这个 8 周 Agent / AI 应用开发转型项目。先完整阅读 `AI_AGENT_8W_HANDOFF.md`、项目 `README.md`、`course/README.md`、`course/tomorrow_start.md` 和 `course/resources_2026.md`，再检查 Git 状态、Python 版本、依赖、测试和静态检查。不要重做已经存在的课程或项目骨架，不要擅自改变“Python 后端 + RAG + LangGraph + 评测/安全”的主线。先报告环境恢复结果和基线问题，然后从 Day 1 陪我执行；每天保留 45–60 分钟无 AI 编码。所有改动都应小步验证并记录到错误日志/项目复盘中，真实密钥不得写入仓库。

## 8. 8 周完成标准

- 一个可运行、可测试、可部署、可评测的 Agent 项目。
- 能演示文档导入、知识问答、引用、订单查询、工单确认和令牌防重放。
- 能解释 RAG、Tool Calling、Agent 状态、人工确认、失败恢复、评测和安全边界。
- 能在无 AI 条件下完成基础 Python、SQL、FastAPI 和 Tool Calling 编码。
- 一份面向 AI 应用研发的中文简历、演示视频、架构图、评测报告和投递记录。

