# 学习记录｜阶段 1：Python、FastAPI 与 Agent 基础流程

> 整理日期：2026-09-08  
> 当前进度：已完成环境恢复和项目全貌的大部分第一轮讲解，最近讲完离线检索评测；详细跨主机进度与下一步见 `AI_AGENT_8W_HANDOFF.md`。

## 1. 当前环境

- 项目目录：`D:\agent1\projects\agent-ai-8week`
- 环境管理：Miniconda
- Conda 环境：`agent-ai-8week`
- Python：3.12
- IDE：PyCharm
- PyCharm 解释器：`C:\Users\14374\miniconda3\envs\agent-ai-8week\python.exe`
- 本地模式：SQLite，不需要模型 API、PostgreSQL、Redis 或 Docker
- 基线：15 个测试通过，Ruff 检查通过

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

## 下一阶段

安全与审计的第一轮讲解和实操已完成。下一步完成测试体系、Docker/部署和作品演示，再用 1～2 个学习回合压缩完成第 1 周 FastAPI CRUD，随后从第 2 周数据库与测试开始正式动手。RAG、LLM、Agent、评测和安全仍不视为已经独立掌握。

跨主机继续学习时，优先阅读仓库根目录的 `AI_AGENT_8W_HANDOFF.md`。
