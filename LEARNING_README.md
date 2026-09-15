# 学习记录｜阶段 1：Python、FastAPI 与 Agent 基础流程

> 整理日期：2026-09-15
> 当前进度：第 1、2 周已完成第一轮学习和引导式复习；第 3 周 Day 1～Day 6 已完成，并完成附加节《SmartPV 知识库导入与检索隔离》。Day 5 手写 Agent Loop，Day 6 把循环接进 `POST /chat`，主路径已由「Python 规则选工具」换成「模型选工具、服务端校验执行」。详细跨主机进度见 `AI_AGENT_8W_HANDOFF.md`，面试题见 `INTERVIEW_README.md`。

## 1. 当前环境

- 项目目录：`D:\agent1\projects\agent-ai-8week`
- 环境管理：Miniconda
- Conda 环境：`agent-ai-8week`
- Python：3.12
- IDE：PyCharm
- PyCharm 解释器：`C:\Users\14374\miniconda3\envs\agent-ai-8week\python.exe`
- 本地模式：SQLite，不需要模型 API、PostgreSQL、Redis 或 Docker
- 基线：73 个测试通过，Ruff 检查通过（Day 4 结束时为 28，加入知识库导入测试后为 34，加入 Agent Loop 测试后为 46，接入 `POST /chat` 后为 70，接入真实模型适配后为 73）

当前 PowerShell 无法自动加载 Conda 初始化脚本。只要 PyCharm 已选择上面的解释器，就可以直接使用：

```powershell
python --version
python -m pytest -q
python -m ruff check .
```

启动 FastAPI：

```powershell
python -m uvicorn support_agent.main:app --reload
```

接口文档：<http://127.0.0.1:8000/docs>

## 2. Python 基础

### 列表、循环和判断

列表用于按顺序保存多个数据：

```python
names = ["apple", "banana", "apple"]
```

使用循环和条件可以稳定去重：

```python
unique_names = []

for name in names:
    if name not in unique_names:
        unique_names.append(name)
```

### 字典与计数

字典保存“键 → 值”的对应关系：

```python
counts = {}

for name in names:
    counts[name] = counts.get(name, 0) + 1
```

这里的 `get(name, 0)` 表示：找不到该名称时从 `0` 开始计数。

### 函数

函数把一段可重复使用的逻辑包装起来：

```python
def count_items(items):
    result = {}
    for item in items:
        result[item] = result.get(item, 0) + 1
    return result
```

当前需要理解：参数是函数接收的数据，`return` 是函数交回的结果。

### JSON 文件

JSON 是 API、配置和本地数据文件中最常见的数据格式之一。

```python
import json

with open("tasks.json", "w", encoding="utf-8") as file:
    json.dump(tasks, file, ensure_ascii=False, indent=2)

with open("tasks.json", "r", encoding="utf-8") as file:
    tasks = json.load(file)
```

- `json.dump()`：将 Python 数据写入文件。
- `json.load()`：从文件读取 Python 数据。
- 保存和读取必须使用同一个文件路径。

### 异常处理

```python
try:
    ...
except FileNotFoundError:
    print("文件不存在")
except json.JSONDecodeError:
    print("JSON 内容损坏")
```

异常处理让程序在可预期的错误发生时给出清晰结果，而不是直接崩溃。

## 3. dataclass 与 Pydantic

- `dataclass`：适合程序内部的简单数据对象，例如 CLI 中的 `Task`。
- Pydantic：适合不可信的 API 输入和稳定的 API 输出，会进行字段校验。

项目中的典型选择：

```text
Task                    → dataclass
ChatRequest             → Pydantic
ChatResponse            → Pydantic
FeedbackRequest         → Pydantic
```

关键认识：普通类型注解主要是提示；Pydantic 会在运行时执行数据校验，并在 FastAPI 中自动产生 `422` 响应。

## 4. CLI 任务管理器

文件：`exercises/week01/task_cli.py`

常用命令：

```powershell
python exercises/week01/task_cli.py add "学习 Python"
python exercises/week01/task_cli.py list
python exercises/week01/task_cli.py done 真实任务ID
python exercises/week01/task_cli.py delete 真实任务ID
```

它实现了最小 CRUD：

```text
add     → 创建
list    → 查询
done    → 修改
delete  → 删除
```

`TaskRepository` 把任务文件路径、读取和保存逻辑放在同一个对象中。类的一个常见用途就是把相关数据和操作组织在一起。

## 5. FastAPI 与 HTTP

Swagger 地址：<http://127.0.0.1:8000/docs>

常见 HTTP 方法：

| 方法 | 用途 |
|---|---|
| `GET` | 查询数据 |
| `POST` | 创建数据或触发处理 |
| `PUT/PATCH` | 修改数据 |
| `DELETE` | 删除数据 |

常见状态码：

| 状态码 | 含义 |
|---|---|
| `200` | 请求成功 |
| `201` | 成功创建数据 |
| `400` | 请求内容有问题 |
| `403` | 没有权限执行 |
| `404` | 资源不存在 |
| `409` | 当前操作与已有状态冲突 |
| `422` | Pydantic 输入校验失败 |

参数位置：

```text
路径参数  → /sessions/{session_id}
请求头    → x-user-id
JSON 请求体 → POST /chat
上传文件  → POST /documents
```

## 6. 已体验的接口

### `GET /health`

检查服务状态。当前 `llm_enabled` 为 `false`，表示没有启用真实 LLM。

### `POST /documents`

上传 `.txt`、`.md` 或 `.pdf` 文件，限制 5 MB。系统会检查文件、计算摘要、识别重复内容并保存文档片段。

### `POST /chat`

统一聊天入口，会创建会话、保存消息、选择处理路线并返回结果。

### `GET /sessions/{id}`

按会话 ID 查询历史，并通过 `x-user-id` 检查会话所有权。

### `POST /feedback`

对某条回答评分。`rating` 只能是 `-1`、`0` 或 `1`。

### `POST /evaluations/run`

使用40条固定样本测试检索结果，不靠人工感觉判断效果。

## 7. 当前 Agent 到底是不是真正的 LLM Agent

当前是“规则驱动的 Agent 原型”，不是让大语言模型自由理解意图并选择工具。

```text
“计算 ...”开头          → 计算器
包含 A1001 形式的订单号 → 订单查询
包含工单/投诉/转人工    → 工单确认流程
命中危险关键词          → 安全拦截
其他内容                → 知识库检索
```

因此，计算结果不是固定回答，而是 Python 根据用户输入实时计算；但“是否调用计算器”仍由固定格式和规则判断。

后续真正接入 LLM Tool Calling 后，将变为：

```text
自然语言
  → LLM 理解意图
  → LLM 选择工具并生成参数
  → 服务端校验参数
  → Python 安全执行工具
  → LLM 组织最终回答
```

即使使用 LLM，也不能直接相信任模型。工具白名单、权限检查、异常处理和人工确认仍必须由服务端负责。

> 进度更新（2026-09-15）：上面那套「模型选工具 → 服务端校验执行 → 结果回传模型」的流程已经在 `services/agent_loop.py` 里真正写出来了（见 Day 5 一节），并在当天接进了 `POST /chat`（见 Day 6 一节）。所以现在准确的说法是：**`/chat` 的主路径已经是 Agent Loop，本节描述的规则路由降级为「本地规则模型」的判据**——没有配置远程模型时，由它把意图翻译成同样的工具申请，链路和校验完全一致。本节讲的安全边界（白名单、权限、确认令牌）没有变，只是执行它们的位置从 `respond()` 的 if 分支挪进了循环。

## 8. 计算器为什么能处理不同数字

计算器使用 Python AST 解析表达式，而不是保存固定答案。

```text
“计算 (18 + 6) * 3”
  → 去掉“计算”前缀
  → 解析 `(18 + 6) * 3`
  → 只执行允许的数学运算
  → 返回 72
```

它允许数字、加减乘除、整除、取余和有限幂运算，拒绝函数调用、变量和系统命令。项目没有使用危险的 `eval()`。

## 9. 工单的人工确认

创建工单属于写操作，分为两步：

```text
用户提出创建工单
  → 系统返回 pending_action 和确认令牌
  → 用户明确提交确认令牌
  → 验证签名、用户、操作和有效期
  → 创建工单
  → 记录审计日志
```

相同令牌第二次提交会返回 `409`，这是防重放保护，可避免重复执行写操作。

核心原则：Agent 可以建议高风险操作，但不能绕过用户确认直接执行。

## 10. 项目分层

```text
main.py        → HTTP 接口入口
schemas.py     → API 输入输出校验
graph.py       → 处理路线选择
services/      → 业务逻辑、工具、RAG、安全和模型调用
models.py      → 数据库表结构
db.py          → 数据库连接与会话
config.py      → 环境配置
observability.py → 请求日志与耗时记录
```

分层的价值是让每部分职责清楚、便于测试和替换，避免把全部逻辑堆在一个接口函数里。

## 11. 数据库基础

- `Conversation`：一段会话。
- `Message`：一条用户或助手消息。
- 一段会话可以包含多条消息。
- `Message.session_id` 关联 `Conversation.id`。
- 主键唯一标识一条记录。
- 外键表示表之间的关联。
- 索引用于加快常用查询。

保存数据时暂时记住：

```text
add     → 将对象加入当前事务
flush   → 将操作发送给数据库，暂不最终确认
commit  → 正式提交事务
rollback → 发生错误时撤销未提交修改
```

## 12. 进入下一阶段前应能说明

- 列表和字典分别适合保存什么数据。
- `json.dump()` 与 `json.load()` 的作用。
- 为什么需要处理文件不存在和 JSON 损坏。
- dataclass 与 Pydantic 的主要区别。
- CLI CRUD 与 HTTP CRUD 的对应关系。
- `200`、`201`、`404`、`409`、`422` 的基本含义。
- 当前系统为什么属于规则驱动 Agent。
- 为什么数学结果不是固定答案。
- 为什么工单必须二次确认并防止令牌重放。
- `Conversation` 与 `Message` 是什么关系。

不要求现在默写全部代码；能够用自己的话讲清上述流程即可。

## 13. 安全与审计实操进度（2026-09-08）

- 已通过 Swagger 验证创建工单必须二次确认，相同令牌再次提交返回 `409`，理解防重放目的。
- 已验证会话所有权隔离：其他用户访问同一会话 ID 返回 `404`，避免泄露资源是否存在。
- 已用虚构手机号观察到 HTTP 日志不记录正文，但聊天历史会原样入库，理解日志脱敏与数据存储脱敏是两层问题。
- 已理解执行层必须独立校验权限、参数和人工确认，不能只依赖 Prompt Injection 关键词检测。
- 已完成审计字段判断练习：内部用户 ID、动作、资源、时间、结果应该记录；完整令牌和 API Key 不应原样记录；业务正文应按需摘要或脱敏。
- 当前属于引导下实操成功，尚未独立实现或通过闭卷验收。

## 14. 测试体系

- 单元测试检查一个函数或小模块，例如安全计算器、订单查询和确认令牌。
- 接口测试从 HTTP 入口经过校验、业务逻辑和数据库，再检查响应。
- 工作流测试检查多个步骤及业务规则，例如“申请工单确认 → 首次创建成功 → 重复令牌返回 409”。
- `tests/conftest.py` 使用临时数据库和 FastAPI 依赖替换，不污染日常使用的 `support_agent.db`。
- 用户已在 PyCharm 中亲自运行工具测试、API 测试和全量测试；第 2 周结束时基线为 `23 passed`，加入 LLM 重试测试后更新为 `28 passed`。
- 测试通过只代表已有测试覆盖的行为符合预期，不代表真实模型、网络和所有边界情况都没有问题。

## 15. Docker、健康检查与 CI

- Dockerfile 将 Python 3.12、项目依赖、代码和启动命令组合成可重复运行的镜像。
- Docker Compose 同时管理 FastAPI、PostgreSQL/pgvector 和 Redis；容器之间通过服务名通信。
- PostgreSQL 使用 Volume 保存数据，重新创建容器时数据不必随容器消失。
- PostgreSQL 和 Redis 配置了健康检查，API 等待它们健康后启动。
- API 已增加自身健康检查；Compose 中 API、PostgreSQL 和 Redis 三个容器均已真实构建、启动并显示为 healthy。
- Docker Desktop、镜像、容器和本机 Volume 不提交到 Git；另一台主机从仓库重新构建，业务演示数据通过 `sample_data/` 再导入。
- 2026-09-11 Docker 重装后确认旧 PostgreSQL Volume 仍存在，原卷保留 8 张表但业务记录为空；随后重新导入 4 份样例文档并成功完成一次知识库问答。
- 当前 `/health` 只能证明 FastAPI 能响应，没有深度检查数据库、Redis 和外部模型。
- Redis 服务已经写入 Compose，但当前业务代码尚未真正使用缓存或限流。
- GitHub Actions 会在推送或 PR 时安装 Python、运行 Ruff 和 pytest；当前属于 CI，还没有自动发布到服务器的 CD。

## 16. 项目演示与面试表达

固定演示顺序：

```text
健康检查
→ 导入文档并展示重复检测
→ 知识问答与引用
→ 计算器和订单查询
→ 工单二次确认与防重放
→ Prompt Injection 拦截
→ 自动化测试与离线评测
```

面试表达按“业务问题 → 架构 → RAG → 工具与安全 → 测试评测 → 限制和下一步”组织。

当前可以真实声称 FastAPI、SQLite 本地模式、PostgreSQL/pgvector Compose 模式、真实分卷知识库导入、语料隔离与拒答阈值、混合检索、手写 Agent Loop 与 Tool Calling 适配层、模型选工具的主路径（`POST /chat` 已接入）、接入真实 OpenAI 兼容服务（含思考模式模型的思维链回传）、无 API Key 可跑的本地规则模型、写操作人工确认、会话历史回填与工具轨迹审计、LLM 有限重试、73 项测试、40 条评测样本、Docker 和 CI 配置已经存在。不能声称高质量语义 Embedding、Redis 缓存/限流、完整 Trace、云端部署和最终回答评测已经完成。

## 17. 当前准确进度

项目全貌第一遍已经完成，包括：Python/FastAPI 基础、数据库关系、规则路由、工具调用、RAG、LLM 与 Agent 区别、会话与上下文、可靠性、日志、评测、安全审计、测试、Docker/CI 和项目演示。

这些大多属于概念讲解和引导下实操，不能等同于独立掌握。当前独立编码能力仍处于第 1 周基础阶段。

## 18. 压缩版第 1 周 FastAPI CRUD（已完成）

- 新增 `exercises/week01/task_api.py`，实现内存版任务管理器。
- 已实现 `POST /tasks`、`GET /tasks`、`PATCH /tasks/{task_id}` 和 `DELETE /tasks/{task_id}`。
- 用户在代码骨架上亲自补充了完成任务和删除任务的核心循环。
- 已通过 Swagger 验证创建、查询和修改流程，并理解 `404`、`422` 和 `501` 的区别。
- 新增 `tests/test_task_api_exercise.py`，自动验证完整 CRUD、重复删除返回 `404`、空标题返回 `422`。
- 内存版练习测试为 `2 passed`；Ruff 检查通过。
- 当前数据保存在进程内存的 `tasks` 列表中，服务器重启后会消失，这是进入数据库学习的直接问题。

## 19. 第 2 周数据库、测试与 Docker（第一轮完成）

- 用户通过停止并重启服务，亲自观察到内存版任务消失、SQLite 版任务仍然存在，理解了持久化的作用。
- 新增 `exercises/week02/task_api_sqlite.py`，使用原生 SQLite SQL 实现完整任务 CRUD。
- 已学习 `CREATE TABLE`、`INSERT`、`SELECT`、`UPDATE`、`DELETE`、参数占位符、主键、非空约束和事务。
- 使用 `EXPLAIN QUERY PLAN` 对比：按主键 `id` 查询使用索引，按普通 `title` 查询执行全表扫描。
- 已理解索引提高读取速度，但增加存储和写入维护成本，不能给所有字段盲目加索引。
- 已理解事务中的 `add`、`flush`、`commit` 和 `rollback`，以及工单与确认审计必须一起提交的原因。
- 已学习主键、唯一、非空、外键和 CHECK 约束，理解 Pydantic、业务校验和数据库约束不能互相替代。
- 新增 `exercises/week02/task_api_sqlalchemy.py`，使用异步 SQLAlchemy、ORM 模型、AsyncSession 和 FastAPI 依赖注入实现完整 CRUD。
- 已对照理解“类→表、对象→行、属性→列”，并学习 `session.add()`、`session.get()`、`select()`、`session.delete()` 和事务提交。
- 已学习 `Conversation → Message → Feedback` 的一对多和外键关系，以及 SQLite 外键默认执行检查的当前限制。
- 已理解 FastAPI 依赖注入如何提供数据库 Session 和配置，以及测试如何替换正式数据库。
- 新增原生 SQLite 和 SQLAlchemy 两项完整 CRUD 测试；后续又完成会话分页、Mock 和事务失败回滚测试，当前项目全量测试为 `23 passed`，Ruff 通过。
- 当前内容为引导下实现和理解，尚未达到无提示独立写出异步 SQLAlchemy CRUD 的程度。

## 20. 当前主机 OpenSSL 兼容问题

- Windows Code Integrity 企业策略阻止了 Conda 环境中 conda-forge 的 `libssl-3-x64.dll`，导致 Uvicorn 导入 `_ssl` 时失败；这不是 SQLAlchemy 代码错误。
- 已使用本机缓存的 defaults OpenSSL 3.5.7 离线替换，未联网下载，也未替用户接受 Anaconda 服务条款。
- 修复后 SSL 导入、19 项测试、Uvicorn、SQLAlchemy `POST /tasks` 和 `GET /tasks` 均验证成功。
- 当前主机暂时不要直接执行 `conda env update -f environment.yml --prune`，否则 conda-forge OpenSSL 可能被重新安装。其他主机如果没有企业签名策略，可继续按原环境文件使用。

## 21. 第 3 周 LLM API 与工具调用（进行中）

### Day 1：Token、上下文与生成参数

- 已理解 Token 是模型处理和计费的基本单位，不等同于固定字数。
- 已理解上下文包含系统指令、用户问题、历史对话、RAG 资料、工具结果和模型输出空间。
- 能判断历史对话和 RAG 资料通常是优先压缩对象，不能随意删除安全指令和当前问题。
- 已理解低 `temperature` 更适合提取、分类和结构化工具参数，高值更适合创意任务；`temperature=0` 也不保证绝对确定。
- 成本只要求理解输入、输出分别计费以及多轮 Agent 会增加费用和延迟，不继续练习手工费用计算。

### Day 2：Prompt、Few-shot 与结构化输出

- 已理解应用指令、业务资料和用户输入的信任边界；RAG 文档中的文字属于数据，不能改变系统权限。
- 已理解 Prompt Injection 不能只靠提示词拦截，最终权限和写操作校验必须在服务端完成。
- 已学习 Few-shot 用示例提高输出格式稳定性，但不能替代 Pydantic 和业务权限校验。
- 已区分格式校验与业务校验：合法的工具名和订单号格式不代表当前用户有权查询该订单。
- 已阅读 `src/support_agent/services/llm.py`，理解无远程配置时的 `local_answer()` 只是 Python 拼接检索片段，不是本地 LLM。

### Day 3：手写工具调用边界

- 已阅读并运行 `examples/manual_agent.py`，正常得到计算结果和模拟订单结果。
- 已理解模型看到的工具说明只用于帮助选择工具，服务端 `TOOLS` 注册表才决定允许执行的函数。
- 已理解合法 JSON 仍可能缺字段、类型错误或格式错误，执行前仍需参数模型、权限检查和高风险操作确认。
- 用户选择跳过未知工具和损坏 JSON 的简单报错实验，不影响核心概念学习。

### Day 4：超时、重试、错误映射与降级

- 已理解 `400/401` 等确定性问题通常不重试，`429/503/网络超时` 等暂时性故障可以有限重试。
- 已理解指数退避、最大尝试次数和总时间上限的目的，以及无限重试对费用、延迟、服务压力和重复执行的风险。
- 已理解底层模型客户端负责异常分类、有限重试和错误映射，上层 Agent 负责业务降级和会话保存。
- 已分析当前 `200 + 友好提示` 的优点和监控缺陷，理解可通过结构化 `degraded` 状态区分正常回答与降级回答。
- 两道面试题及整理后的答案已写入 `INTERVIEW_README.md`。
- 已在 `services/llm.py` 实现最多三次尝试：`401/403` 等确定性错误不重试，`429/500/502/503/504`、超时和网络异常有限重试，响应结构损坏直接映射为不可重试错误。
- `LLMError` 新增 `category` 和 `retryable`，在不泄露厂商异常的同时为上层判断保留结构化信息。
- 新增 `tests/test_llm_retry.py` 的 5 个 Mock 测试，不访问真实模型；项目全量测试更新为 `28 passed`，Ruff 通过。
- 当前尚未实现结构化降级响应、模型故障指标、随机抖动、服务端等待提示和总重试时间预算。

### 附加节：SmartPV 知识库导入与检索隔离（2026-09-15）

> 本节是插在 Day 4 之后的工程实践节：把真实本地知识库导入 PostgreSQL/pgvector，并给检索加上语料隔离、敏感章节过滤和拒答阈值。原计划的 Day 5（手写 Agent Loop）顺延到本节之后。

**为什么需要这一节**

- 之前演示只用了 `sample_data` 的 4 份示例文档，语料太少、噪声太低，检索分数好看但不代表真实效果。
- 接入真实分卷知识库后，库里会同时存在演示文档和正式资料，必须在检索层就把范围收窄，否则相似度分数会在无关语料之间互相干扰。
- 真实资料里包含账号、密码、默认口令一类内容，这些既不能进普通问答，也不适合放进可以被检索到的位置。

**语料结构与解析（`src/support_agent/services/knowledge_base.py`，新增）**

- 知识库根目录由 `SMARTPV_KB_PATH` 指定，包含 `HCSA-SmartPV-V2.0-index.json` 与 `HCSA-SmartPV-V2.0-知识库分卷/` 两部分。
- 索引 JSON 提供 `modules` 和 `appendices` 两组条目，每条包含 `id`、`title`、`pages`（如 `p1–36`）。
- 分卷文件按 `模块M1-*.md`、`附录A-*.md` 命名；脚本校验每个条目只能匹配到一份分卷，多份或零份都直接报错，避免静默漏导。
- 章节切分优先按 Markdown 二级标题 `##` 切；整篇没有 `##` 时（M9/M12 这类分卷）退化为按独立粗体行 `**小节名**` 切分。
- 每一个章节生成一个 `KnowledgeChunk`，携带来源元数据：`document_id`、`document_title`、`section_title`、`page_start`/`page_end`、`source_file`、`corpus_id`、`visibility`、`restricted`。
- `corpus_id` 固定为 `smartpv_v2`，`visibility` 为 `local_only`，用于后续做范围隔离和权限判断。
- 标题命中「账号、密码与默认值」「密码重置」的章节默认跳过；只有显式传入 `--include-restricted` 才会导入，并把 `restricted` 标记为 `True`。

**导入流程（`RAGService.ingest_smartpv_corpus` 与 `scripts/ingest_smartpv.py`，新增）**

- 按分卷文件分组后逐个导入，用文件 SHA-256 与已有的 `SourceDocument.checksum` 比对，重复导入直接记为 `documents_skipped`，与 `POST /documents` 的去重策略保持一致。
- 每个章节先按 `chunk_size=700`、`overlap=100` 二次切块，再把章节元数据原样写进 `DocumentChunk.chunk_metadata`。
- 导入完成后打印 `新文档 / 跳过 / 章节 / 检索片段` 四项统计，便于核对规模。
- PostgreSQL 侧沿用 pgvector 镜像，Compose 中把数据库端口改为 `127.0.0.1:5433:5432`：只绑定本机回环地址，不暴露给局域网，同时避开本机已占用的 5432。

**检索隔离与拒答阈值（`src/support_agent/services/rag.py`、`services/agent.py`、`config.py`）**

- `RAGService.search()` 新增三个参数：`corpus_id`、`include_restricted`、`min_score`。
- `corpus_id` 过滤：章节元数据的 `corpus_id` 与目标不一致就直接跳过。这样示例文档和正式资料即使都被切块入库，也不会互相进入对方的检索结果。
- `restricted` 过滤：没有显式放行时，`restricted` 为 `True` 的章节不参与检索。
- 打分仍为混合检索 `0.55 * 词面 + 0.45 * 向量`，但只有同时满足 `score > 0` 且 `score >= min_score` 的片段才算命中。
- `config.py` 新增 `retrieval_corpus_id`（默认 `None`）和 `retrieval_min_score`（默认 `0.0`）；Compose 的 API 服务注入 `RETRIEVAL_CORPUS_ID=smartpv_v2`、`RETRIEVAL_MIN_SCORE=0.4`。
- `agent.py` 把这两个配置传进检索；**当 `hits` 为空时直接拒答**（「当前知识库没有找到足够可靠的依据，请补充问题信息或转人工确认。」），不再调用模型。
- 拒答发生在调用模型之前，因此既避免了用无用片段让模型硬编答案，也省掉了一次模型调用成本。

**测试与基线**

- 新增 `tests/test_knowledge_base.py` 的 6 个测试：`##` 切分、独立粗体切分、默认排除受限章节并写入元数据、`include_restricted=True` 时保留并打标记、分卷缺失时报错、导入后元数据落库且 `corpus_id` 检索隔离生效（含用 `missing_corpus` 查询返回空）。
- 全量测试由 `28 passed` 更新为 `34 passed`，Ruff 检查通过。

**掌握程度**

- 本节属于概念讲解 + 引导下实操：用户能够说明语料隔离和拒答阈值各自解决什么问题、为什么两者不能只留一个。
- 尚未独立实现的部分：阈值调参流程、按用户或租户动态切换 `corpus_id`、受限章节的独立授权访问通道。

### Day 5：手写「模型 → 工具 → 结果 → 模型」的 Agent Loop（2026-09-15）

**本节要回答的问题**

1. 模型说「我要调用 `calculator`」，这句话到底是命令还是申请？
2. 为什么循环必须有最大轮数？轮数用尽之后应该怎么办？
3. 工具执行失败时，是抛异常结束，还是把错误交回模型？

**Day 5 之前项目里没有 Agent Loop**

- `services/agent.py` 的路由由 `graph.py` 的固定规则决定：命中「计算」关键字走计算器，出现 `A1001` 这类订单号走订单查询。
- 也就是说，**是 Python 在选工具，不是模型在选工具**。这能跑通，但它不是 Tool Calling。
- 真正的 Tool Calling 顺序是反过来的：模型看到工具清单和用户问题，自己决定要不要调、调哪个、传什么参数。

**关键区分一：工具说明书 ≠ 工具白名单**

| | 位置 | 作用 | 谁看 |
|---|---|---|---|
| 工具说明书 | 随请求发给模型的 `tools` 字段 | 让模型知道有哪些工具、参数长什么样 | 模型 |
| 工具白名单 | 服务端进程内的 `dict[str, ToolSpec]` | 真正决定哪个函数可以被执行 | 服务端 |

- 说明书是「建议」，白名单是「权限」。模型可以编出一个不存在的工具名，服务端必须拒绝。
- 落到代码里：`ToolSpec.as_schema()` 只输出 `name` / `description` / `parameters`，**`handler` 永远不会出现在发给模型的 JSON 里**。
- 测试 `test_registry_is_the_only_source_of_tool_schemas` 就是在守这条线：如果哪天有人图省事把 `handler` 塞进 schema，这个测试会红。

**关键区分二：模型的参数是不可信输入**

模型返回的 `arguments` 是一个 JSON 字符串，它可能：不是合法 JSON、是 JSON 数组而不是对象、缺必填字段、类型不对、或者塞了没定义的额外字段。

所以 `parse_arguments()` 设了四道关：

```text
1. json.loads 能解析        → 否则「工具参数不是合法 JSON」
2. 结果必须是 JSON 对象      → 否则「工具参数必须是 JSON 对象」
3. 不能有未定义字段          → 否则「出现未定义参数」
4. 必填字段齐全 + 类型正确    → 否则「缺少必填参数」/「参数 x 必须是字符串」
```

第 3 条值得单独说：多出来的字段要**拒绝**，不能静默忽略。静默忽略会让 `{"order_id": "A1001", "admin": true}` 这种越权参数悄悄通过，看起来没事，但一旦以后 handler 改成读取整个参数字典，漏洞就出现了。

即使参数全部合法，工具内部还有第二层防线：`calculator` 走的是白名单 AST（`safe_calculate`），表达式里出现函数调用、属性访问就直接报错。测试里用 `__import__("os").getcwd()` 验证过这条路走不通。

**循环本身只有四步**

```text
messages = [system, user]
循环最多 5 轮：
  1. 把 messages + 工具说明书交给模型 → 拿回 AssistantTurn
  2. 把这个回复写回 messages（role=assistant）
  3. 如果它没申请工具 → 这就是最终答案，结束
  4. 如果它申请了工具 → 服务端校验并执行 → 结果以 role=tool 写回 messages
```

第 2 步和第 4 步的顺序不能反：`role=tool` 的消息必须紧跟在它对应的 `assistant.tool_calls` 之后，并且带上 `tool_call_id`，否则接口会报消息顺序错误，模型也分不清哪个结果对应哪次调用。

**为什么必须有最大轮数**

- 模型可能陷入死循环：调用工具 → 结果不满意 → 换个参数再调 → 还是不满意……每一轮都是真金白银的 token 和延迟。
- 也可能是工具持续报错，模型持续重试同一条路。
- 更糟的情况是模型把「工具失败」理解成「我需要再试一次」，而没有上限的循环会把一次用户提问放大成几十次调用。
- 所以 `MAX_ROUNDS = 5`。轮数用尽后的处理不是抛异常，而是**禁用工具再问一次**：`model.chat_with_tools(messages, None)`，此时请求里不带 `tools` 字段，模型只能用手上已有的信息作答。这样用户至少能拿到一个基于部分信息的回答，而不是一个 500 错误。

**工具失败是「信息」，不是「崩溃」**

`execute_tool_call()` 的返回值是 `ToolOutcome(ok, text)`，无论失败原因是什么都返回一段文本，绝不向上抛异常：

```text
未知工具        → 错误：工具 xxx 不在允许列表中
写操作工具      → 错误：工具 xxx 是写操作，需要人工确认后才能执行
参数不合法      → 错误：缺少必填参数：['order_id']
工具业务失败    → 错误：未找到订单 A9999
工具自身异常    → 错误：工具执行失败（KeyError）
```

这样做有三个后果：整轮对话不会因为一次工具失败而中断；模型能看到具体错误并自己纠正参数；`ToolCallRecord` 里留下了完整轨迹，事后可以回放和统计工具失败率。

**写操作不自动执行**

`ToolSpec` 有一个 `writes` 标记，为 `True` 时 `execute_tool_call()` 直接拒绝，不调用 handler。

- 理由和项目原来「创建工单需要确认令牌」是同一个：模型的话只能当成申请，写操作必须有人点头。
- 测试 `test_write_tool_is_never_executed_automatically` 用一个假工单工具验证了 handler 确实没被调用。
- Day 6 会把这里的拒绝接到真正的确认令牌流程上。

**代码落点**

- `src/support_agent/services/llm.py`（改写）
  - 抽出 `_chat()`：统一处理超时、有限重试、错误分类，`answer()` 和 `chat_with_tools()` 共用，不再重复一遍重试逻辑。
  - 新增 `ToolCallRequest`（`id` / `name` / `arguments`）和 `AssistantTurn`（`content` + `tool_calls`）。
  - `AssistantTurn.from_message()` 负责把模型响应解析成结构化对象，结构不对统一归为 `invalid_response` 且不重试。
  - 新增 `chat_with_tools(messages, tools)`：只负责翻译，不执行任何工具、不判断工具名是否合法。
- `src/support_agent/services/agent_loop.py`（新增）
  - `ToolSpec`：工具定义，含 `as_schema()` 与 `writes`。
  - `build_tool_registry()`：服务端白名单，含 `calculator` 与 `query_order`。
  - `parse_arguments()` / `ToolArgumentError`：参数校验四道关。
  - `execute_tool_call()` / `ToolOutcome`：永不抛异常的执行入口。
  - `run_agent_loop()` / `LoopResult` / `ToolCallRecord`：最多 5 轮循环与执行轨迹。
  - `ChatModel` 是一个 `Protocol`，所以循环只依赖「一个能收消息和工具清单、返回 `AssistantTurn` 的东西」，真实客户端和测试假模型都满足它。
- `tests/test_agent_loop.py`（新增，12 个测试）
- `examples/agent_loop_demo.py`（新增）：用脚本化假模型跑一次「计算器 + 订单查询」的两轮调用，打印每轮意图和执行轨迹，不需要任何 API Key。

**测试与基线**

新增 12 个测试，全部不连真实模型：直接作答单轮结束、工具结果正确回传（含 `role=tool` 与 `tool_call_id` 校验）、说明书只暴露三个字段、未知工具被拒且循环继续、参数不是合法 JSON、缺必填参数、含未定义参数、订单不存在、计算器沙箱不可绕过、写操作工具不自动执行、5 轮用尽后禁用工具收敛、模型故障降级。

全量测试由 `34 passed` 更新为 `46 passed`，Ruff 检查通过。

**掌握程度**

- 本节为概念讲解 + 代码实现：Agent Loop 是本次实际写出来的，不是只读现有实现。
- 用户需要能回答的是：为什么「模型说要调用工具」不等于「工具会被执行」；轮数上限失效后系统如何收场；工具报错为什么不能抛异常。
- 尚未独立完成的部分：本节的代码由 AI 生成，用户尚未闭卷重写；Day 7 会安排关闭 AI 重写 `safe_calculate` 的核心递归逻辑。
- 尚未实现的部分：会话历史持久化、更细的参数类型校验、未知工具的单独指标、模型频繁申请工具的成本告警。

### Day 6：把 Agent Loop 接进 POST /chat（2026-09-15）

**这一节要解决的问题**

Day 5 结束时，Agent Loop 是个能跑、能测、但没人用的模块：`POST /chat` 仍然走 `graph.py` 的规则路由，真实链路依旧是「Python 用关键词判断意图，再决定调哪个工具」。这一节把它接到主路径上。

改完之后，`/chat` 里各环节的归属：

| 环节 | Day 5 之前 | Day 6 |
|---|---|---|
| 判断用户想干什么 | `graph.py` 关键词规则 | 模型（远程或本地） |
| 决定调哪个工具 | `respond()` 里的 if 分支 | 模型提出申请，服务端白名单放行 |
| 回答业务问题 | `respond()` 里固定先检索再拼提示词 | 模型自己决定何时调 `search_knowledge_base` |
| 提示词注入拦截 | 规则路由的 `blocked` 分支 | 位置不变，仍在进循环之前 |
| 创建工单 | 规则命中 `ticket` 分支 | 模型申请 `create_ticket`，服务端拦下并返回确认令牌 |

**决定一：「模型」是一个接口，不是某家厂商**

Agent Loop 只依赖一个 `ChatModel` 协议——能收「消息 + 工具清单」、返回一个 `AssistantTurn` 的东西。既然如此，「模型」就不必非得是远程 API。新增的 `RuleBasedLocalModel` 用规则实现了同一个方法：

| | 远程模型（`OpenAICompatibleClient`） | 本地规则模型（`RuleBasedLocalModel`） |
|---|---|---|
| 谁决定调哪个工具 | 模型依据提示词和工具说明自己判断 | 复用 `graph.py` 的规则分类，把意图映射成工具申请 |
| 没配 API Key 时 | 不可用 | 正常工作 |
| 在测试里 | 需要 mock | 直接跑真实链路 |

这件事的价值不只是「省一个 API Key」：**它让测试能对整条链路做端到端断言，而不是对一堆 mock 做断言**。项目里原有的 4 个 `/chat` 接口测试没有改一行断言就继续通过——因为对外契约和用户可见行为都没变，换掉的只是内部由谁来做决定。

代价也要说清楚：本地模型不做任何语言理解，只是把规则路由的输出翻译成工具申请；它也没有能力在同一轮里既申请工具又给出结论，所以固定是两轮（申请 → 收敛）。

**决定二：规则没有消失，只是换了位置**

`graph.py` 从「主路径」变成了「本地模型的大脑」。但有一类规则**必须留在主路径上，不能交给模型**：

- 提示词注入检测留在 `SupportAgent.respond()` 里，在进循环之前执行。理由很直接：**安全判断不能交给一个可能被说服的东西**。测试 `test_prompt_injection_is_blocked_before_the_loop` 断言这种情况下模型一次都没被调用。

**决定三：知识库检索变成一个工具**

原来「知识问答」是 `respond()` 里的一段 if 分支：先检索，再把片段拼进提示词，再调模型。现在它是白名单里的普通工具 `search_knowledge_base`，由模型自己决定什么时候检索、用什么 query。

为了让它挂进同一个循环，工具执行约定放宽了一格：

- `ToolSpec.handler` 允许是同步函数，也允许是协程；
- `execute_tool_call()` 变成 `async`，用 `inspect.isawaitable()` 判断返回值要不要 await；
- 于是「必须访问数据库的检索」和「纯计算的 calculator」在循环里没有任何区别。

**检索为空时服务端必须兜底。** 模型完全可能嘴上说「我查过了，退款是七个工作日」而实际上工具返回了空。所以 `respond()` 里保留了硬判断：本轮调用过 `search_knowledge_base` 但一条命中都没有，就直接覆盖成拒答话术。测试 `test_empty_retrieval_overrides_the_model_answer` 用一个会编造答案的假模型验证了这条覆盖确实生效。

**决定四：待确认的写操作是一个独立的结束状态**

Day 5 里写操作被拒绝后会返回一段错误文本给模型，模型再补一句「这个需要你确认」——能走通，但很别扭：**「需要人工确认」是服务端的状态，不该由模型来复述**。

Day 6 给 `ToolOutcome` 和 `ToolCallRecord` 都加上 `requires_confirmation`。循环一旦发现这种调用，就在本轮其余调用执行完之后立刻收场，`stopped_reason="needs_confirmation"`，由 `SupportAgent` 换成一张真正的确认令牌。用户看到的 `pending_action` 和原来完全一样，但它的来源从「模型的措辞」变成了「服务端的确切状态」。

顺带调整了一处判定顺序：**先校验参数，再判断写操作**。参数本身就不合法的写操作不该生成确认请求——不能让用户去确认一个连参数都错的请求。

**会话历史**

`run_agent_loop()` 新增 `history` 参数，历史消息插在 system 之后、本轮用户消息之前。读取时机很关键：**必须在写入本轮用户消息之前读**，否则本轮问题会在上下文里出现两次。

`Message` 表只保存对用户可见的对话；工具轨迹属于运维信息，写进 `AuditLog`（`action="agent_loop_tool_calls"`），记录轮数、停止原因和每次调用的名字与成败。这样排查「某次回答为什么不对」时，能直接看到当时到底调了什么工具。

**代码落点**

- `src/support_agent/services/agent_loop.py`（扩展）
  - `ToolSpec.handler` 支持协程；`execute_tool_call()` 改异步，用 `inspect.isawaitable()` 兼容两种工具。
  - `ToolOutcome` / `ToolCallRecord` 增加 `parsed` 与 `requires_confirmation`。
  - 新增结束状态 `needs_confirmation`；`run_agent_loop()` 支持 `history`。
  - 新增 `build_support_registry(searcher)`：在核心工具之上补上需要请求上下文的 `search_knowledge_base` 与 `create_ticket`。
- `src/support_agent/services/local_model.py`（新增）：`RuleBasedLocalModel`，实现与远程客户端相同的 `chat_with_tools`。
- `src/support_agent/services/agent.py`（重写 `respond`）：读历史 → 前置注入拦截 → 组装注册表 → 跑循环 → 提取引用与确认令牌 → 空检索兜底 → 写审计日志。
- `src/support_agent/config.py`：新增 `agent_max_rounds`（默认 5）与 `chat_history_limit`（默认 10）。
- `tests/test_local_model.py`（新增 9 个）、`tests/test_agent_integration.py`（新增 12 个）、`tests/test_agent_loop.py`（新增 3 个）。

**测试与基线**

新增 24 个测试，全量由 `46 passed` 更新为 `70 passed`，Ruff 检查通过。

- 本地模型的意图映射：订单 → `query_order`、算式 → `calculator`、业务问题 → `search_knowledge_base`、投诉 → `create_ticket`（保留订单号）、注入 → 不申请任何工具、目标工具不在白名单 → 如实告知。
- 端到端：算式和订单经工具完成、工具轨迹落审计日志、第二轮上下文里能看到第一轮对话、空检索覆盖模型答案、知识问答的引用来自工具返回值、写操作仍走确认令牌、注入在循环前被拦下、远程模型确实经 `chat_with_tools` 调用且拿到 4 个工具、模型故障降级、会话不存在与越权访问。
- 循环层：写操作提前收敛、非法参数的写操作不生成确认、异步 handler 会被 await、历史消息位置正确。

**掌握程度**

- 本节是在用户确认「继续做这个项目」后由 AI 实现的，用户尚未闭卷重写其中任何一段。
- 用户需要能回答的是：为什么本地规则模型值得存在（提示：测试和离线演示，不是省钱）；安全规则为什么不能交给模型；检索为空时为什么必须由服务端覆盖答案。
- 尚未实现的部分：工具参数的枚举与嵌套对象校验、未知工具的独立指标、模型频繁申请工具的成本告警、跨轮的轮数预算、工具结果的注入过滤。

## 下一阶段

进入第 3 周 Day 7：关闭 AI 重写核心逻辑（`safe_calculate` 的递归下降解析、`parse_arguments` 的校验），并为工具层的异常路径补上评测样本。完成本节后，将两道面试题和标准答案追加到 `INTERVIEW_README.md`，并再次更新阶段进度。

跨主机继续学习时，优先阅读仓库根目录的 `AI_AGENT_8W_HANDOFF.md`。

跨主机继续学习时，优先阅读仓库根目录的 `AI_AGENT_8W_HANDOFF.md`。
