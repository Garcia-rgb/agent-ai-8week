# AI Agent / AI 应用开发 8 周转型计划｜跨主机交接

> 更新日期：2026-09-16
> 用途：在另一台主机继续本项目和学习对话。新 Codex 应先读本文件，再读 `LEARNING_README.md`、`INTERVIEW_README.md`、`README.md` 和 `course/README.md`。

## 学员目标与学习策略

- 目标方向：初级 Agent / AI 应用开发、AI 后端、RAG/企业知识库研发。
- 当前重点：建立 Python 后端、大模型 API、RAG、Agent 工作流、评测与部署能力，形成可以演示和面试讲解的完整作品。
- 不把预训练、强化学习、基础模型研究或多 Agent 炫技作为当前主线。
- 学习策略：先完成项目全貌第一遍，再压缩回顾第 1 周，随后从第 2 周开始正式动手。

## 1. 项目位置与 Git 状态

- GitHub：`https://github.com/Garcia-rgb/agent-ai-8week.git`
- 主分支：`main`
- 当前项目：光伏电站技术支持 Agent（包名 `smartpv-support-agent`，当前版本 1.3.0），兼作 8 周学习、作品集和面试项目。
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
conda run -n agent-ai-8week python scripts/ingest_smartpv.py --source "D:\资料汇总"
conda run -n agent-ai-8week python -m pytest -q
```

不要复制当前主机的 Miniconda 环境目录，也不要提交或传输真实 API Key。

## 2. 当前主机环境记录

- IDE：PyCharm
- Miniconda：`C:\Users\14374\miniconda3`
- Conda 环境：`agent-ai-8week`
- Python：3.12
- PyCharm 解释器：`C:\Users\14374\miniconda3\envs\agent-ai-8week\python.exe`
- 当前全量基线：210 个测试通过（1 skipped，需要模型文件的用例默认跳过），共 211 项，覆盖率 88.84%，Ruff 检查通过。
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
- 从第 3 周 Day 4 起，每节结尾固定设置两道面试级问题。问题必须能从当节教学内容中推导，重点考查原理、设计取舍和项目实现，不再使用过于简单的事实复述题。
- 每节完成后，将两道面试题、标准答案、30 秒表达和项目对应情况追加到根目录 `INTERVIEW_README.md`；不记录用户的原始回答。
- 每完成一个阶段，应同步更新本文件和 `LEARNING_README.md`，并明确标注“概念讲解、引导实操、独立验收、代码实现”分别完成到哪一步。

## 4. 已完成的环境与项目工作

- 从旧主机传输包恢复并整理了项目。
- 删除了用户不再需要的旧 `bookstore` 项目和旧资料；没有继续处理旧的 `agent1` 远端仓库。
- 为本项目建立独立 Git 仓库，后续已连接到 `Garcia-rgb/agent-ai-8week`。
- 安装 Miniconda，创建 `agent-ai-8week` 环境，安装项目及开发依赖。
- 创建本地 `.env`，使用 SQLite 和确定性本地回答模式。
- 运行种子脚本、测试和 Ruff 检查。
- 用户已经在 PyCharm 中成功运行 CLI 和 FastAPI/Swagger。
- **Docker Compose 路径（PostgreSQL + Redis）已于 2026-09-18 实测**（Docker Desktop 4.90.0 / Engine 29.7.2）：
  `docker compose up --build -d` 起 `api` / `postgres` / `redis` 三容器全部 healthy；容器内 `/health` 报
  `version=1.3.0`、`embedding_backend=hash`、`cache={backend: redis, degraded: false}`；写操作四道闸在
  PostgreSQL 事务下依次是 201 / 409 / 400（签名）/ 403（归属）/ 400（格式）；连续 30 次 `/chat` 后第 31 次
  返回 429 并带 `Retry-After`；`docker compose down` 再 `up -d` 后数据全部保留。过程中修掉两个真问题：
  ① `Dockerfile` 的 `COPY static` 原本排在 `pip install` 之后，hatch 的 `force-include` 找不到该目录会让
  构建直接失败（已把 COPY 前移）；② PG 命名卷里的 `tickets` 表仍是旧列名 `order_id`，`create_all` 不会改
  已存在表的列名，写入时报 500（已 `ALTER TABLE tickets RENAME COLUMN order_id TO device_sn`）。为此新增
  `scripts/check_schema.py` 做表结构漂移自检（有漂移时退出码为 1）。容器内语料需从宿主机导入
  （`DATABASE_URL` 指向映射端口 5433），导入后 20 文档 / 212 片段与本地 SQLite 完全一致。
- **交付完备性补齐（2026-09-18，并入 1.3.0，用户要求「把项目弄全面、做到可交付」）**：
  - 新增三份文档：`CONTRIBUTING.md`（环境、约定、提交前检查，以及「改了 A 必须同步 B」的连带清单）、
    `SECURITY.md`（已实现的安全边界、部署前必改项，以及「没有真正的身份认证」这条诚实声明）、
    `docs/deployment.md`（部署到服务器、升级与回滚、上线检查清单）。此前 README 只覆盖「在开发机上跑起来」。
  - **修掉 `doctor` 的一个真缺陷**：`cli.py::_render` 原按 `status != OK` 收集问题，于是「没配远程模型」——
    一个受支持的默认模式、新克隆的仓库和 CI 都长这样——也会让退出码为 1，与 README 一直写的
    「可直接串进 CI 或部署脚本」矛盾。现在只有 `FAIL` 返回非零，并新增 `--strict` 供部署门禁把警告升级为失败。
  - **补 `tests/test_cli.py`（12 例）**：`cli.py` 此前零覆盖，而它是对外入口、退出码被部署脚本依赖。
  - **CI 扩面**（`.github/workflows/ci.yml`）：从「只跑 3.12 的 ruff + pytest」扩到 3.11/3.12/3.13 矩阵、
    `python -m build` 后把 wheel 装进干净虚拟环境跑 `version` / `doctor` / 起服务打 `/health` 与 `/`、
    以及 Docker 镜像构建与启动检查。后两条正是历史上真实坏过的路径（`static/` 没进 wheel、Dockerfile COPY 顺序）。
  - `.env.example` 补 5 个缺失配置项（`RETRIEVAL_CORPUS_ID`、`CHUNK_SIZE`、`CHUNK_OVERLAP`、
    `EMBEDDING_BATCH_SIZE`、`EMBEDDING_MAX_LENGTH`）；`pyproject.toml` 加覆盖率门限 80%（当前 88.84%）；
    镜像改为非 root 运行（`USER appuser` + 交出 `/app` 所有权，否则 SQLite 形态写不出库文件），
    compose 三个服务加 `restart: unless-stopped`。
  - 测试 198 → **210 passed / 1 skipped（共 211 项）**，覆盖率 83% → **88.84%**，Ruff 通过。
    改动仍**未提交、未推送**，远端停在 `a151753`。

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
- 设备查询使用模拟设备档案数据。
- 创建工单需要确认令牌，并检查签名、有效期和防重放。
- 当前 LangGraph 是规则驱动的一步工作流，不是持续自主循环的 Agent。
- 真正 Tool Calling 的基本流程：模型提出工具和参数，服务端校验并执行，再把结果交回模型。
- Agent Loop 必须限制轮数、工具白名单、权限和写操作确认。
- 2026-09-15 已把上述流程真正写进 `services/agent_loop.py`：模型自主选择工具、服务端校验并执行、结果回传后继续循环，最多 5 轮。
- 2026-09-15（同日 Day 6）该循环已接入 `POST /chat`，主路径不再是「Python 按关键词选工具」。现在的分工是：判断意图和选工具由「模型」负责，工具白名单、参数校验、写操作拦截、空检索拒答和提示词注入检测仍由服务端负责。
- 「模型」在这里是一个接口（`ChatModel` 协议）。配置了 `LLM_BASE_URL`/`LLM_API_KEY`/`LLM_MODEL` 时用远程模型；没配置时自动退回 `RuleBasedLocalModel`——它复用 `graph.py` 的规则把意图翻译成工具申请。因此本地无密钥也能跑完整链路，CI 里可以真跑而不必 mock 模型。

### RAG

- 文档解析、切块、块大小 700、重叠 100。
- 向量生成已抽成可切换后端（`services/semantic.py`）：默认 384 维本地 Hash Embedding（零依赖，
  语义能力弱），配好模型目录后换成 512 维本地 ONNX 语义模型（bge-small-zh-v1.5，离线、无 API 成本）。
  **换后端必须重建表并重新导入语料**，两者不是同一个向量空间。
- 混合检索分数：单字重叠 0.30 + 二元字组 0.35 + 向量 0.35，默认 Top-K 为 5。
- 用户亲自观察到：原词查询分数最高，同义表达略低，无关问题最低。
- 口语问法专项（2026-09-15 用户要求「啥是合母」也能问出来）：查询侧先剥掉虚词和语气词再做两字组合，
  因为逐字切分下「合母」「控母」共享「母」区分不开，且口语字会摊薄实词权重。文档侧不剥停用词。
  **`tokenize` 不能改**——库里既有的向量由它生成，改了查询向量与库内向量就错位。
- 已解释 Embedding 负责找资料，LLM 负责组织回答。
- `EMBEDDING_BACKEND` / `EMBEDDING_MODEL_PATH` / `EMBEDDING_DIMENSION` 三项决定用哪个后端；
  配了 `onnx` 但依赖或模型缺失时直接报错，不静默退回哈希向量（两者空间不同，混用无法解释）。
  片段元数据里记了后端指纹（`hash:384` / `onnx:512`），库是哪套模型建的查得出来；
  检索时若发现片段向量长度与当前查询不一致，语义那一路记 0 并打警告，不使用截断出来的假分数。

### 会话、状态与可靠性

- 区分聊天历史、Agent 临时状态和长期用户记忆。
- 2026-09-15（Day 6）起，同一会话的历史消息会回填进 Agent Loop 的上下文（默认最近 10 条，单条截断 2000 字符），因此已经具备会话内的语义记忆；读取时机是「写入本轮用户消息之前」，否则本轮问题会重复出现。跨会话的长期记忆仍未实现。
- 工具调用轨迹不写进 `messages` 表，而是写进 `AuditLog`（`action="agent_loop_tool_calls"`），记录轮数、停止原因和每次调用的名字与成败。
- 已讲上下文窗口、摘要、检索和结构化状态。
- 已讲并实现 LLM 超时、有限重试、错误分类与降级；当前客户端最多尝试三次，暂时性错误采用 1 秒、2 秒退避，确定性请求错误和响应结构错误不重试。
- 已讲结构化请求日志：`request_id`、路径、状态码和 `duration_ms`。
- 当前日志能看整个 HTTP 请求耗时，还不能细分检索、数据库、工具和模型各阶段耗时。

### 评测（2026-09-15 已升级为三层）

- 讲解过 `src/support_agent/services/evaluation.py`；原实现只有检索层。
- 现已扩成三层：`retrieval`（Top-K 是否覆盖预期关键词）、`tool`（`expected` 都选到、`forbidden` 没碰）、`answer`（`status` / `answer_source` / `must_contain` / `must_not_contain`）。样本里声明了哪层就评哪层，没声明的层不进分母。
- 顶层 `expected_keywords` 仍然可用，等价于 `retrieval.expected_keywords`，旧评测集不改也能跑，且只声明检索层时不触发模型调用。
- **关键设计：评测不自己写判定。** 为此把 `respond` 拆成两半——`run_turn`（跑完整链路并判终态，无落库副作用）与 `respond`（在它之上加建会话、写消息、签令牌）。评测的检索层调 `SupportAgent.retrieve`，工具层和回答层调 `run_turn`，与 `/chat` 是同一份代码。
- 工具层统计的是「选对工具」而非「执行成功」：写操作被拦下待确认时 `ok=False` 但算选对，参数校验没过才算选错。
- 响应新增 `model`（本次用的模型，不同模型分数不可比）与 `layers`（分层通过率）；失败时给出可读原因，如 `status=completed，期望 pending_confirmation`。
- 实测（`deepseek-v4-flash`，8 条样本）：样本口径 8/8，三层各 3/3、5/5、5/5。另跑一组故意写错的负样本验证区分力：检索层 `missing_keywords`、工具层 `missing_tools`、回答层 `reasons` 各自正确判 F。
- 仍未做：监控指标（延迟至今只有整请求耗时，没有按检索/模型/工具分段），以及云端部署。

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

> 项目全貌第一遍和压缩版第 1 周已完成；第 2 周已完成第一轮讲解、引导实操和引导式复习。第 3 周 Day 1～Day 6 已完成第一轮学习和代码实操，并额外完成「SmartPV 知识库导入与检索隔离」一节；Day 5 手写 Agent Loop，Day 6 把循环接进 `POST /chat`，主路径已由「Python 规则选工具」换成「模型选工具、服务端校验执行」。下一步进入 Day 7。

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

完成第 2 周时全量测试为 `23 passed`。Docker Compose 已真实构建并启动 API、PostgreSQL/pgvector、Redis；已将 4 份示例文档导入 PostgreSQL 并完成一次端到端 RAG 问答（那批示例语料现已从仓库移除，语料统一改为导入本地知识库）。第 2 周 Day 7 已完成引导式复习与会话查询练习，但尚未完成完全无提示的闭卷重写。

### 阶段 D：第 3 周 LLM API 与手写 Agent（进行中）

- Day 1：已学习 Token、上下文窗口、输入/输出成本、`temperature` 和最大输出长度。
- Day 2：已学习指令与数据边界、Prompt Injection、Few-shot、结构化输出，并阅读 `services/llm.py` 的 Prompt 与请求结构。
- Day 3：已阅读并运行 `examples/manual_agent.py`，理解工具说明、服务端白名单、JSON 参数和执行权限之间的区别。
- Day 4：已学习并实现 `401/429/503/超时/响应损坏` 的分类、有限重试、退避等待、错误映射和 Agent 降级；完成两道面试题并建立 `INTERVIEW_README.md`。
- Day 4 代码状态：新增 `tests/test_llm_retry.py` 的 5 个 Mock 测试；全量基线更新为 `28 passed`，Ruff 通过。尚未实现结构化降级字段、模型故障指标、随机抖动和总时间预算。
- 附加节（2026-09-15）SmartPV 知识库导入与检索隔离：新增 `services/knowledge_base.py` 与 `scripts/ingest_smartpv.py`，把本地 HCSA-SmartPV V2.0 分卷按章节导入**当前 `DATABASE_URL` 指向的库**（SQLite 与 PostgreSQL/pgvector 都可以，不存在「只能导进 PostgreSQL」），章节元数据带 `corpus_id=smartpv_v2`、`visibility=local_only` 和 `restricted` 标记；账号密码、密码重置章节默认排除，需显式 `--include-restricted` 才导入。`RAGService.search()` 新增 `corpus_id`、`include_restricted`、`min_score` 三个参数，实现语料隔离与拒答阈值；`config.py` 新增 `retrieval_corpus_id` 与 `retrieval_min_score`，Compose 注入 `smartpv_v2` 和 `0.4`；检索命中为空时 `agent.py` 直接拒答、不调用模型。新增 `tests/test_knowledge_base.py` 的 6 个测试，全量基线更新为 `34 passed`，Ruff 通过。
- Day 5（2026-09-15）：已手写「模型 → 工具 → 结果 → 模型」的最多 5 轮 Agent Loop。新增 `services/agent_loop.py`（`ToolSpec` 工具说明书、`build_tool_registry()` 服务端白名单、`parse_arguments()` 四道参数校验、`execute_tool_call()` 永不抛异常、`run_agent_loop()` 与 `LoopResult`/`ToolCallRecord`）；改写 `services/llm.py`，抽出共用的 `_chat()` 重试层并新增 `ToolCallRequest`、`AssistantTurn`、`chat_with_tools()`；新增 `tests/test_agent_loop.py` 的 12 个离线测试和 `examples/agent_loop_demo.py` 演示脚本。全量基线更新为 `46 passed`，Ruff 通过。关键区分：工具说明书（发给模型）≠ 工具白名单（服务端执行）；模型参数一律先校验再执行；轮数用尽后禁用工具强制收敛；写操作工具不自动执行。
- Day 6（2026-09-15）：把 Agent Loop 接进 `POST /chat`，主路径不再是规则路由。新增 `services/local_model.py` 的 `RuleBasedLocalModel`（与远程客户端实现同一个 `chat_with_tools` 接口，无 API Key 时可跑完整链路）；`agent_loop.py` 扩展为支持异步工具 handler、`needs_confirmation` 结束状态、`history` 入参，并新增 `build_support_registry()` 挂载 `search_knowledge_base` 与 `create_ticket`；重写 `SupportAgent.respond()`，负责读历史、前置注入拦截、组装注册表、跑循环、提取引用与确认令牌、空检索兜底、写工具轨迹审计。`config.py` 新增 `agent_max_rounds`（5）与 `chat_history_limit`（10）。新增 `tests/test_local_model.py`（9 个）与 `tests/test_agent_integration.py`（12 个），`test_agent_loop.py` 增补 3 个。全量基线更新为 `70 passed`，Ruff 通过。
- 接入真实模型（2026-09-15）：在 `.env` 中填入 `LLM_BASE_URL=https://api.deepseek.com`、`LLM_MODEL=deepseek-v4-flash`、`LLM_API_KEY` 即可切到真实模型。`AssistantTurn` 新增 `reasoning_content`，`to_message()` 会在回传消息里带上它——DeepSeek V4 思考模式默认开启，且携带 `tools` 的请求必须原样回传历史思维链，否则续轮返回 400。新增 `scripts/check_llm.py` 一键自检（真调一次问答 + 一次工具循环，不写库、不产生写操作）。同时修掉一个既有缺陷：`Settings` 会读本机 `.env`，导致填了真实密钥后本地 `pytest` 与 CI 结果不一致（8 个用例失败）；现在 `tests/conftest.py` 用 autouse fixture 把 `env_file` 置空，测试不再依赖本机 `.env`。新增 3 个 `reasoning_content` 回归测试，全量基线更新为 `73 passed`，Ruff 通过。
- 本地导入 SmartPV 语料（2026-09-15）：已把 HCSA-SmartPV V2.0 分卷导入**本地 SQLite**（不是 PostgreSQL）。原始资料在 `D:\资料汇总`（`HCSA-SmartPV-V2.0-index.json` + `HCSA-SmartPV-V2.0-知识库分卷\`，19 篇 markdown）。命令：`python scripts/ingest_smartpv.py --source "D:\资料汇总"`；实测结果 `新文档 19，跳过 0，章节 95，检索片段 195`。导入后本地库共 23 篇文档 / 199 个片段，其中 `corpus_id=smartpv_v2` 的 195 个。注意本地 `.env` **没有**设置 `RETRIEVAL_CORPUS_ID` 与 `RETRIEVAL_MIN_SCORE`（Compose 里设了 `smartpv_v2` / `0.4`），所以本地检索目前不按语料过滤、也不卡分数；仓库自带的示例文档已于同日删除，因此本地库里实际只剩 SmartPV 语料。换台主机若要复现，需先确认 `D:\资料汇总`（或等价路径）存在，并显式传 `--source`——`.env` 里没有 `SMARTPV_KB_PATH`。
- 业务域改造（2026-09-15）：把仓库里原「电商订单客服」示例域整体换成了「光伏电站技术支持」。`services/tools.py` 的 `Order`/`MOCK_ORDERS`/`query_order`/`find_order_id` 改为 `Device`/`MOCK_DEVICES`/`query_device`/`find_device_sn`——按 `SN-2024-000123` 形式的序列号查型号、额定功率、运行状态、固件版本和并网情况；`graph.py` 的路由 `order` → `device`，状态字段 `order_id` → `device_sn`；`agent_loop.py` 的系统提示词、`query_device` 工具说明书和 `create_ticket` 的 `device_sn` 参数同步改写；`local_model.py` 的意图映射与话术改成设备口径；`models.py` 的 `tickets.order_id` 列改名 `device_sn`（**已有的本地库必须重建**，`create_all` 不会修改已存在表的列名），`schemas.py`、`main.py`、`agent.py` 的确认令牌载荷同步。示例语料与评测集整块删除：`sample_data/`（4 份电商政策文档）、`evals/dataset.jsonl`（40 条评测）、`scripts/seed.py` 全部移除，`Dockerfile` 不再 `COPY` 它们，`Makefile` 的 `seed` 目标换成 `ingest`；评测接口改为 `POST /evaluations/run?dataset_path=<路径>`，评测集由调用方指定。FastAPI 应用名改为「光伏电站技术支持 Agent」。重建本地库并重新导入后为 19 篇文档 / 195 片段，`tickets` 列为 `device_sn`；全量 `73 passed`，Ruff 通过。端到端实测：设备查询返回结构化档案、「绝缘阻抗低」命中手册里的告警 2062、不存在的序列号被正确拒绝。
- 本地客户端（2026-09-15）：新增 `static/index.html`——单文件、无构建的客户端页面，含会话列表、可展开的引用来源、工单二次确认卡片、回答反馈和文档导入；`main.py` 追加 `GET /` 与 `/static` 挂载，**必须注册在所有 API 之后**，否则静态挂载会遮蔽接口。新增 `scripts/start_client.py` 一键启动：端口被占自动顺延（Docker Desktop 会占着 8000）、等服务起来再开浏览器、启动时打印语料规模与模型模式、远程模型直连不通时自动挂载本机代理（实测 `127.0.0.1:7897`）。新增 `scripts/create_desktop_launcher.py`，在桌面生成双击即用的 `.cmd` 启动器。两个踩过的坑：① `os.startfile` 执行手写的 `.lnk` 报 WinError 1155——Windows 要求 `.lnk` 必须带 `LinkTargetIDList`（shell 命名空间的二进制目录链），缺了它文件看着像快捷方式却无法执行，手写该结构风险高，所以改成桌面 `.cmd`；② 批处理文件内容必须保持纯 ASCII——`chcp 65001` 对同一文件后续行的解析不可靠，中文写进去会报「命令语法不正确」，因此窗口标题改由 Python 的 `SetConsoleTitleW` 设置。注意本机 `D:\agent1` 到 DeepSeek 的直连状况**会变**（Clash 的 TUN/规则模式切换，实测过 ConnectError 也实测过直连成功），不要假定必须挂代理；客户端只在直连探测失败时才自动挂本机代理，两条路径都已验证可用。全量 `73 passed`，Ruff 通过。
- 追加单份资料导入（2026-09-15）：新增 `scripts/ingest_document.py`，用于把零散的单份文档补进同一个语料库。与 `scripts/ingest_smartpv.py` 的分工是——后者只认 HCSA 分卷的固定目录结构（`index.json` + `知识库分卷/`，按 `M1`…`附录E` 前缀匹配文件），无法用于追加新收到的资料；前者接受任意 `--file`，把 docx 的 `Heading1/2` 映射为 Markdown 的 `##`/`###` 后复用同一套章节切分，并复用 `KnowledgeChunk` 生成同构元数据、写同一个 `corpus_id`，因此追加资料与原有语料 `RETRIEVAL_CORPUS_ID` 过滤下不会互相隔离。docx 正文直接解析包内 `word/document.xml`，**不依赖 python-docx**（未安装），包内表格转成 Markdown 表格、列表保留标记。这一步放弃 `tencent-local-office-edit`（editor_sdk）通道是有依据的：该通道的 `doc_resolve_document_structure` 每段只回 `text_preview`（上限 200 字），且工具清单里没有任何全文导出工具，无法用于把长文档转成语料。实测导入《第3册-交直流屏柜原理（结合图纸扩充版）》（微信收到、176 段 / 6 张表 / 15 章 / 约 6.8k 字）：章节 15、新增片段 17，转出的 Markdown 存档到 `D:\资料汇总\拓展资料\第3册-交直流屏柜原理.md`；本地库变为 20 篇文档 / 212 片段，`corpus_id` 与 HCSA 语料一致。检索验证：问「合母和控母有什么区别」新文档得分 0.701 居首（高于 HCSA 的 0.449），真模型端到端作答并正确引用该文档（0.51~0.71）。重复导入同一内容按校验和跳过。注意：该分册的关键信息有一部分在图纸图片里，本通道只取文字、不解析图片，所以图纸细节仍检索不到。
- 口语化检索（2026-09-15）：用户提出「啥是合母」这类大白话也要能问出来。先做离线对照实验再动手，量出的结论是——问题不在"问不出来"而在"排不进前 5"：「合母和控母有什么区别」的正确章节排第 9、「合母控母有啥不一样」第 12、「这两个母线有啥区别」第 23，Top-5 里根本没有原文，模型自然答不准。根因是 `tokenize` 逐字切分：`合母`/`控母` 都退化成共享「母」的单字，区分不开；且词面分数的分母是查询总字数，口语里的「啥/是/有/么」把实词权重摊薄，问句越长口语字越多分数掉得越狠。改法只动打分、不动向量：`embeddings.py` 新增 `STOPWORDS`/`strip_stopwords`/`bigram_terms`/`retrieval_terms`，`RAGService.search()` 改为三路 `0.30*单字 + 0.35*二元字组 + 0.35*哈希向量`，查询侧先剥虚词再做两字组合（文档侧不剥）。踩坑一次：第一版只给二元字组那一路剥了停用词，单字那路分母仍是原句字数，分数没提上去，两边必须用同一份剥过的文本。**`tokenize` 保持原样**——库里 212 条向量由它生成，改动会让既有向量与查询向量错位，`tests/test_embeddings.py` 专门守这条。实测 8 个口语问法全部进入前 5；分数分界看起来干净（库内 ≥0.513、库外噪声 ≤0.377），当时据此认为 `RETRIEVAL_MIN_SCORE=0.45` 可用（该值从未写入 `.env`）。**注：这个结论后来被推翻，见下文「行业元数据与版本并列」一条——那条测量只采了少数噪声词，扩大噪声集后分布是重叠的。**新增 `tests/test_embeddings.py`（5 条）与 `test_rag.py` 的口语召回测试（1 条），全量基线 `79 passed`，Ruff 通过。
- 响应协议（2026-09-15）：补齐此前被跳过的 `/chat` 终态协议（Codex 定义里排在开发顺序第 2 步）。`schemas.py` 新增 `ChatStatus`（`completed` / `degraded` / `pending_confirmation` / `blocked` / `failed`）与 `AnswerSource`（`knowledge` / `tool` / `model` / `policy` / `fallback`），`ChatResponse` 增加 `status`、`answer_source`、`retryable`。`agent.py::respond` 把四条出口整理成固定的优先级顺序，**终态一律由服务端判定**，模型无权声明自己这一轮属于哪一种。`degraded` 能不能重试不另设规则，直接复用 `LLMError.retryable`（`rate_limit`/`service`/`network` 为真，`authentication`/`request`/`invalid_response` 为假），为此 `LoopResult` 新增 `retryable` 字段并在两处 `llm_error` 分支回填。顺手修掉一个既有矛盾：原先「检索为空」的覆盖发生在「待确认」之后，会出现 `pending_action` 已给出、`answer` 却是拒答话术的返回；现在两个分支互斥，待确认优先级更高。前端 `static/index.html` 按 `status` 渲染状态标签（已拦截 / 模型不可用 / 等待人工确认 / 没有依据未作答）并标出正常回答的依据来源，不再靠文本猜。新增 3 个测试（无工具作答标为 `model`、确定性模型错误不可重试、`/chat` 契约字段齐全），全量 `82 passed`，Ruff 通过。端到端实测四种终态：注入 → `blocked`/`policy`；计算器与设备查询 → `completed`/`tool`；口语问题「啥是合母」→ `completed`/`knowledge`（5 条引用）；工单 → `pending_confirmation`/`policy`。`failed` 目前**实测触发不到**：本地 `.env` 的 `RETRIEVAL_MIN_SCORE=0.0` 让检索永远返回 top_k 条，`not hits` 不可达——这与先前记录的抗幻觉兜底缺口是同一件事，建议的阈值 `0.45` 仍未写入。历史消息表没有 `status` 列，所以从侧栏重新打开旧会话时不会显示状态标签（只影响回放，不影响新回答）。
- 分层评测（2026-09-15）：离线评测从「只看检索」扩成三层。`evaluation.py` 的样本格式改为 `retrieval` / `tools` / `answer` 三个可选块，顶层 `expected_keywords` 保持兼容（等价于 `retrieval.expected_keywords`），只声明检索层的样本不触发模型调用。为做到「评测不自己写判定」，把 `agent.py::respond` 拆成 `run_turn`（跑完整链路并判终态，**无落库副作用**）与 `respond`（在它之上加建会话、写消息、签令牌）；评测的检索层调新方法 `SupportAgent.retrieve`（与线上同语料、同阈值、同去重，**顺带修掉原先评测不传 `corpus_id` 的偏差**），工具层与回答层调 `run_turn`。工具层语义明确为「选对工具」而非「执行成功」：写操作被拦下待确认时 `ok=False`，但那是设计要的行为，算通过；参数校验没过才算选错。`EvaluationResponse` 新增 `model`（本次所用模型，不同模型分数不可比）与 `layers`（分层通过率，未声明该层的样本不进分母），失败明细带可读原因（如 `status=completed，期望 pending_confirmation`）。新增 6 个测试，全量 `88 passed`。实测：`deepseek-v4-flash` 跑 8 条样板 8/8，三层分别 3/3、5/5、5/5；另跑一组故意写错的负样本验证区分力，`missing_keywords` / `missing_tools` / `reasons` 均正确判 F。评测集仍不进仓库，样板在 `D:\资料汇总\拓展资料\评测集-示例.jsonl`。
- 行业元数据与版本并列（2026-09-15）：给每个片段加上行业标签，检索时先看标签再比相似度。新增 `services/industry.py`：`device_models`（机型词典 + 完整型号正则，如 `SUN2000`、`SUN2000-100KTL-M1`、`LUNA2000`）、`protocols`（长模式优先的协议正则，`Modbus TCP` 先于裸 `Modbus`）、`document_version`（标题/分册名，如 `V2.0`、`第3册`）、`scenario`（由语料编号映射到户用/工商业/地面电站等）、`content_type`（由小节标题判 reference/procedure/faq）。**关键教训：标签必须从片段正文抽。** 第一版只扫小节标题，实测 95 个章节只命中 4 个机型、0 个协议——光伏资料的标题常是「6.2 绝缘阻抗故障定位」，真正提到 RS485、SUN2000 的是正文；修正后 18/95 章节带协议、43/95 带机型。抽不到一律留空，不写「可能是某型号」这类模糊值。检索打分保持三路文本分不变，另加元数据加减：命中所问机型/协议/场景 +0.06，明确属于别类 -0.10。**刻意不做硬过滤**——语料对机型版本覆盖不完整，硬过滤会把跨机型通用的章节一起杀掉，模型反而拿不到任何依据；所以标签只影响排序。实测「户用逆变器怎么组网」加权前第 2～5 条混着「7.2 地面电站逆变器产品」和跨模块速查，加权后收敛到户用的 2.2/2.6 组网章节；「储能柜的容量是多少」把无关分册的「事故放电与容量校核」挤出前五。另新增 `RAGService.detect_conflicts()` 与 `ChatResponse.conflicts`：一次回答的依据落在两个及以上 `document_version` 且分数差在 15% 以内时，并列返回各版本的说法与出处，前端渲染成提示条；语义是「依据跨了版本，需你按现场型号确认」，不是断言资料互相矛盾。系统提示词同步写死「不同版本说法不一致时必须并列讲出，不要自己挑一个」。真模型实测「直流母线电压是多少」触发 `conflicts=2`（V2.0 + 第3册），回答开头即「我按检索到的资料并列如下」，逐条标注版本/场景/协议/机型；单版本问题（「啥是合母」）`conflicts` 为空，不产生噪音。语料按新标签重导（清空两张表后重导，仍是 20 文档 / 212 片段，其中 V2.0 共 195、第3册 17）。新增 `tests/test_industry.py`（10 条）与 `tests/test_rag.py` 的加权、冲突、引用标签测试（5 条），全量 `102 passed`，Ruff 通过；真模型评测 8/8，三层未退化。**遗留问题（重要）：** 拒答阈值定不下来。扩大噪声样本后实测库内 15 问 top1 最低 0.439（「储能柜的容量是多少」）、库外 12 个噪声最高 0.560（「Python 怎么装环境」命中「2.7 设备安装要点」），**分布重叠**，所以单一全局阈值分不开：设 0.45 会同时误拦真问题、放行噪声。此前「噪声 ≤0.377、阈值 0.45 可用」的结论是采样太少导致的，已在上文更正。`RETRIEVAL_MIN_SCORE` 因此仍是 0.0，`status=failed` 在真实链路上依然触发不到。要真解决得先改打分（高频字 IDF 降权、查询实词覆盖率门槛），再谈阈值。另：Codex 定义里的 `lookup_register` / `convert_register_value` / `compare_protocol_versions` 未实现——它们需要结构化点表，而当前语料实测寄存器地址表 0 条，没有素材就不拿假数据顶上。
- 语料范围判据与前置拒答（2026-09-16）：把「拒答」从分数阈值改成两个语料范围判据，并把判定**前置到调用模型之前**。先说诊断——哈希向量下分数阈值分不开库内与库外：试了 IDF 的四种加权变体（单字 IDF / 词组 IDF × 锐化 1.0 / 2.0）、把语料里不存在（`df=0`）的查询词剔出分母、用凝固度（点互信息）过滤跨词拼出的假词组，**全部重叠**（库内最低 0.182「Modbus 协议怎么读数据」，库外最高 0.353「车险怎么买」）。根因是哈希向量只做字符碰撞，「Python 装环境」与语料里的「安装环境」在字符层面确实相似。过程中两个反直觉现象值得记：`读` 在整份光伏资料里 `df=0`，IDF 权重被推到最高（6.36），反而稀释了库内问题的分数；`装环` 是「安装」+「环境」跨词切出的假词组，`df` 极低同样拿到最高权重，把「Python 怎么装环境」抬到 0.27——**IDF 用在小语料的单字空间里方向不可靠，`df` 极低既可能是真术语也可能是偶然字**。定案的改法：（1）`CORPUS_MISSING_MIN_CHUNKS` 取代原按文档数的门槛——语料是按分卷组织的，20 个文件里有 212 个片段，按文档数算的 30 门槛让判据**整个没生效**；（2）缺失比例上限从 0.75 收到 0.60；（3）新增 `has_unknown_foreign_token()`：外文词是完整、不可再分的 token，不受跨词切分污染，「Python」「Windows」在语料里一个都没有就是强跑题信号，判定用 `all` 而非 `any`（查询里只要有一个外文词语料认识，如 AFCI / Modbus / RS485，就不据此拒答）；（4）判定抽成纯函数 `out_of_corpus()`，`search` 与前置拦截共用同一份语料统计（新方法 `RAGService.corpus_index()`）；（5）`SupportAgent.run_turn` 在调模型之前先调 `RAGService.is_out_of_corpus()`，命中即返回 `failed` / `policy`、**零模型调用**。第 (5) 条是端到端实测逼出来的：库外问题原本返回 `status=completed` / `source=model` / 0 引用——拒答话术是**模型自己写的**，因为它看到跑题问题压根不去调检索工具，直接凭「我是光伏助手」拒答，于是服务端那句「检索过但没有依据」的兜底永远等不到，判定实际落在模型手里；这也意味着此前修好的检索判据在链路上**没人用**。实测：30 条库内问题全部放行、30 条库外问题全部拦下（无误拦、无漏放），样本存 `D:\资料汇总\拓展资料\检索范围样本.jsonl`；真模型端到端复验——库内 `completed` / `knowledge`（5 条引用），库外 `failed` / `policy` 且模型零调用。新增 4 个测试（`has_unknown_foreign_token` 的四类输入、语料够大时拦截、门槛前后对照、模型零调用的前置拦截），全量 `106 passed`，Ruff 通过。**遗留：** 这是词汇层面的近似而非语义理解——问题改用与语料完全不同的措辞时仍会漏放；阈值的两个常数（缺失比例 0.60、最少 60 片段）是在当前 212 片段语料上校准的，语料规模变化后要重测。根治要等真实语义向量。
- 本地语义向量与向量后端（2026-09-16）：把「向量生成」从检索逻辑里拆出来，并接上真实的本地语义模型。先说为什么必须换——哈希向量只是字符碰撞，把「Python 怎么装环境」和语料里的「安装环境」判成相似，所以上一轮只能靠词汇判据兜住跑题。新增 `services/semantic.py`：`EmbeddingBackend` 协议 + `HashEmbeddingBackend`（384 维，零依赖兜底）+ `OnnxEmbeddingBackend`（512 维，bge-small-zh-v1.5，onnxruntime + tokenizers + 模型目录）。模型从 ModelScope 的 `Xenova/bge-small-zh-v1.5` 取 onnx 权重（90MB，本机 huggingface 不通、modelscope 通），放在仓库外 `D:\资料汇总\拓展资料\modelsge-small-zh-v1.5`；依赖走可选 extra（`pip install -e ".[semantic]"`），不进核心依赖、不进镜像、不进仓库。**池化用 `[CLS]` 位**（BGE 官方用法）——实测比平均池化分得更开：相关 +0.543 / 无关最高 +0.361，平均池化是 +0.508 / +0.289。三条设计纪律：（1）配置写了 `onnx` 但依赖或模型缺失时**直接报错**，不静默退回哈希向量，因为两者是两个不同的向量空间，混用会让检索结果无法解释；（2）维度成为配置项（`EMBEDDING_DIMENSION`，留空按后端取 384/512），`models.py` 的 `Vector(...)` 跟随它，换后端要 `python scripts/ingest_smartpv.py --reset`（顺带给该脚本加了 `--reset`，用 `drop_all` 而不是删库文件——Windows 上库文件常被运行中的服务占着删不掉）；（3）检索时若片段向量长度与当前查询不一致，语义那一路记 0 并打警告——余弦相似度在长度不等时会按短的截断，静默给出一个看着正常的假分数，比 0 分危险。入库把后端指纹写进片段元数据。顺手修了测试隔离的一个真漏洞：`get_settings` 带 `lru_cache`，而 `db` 模块在导入时就调用过它一次（那时读的还是本机 `.env`），所以只把 `Settings.model_config['env_file']` 置 None 并不够——测试会带着开发机的 `EMBEDDING_BACKEND=onnx` 进来，每次建向量都去加载 90MB 模型；现在 `conftest` 里同时清缓存。**实测结果（212 片段语料，30 条带术语问题 + 10 条改写问法 + 30 条库外问题）：**（a）库内 top1 分数最低 0.226 → 0.324、中位 0.518 → 0.581；排序命中率（领域术语出现在 top-1）83% → 87%，top-3 均 90%；（b）**分数阈值这条路在语义向量下更走不通**：库外 top1 最高从 0.353 涨到 0.486——「怎么考驾照」被判定为与语料里「危险品运输管理」一节相关（原始语义 0.531，词面覆盖率甚至 1.000，因为那节真的提到驾驶证）。哈希向量之所以「分开」了库内库外，只是因为它随机；换成真语义模型后，通用中文句子之间的相似度本来就高，用「问题与语料最像那段」的余弦当判据同样重叠（库外最高 0.604 / 库内最低 0.505）；（c）顺带量出 `SEMANTIC_TRUST_FLOOR`（语义分按词面覆盖率打折）这个常数是给哈希向量设的，换成真模型后它只在压制有效信号——折扣开着时换语义向量 top-1 一条都没多，去掉后 25/30 → 26/30；于是把它下放到后端自己声明（哈希 0.4、语义 1.0）。**新暴露的问题（重要）：判据会误拦口语化的真问题。** 10 条改写问法里有 7 条被词汇判据拦掉（「天太热机器会不会自己降低出力」「柜子里一直嗡嗡响，是不是坏了」），而它们问的确实是这份资料里的事（温度降额、异响排查）。原因是判据只看「问题用的词语料里有没有」，与向量好坏无关；提高缺失比例上限会让库外问题一并放进来，词面与语义两个维度都试不出干净的分界线。需要先定取舍：接受误拦，或把命中判据时的回答从「拒答」改成「请补充设备型号或现象」。**pgvector 仍未接线，这次给出了明确理由与前置条件：** 打分用的 IDF 权重依赖全语料词频（`corpus_index()`），只取向量近邻候选就算不出这份 df，除非先把词频统计挪到入库时落库；212 片段的全量扫代价可忽略，所以做成「有开关但从不触发」只会增加解释成本。顺序是：先 df 落库，再加 ANN 预筛与索引。新增 `tests/test_semantic.py`（14 条，含真实模型用例，用 `SEMANTIC_MODEL_PATH` 显式开启、CI 上跳过），全量 `119 passed`（1 skipped），Ruff 通过。真模型端到端复验：库内带术语 `completed`/`knowledge`（5 条引用，top1 0.884）、库内改写口语 `completed`/`knowledge`、库外两条均 `failed`/`policy` 且模型零调用。/health 现在会报出 `embedding_backend` 与 `embedding_dimension`，排查「检索结果不对」时先看这里。
- Redis 检索缓存与请求限流（2026-09-16）：把 Compose 里一直空挂的 Redis 真正用起来。先说为什么值得做——一次 `/chat` 可能触发多轮模型往返，是整套接口里最贵的一个，而每轮都要读一遍全语料（212 片段）切词统计词频：实测库内问题 385ms、跑题问题 340ms 都花在这上面。
  新增 `services/cache.py`，四层结构：
  ① `KeyValueStore` 抽象只给四种原语（get / set / incr / close），不做 Redis 客户端的全量透传——上层用不到的能力留在那里，只会让人猜「这个项目到底靠 Redis 做了多少事」；
  ② `MemoryStore` 是进程内实现，也是**没配 `REDIS_URL` 时的默认路径**（本地开发和 CI 走这条，功能完整）；
  ③ `RedisStore` 只做薄封装，但超时必须设短（1 秒）——这个存储对正确性不是必需的，让一个慢 Redis 拖住整个请求比直接降级更糟。自增 + 首次设过期用一段 Lua 保证原子：分两次发命令在并发下会出现「键已创建但过期没设上」，计数永远不清零；
  ④ `ResilientStore` 把前两者包起来，失败后**打开熔断**，冷却期内（默认 30 秒）直接走兜底。
  **缓存的是链路上最贵的那一步。** 存的是「命中哪些片段、各得多少分」，不是 `SearchHit` 本身——后者装的是 ORM 对象，序列化进缓存既脆弱又容易和库里的数据脱节。命中后按 id 回库取正文，片段被删掉时自然少返回，不会拿旧快照当依据。空结果也缓存：跑题问题会被反复问到，而判定本身比算分还贵。键里带上所有会改变结果的输入——归一化后的查询、`top_k`、语料、是否含受限内容、分数阈值、**向量后端指纹**，少带任何一个都会变成「改了配置却还读到旧结果」。用归一化后的查询而不是原始问句是有意的：剥停用词不改变语义，「啥是控母」和「控母」本该共用一份。
  **失效用「语料代次」而不是删 key。** 导入文档时把代次 +1，新 key 天然带新代次，旧的靠 TTL 过期——Redis 下按前缀删要 SCAN 全库，代价远高于等它过期。代价是：绕过 `RAGService` 直接写库的路径（`scripts/ingest_document.py`）必须自己调一次 `invalidate()`。这个是写测试时才暴露的：`tests/test_rag.py` 里的 helper 直接写库，导致「建完数据立刻检索」吃到的是建数据之前的缓存。漏掉这一步的表现很隐蔽——刚导进去的内容在 TTL 内查不到，看起来像导入失败。
  **限流用固定窗口**（窗口编号进 key，一次 `INCR` 判定）。选它而不是滑动窗口，是因为滑动窗口要为每个请求在 Redis 里存时间戳再按范围清理，而「防止单个用户打爆模型调用」这个目的用一次 `INCR` 就够了——代价是窗口交界处最坏放过两倍流量，可以接受。判定放在 `/chat` 最前面：被拒的请求不建会话、不写消息、不调模型。正常响应带 `X-RateLimit-Limit` / `Remaining`（客户端才能自己收敛），`Retry-After` 只在 429 时给——正常响应里带上它，客户端会以为自己也需要等待，反而主动降速。
  **一条纪律：缓存服务不可用绝不能让接口不可用。** 实测把 `REDIS_URL` 指向本机没服务的 6379：首次操作吃满 1008ms 连接超时，之后 0.0ms——熔断生效。没有熔断的话每个请求都要吃一遍超时，接口会从「缓存失效」变成「整体变慢」。降级的代价写进日志和 `/health`：多进程下命中率下降、限流额度按进程数放大，所以 `/health` 现在报 `cache.backend` / `primary` / `degraded`。
  **实测（212 片段，onnx 512 维，未配 `REDIS_URL` 即进程内实现）：**（a）库内问题第一次 385ms → 第二次 11ms，全语料统计调用 1 次 → 0 次；（b）跑题问题第一次 340ms → 第二次 0.3ms（命中后连查询向量都不用算）；（c）真 HTTP 服务（`REDIS_URL` 指向不可达地址，限额 3）：第 1 次 1.83s（含模型加载和那次超时）、第 2/3 次 0.04s / 0.03s、第 4 次 429 只用 0.006s——**被拒请求没有吃 Redis 超时**，这是熔断在起作用；429 带 `retry-after`，且被拒请求没有留下会话（会话数 3 而不是 4）；（d）`/health` 降级后如实报 `{"backend":"memory","primary":"redis","degraded":true}`。
  新增 `tests/test_cache.py`（35 条）。测试全部走进程内实现、不依赖真实 Redis（CI 上也没有服务），因为键构造 / 代次失效 / 窗口计数 / 故障降级这些逻辑跟用哪个存储无关；Redis 那一路用一个假客户端验证发出去的命令和对错误的反应。两个可测性改动值得记：`MemoryStore` 和 `RateLimiter` 的时钟都做成可注入——过期和窗口切换要靠时间流逝才能验证，而「睡够 TTL」会让测试变慢又脆弱。全量 `154 passed`（1 skipped），Ruff 通过。
  **踩到的坑（值得单独记）：片段 id 是 UUID 字符串，不是自增整数。** 缓存读回时按 `int()` 解析，结果是缓存写进去了、读回来解析失败被当成未命中——**没有任何报错，只是缓存永远不生效**。测试也没抓到，因为我手写的假数据用了整数 id、没走真实模型。现在统一按字符串处理，测试也改用真实形态的 id。
- 软件化与 1.0.0 发布（2026-09-16）：把仓库包装成可安装、可分发、有版本体系的软件。版本号收敛为单一来源 `src/support_agent/__init__.py` 的 `__version__`（现为 **1.0.0**），`pyproject.toml` 改为 `dynamic = ["version"]` 交给 hatch 读取，OpenAPI 文档、`/health` 与 CLI 引用同一个值——此前 FastAPI 里写死 `0.1.0`，改版本要改好几处。包名从第 1 周遗留的 `enterprise-support-agent` 改为 `smartpv-support-agent`；补 `LICENSE`（MIT，用 hatchling 1.27+ 的 PEP 639 写法 `license = "MIT"` + `license-files`）与 `CHANGELOG.md`（Keep a Changelog 格式，把 0.1.0 → 1.0.0 四个阶段回填，每段附当时实测的数字）。新增命令行入口 `src/support_agent/cli.py`：`smartpv-agent version` / `doctor` / `serve`，等价写法 `python -m support_agent`；`doctor` 逐项检查配置、数据库与语料规模、向量后端、模型、检索与拒答参数、缓存与限流并返回退出码，`--deep` 会真的加载模型编一句话。两个刻意的取舍：`cache` 一行先真实读写一次再看状态，否则「配了 `REDIS_URL` 却连不上」会显示成一切正常（熔断要先被触发才会打开）；CLI 输出统一英文 ASCII，因为这份输出是要贴进日志和 issue 的，非 UTF-8 代码页会把中文打成问号。顺手修掉一处真缺口：`STATIC_DIR` 原本写死 `parents[2]/"static"`，装成 wheel 或在容器里跑时 `GET /` 会静默消失；现改为按「`SMARTPV_STATIC_DIR` → 仓库布局 → 当前工作目录 → 包内」依次查找，并用 hatch `force-include` 把 `static/` 打进 wheel 的 `support_agent/static`。Dockerfile 补 `COPY static`、`LABEL` 与 `HEALTHCHECK`，`/health` 增加 `version`。验证：`python -m build --no-isolation` 产出 `smartpv_support_agent-1.0.0-py3-none-any.whl` 与 sdist，wheel 的 `Metadata-Version: 2.5`、`License-Expression: MIT`、`[console_scripts] smartpv-agent` 与包内页面都核对过；`doctor --deep` 在 212 片段语料上报 `onnx | loaded | dimension=512 | signature=onnx:512`；全量 `154 passed`（1 skipped），Ruff 通过。
- 命中判据时改为追问（2026-09-16，**1.1.0**）：上一轮遗留的那个取舍由用户拍板——命中语料范围判据时不再拒答，改成「请补充设备型号或现象」。改动集中在三处：`schemas.py` 新增终态 `needs_clarification` 与字段 `clarification`（`reason` + `hints`）；`rag.py` 把判据拆成 `corpus_scope_reason()`（返回 `missing_terminology` / `unknown_foreign_terms` / `None`），`out_of_corpus()` 与 `RAGService.is_out_of_corpus()` 降为它的布尔封装，判据本身一个字没改；`agent.py` 的前置拦截改为返回 `needs_clarification` / `policy` 加追问话术（两种原因两套话术），**仍然零模型调用**。前端增加该状态标签，并把 `hints` 渲染成「请补充：设备型号…」提示项。**这不是精度提升，别当成误拦被修好了**：判据仍是词汇层面的近似，口语化真问题照样撞上它，改的只是代价形态——从「答不出」变成「多问一句」。`failed` 的语义随之收窄到「模型检索过但一条依据都没有」。实测：`Python 怎么装环境`（外文词判据）与 `柜子里一直嗡嗡响，是不是坏了`（措辞判据）都得到 `needs_clarification` 且模型零调用；库内问题 `MPPT 怎么跟踪组串电压` 判定返回 `None`、照常作答。测试 154 → 156 passed（两种原因各补一条），Ruff 通过。版本号 1.0.0 → 1.1.0，CHANGELOG 有对应段落，README 的终态表、`/chat` 协议节与「这个版本改了什么」表均已同步。
- 工具类问题豁免判据（2026-09-16，**1.1.1**）：修掉一个让结构化工具整个失效的缺陷。语料范围判据只该裁决「必须靠知识库才能回答」的问题，但它连设备查询与建单一起拦了：实测（212 片段真实语料）`SN-2024-000123 这台设备现在什么状态` 的词组缺失比例 0.62、`SN-2024-000123` 单独问 0.67、`帮我建个工单` 0.67，三条都被判成跑题返回追问，`query_device` 与 `create_ticket` 于是永远走不到；而同一件事换个说法（`设备 SN-2024-000123 现在是什么状态`，缺失 0.50）就能通过——**拦下它们的不是「话题不相关」，而是「措辞没对上语料」**。修复是加一层豁免：新增 `services/tools.py::has_structured_anchor()` 认三类锚点（设备序列号、算术表达式 `100*0.986` / `100 乘以 0.986`、工单诉求 `工单` / `报修` / `派单` / `转人工` / `投诉`），命中则 `agent.py` 的前置拦截跳过判据、把问题交给模型去选工具；**判据本身一个字没改**，跑题问题照旧被拦。锚点只证明「有工具可答」，不证明「答得出来」——查不到的序列号仍由工具自己报错（`SN-2024-000999` 那条用例守着）。这个缺口此前一直藏在测试盲区里：判据按片段数启用（门槛 60），而集成测试的语料远小于门槛，所以 `test_chat_queries_a_device_through_the_tool` 一直是绿的；新用例用 `_seed_identical_chunks()` 把语料撑到 65 个片段才复现，并留了一条跑题对照组，防止豁免把判据整条旁路掉。**踩到的另一个坑：uvicorn 不给 `--reload` 时不会热更**，改完代码没重启服务，端到端验证打到的还是旧代码——同一个端口上新旧实例都可能在跑，用 `/health` 里有没有新加的字段（如 `version`）来辨认。实测：设备查询回到 `completed` / `tool`（返回机型 `SUN2000-100KTL-M1`、额定功率 100kW、运行状态「并网发电」、固件版本），建单回到 `pending_confirmation` / `policy` 并带确认令牌，`Python 怎么装环境` 仍是 `needs_clarification` / `unknown_foreign_terms` 且模型零调用。测试 156 → 167 passed（锚点单元用例 10 条、集成用例 1 条），Ruff 通过。版本号 1.1.0 → 1.1.1。
- 清理电商示例域残迹（2026-09-16，**1.1.2**）：诊断「回答不够智能」时顺带扫出第 1 周电商版本没清干净的残迹。诊断结论先摆清楚——接口本身是通的（`GET /models` 与 `/chat/completions` 都返回 200），且这个 key 实际可用两个模型：`deepseek-flash`（当前 `.env` 里 `LLM_MODEL=deepseek-v4-flash` 解析到的就是它）与 `deepseek-v4-pro`（旗舰，同一个 key 可用但没有配）；用户选择保留 flash，只清遗留。清理范围：`llm.py::ANSWER_SYSTEM_PROMPT` 的身份从「你是企业客服」改为「你是光伏电站技术支持工程师」（这条提示词只有 `scripts/check_llm.py` 的单轮问答自检在用，`/chat` 走的是 `agent_loop.SYSTEM_PROMPT`，因此对外行为不变）、`check_llm.py` 的自检资料与提问、`smoke.py` 的问答与建单话术、`docs/resume_template.md` 的项目名、`INTERVIEW_README.md` 与 `LEARNING_README.md` 的举例、`course/week07.md` 的演示步骤，以及四个测试文件里的「退款」夹具（一律换成光伏文本）。同时修掉 `smoke.py` 的一个真缺陷：它调 `POST /evaluations/run` 时没带必填的 `dataset_path`（评测集移出仓库后该接口改为由调用方指定路径），脚本一直是坏的，现改为读环境变量 `SMOKE_DATASET_PATH`、未设置就跳过评测并在输出里说明。两处刻意**没有动**：`industry.py` 的 `M12`/`M13` 是语料真实分册主题（M13 讲运输与 EHS 安全），不是遗留；`AI_AGENT_8W_HANDOFF.md` 与 `CHANGELOG.md` 里的历史条目保留原文，它们记的是当时的事实。实测：`scripts/smoke.py` 全流程通过（健康检查 → 知识问答有引用 → 工单确认 → 防重放 409 → 评测按提示跳过），`scripts/check_llm.py` 通过（单轮问答依据给定片段作答、工具循环 2 轮、`calculator` 返回 5.0），167 passed（1 skipped）、Ruff 通过。版本号 1.1.1 → 1.1.2。
- 回答去掉标签噪声（2026-09-16，**1.1.3**）：用户觉得「回答不够智能」，查真实会话记录后定位到根因不是模型档位，而是元数据被抄进了正文。检索片段附带的行业标签会逐个罗列机型，真实语料里最长的一条列了 14 个型号、标签长达 224 字；而 `agent_loop.SYSTEM_PROMPT`（「检索结果每条都标注了它出自哪一版资料、哪个机型场景和协议；引用时说明这些标签」）与 `search_knowledge_base` 的工具说明（「回答时要带上这些标签」）**两处都在要求模型把这些标签写进回答**，模型便照做了。实测一条绝缘阻抗排查的回答共 1814 字，其中 4 处「**出处：V2.0 · 工商业 · SUN2000-8KTL/SUN2000-8KTL-/…（十几个型号）· procedure**」合计 581 字（占 32%），整篇读起来像资料目录而不是排查指导。修复分两层：① 服务端标签瘦身——`industry.describe_facets()` 抽出 `_describe_models()`，机型超过 `MODEL_LIST_LIMIT`（3 个）就归纳成「N 个机型通用」，少数几个机型仍逐个列出（那正是「这段只适用这几款」的关键信息，不能省）；② 提示词改口径——`SYSTEM_PROMPT` 补上「直接回答用户问的那件事：给结论和可执行的步骤，不要交代检索过程、不要解释信息来源、不要把资料标签复述一遍」并要求引用只用一句短标签带过，同时把「提醒用户按现场确认」收敛为只在真有版本差异或机型适用性限制时出现（原来每轮都会附一段泛泛免责）；`search_knowledge_base` 的工具说明同步说明那些标签是给模型自己核对依据用的。**抗幻觉的判定一条没动**：`citations`、`conflicts`、`has_structured_anchor`、语料范围判据全部照旧。实测：同一问题回答 1814 字 → 940 字且无标签罗列，改为直接给 7 步可执行排查（下电验电 → 查 PE 线 → 测对地绝缘 → 查 MC4 接头 → 逐路定位 → 百分比换算并附算例 → 潮气导致的可调项）；问「直流母线电压是多少」仍返回 `conflicts=2` 并列两种口径；设备查询仍为 `completed`/`tool`；机型适用范围差异仍在回答末尾点明（工商业版把该定位法标注为仅适用 SUN2000-12/15/17/20KTL-M2）。**这条改动只去噪声、不提升精度**，它解决不了「回答像不像工程师」的问题——那取决于模型档位（`.env` 的 `LLM_MODEL` 由 `deepseek-flash` 换成 `deepseek-v4-pro` 即可，但公司环境不允许）。测试 167 → 168 passed（新增 `describe_facets` 机型归纳用例），Ruff 通过。版本号 1.1.2 → 1.1.3。
- 第 5 周开工：LangGraph 检查点与 MCP Server（2026-09-17，**1.2.0**）：用户选定「补 LangGraph 与 MCP」后先核对现状，结论与原先的判断不同——`graph.py` 其实早已用 LangGraph 写好（`StateGraph` + 条件边 + `compile`，被 `local_model.py` 拿去做意图分类），缺的是检查点、错误节点与 MCP，所以第 5 周是从 Day 3 起步，不是从零开始。做了五件事：
  ① **检查点与中断恢复**：`build_route_graph()` 新增 `checkpointer` 与 `interrupt_after` 两个可选参数，默认 `None` 时行为与改动前完全一致（`local_model` 正在调用它，默认值不能变）。实测 `interrupt_after=["classify"]` 时第一次 `invoke` 停在 `next=('ticket',)`，带同一个 `thread_id` 用 `invoke(None, config)` 续跑后 `next=()`——这是 durable execution 的最小形态，也是「写操作等人工确认」在图层面的实现方式（与 Day 6 的签名令牌可对照看）。新增 `docs/state_graph.md`（mermaid 状态图 + State/Node/Edge 三张表 + 与数据库会话的区别）与 `examples/graph_checkpoint_demo.py`（无检查点 / 有检查点 / 中断恢复三段对照）。
  ② **工具超时**：`ToolSpec.timeout_seconds`（默认 10 秒，要查库的 `search_knowledge_base` 放宽到 15 秒）。关键坑是**同步 handler 不能直接在事件循环里调用**：`calculator` 与 `query_device` 都是同步函数，直接 `await asyncio.wait_for(handler(...), t)` 会让这次调用占住事件循环，`wait_for` 的计时器根本没机会触发——**写成超时、实际不生效**，是最容易蒙混过关的一种假安全。现在先 `asyncio.to_thread` 再等，并保留「同步函数返回协程」的兼容（`build_support_registry` 里的 handler 就是 lambda 包协程）。边界要写清：超时只让调用方不再等待，**不能中止已经在跑的同步工具**，所以「超时 ≠ 操作已回滚」，会写数据的工具必须自己支持取消或做成幂等。
  ③ **重复失败上限**：同一个「工具 + 参数」连失 `MAX_TOOL_RETRIES`（2）次后，第三次直接返回 `repeated_failure`，不再给 handler 执行机会。判定键是「工具名 + 参数原文」，换参数重试不受影响；写操作被拦下不计入——它本来就要等人工确认，计数会把正常流程误判成模型在原地打转。
  ④ **错误分类**：`ToolOutcome.error_kind` 与 `ToolCallRecord.error_kind` 分七类（`unknown_tool` / `invalid_arguments` / `needs_confirmation` / `timeout` / `tool_error` / `internal_error` / `repeated_failure`），审计与指标可以按类型统计，不必对着一堆中文错误串做关键词匹配。
  ⑤ **MCP Server 与 Client**：`src/support_agent/mcp_server.py` 暴露一个 Tool（`query_device`）、一个 Resource（`device://catalog`，只读设备清单）、一个 Prompt（`fault_report`，故障上报模板），只读不写；`scripts/mcp_client_demo.py` 走 stdio 跨进程调用，`tests/test_mcp.py` 真起子进程做集成测试。**MCP 2.x 的坑必须先记**：`FastMCP` 已改名 `MCPServer`（在 `mcp.server.mcpserver`），字段统一成 snake_case（`serverInfo` → `server_info`、`isError` → `is_error`），照 1.x 文档写会一路撞 `ModuleNotFoundError` 与 `AttributeError`。第一版把「查不到设备」写成普通返回值，Client 收到 `isError=False`——协议层看不出这次调用失败了，Host 想做「工具失败率」只能读文本猜；改成抛 `MCPServer` 的 `ToolError` 后转成 `isError=True` 且错误文本仍可读。依赖新增 `mcp>=2,<3`（`environment.yml` 走 `-e .[dev]`，会自动带上）。
  测试 168 → 191 passed（`tests/test_graph.py` 12 例、`tests/test_agent_loop.py` 容错 6 例、`tests/test_mcp.py` 5 例），Ruff 通过。文档新增 `docs/state_graph.md` 与 `docs/mcp.md`（后者含 Host/Client/Server 分工、Tools/Resources/Prompts 区别、以及鉴权·用户同意·权限边界分别归谁的答案），`docs/architecture.md` 补「工具容错」一节。**本机跑全量的两个注意点**：单次约 2–6 分钟；结尾常被沙箱拦一次临时文件删除，后台任务因此标 failed，但测试本身全绿。`--basetemp` 必须写 Windows 绝对路径，`$(pwd)` 给出的 `/d/...` 会被解析成 `D:\d\...`。
- 第 5 周 Day 6：确认令牌四道闸的演示与两处缺陷修复（2026-09-17，**1.2.1**）：开工先核对，结论与预先判断不同——防篡改（HMAC 签名）、防过期（`exp`）、防重放（`/tickets` 返回 409）**都已经实现**了，`tests/test_api.py` 也在测重放。原先「缺防重放」的判断是 grep 只扫了 `services/`、漏了 `main.py` 造成的。所以 Day 6 缺的是演示，而真正的问题在补测试时才露出来：
  ① **验签的拒绝原因是死代码**。`verify_confirmation_token` 的签名比对写在 `try` 块内部，抛出的 `ValueError("确认令牌签名无效")` 被同一个 `try` 的 `except ValueError` 接住并重包成笼统的「确认令牌无效」——这个分支调用方永远看不到。它能藏住的原因是原用例写成 `match="无效"`，两种消息都能匹配，测试一直是绿的（**松匹配的断言等于没断言**）。修法是把签名比对移出 `try`，四种结果分开：格式无效 / 签名无效 / 已过期 / 内容无效；另补两处守卫（正文不是对象、`exp` 不是数字时同样抛 `ValueError`），否则 `payload.get` 抛 `AttributeError`、`int()` 抛 `TypeError`，而调用方只接 `ValueError`，结果是 500 而不是 400。
  ② **防重放是「先查再写」，并发下会漏**。原来在 `audit_logs` 里查一条 `confirmation_consumed` 记录，查到就 409；检查与写入之间有时间窗，两个并发请求都能查到「没人用过」，同一张令牌建出两条工单。现在新增 `consumed_confirmation_tokens` 表、`token_hash` 做主键，重复写入直接撞唯一约束——**把并发正确性交给数据库，而不是交给两次查询之间的时间差**。顺带把判据与审计拆开：审计可以清理轮转，判据被删掉等于安全属性静默消失。消费记录与工单同一事务提交，所以不会出现「令牌已烧掉、工单却没建」；记录只存哈希不存原文。四道闸的顺序也写进了文档：签名 → 有效期 → 归属 → 单次使用，**验签必须排在判重之前**，否则被改过的令牌会被判成「已使用」，从响应里就能反推出这张令牌存在过。
  新增 `examples/confirmation_token_demo.py`（四段：201 / 409 已使用 / 400 签名无效 / 400 已过期；跑在临时库上，`logging.disable(INFO)` 压掉请求日志，不连模型也不加载 ONNX，结果固定）。注意一个环境坑：本机 TestClient 用的日志器叫 `httpx2` 而不是 `httpx`，按名字压级别会静默失效，要用 `logging.disable(logging.INFO)`。测试 191 → 198 passed（`test_security.py` 2 → 7 例、`test_api.py` 新增过期与唯一约束两例），Ruff 通过。文档：`docs/architecture.md` 新增「写操作确认与四道闸」一节并补数据表，README 优化对照表加两行，`CHANGELOG` 1.2.1 段。版本号 1.2.0 → 1.2.1（安全修复属修订号）。
- 第 4 周缺口补齐：切块参数对照实验（2026-09-18，**1.3.0**）。`700/100` 以前是拍的，这次把它变成试过的。做法是同一份语料（分卷 19 份 + 第3册）、同一份 40 条带 `expect_keyword` 标注的评测集、同一条线上检索路径（`SupportAgent.retrieve`），只换 `chunk_size/overlap`，每组参数用独立的一次性 SQLite 库互不共享索引：
  - 300/50 → 446 片段 / `hit@1` 0.625 / `MRR` 0.663；700/100 → 207 片段 / 0.700 / 0.727；1200/150 → 143 片段 / 0.700 / 0.738。
  - **结论：细切块明确更差**（片段数翻倍而 `hit@1` 掉 0.075）；1200/150 与 700/100 的差距落在 1–2 条样本内、且这 8 条名次不同的样本里两边各有胜负，**不足以换默认值**，所以维持 700/100。三个发现里最值得记的是第三条：**三组返回空结果的样本是完全同一批 7 条**，说明语料范围判据与切块粒度无关——切块改变的是片段怎么分组，不改变某个词组在整份语料里出现过没有。
  - 口径自检：700/100 组跑出 207 片段 / 0.700，开发库是 212 片段 / 0.700（差 5 是因为第3册在开发库由 `.docx` 导入得 17 片段、实验里用 `.md` 得 12 片段），命中率一致说明实验口径复现了线上那一次。
  - 顺带修掉一个真问题：`scripts/ingest_smartpv.py` 此前直接用 `RAGService` 的构造默认值（700/100），**没读 `CHUNK_SIZE` / `CHUNK_OVERLAP` 配置**——`.env` 改了切块参数只会影响别处，导入仍按 700 切，属「看着生效、其实没生效」的一类。现改读 `settings.chunk_size / chunk_overlap`，并开 `--chunk-size` / `--overlap` 供实验逐组覆盖。
  - 产出：`scripts/chunking_experiment.py`（`--configs` 指定多组、`--report` 只汇总）、`docs/chunking_experiment.md`（含「这个实验不能说明什么」一节）、`docs/diagrams/architecture.svg`、README 的 `/chat` 时序图（mermaid）、`docs/demo_script.md`、重写的 `docs/resume_template.md`。明细落 `.chunking-experiment/*.json` 并已 gitignore（明细带评测集原问题，评测集本身不入仓库）。该次收尾时为 198 passed、1 skipped（跳过的那项需本地模型文件），Ruff 通过；后续补齐交付面后为 210 项。
- 面试材料两份（2026-09-18，**无代码改动、不升版本**）：用户要求「把技术栈总结好教会我」并「作为面试官来问我项目内容，问题和答案都准备好」。产出两份文档：
  - `docs/tech_stack_guide.md`（技术栈教学手册）：按**层次**而不是按产品名组织——语言与分发 / 接口层 / 数据层 / 检索层 / Agent 层 / 可靠性层 / 安全层 / 验证与交付。每节固定四段：它解决什么问题 → 核心代码与变量对照 → 面试官会从哪切进来 → 必须记住的数字。最后用**三条数据流**（一次 `/chat`、一次语料导入、一次写操作确认）把八层串起来，另附五句开场总结与一张 16 条的复习检查表。所有数字都取自仓库真实值（权重 0.30/0.35/0.35、锐化 2.0、加减 +0.06/-0.10、缺失比例 0.60、门槛 60 片段、`MAX_ROUNDS=5`、`MAX_TOOL_RETRIES=2`、超时 10s/15s、TTL 300s、冷却 30s、限流 30/60s、令牌 600s、7 类 `error_kind`）。
  - `docs/mock_interview.md`（模拟面试问答集）：42 题，按**面试真实节奏**分轮——开场 / 项目全貌 / RAG 深挖 / Agent 与工具 / 可靠性与性能 / 安全 / 工程与交付 / **诚实边界** / 反问。每题给四块：面试官原话 + 难度标记（基础 / 深挖 / 陷阱）、可直接背的口语答案、追问预警与接法、仓库证据位置。第 7 轮专问「没做到的地方」，把诚实边界（没有真实认证、CI 未跑过、没有迁移工具、pgvector 只到类型层）写成主动交代的答案；Q39 复盘了简历四处不实声称是怎么自查出来的。末尾附 `interview_bank.md` 那 15 题与 10 个故障案例的对照表，故障案例统一按「排查顺序 → 项目里对应哪一处 → 这条我有没有做过」三段答。
  - 同步：`docs/interview_bank.md` 顶部加指向参考答案的说明（它此前只有题目没有答案）；README 的仓库导航补两行。
- 下一步：第 5 周只剩 Day 7（关掉 AI 实现一个新的只读工具）；之后回到第 3 周遗留的 Day 7——让用户独立重写 `safe_calculate` 的受限 AST 求值与 `parse_arguments` 的参数校验，并为工具层异常路径补评测样本（分层评测已经就绪，正好用它来量）。**第 7 周的展示件已补三样**（架构图、时序图、演示视频脚本），剩下真正要用户做的是「按脚本录一遍视频」与「按新简历模板填写个人经历」。项目侧只剩一项与 Codex 定义的差距：结构化点表（`lookup_register` / `convert_register_value` / `compare_protocol_versions`），需要先选定脱敏点表资料。（原 ① 响应协议、② 评测升级、③ 光伏行业专属均已于 2026-09-15 完成；拒答链路与本地语义向量已于 2026-09-16 完成；Redis 检索缓存与限流已于 2026-09-16 完成；软件化打包与 1.0.0 发布已于 2026-09-16 完成；口语化误拦的取舍已定案（改成追问）；工具类问题豁免判据已完成（1.1.1）；电商示例域残迹清理已完成（1.1.2）；回答去标签噪声已完成（1.1.3）；第 5 周 LangGraph 检查点与 MCP 已完成（1.2.0）；第 5 周 Day 6 确认令牌四道闸与两处缺陷修复已完成（1.2.1）；第 4 周切块对照实验与展示件已完成（1.3.0）；pgvector 仍未接线，理由与前置条件见上两条。）

## 8. 建议给下一台主机 Codex 的首条提示词

用户可以在新对话中发送：

```text
请先读取仓库根目录的 AI_AGENT_8W_HANDOFF.md、LEARNING_README.md、INTERVIEW_README.md、README.md 和 course/README.md，接着当前学习进度继续。第 1、2 周已完成第一轮学习和引导式复习；第 3 周 Day 1～Day 6 已完成。LLM 客户端已实现错误分类、有限重试和工具调用适配；`services/agent_loop.py` 手写了最多 5 轮的 Agent Loop（含工具白名单、参数校验、写操作确认、轮数用尽强制收敛）；Day 6 已把该循环接进 `POST /chat`，主路径是「模型选工具、服务端校验执行」，并新增 `RuleBasedLocalModel`，使无 API Key 时也能跑完整链路。此外已完成附加节「SmartPV 知识库导入与检索隔离」，检索层支持 corpus_id 语料隔离与最低相关度阈值，命中为空时直接拒答；并做过一轮「口语化检索」改造，查询侧剥虚词 + 二元字组打分，使「啥是合母」这类大白话与书面语问法等价。项目当前版本 1.3.0（包名 `smartpv-support-agent`，命令行 `smartpv-agent version|doctor|serve`），基线 210 passed（1 skipped，共 211 项，覆盖率 88.84%）。`/chat` 已经补上终态协议：返回 `status`（`completed`/`degraded`/`pending_confirmation`/`blocked`/`failed`）、`answer_source`（`knowledge`/`tool`/`model`/`policy`/`fallback`）和 `retryable`，终态一律由服务端判定，模型无权声明。离线评测已从「只看检索」升级为三层（检索 / 工具选择 / 最终回答），且不自己写判定，而是复用线上代码——`run_turn` 由 `respond` 拆出（跑完整链路判终态、无落库副作用），评测的检索层与回答层都调它。此外已接入真实模型：在 `.env` 填 `LLM_BASE_URL`/`LLM_MODEL`/`LLM_API_KEY` 即切换到远程模型，适配层已处理思考模式的 `reasoning_content` 回传，`scripts/check_llm.py` 可一键自检；测试套件不读 `.env`，与本机配置无关。片段已带行业标签（机型 / 协议 / 文档版本 / 场景 / 片段类型，见 `services/industry.py`），检索时先看标签再比相似度，标签只影响排序不做硬过滤；依据跨版本时 `/chat` 以 `conflicts` 字段并列返回各版本说法，不替用户挑一个。拒答链路已打通：不再依赖分数阈值，改用两个语料范围判据（词组缺失比例、外文词是否全不认识），并在调用模型之前判定，命中后返回 `needs_clarification`/`policy` 请用户补充设备型号或现象、零模型调用（带设备序列号、算式或工单诉求的问题豁免这条判据，交给工具承接，见 `has_structured_anchor`）。第 5 周已推进到 Day 6：`graph.py` 加上检查点与中断恢复（`build_route_graph(checkpointer=..., interrupt_after=...)`，默认关闭、行为不变），工具层补了独立超时、重复失败上限与失败分类（`error_kind` 七类），新增 MCP Server（`python -m support_agent.mcp_server`，暴露 Tool/Resource/Prompt 各一个，只读不写；注意 MCP 2.x 里 `FastMCP` 已改名 `MCPServer`、字段为 snake_case），并把写操作确认的四道闸（签名 / 有效期 / 归属 / 单次使用）演示化——单次使用改由 `consumed_confirmation_tokens` 的主键约束判定，不再「先查再写」，`python examples/confirmation_token_demo.py` 可复现四段结果。第 4 周的切块参数对照实验也已补上：三组参数各建一份独立索引（300/50 得 446 片段 / `hit@1` 0.625；700/100 得 207 / 0.700；1200/150 得 143 / 0.700），结论是细切块明确更差、粗切块与默认值差在噪声内，故维持 700/100，详见 `docs/chunking_experiment.md`；实验脚本是 `scripts/chunking_experiment.py`（`--configs` / `--report`），顺带修掉 `scripts/ingest_smartpv.py` 不读 `CHUNK_SIZE` / `CHUNK_OVERLAP` 配置的问题。作品集展示件已补：`docs/diagrams/architecture.svg`（分层架构图）、README 里的一次 `/chat` 请求时序图（mermaid）、`docs/demo_script.md`（3–5 分钟演示视频的分镜与旁白稿）；`docs/resume_template.md` 已重写为如实版（删掉四处与仓库不符的声称，每条要点注明证据位置）。下一步是第 5 周 Day 7（关掉 AI 实现一个新的只读工具）；之后回到第 3 周遗留的 Day 7：让用户关闭 AI 独立重写 `safe_calculate` 的受限 AST 求值与 `parse_arguments` 的参数校验，并为工具层异常路径补评测样本。请用中文、概念优先、少讲不必要语法。每节最后设置两道能够从当节内容推导的面试级问题；每节完成后，把题目、标准答案、30 秒表达和项目对应情况追加到 INTERVIEW_README.md，不记录用户原始回答。不要把讲过等同于已经掌握。
```

## 9. 新主机开始前的核对清单

1. `git pull` 后确认存在本文件、`LEARNING_README.md` 和 `INTERVIEW_README.md`。
2. 创建或同步 Conda 环境，不要硬编码当前主机的解释器路径。
3. 从 `.env.example` 创建 `.env`。默认留空即可（走本地规则模型）；若要接真实模型，填入 `LLM_BASE_URL` / `LLM_MODEL` / `LLM_API_KEY` 三项后再运行 `python scripts/check_llm.py` 自检。`.env` 不进 Git，密钥不要跨主机传输。
4. 运行全部测试（211 项）和 Ruff。要跑本地语义向量，先 `pip install -e ".[semantic]"` 并准备模型目录（见 `.env` 的 `EMBEDDING_BACKEND`），换后端后用 `python scripts/ingest_smartpv.py --source <资料目录> --reset` 重建语料。种子脚本已随示例语料一并删除，语料改用 `python scripts/ingest_smartpv.py --source <资料目录>` 导入；桌面客户端用 `python scripts/create_desktop_launcher.py` 生成。
5. 启动服务并打开 Swagger。
6. 先确认用户希望继续“全貌讲解”，不要擅自重头重复 Python 基础。
