# AI Agent / AI 应用开发 8 周转型计划｜跨主机交接

> 更新日期：2026-09-11
> 用途：在另一台主机继续本项目和学习对话。新 Codex 应先读本文件，再读 `LEARNING_README.md`、`README.md` 和 `course/README.md`。

## 学员目标与学习策略

- 目标方向：初级 Agent / AI 应用开发、AI 后端、RAG/企业知识库研发。
- 当前重点：建立 Python 后端、大模型 API、RAG、Agent 工作流、评测与部署能力，形成可以演示和面试讲解的完整作品。
- 不把预训练、强化学习、基础模型研究或多 Agent 炫技作为当前主线。
- 学习策略：先完成项目全貌第一遍，再压缩回顾第 1 周，随后从第 2 周开始正式动手。

## 1. 项目位置与 Git 状态

- GitHub：`https://github.com/Garcia-rgb/agent-ai-8week.git`
- 主分支：`main`
- 当前项目：企业知识库客服 Agent，兼作 8 周学习、作品集和面试项目。
- 当前主机目录：`D:\agent1\projects\agent-ai-8week`
- 本地开发默认使用 SQLite；真实模型、PostgreSQL、Redis 和 Docker 都不是启动必需条件。
- `.env` 和本地数据库不进入 Git；新主机需要从 `.env.example` 创建自己的 `.env`。

另一台主机已有仓库时：

```powershell
git pull
conda env update -f environment.yml --prune
```

第一次获取时：

```powershell
git clone https://github.com/Garcia-rgb/agent-ai-8week.git
cd agent-ai-8week
conda env create -f environment.yml
Copy-Item .env.example .env
conda run -n agent-ai-8week python scripts/seed.py
conda run -n agent-ai-8week python -m pytest -q
```

不要复制当前主机的 Miniconda 环境目录，也不要提交或传输真实 API Key。

## 2. 当前主机环境记录

- IDE：PyCharm
- Miniconda：`C:\Users\14374\miniconda3`
- Conda 环境：`agent-ai-8week`
- Python：3.12
- PyCharm 解释器：`C:\Users\14374\miniconda3\envs\agent-ai-8week\python.exe`
- 当前全量基线：23 个测试通过，Ruff 检查通过。
- PowerShell 的配置脚本受执行策略限制，终端可能无法直接识别 `conda`。PyCharm 选对解释器后直接使用 `python` 即可；也可以使用 `conda run -n agent-ai-8week ...`。
- 2026-09-09 Windows 企业代码完整性策略曾阻止 conda-forge 的 OpenSSL 3.6.4；已用本机缓存的 defaults OpenSSL 3.5.7 离线修复。当前主机暂不执行 `conda env update -f environment.yml --prune`，避免恢复被拦截的 DLL。
- 2026-09-11 已重新安装并验证 Docker Desktop；Compose 可正常启动 API、PostgreSQL/pgvector 和 Redis，三个容器均通过健康检查。
- Docker 本机镜像、容器、Volume 和 Docker Desktop 安装不进入 Git；跨主机只同步 Dockerfile、Compose 配置、样例数据和代码，新主机需自行安装 Docker Desktop 并重新构建。

常用命令：

```powershell
python --version
python -m pytest -q
python -m ruff check .
python -m uvicorn support_agent.main:app --reload
```

Swagger：`http://127.0.0.1:8000/docs`

## 3. 用户的学习目标与偏好

- 用户使用 PyCharm，本阶段目标是快速建立 AI Agent 项目的整体认识，然后通过动手逐渐补齐编码能力。
- 使用中文教学，先讲用途和流程；除非出现错误或关键点，不需要逐行展开 Python 语法。
- 用户目前能够跟着示例修改、运行和观察结果，但从空白独立写完整代码仍有困难。
- 不要把“已经讲过”当成“已经独立掌握”。要明确区分概念预览、跟做成功和独立验收。
- 用户认可先讲完整项目全貌，再快速回顾第 1 周，随后从第 2 周进入更正式的动手学习。
- 第 1 周不要耗费太久：用一个小型 FastAPI 任务 CRUD 在 1～2 个学习回合内压缩验收，基础语法随用随补。
- 教学节奏宜短：讲一个概念，给一个可观察的小实验，再让用户说出自己的判断。

## 4. 已完成的环境与项目工作

- 从旧主机传输包恢复并整理了项目。
- 删除了用户不再需要的旧 `bookstore` 项目和旧资料；没有继续处理旧的 `agent1` 远端仓库。
- 为本项目建立独立 Git 仓库，后续已连接到 `Garcia-rgb/agent-ai-8week`。
- 安装 Miniconda，创建 `agent-ai-8week` 环境，安装项目及开发依赖。
- 创建本地 `.env`，使用 SQLite 和确定性本地回答模式。
- 运行种子脚本、测试和 Ruff 检查。
- 用户已经在 PyCharm 中成功运行 CLI 和 FastAPI/Swagger。

## 5. 已讲解和体验的内容

### Python 与 FastAPI 基础

- `list`、`dict`、循环、函数、类型提示和异常的基本作用。
- JSON 保存/读取；曾出现保存 `tasks.json` 却读取 `task.json` 的路径不一致问题。
- `dataclass` 用于内部简单对象，Pydantic 用于 API 输入输出和运行时校验。
- CLI 任务管理器的 `add`、`list`、`done`、`delete` 四个命令。
- `class`、`self`、`__init__`、argparse 和程序入口的概念。
- HTTP 方法、常见状态码、FastAPI 路由和 Swagger。

### 项目接口

- `GET /health`
- `POST /documents`
- `POST /chat`
- `GET /sessions/{session_id}`
- `POST /feedback`
- `POST /tickets`
- `POST /evaluations/run`

### Agent 项目全貌

- 当前路由主要由固定规则驱动，不是 LLM 自主识别意图。
- 计算器使用受限 AST 实时计算，不是固定答案，也没有使用危险的 `eval()`。
- 订单查询使用模拟订单数据。
- 创建工单需要确认令牌，并检查签名、有效期和防重放。
- 当前 LangGraph 是规则驱动的一步工作流，不是持续自主循环的 Agent。
- 真正 Tool Calling 的基本流程：模型提出工具和参数，服务端校验并执行，再把结果交回模型。
- Agent Loop 必须限制轮数、工具白名单、权限和写操作确认。

### RAG

- 文档解析、切块、块大小 700、重叠 100。
- 当前本地 Hash Embedding 为 384 维，适合免费演示，但语义能力弱。
- 混合检索分数：词面匹配 0.55 + 向量匹配 0.45，默认 Top-K 为 5。
- 用户亲自观察到：原词查询分数最高，同义表达略低，无关问题最低。
- 已解释 Embedding 负责找资料，LLM 负责组织回答。
- 当前 `EMBEDDING_MODEL` 配置尚未接入实际检索实现；检索仍使用本地 Hash Embedding。

### 会话、状态与可靠性

- 区分聊天历史、Agent 临时状态和长期用户记忆。
- 当前项目会保存会话，但不会把历史重新送入回答和路由，因此还不具备真正的语义记忆。
- 已讲上下文窗口、摘要、检索和结构化状态。
- 已讲超时、重试、幂等和降级；当前 LLM 客户端为 30 秒超时，没有自动重试。
- 已讲结构化请求日志：`request_id`、路径、状态码和 `duration_ms`。
- 当前日志能看整个 HTTP 请求耗时，还不能细分检索、数据库、工具和模型各阶段耗时。

### 评测

- 最近一节刚讲完 `src/support_agent/services/evaluation.py`。
- 当前 40 条离线样本只评测检索：检查 Top-5 片段是否包含全部预期关键词。
- 已区分单题 `top_score` 与总体通过率 `score`。
- 已指出限制：即使检索资料正确但模型回答错误，当前评测仍可能通过。
- 完整评测应该拆成检索、工具选择/参数和最终回答三层。

### 安全与审计（2026-09-08 已完成第一轮讲解与实操）

- 用户通过 Swagger 亲自验证了工单二次确认：首次提交返回 `201`，相同确认令牌重复提交返回 `409`。
- 已理解执行层是高风险操作的最后防线；模型提示词和检索过滤可能被绕过，写操作仍须在工具执行层校验权限、参数和人工确认。
- 用户通过 Swagger 验证了会话所有权隔离：`u1` 可读取自己的会话，`u2` 使用相同会话 ID 时返回 `404`，避免泄露资源是否存在。
- 用户观察了敏感信息处理差异：结构化 HTTP 日志不记录请求正文，但当前数据库会原样保存聊天中的测试手机号；已理解入库及发送外部模型前应按需脱敏。
- 已理解审计日志应记录内部用户 ID、动作、资源 ID、时间和结果；完整确认令牌与 API Key 不应原样记录，投诉正文应按需摘要或脱敏。
- 上述内容属于概念理解和引导下实操，尚未独立实现安全功能。

## 6. 掌握程度（务必如实对待）

- 环境操作与运行命令：能够在指导下完成。
- CLI 四个命令和 Swagger：已经实际使用。
- Python/FastAPI 基础：理解一般，尚不能稳定从空白独立完成 CRUD。
- LLM、RAG、Agent、上下文、可靠性：完成第一轮概念预览，能够判断一些现象，但尚未完成正式实现和验收。
- 数据库：已在引导下完成原生 SQLite 和异步 SQLAlchemy CRUD、索引观察、事务、约束、外键和依赖注入，尚不能无提示独立重写。
- 测试：已完成 Fixture、依赖替换、Mock、API 分页测试和事务回滚测试的第一轮实操；LangGraph、评测仍主要是读过现有实现并理解大意。

因此不能简单记录为“学到第 6 周”。更准确的说法是：

> 项目全貌第一遍和压缩版第 1 周已完成；第 2 周 Day 1～Day 6 已完成第一轮讲解与实操，下一步进行 Day 7 无 AI 复盘与验收。

## 7. 约定的后续顺序

### 阶段 A：项目全貌第一遍（已完成）

已经讲完测试体系、Docker/健康检查/CI、项目演示和面试表达。此阶段以理解和引导下实操为主，不视为已经独立掌握。

### 阶段 B：压缩回顾第 1 周（已完成）

用内存或 JSON 实现最小 FastAPI 任务管理器：

```text
POST   /tasks
GET    /tasks
PATCH  /tasks/{id}
DELETE /tasks/{id}
```

已经新增 `exercises/week01/task_api.py`，用户在骨架上完成 PATCH 和 DELETE 的核心逻辑；新增 `tests/test_task_api_exercise.py`。练习测试 `2 passed`，全量测试 `17 passed`。用户能够说明请求、校验、状态码和 CRUD 的基本对应关系，但仍不视为完全闭卷掌握。

### 阶段 C：从第 2 周正式动手

当前已完成 SQLite/SQLAlchemy CRUD、查询、索引、事务、约束、外键、依赖注入、pytest Fixture/Mock、会话分页、事务回滚和 Docker Compose 的第一轮实操，新增或修改：

- `exercises/week02/task_api_sqlite.py`
- `exercises/week02/task_api_sqlalchemy.py`
- `tests/test_task_api_sqlite_exercise.py`
- `tests/test_task_api_sqlalchemy_exercise.py`
- `tests/test_sessions_api.py`
- `tests/test_agent_transaction.py`
- `.dockerignore`
- `docker-compose.yml` 的 API 健康检查

全量测试为 `23 passed`。Docker Compose 已真实构建并启动 API、PostgreSQL/pgvector、Redis；已将 4 份 `sample_data` 文档导入 PostgreSQL并完成一次端到端 RAG 问答。下一步是第 2 周 Day 7：无 AI 复写会话/消息查询、运行全部测试并复盘，然后进入第 3 周 LLM API 与手写 Agent。

## 8. 建议给下一台主机 Codex 的首条提示词

用户可以在新对话中发送：

```text
请先读取仓库根目录的 AI_AGENT_8W_HANDOFF.md、LEARNING_README.md、README.md 和 course/README.md，接着当前学习进度继续。项目全貌第一遍和压缩版第 1 周已经完成；第 2 周 Day 1～Day 6 已在引导下完成，包含 SQL/SQLAlchemy、事务、依赖注入、pytest Fixture/Mock、会话分页、事务回滚及 Docker Compose 实操，当前全量测试为 23 passed。下一步进行第 2 周 Day 7 无 AI 复盘与验收，然后进入第 3 周。请用中文、概念优先、少讲不必要的语法；优先让我通过小实验观察现象，再补关键代码和测试。不要把讲过等同于已经掌握。
```

## 9. 新主机开始前的核对清单

1. `git pull` 后确认存在本文件和 `LEARNING_README.md`。
2. 创建或同步 Conda 环境，不要硬编码当前主机的解释器路径。
3. 从 `.env.example` 创建 `.env`；默认先不要填写真实模型密钥。
4. 运行种子脚本、23 个测试和 Ruff。
5. 启动服务并打开 Swagger。
6. 先确认用户希望继续“全貌讲解”，不要擅自重头重复 Python 基础。
