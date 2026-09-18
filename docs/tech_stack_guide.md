# 技术栈教学手册

> 用途：把项目里这 8 项技术栈讲到「能对别人讲清楚、被追问也接得住」的程度。
> 读法：每节先看「它解决什么问题」，再看代码与变量对照，最后看「面试官会从哪切进来」。
> 本手册里的数字全部取自这个仓库，随时可以用 `python -m support_agent doctor` 和 `pytest` 复现。

## 目录

时间紧就只看两节：第 0 节拿到全景，第 9 节拿到三条数据流。这两节是骨架，其余八节是把骨架上的每根骨头讲透。

- [0. 全景：8 项技术栈分别站在哪一层](#0-全景8-项技术栈分别站在哪一层)
    ○ 一张表看清八层各自站在哪、主要文件在哪
- [1. 语言与分发：Python 3.12 + 打包](#1-语言与分发python-312--打包)
    ○ 单一版本号来源、`console_scripts` 入口、wheel 里的静态资源
- [2. 接口层：FastAPI + Pydantic](#2-接口层fastapi--pydantic)
    ○ 8 个端点、`ChatStatus` 六态、为什么 `status` 和 `answer_source` 要分开
- [3. 数据层：SQLAlchemy 2 + SQLite / PostgreSQL + pgvector](#3-数据层sqlalchemy-2--sqlite--postgresql--pgvector)
    ○ 9 张表、向量列的双模式降级、代次失效
- [4. 检索层：混合打分 + 本地语义向量 + 行业元数据](#4-检索层混合打分--本地语义向量--行业元数据)
    ○ 三路权重、ONNX 指纹、语料范围判据为什么必须前置
- [5. Agent 层：手写 Loop + LangGraph](#5-agent-层手写-loop--langgraph)
    ○ 模型只申请、服务端校验、超时与重复失败上限、检查点恢复
- [6. 可靠性层：Redis 缓存 + 限流 + 熔断](#6-可靠性层redis-缓存--限流--熔断)
    ○ 缓存键、固定窗口限流、Redis 挂掉后接口为什么不跟着挂
- [7. 安全层：注入拦截 + 写操作四道闸](#7-安全层注入拦截--写操作四道闸)
    ○ 验签为什么必须在判重之前、防重放靠主键冲突
- [8. 验证与交付：pytest + 三层评测 + Docker + MCP](#8-验证与交付pytest--三层评测--docker--mcp)
    ○ 211 项测试、分层评测的 `tools` 层语义、双模式部署、旁路 MCP
- [9. 三条数据流，把八层串起来](#9-三条数据流把八层串起来)
    ○ 一次 `/chat`、一次语料导入、一次写操作确认
- [10. 五句必须背下来的总结](#10-五句必须背下来的总结)
    ○ 被问「介绍一下你的项目」时的开场五句
- [11. 复习检查表](#11-复习检查表)
    ○ 16 条自测项，答不出就回上面找对应小节

---

## 0. 全景：8 项技术栈分别站在哪一层

一层一层往上搭，这项技术栈就是这一层的建筑材料。

| 层 | 技术栈项 | 主要文件 | 这一层解决什么 |
| --- | --- | --- | --- |
| 语言与分发 | Python 3.12 | 全仓库 · `pyproject.toml` · `cli.py` | 现代类型标注；打包成 wheel，暴露出 `smartpv-agent` 命令 |
| 接口层 | FastAPI + Pydantic | `main.py` · `schemas.py` | 8 个 HTTP 端点；每个请求和响应都由 Pydantic 模型约束 |
| 数据层 | SQLAlchemy 2 + SQLite / PostgreSQL + pgvector | `models.py` · `db.py` | 9 张表；向量列在 SQLite 退化成 JSON、在 PostgreSQL 走 pgvector |
| 检索层 | 自研混合检索 + 本地 ONNX 语义向量 | `services/rag.py` · `embeddings.py` · `semantic.py` · `industry.py` | 三路打分 + 行业元数据加减 + 语料范围判据 |
| Agent 层 | 手写 Agent Loop + LangGraph | `services/agent_loop.py` · `graph.py` · `local_model.py` | 模型申请工具、服务端校验执行；LangGraph 管意图分类与检查点 |
| 可靠性层 | Redis（可降级） | `services/cache.py` | 检索缓存 + 固定窗口限流 + 熔断降级 |
| 安全层 | HMAC 令牌 + 注入拦截 | `services/security.py` · `models.ConsumedConfirmationToken` | 写操作四道闸；注入在进循环之前就拦掉 |
| 验证与交付 | pytest + 三层评测 + Docker + MCP | `tests/` · `services/evaluation.py` · `docker-compose.yml` · `mcp_server.py` | 211 项测试、分层评测、双模式部署、旁路 MCP 服务 |

源代码总量约 4900 行，最大的四个文件是 `rag.py`(597)、`cache.py`(490)、`agent_loop.py`(421)、`agent.py`(400)。

---

## 1. 语言与分发：Python 3.12 + 打包

### 它解决什么问题

一个学习项目要能当作品集，最低要求是「别人拿到能装、能跑、能查版本」。这靠三件事：单一版本号来源、一组 `console_scripts` 入口、一份能打进 wheel 的静态资源。

### 核心代码与变量对照

```python
# src/support_agent/__init__.py
__version__ = "1.3.0"
__version_info__ = tuple(int(part) for part in __version__.split("."))
```

其中：

- `__version__` —— 全项目版本号的唯一来源，值是 `"1.3.0"`
- `__version_info__` —— 拆成整数元组 `(1, 3, 0)`，方便比较大小
- `pyproject.toml` 里写 `dynamic = ["version"]`，由 hatch 来读这个值，所以改版本只改这一行

```python
# src/support_agent/main.py
app = FastAPI(title="光伏电站技术支持 Agent", version=__version__)

# src/support_agent/cli.py
def main() -> int:
    # 子命令：version / doctor / serve
    ...
```

其中：

- `version=__version__` —— 让 OpenAPI 文档和 `/health` 报的版本跟着上面那个变量走，不写死
- `main()` —— `smartpv-agent` 命令的入口函数，返回值就是进程退出码
- `doctor` 子命令 —— 逐项打印配置、语料规模、向量后端、缓存状态，任一硬伤返回非 0

### 面试官会从哪切进来

「你的版本号怎么管理？」——答单一来源 + hatch 动态读取 + 四步发布（改 `__version__` → 更新 CHANGELOG → `python -m build --no-isolation` → 核对 wheel 名）。**不要**答「我在好几个文件里都改了」。

### 你必须记住的数字

- 版本 `1.3.0`
- 包名 `smartpv-support-agent`，命令 `smartpv-agent version|doctor|serve`
- `dist/` 里必须有同版本的 `.whl` 和 `.tar.gz` 各一份

---

## 2. 接口层：FastAPI + Pydantic

### 它解决什么问题

Agent 系统最容易出的问题不是答错，而是**调用方不知道这一轮到底怎么了**——是答好了、在等确认、还是压根没依据？所以接口层的重点不在路由数量，而在**终态协议**。

### 核心代码与变量对照

```python
# src/support_agent/schemas.py
ChatStatus = Literal[
    "completed", "degraded", "pending_confirmation",
    "needs_clarification", "blocked", "failed",
]
AnswerSource = Literal["knowledge", "tool", "model", "policy", "fallback"]

class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    status: ChatStatus = "completed"
    answer: str
    answer_source: AnswerSource = "model"
    citations: list[Citation] = []
    pending_action: PendingAction | None = None
    clarification: Clarification | None = None
    retryable: bool = False
    conflicts: list[VersionConflict] = []
```

其中：

- `ChatStatus` —— 这一轮**成功了吗**。六个值是互斥的，服务端判定，模型无权声明
- `AnswerSource` —— 这句话的**依据来自哪里**。和 `status` 是两个正交维度，评测按它分层统计
- `citations` —— 知识库检索命中的原文出处，只有 `answer_source=knowledge` 时非空
- `pending_action` —— 写操作被拦下时给的确认令牌，对应 `status=pending_confirmation`
- `clarification` —— 语料范围判据命中时给的原因和建议补充项，对应 `status=needs_clarification`
- `retryable` —— 只有模型故障且属于暂时性错误时才为真，客户端据此决定要不要自动重试
- `conflicts` —— 依据跨了两个以上资料版本时并列返回，语义是「按现场型号确认」，不是「资料互相矛盾」

八个端点集中在 `main.py`：

```text
GET  /health              配置、语料规模、向量后端、缓存状态、限流额度
POST /documents           上传文档并导入语料
POST /chat                主链路，返回上面的 ChatResponse
GET  /sessions            会话列表
GET  /sessions/{id}       单个会话与全部消息
POST /feedback            对某条消息打分
POST /tickets             凭确认令牌建工单
POST /evaluations/run     跑一次离线评测
GET  /                    单文件前端页面（挂在所有 API 之后）
```

### 面试官会从哪切进来

「为什么返回 `200` 还要在 body 里带一个 `status`？」——因为 HTTP 状态码描述的是**传输层**结果，而这六种终态都是「请求成功处理完了」，区别在业务含义。用 HTTP 码表达业务终态会导致客户端靠猜。

「为什么 `GET /` 要挂在最后？」——FastAPI 的 `mount` 一旦挂到 `/static` 就会遮蔽后续注册的路由；顺序错了表现为接口突然 404 而页面正常。

### 你必须记住的数字

- 6 个 `ChatStatus` + 5 个 `AnswerSource`
- 8 个端点
- 首页 HTML 约 24.7KB，用相对路径 fetch，换端口也能用

---

## 3. 数据层：SQLAlchemy 2 + SQLite / PostgreSQL + pgvector

### 它解决什么问题

同一份代码要在两种模式下跑：本地 SQLite（开发、CI、演示，零依赖）和 PostgreSQL + pgvector（容器模式，展示真实向量库）。难点是**向量列**——两种数据库的向量存储完全不同。

### 核心代码与变量对照

```python
# src/support_agent/models.py
VECTOR_DIMENSION = get_settings().vector_dimension

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    embedding: Mapped[list[float]] = mapped_column(
        Vector(VECTOR_DIMENSION).with_variant(JSON, "sqlite")
    )
```

其中：

- `VECTOR_DIMENSION` —— 建表时的列宽，值来自配置（哈希后端 384、ONNX 后端 512）
- `Vector(VECTOR_DIMENSION)` —— pgvector 的向量列类型，只在 PostgreSQL 下生效
- `.with_variant(JSON, "sqlite")` —— SQLAlchemy 的方言变体：连的是 SQLite 时这一列改用 JSON 存
- `Mapped[list[float]]` —— ORM 类型标注，读出来是浮点列表

```python
# src/support_agent/models.py
class ConsumedConfirmationToken(Base):
    __tablename__ = "consumed_confirmation_tokens"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64))
    ticket_id: Mapped[str | None] = mapped_column(ForeignKey("tickets.id"), nullable=True)
```

其中：

- `token_hash` —— **主键**。这不是为了唯一标识，而是为了把「防重放」压成一次原子写入
- `user_id` —— 令牌归属人，用于第三道闸「归属校验」
- `ticket_id` —— 消费后建出的工单，与令牌记录**同一事务**提交

九张表：`conversations` / `messages` / `source_documents` / `document_chunks` / `tickets` / `feedback` / `evaluation_runs` / `audit_logs` / `consumed_confirmation_tokens`。

### 面试官会从哪切进来

「你用了 pgvector 吗？」——**这是最危险的一问，必须如实分层回答**：向量列用 `pgvector.sqlalchemy.Vector` 声明，`Vector(512)` 有方言变体，compose 里用的是 `pgvector/pgvector:pg16` 镜像、`scripts/init.sql` 建 extension；但**没有接 ANN 索引**，也没有写 `<=>` 距离查询，开发库是 SQLite。所以准确说法是「pgvector 用到类型层与部署层，没用到检索层」。

「为什么不接 ANN 索引？」——打分里的 IDF 权重依赖全语料词频，只取向量近邻候选就算不出 df，除非先把词频统计落库；而 212 个片段全量扫的代价可以忽略。做「有开关但从不触发」只是增加解释成本。

### 你必须记住的数字

- 9 张表
- 212 个检索片段 / 20 篇文档
- 向量维度：hash 384、onnx 512
- `chunk_size=700`、`chunk_overlap=100`

---

## 4. 检索层：混合打分 + 本地语义向量 + 行业元数据

### 它解决什么问题

三个独立问题必须分开解决，混在一起就调不动：

1. **口语化问法排不进前五** —— 「合母和控母有啥区别」的正确章节排第 9
2. **跑题问题拿到不低的分** —— 「Python 怎么装环境」撞上「安装环境」
3. **型号场景不对的章节排在前面** —— 问户用机型，出来地面电站

### 核心代码与变量对照

```python
# src/support_agent/services/rag.py
TEXT_WEIGHTS = {"lexical": 0.30, "phrase": 0.35, "semantic": 0.35}
COVERAGE_SHARPNESS = 2.0
MATCH_BONUS = 0.06
CONFLICT_PENALTY = 0.10
CORPUS_MISSING_CEILING = 0.60
CORPUS_MISSING_MIN_CHUNKS = 60

score = (
    TEXT_WEIGHTS["lexical"] * lexical**COVERAGE_SHARPNESS
    + TEXT_WEIGHTS["phrase"] * phrase**COVERAGE_SHARPNESS
    + TEXT_WEIGHTS["semantic"] * semantic
)
if signals.matched:
    score += MATCH_BONUS * len(signals.matched)
if signals.conflicted:
    score -= CONFLICT_PENALTY * len(signals.conflicted)
```

其中：

- `TEXT_WEIGHTS` —— 三路文本信号的权重。`lexical` 管召回（单字重叠），`phrase` 管区分（两字组合），`semantic` 管语义
- `lexical` / `phrase` —— 查询词在片段里的加权覆盖率，权重是按 IDF 算的
- `semantic` —— 查询向量与片段向量的余弦相似度，负数截断到 0
- `COVERAGE_SHARPNESS` —— 覆盖率锐化指数，取 2.0 表示做平方。实测不加锐化时间隔只有 0.016，平方后 0.089
- `signals.matched` / `signals.conflicted` —— 片段行业标签与查询意图的匹配/冲突列表
- `MATCH_BONUS` / `CONFLICT_PENALTY` —— 元数据加减分。**只做加减不硬过滤**，因为语料对机型覆盖不全
- `CORPUS_MISSING_CEILING` —— 查询词组在整份语料里的缺失比例上限，超过判定为跑题
- `CORPUS_MISSING_MIN_CHUNKS` —— 上面那条判据的启用门槛，按**片段数**算（曾是按文档数算，导致判据整个没生效）

口语化的关键在查询侧预处理：

```python
# src/support_agent/services/embeddings.py
STOPWORDS = frozenset({...})
def strip_stopwords(text): return "".join(c for c in text if c not in STOPWORDS)
def bigram_terms(text): ...
```

其中：

- `STOPWORDS` —— 虚词与口语词集合（啥、是、有、么、怎么……）
- `strip_stopwords()` —— 把虚词剥掉
- `bigram_terms()` —— 相邻两字成组，`合母`/`控母` 就是靠这一步才区分得开
- **只对查询侧剥，文档侧不剥**；两边的分母必须是同一份剥过的文本，否则分数提不上去

行业的标签只在排序上起作用：

```python
# src/support_agent/services/industry.py
MODEL_LIST_LIMIT = 3
def _describe_models(names): 
    # 机型 > 3 个归纳成「N 个机型通用」，≤3 个逐个列出
```

其中：

- `MODEL_LIST_LIMIT` —— 标签里最多列几个型号。改之前最长标签 224 字，改完 20 字
- 三个抽取入口：`device_models`（机型）、`protocols`（协议）、`document_version`（版本）+ `scenario` + `content_type`
- **标签必须从片段正文抽，不能只扫小节标题**：第一版只扫标题，95 个章节只命中 4 个机型、0 个协议

### 面试官会从哪切进来

「为什么不直接用一个分数阈值拒答？」——因为库内库外**分布重叠**，这是实测过的：哈希向量下库内最低 0.182、库外最高 0.353；换成真语义向量后库外反而涨到 0.486（「怎么考驾照」撞上「危险品运输管理」一节，那节真的提到驾驶证）。**换了更好的向量，阈值这条路更走不通**，因为通用中文句子之间的相似度本来就高。

「那你怎么拒答？」——改用两个**语料范围判据**：词组缺失比例 ≥0.60，或查询里的外文词一个都不认识。而且**判定必须前置在调模型之前**——实测模型遇到跑题问题压根不调检索工具，直接凭身份拒答，所以服务端那句「检索过但没有依据」的兜底永远等不到。

「判据的代价是什么？」——仍是词汇层面的近似。10 条口语化改写问法里有 7 条被误拦。所以命中判据时返回的**不是拒答而是追问**（`needs_clarification`）。这不是精度提升，只是把代价形态从「答不出」换成「多问一句」。

### 你必须记住的数字

- 权重 0.30 / 0.35 / 0.35，锐化指数 2.0
- 元数据加减 +0.06 / -0.10，只影响排序不做硬过滤
- 缺失比例阈值 0.60，启用门槛 60 个片段
- 语料 20 文档 / 212 片段
- 切块对照：300/50 → 446 片段 / hit@1 0.625；700/100 → 207 / 0.700；1200/150 → 143 / 0.700
- 三组返回空结果的样本**完全同一批 7 条**

---

## 5. Agent 层：手写 Loop + LangGraph

### 它解决什么问题

这是项目的主干。要回答的是：**模型说「我要调这个工具」之后，服务端凭什么相信它？**

### 核心代码与变量对照

```python
# src/support_agent/services/agent_loop.py
MAX_ROUNDS = 5
MAX_TOOL_RETRIES = 2
DEFAULT_TOOL_TIMEOUT = 10.0

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[[dict[str, Any]], Any]
    writes: bool = False
    timeout_seconds: float = DEFAULT_TOOL_TIMEOUT

    def as_schema(self) -> dict[str, Any]:
        """转成 OpenAI 兼容接口 tools 字段要求的格式；handler 绝不出现在这里。"""
```

其中：

- `MAX_ROUNDS` —— 一轮对话最多几轮模型往返，值 5
- `MAX_TOOL_RETRIES` —— 同一个「工具 + 参数」最多失败几次，值 2
- `ToolSpec.name` —— 工具名，模型只能按这个名字申请
- `ToolSpec.description` —— 给模型看的说明书
- `ToolSpec.parameters` —— JSON Schema，服务端也拿它做参数校验
- `ToolSpec.handler` —— 真正的执行函数，**只在服务端存在**
- `ToolSpec.writes` —— 是否写操作，为真的工具不会被循环自动执行
- `as_schema()` —— 把 `handler` 摘掉后发给模型。**说明书 ≠ 执行权**，这是整个 Agent 层最重要的一条分界

工具执行函数永不抛异常：

```python
async def execute_tool_call(name, raw_arguments, registry) -> ToolOutcome:
    spec = registry.get(name)
    if spec is None:
        return ToolOutcome(False, f"错误：工具 {name} 不在允许列表中", error_kind="unknown_tool")
    try:
        arguments = parse_arguments(spec, raw_arguments)
    except ToolError as exc:
        return ToolOutcome(False, f"错误：{exc}", error_kind="invalid_arguments")
    if spec.writes:
        return ToolOutcome(False, ..., requires_confirmation=True, error_kind="needs_confirmation")
    try:
        result = await asyncio.wait_for(_invoke(spec, arguments), timeout=spec.timeout_seconds)
    except TimeoutError:
        return ToolOutcome(False, ..., error_kind="timeout")
```

其中：

- `ToolOutcome` —— 一次调用结果，字段是 `ok` / `text` / `parsed` / `requires_confirmation` / `error_kind`
- `error_kind` —— 七分类：`unknown_tool` / `invalid_arguments` / `needs_confirmation` / `timeout` / `tool_error` / `internal_error` / `repeated_failure`
- `parse_arguments()` —— 四道校验：是不是 JSON 字符串 → 能不能解析成对象 → 有没有未定义字段（**拒绝而不是忽略**）→ 必填和类型对不对
- 顺序：**先校验参数，再判写操作**。不能让用户去确认一个参数本身就不合法的操作

超时能真的生效，靠的是这一层：

```python
async def _invoke(spec, arguments):
    if inspect.iscoroutinefunction(spec.handler):
        return await spec.handler(arguments)
    result = await asyncio.to_thread(spec.handler, arguments)
    if inspect.isawaitable(result):
        return await result
    return result
```

其中：

- `asyncio.to_thread()` —— 把同步 handler 丢到线程里执行
- **不这样做超时就是摆设**：同步函数直接在事件循环里调用会占住整个循环，`wait_for` 的计时器根本没机会触发。写成超时、实际不生效，是最容易蒙混过关的假安全

LangGraph 那一路（`graph.py`）：

```python
ROUTES: tuple[Route, ...] = ("blocked", "calculator", "device", "ticket", "knowledge")

def build_route_graph(checkpointer=None, interrupt_after=None):
    graph.add_node("classify", classify)
    for route in ROUTES:
        graph.add_node(route, passthrough)
        graph.add_edge(route, END)
    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", lambda state: state["route"])
```

其中：

- `ROUTES` —— 五条业务分支，`classify` 节点判定后走条件边
- `checkpointer` —— 检查点存储器，默认 `None` 时退化成纯计算，行为与改动前一致
- `interrupt_after` —— 在指定节点之后中断，用于「写操作等人工确认」
- 实测：`interrupt_after=["classify"]` 时第一次 `invoke` 停在 `next=('ticket',)`，带同一个 `thread_id` 用 `invoke(None, config)` 续跑后 `next=()`
- **`graph.py` 只被 `local_model.py` 当规则大脑用**，主链路走的是手写 `agent_loop.py`。这个分工必须说清楚，否则会被追问「你到底用了哪个」

### 面试官会从哪切进来

「既然用了 LangGraph，为什么还要手写 Loop？」——codex 定的学习原则就是「先手写 Loop 再上框架，LangGraph 作为唯一主修」。手写一遍才知道检查点、中断恢复、状态传递这些抽象在解决什么；`graph_checkpoint_demo.py` 就是拿手写循环和图层实现对照看的。

「模型传来一个不存在的工具名会怎样？」——`registry.get()` 返回 `None`，直接给 `unknown_tool`，不做动态查找、不用 `getattr`、不拼函数名。

「多传一个参数会怎样？」——拒绝。静默忽略会让越权参数悄悄通过，一旦以后实现改成读整个参数字典，漏洞就暴露了。

### 你必须记住的数字

- `MAX_ROUNDS=5`、`MAX_TOOL_RETRIES=2`、工具超时默认 10 秒、检索工具 15 秒
- 7 类 `error_kind`
- 5 条 LangGraph 路由分支

---

## 6. 可靠性层：Redis 缓存 + 限流 + 熔断

### 它解决什么问题

`/chat` 是整套接口里最贵的一个，而且每一轮都要读一遍全语料（212 片段）切词算词频。实测库内问题一次 **385ms**、跑题问题 **340ms**，全花在这上面。

### 核心代码与变量对照

```python
# src/support_agent/services/cache.py
class KeyValueStore(abc.ABC):      # 只给四个原语：get / set / incr / close
class MemoryStore(KeyValueStore):  # 进程内实现，没配 REDIS_URL 时的默认路径
class RedisStore(KeyValueStore):   # 薄封装，socket 超时 1 秒
class ResilientStore(KeyValueStore):  # 包住前两者，失败后打开熔断
```

其中：

- `KeyValueStore` —— 抽象基类。**只有四个方法**，不做 Redis 客户端的全量透传：上层用不到的能力留在那里，只会让人猜「这个项目到底靠 Redis 做了多少事」
- `MemoryStore` —— 进程内字典实现。本地开发与 CI 走这条，功能完整
- `RedisStore` —— 超时必须设短（1 秒）。这个存储对正确性不是必需的，让慢 Redis 拖住整个请求比直接降级更糟
- `ResilientStore` —— 失败后打开熔断，冷却期（`cache_failure_cooldown_seconds=30`）内直接走兜底

缓存存什么，也是设计要点：

```python
cache_parts = (key_query, top_k, corpus_id or "", include_restricted, min_score,
               self.backend.signature)
cached = await self.cache.get(cache_parts)
...
await self.cache.put(cache_parts, [(hit.chunk.id, hit.score) for hit in ranked])
```

其中：

- `key_query` —— 归一化后的查询（已剥停用词）。「啥是控母」和「控母」共用一份
- `self.backend.signature` —— 向量后端指纹（如 `onnx:512`）。少了它就会「改了配置却还读到旧结果」
- `[(hit.chunk.id, hit.score)]` —— 存的是**片段 id + 分数**，不是 ORM 对象。命中后按 id 回库取正文，片段被删时自然少返回
- 空结果也缓存：跑题问题会被反复问到，而判据比算分还贵

失效用「语料代次」而不是删 key：

- 导入文档时把代次 +1，新 key 天然带新代次，旧的靠 TTL（`cache_ttl_seconds=300`）过期
- Redis 下按前缀删要 SCAN 全库，代价远高于等它过期
- 代价：**绕过 `RAGService` 直写库的路径必须自己调 `invalidate()`**。漏掉的表现很隐蔽——刚导进去的内容在 TTL 内查不到，看起来像导入失败

限流用固定窗口：

```python
# 窗口号进 key，一次 INCR 判定；放在 /chat 最前面
```

其中：

- `rate_limit_requests=30` / `rate_limit_window_seconds=60` —— 单用户每 60 秒 30 次
- 被拒请求**不建会话、不写消息、不调模型**
- 正常响应带 `X-RateLimit-Limit` / `Remaining`，`Retry-After` 只在 429 给

### 面试官会从哪切进来

「Redis 挂了会怎样？」——降级到进程内实现，接口不受影响，只是命中率下降、限流额度按进程数放大。`/health` 的 `cache.{backend, primary, degraded}` 是排障第一站。实测把 `REDIS_URL` 指向不可达地址：首次吃满 1008ms 超时，之后 0.0ms。

「为什么用固定窗口不用滑动窗口？」——滑动窗口要为每个请求存时间戳再按范围清理；而「防止单用户打爆模型调用」这个目的用一次 `INCR` 就够了。代价是窗口交界处最坏放过两倍流量，可以接受。

「怎么保证缓存和数据库不脱节？」——存 id 不存对象；键带全所有会影响结果的输入；失效用代次；直写库的路径自己 `invalidate()`。

### 你必须记住的数字

- 库内问题 385ms → 11ms；跑题问题 340ms → 0.3ms
- 不可达 Redis：首次 1008ms，之后 0.0ms
- TTL 300 秒、熔断冷却 30 秒、限流 30 次 / 60 秒
- `tests/test_cache.py` 35 条测试，全走进程内实现

---

## 7. 安全层：注入拦截 + 写操作四道闸

### 它解决什么问题

Agent 系统有两类独有的攻击面：**用户通过文本改变模型行为**，以及**模型提出的写操作被自动执行**。

### 核心代码与变量对照

```python
# src/support_agent/services/security.py
def create_confirmation_token(payload, secret, ttl_seconds=600) -> str:
    body = {**payload, "exp": int(time.time()) + ttl_seconds}
    encoded = base64.urlsafe_b64encode(json.dumps(body, ...).encode()).decode().rstrip("=")
    signature = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"
```

其中：

- `payload` —— 令牌承载的操作数据，例如要建的工单要素
- `exp` —— 过期时间戳。`ttl_seconds=600` 即 10 分钟
- `encoded` —— Base64url 编码的正文，**只是编码，不负责加密**
- `signature` —— HMAC-SHA256 签名，覆盖的是编码后的正文。所以改内容不重签一定对不上
- 返回格式 `正文.签名` 两段

```python
def verify_confirmation_token(token, secret) -> dict:
    try:
        encoded, supplied_signature = token.split(".", 1)
    except ValueError as exc:
        raise ValueError("确认令牌格式无效") from exc

    expected = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(supplied_signature, expected):
        raise ValueError("确认令牌签名无效")     # ← 在 try 之外
    ...
```

其中：

- 签名比对**写在 `try` 之外**。写进同一个 `try` 里会被自己的 `except ValueError` 接住、重包成笼统的「无效」，那个分支就成了永远走不到的死代码
- 四种拒绝原因必须分得开：格式无效 / 签名无效 / 已过期 / 内容无效
- 只抛 `ValueError`。否则 `payload.get` 抛 `AttributeError`、`int()` 抛 `TypeError`，而调用方只接 `ValueError`，结果是 500 而不是 400

四道闸的顺序是固定且有理由的：

```text
签名 → 有效期 → 归属 → 单次使用
```

其中：

- 前三道都是**无状态**的，不查库
- 第四道靠 `consumed_confirmation_tokens` 的**主键冲突**判定，不是「先查再写」
- **验签必须排在判重之前**：否则被改过的令牌会返回 409「已使用」，从响应里就能反推出「这张令牌存在过」

注入拦截和语料范围判据都在**进循环之前**：

```text
POST /chat
  → 限流（被拒不建会话）
  → 注入检测（命中即 blocked，模型零调用）
  → 语料范围判据（命中即 needs_clarification，模型零调用）
  → 结构化锚点豁免（序列号 / 算式 / 工单诉求 → 跳过判据）
  → 进 Agent Loop
```

其中：

- `has_structured_anchor()` —— 认三类锚点。**它只证明「有工具可答」，不证明「答得出来」**
- 这个豁免修的是一个真缺陷：判据把设备查询和建单一起拦了，`SN-2024-000123 这台设备现在什么状态` 缺失比例 0.62 被判跑题，结构化工具整个失效

### 面试官会从哪切进来

「你的注入检测放在哪？为什么不能做成一个工具？」——放在循环之前。做成工具意味着模型已经先被注入了；写进系统提示词则等于把判据交给被攻击的对象自己执行。

「防重放为什么不能先查再写？」——检查与写入之间有时间窗，两个并发请求都能查到「没人用过」，同一张令牌建出两条工单。把 `token_hash` 做主键，重复写入直接撞唯一约束，把并发正确性交给数据库而不是交给两次查询之间的时间差。

### 你必须记住的数字

- 令牌 TTL 600 秒
- 四道闸顺序：签名 / 有效期 / 归属 / 单次使用
- 四种拒绝原因
- `examples/confirmation_token_demo.py` 四段固定结果：201 / 409 / 400 签名 / 400 过期

---

## 8. 验证与交付：pytest + 三层评测 + Docker + MCP

### 它解决什么问题

「你怎么知道它是对的」——这个问题有三个层次：单元行为、系统行为、回答质量。三者不能互相替代。

### 核心代码与变量对照

```text
tests/  25 个测试文件
  conftest.py                  autouse fixture：把 env_file 置空 + 清 get_settings 缓存
  test_agent_loop.py           工具白名单、参数校验、超时、失败分类
  test_api.py                  /chat 契约、工单、防重放
  test_cache.py                键构造、代次失效、窗口计数、故障降级（35 条）
  test_mcp.py                  真起子进程跨进程测
  ...
```

其中：

- `conftest.py` 的 autouse fixture —— 把 `Settings` 的 `env_file` 置空并 `cache_clear()`。**只置空 env_file 不够**：`db` 模块在导入时就调用过一次 `get_settings`，测试会带着开发机的 `EMBEDDING_BACKEND=onnx` 进来，每次建向量都加载 90MB 模型
- `test_cache.py` 全走进程内实现，不依赖真实 Redis——键构造 / 失效 / 计数这些逻辑跟用哪个存储无关
- `MemoryStore` 和 `RateLimiter` 的时钟做成**可注入**：过期和窗口切换要靠时间流逝才能验证，而「睡够 TTL」会让测试变慢又脆弱

三层评测：

```python
# src/support_agent/services/evaluation.py
# 样本格式：{"question": ..., "retrieval": {...}, "tools": {...}, "answer": {...}}
# 只声明检索层的样本不触发模型调用
```

其中：

- `retrieval` 层 —— 调 `SupportAgent.retrieve()`，与线上同语料、同阈值、同去重
- `tools` 层 —— 语义是「选对工具」而非「执行成功」。写操作被拦下待确认时 `ok=False`，但那是设计要的行为，算通过
- `answer` 层 —— 调 `run_turn()`
- `run_turn()` —— 由 `respond()` 拆出来，跑完整链路判终态但**无落库副作用**
- `EvaluationResponse.model` —— 本次用的哪个模型。不同模型分数不可比，必须随结果一起返回

Docker 与 MCP：

```yaml
# docker-compose.yml
services:
  api:      build: .            # 端口 8000，等 pg 和 redis 健康后再起
  postgres: image: pgvector/pgvector:pg16   # 端口映射到 127.0.0.1:5433
  redis:    image: redis:7-alpine
```

其中：

- `depends_on.condition: service_healthy` —— 两个依赖都配了健康检查，避免 API 抢跑
- `scripts/init.sql` —— 容器首次启动时建 pgvector extension
- `EMBEDDING_BACKEND: hash` —— 容器开箱可用；要跑本地语义模型需改 onnx/512 并挂载模型目录
- **这份 compose 从未在本机实跑过**（这台机器没有 `docker.exe`）

```python
# src/support_agent/mcp_server.py
# 一个 Tool（query_device）、一个 Resource（device://catalog）、一个 Prompt（fault_report）
# mcp 2.x：FastMCP 已改名 MCPServer，字段改 snake_case
```

其中：

- `Tool` —— 模型可调的**动作**
- `Resource` —— 可读的**数据**，由 Host 决定什么时候放进上下文
- `Prompt` —— 预置的**模板**，通常由用户主动触发
- MCP Server 目前是**旁路能力，没有接进 `/chat` 主链路**
- 业务失败必须抛 `ToolError`，才会转成 `isError=True`；写成普通返回值协议层看不出失败

### 面试官会从哪切进来

「工具层评测里，写操作被拦下算通过吗？」——算。这一层的语义是「模型选对了工具」，而写操作待确认是设计要的行为。参数校验没过才算选错。

「MCP 工具有什么风险？」——返回内容不可信，要当用户输入看待；鉴权、用户同意、权限边界分别属于 Host / 用户 / Server 各自的职责。

「你的 CI 跑过吗？」——**如实**：`.github/workflows/ci.yml` 配了 ruff + pytest --cov，但远端仓库停在第 3 周的 commit，之后 84 个文件改动全在本地，所以这份配置**从未执行过**。

### 你必须记住的数字

- 211 项测试（210 passed / 1 skipped），覆盖率 88.84%，最近一次全量约 96 秒
- 23 个测试文件，`test_cache.py` 最多（35 条）
- 三层评测；`docs/` 下的评测集 8 条样板 + 40 条带关键词标注
- 8 个 HTTP 端点、9 张表

---

## 9. 三条数据流，把八层串起来

看完分层之后，用三条流把它们记住。面试时讲架构，讲的就是这三条。

### 流一：一次 `/chat`（最常被问到）

```text
POST /chat
  ① 限流判定（cache.py · RateLimiter）—— 被拒则不建会话、不写消息、不调模型
  ② 建/取会话，读历史（chat_history_limit=10 条）
  ③ 注入检测（security.py）—— 命中即 blocked / policy，模型零调用
  ④ 语料范围判据（rag.py · corpus_scope_reason）—— 命中即 needs_clarification / policy，零调用
     ④' 结构化锚点豁免（tools.py · has_structured_anchor）—— 认序列号 / 算式 / 工单诉求
  ⑤ Agent Loop（agent_loop.py）最多 5 轮
       模型 → 申请工具 → parse_arguments 校验 → 白名单查表 → 写操作拦截 → 超时保护 → 结果回填
  ⑥ 终态判定（agent.py）—— 固定 elif 顺序，服务端说了算
  ⑦ 回收引用与冲突（rag.py · citations / detect_conflicts）
  ⑧ 写回 messages 表 + 审计
```

### 流二：一次语料导入

```text
scripts/ingest_smartpv.py --source <目录>
  ① 读分卷 markdown / docx正文（knowledge_base.py）
  ② 章节切分 → 按 chunk_size=700 / chunk_overlap=100 切片段
  ③ 每个片段抽行业标签（industry.py：机型 / 协议 / 版本 / 场景 / 类型）
  ④ 生成向量（semantic.py：onnx 512 维，指纹写进元数据）
  ⑤ 写 source_documents + document_chunks（checksum 去重）
  ⑥ 语料代次 +1 → 旧缓存自然失效
```

**换 embedding 后端、改切块参数、改列名、改元数据抽取，都必须 `--reset` 重建。**

### 流三：一次写操作确认

```text
模型申请 create_ticket（writes=True）
  ① agent_loop 不执行，返回 requires_confirmation=True
  ② agent.py 判定 status=pending_confirmation，收场
  ③ 调用方签令牌（security.py · HMAC + exp=600s）→ 返给前端
  ④ 用户确认 → POST /tickets 带令牌
  ⑤ 闸一 验签 → 闸二 查有效期 → 闸三 查归属 → 闸四 写 consumed_confirmation_tokens（主键冲突即重放）
  ⑥ 令牌记录与工单同一事务提交
```

---

## 10. 五句必须背下来的总结

被问「介绍一下你的项目」，用这五句起头，每句都能展开成上面某一层。

1. 这是一个**光伏电站技术支持 Agent**——用户问故障排查，它检索本地知识库并给出带引用的答案，需要写操作时拦下来等人工确认。
2. 主干是**手写的 Agent Loop + 混合检索**：模型只负责申请工具，参数校验、白名单、超时、写操作拦截全在服务端。
3. 拒答不靠分数阈值，靠**语料范围判据**并且**前置在调模型之前**——因为实测库内库外的分数分布是重叠的。
4. 缓存和限流都**可以降级**：Redis 挂了接口不受影响，只是命中率下降，`/health` 如实报 `degraded`。
5. 211 项测试、`doctor` 自检、`docker-compose` 双模式（已实测跑通），代码约 4900 行——**但没有真实认证、CI 没跑过、没有数据库迁移工具、pgvector 只到类型层**，这几条必须自己先说。

---

## 11. 复习检查表

能不看材料答出下面每一条，技术栈就算过关了。答不出的回上面找对应小节。

- [ ] 版本号在哪维护？改完要做什么？
- [ ] 6 个 `ChatStatus` 分别什么时候出现？
- [ ] `status` 和 `answer_source` 为什么要分成两个字段？
- [ ] 向量列怎么同时服务 SQLite 和 PostgreSQL？
- [ ] 三路打分的权重和各自管什么？
- [ ] 为什么不用分数阈值拒答？给一个实测数字。
- [ ] 为什么要剥停用词？两边为什么必须用同一份剥过的文本？
- [ ] `handler` 为什么不能出现在 `as_schema()` 里？
- [ ] 同步工具加超时不 `to_thread` 会怎样？
- [ ] 为什么模型返回的多余参数要拒绝而不是忽略？
- [ ] 缓存键为什么必须带向量后端指纹？
- [ ] 语料代次失效的代价是什么？
- [ ] 四道闸的顺序？为什么验签必须在判重之前？
- [ ] 防重放为什么要靠主键冲突？
- [ ] 三层评测的 `tools` 层语义是什么？
- [ ] 哪些事情你的项目**没做到**？（三个）
