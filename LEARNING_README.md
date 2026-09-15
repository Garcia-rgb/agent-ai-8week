# 学习记录｜阶段 1：Python、FastAPI 与 Agent 基础流程

> 整理日期：2026-09-14
> 当前进度：第 1、2 周已完成第一轮学习和引导式复习；第 3 周 Day 1～Day 4 已完成第一轮学习和代码实操，下一步进入 Day 5 手写 Agent Loop。详细跨主机进度见 `AI_AGENT_8W_HANDOFF.md`，面试题见 `INTERVIEW_README.md`。

## 1. 当前环境

- 项目目录：`D:\agent1\projects\agent-ai-8week`
- 环境管理：Miniconda
- Conda 环境：`agent-ai-8week`
- Python：3.12
- IDE：PyCharm
- PyCharm 解释器：`C:\Users\14374\miniconda3\envs\agent-ai-8week\python.exe`
- 本地模式：SQLite，不需要模型 API、PostgreSQL、Redis 或 Docker
- 基线：28 个测试通过，Ruff 检查通过

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

当前可以真实声称 FastAPI、SQLite 本地模式、PostgreSQL/pgvector Compose 模式、混合检索、规则路由、安全工具、LLM 有限重试、28 项测试、40 条评测样本、Docker 和 CI 配置已经存在。不能声称真实 LLM Tool Calling、高质量语义 Embedding、Redis 缓存/限流、完整 Trace、云端部署和最终回答评测已经完成。

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

## 下一阶段

进入第 3 周 Day 5：手写“模型选择工具 → 服务端校验和执行 → 工具结果回传模型”的最多 5 轮 Agent Loop。完成本节后，将两道面试题和标准答案追加到 `INTERVIEW_README.md`，并再次更新阶段进度。

跨主机继续学习时，优先阅读仓库根目录的 `AI_AGENT_8W_HANDOFF.md`。
