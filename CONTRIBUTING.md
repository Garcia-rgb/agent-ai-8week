# 贡献指南

这个仓库同时是学习材料和求职作品：一次改动除了要「能跑」，还得能被讲清楚。
下面是在这个仓库里做事的方式，包括那些**改了 A 就必须同步 B** 的地方——这个项目最容易漏的就是这些连带项。

## 环境准备

两条路，选一条即可，细节见 [README](README.md) 的「安装」与「快速开始」：

```powershell
# 路线一：Conda（本机一直在用的那条）
conda env create -f environment.yml && conda activate agent-ai-8week

# 路线二：venv
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -e ".[dev]"

Copy-Item .env.example .env      # 默认配置即可跑，不需要模型密钥
```

`doctor` 是排查环境的第一站，它逐项报告配置、数据库与语料规模、向量后端、模型、缓存与限流：

```powershell
python -m support_agent doctor --deep    # --deep 会真的加载向量模型编一句话
```

## 日常命令

| 命令 | 作用 |
|---|---|
| `uvicorn support_agent.main:app --reload` | 起服务，<http://127.0.0.1:8000/docs> |
| `python scripts/start_client.py` | 一键起服务 + 开浏览器（自动选端口） |
| `pytest -q` | 全量测试 |
| `ruff check --no-cache .` | 规范检查 |
| `python -m support_agent doctor` | 环境自检 |
| `python -m build` | 出 wheel 与 sdist 到 `dist/` |
| `docker compose up --build -d` | 完整基础设施模式（PostgreSQL + Redis） |

## 提交前跑这四件事

```powershell
ruff check --no-cache .
pytest -q
python -m build
python -m support_agent doctor
```

前三件是常规的。第四件容易被跳过，但它恰好能抓住三类问题：配置项写错、语料没导或导错库、
向量后端与库里存的向量对不上——这些在测试里全是绿的，只有真跑一次自检才看得见。

改动过 `Dockerfile`、`docker-compose.yml` 或 `pyproject.toml` 的打包配置时，**额外重建一次镜像**：

```powershell
docker compose up --build -d
curl http://127.0.0.1:8000/health     # cache.backend 应为 redis、degraded 应为 false
curl -o NUL -w "%{http_code}" http://127.0.0.1:8000/    # 首页 200，验证 static 确实进了镜像
```

## 代码约定

| 主题 | 约定 |
|---|---|
| 注释与文档正文 | 中文 |
| 提交信息 | 英文、conventional commit（`feat:` / `fix:` / `docs:` / `test:` / `refactor:` / `chore:`） |
| CLI 输出 | 英文 ASCII。它是要贴进日志和 issue 的，非 UTF-8 代码页下中文会失真 |
| 版本号 | 只改 `src/support_agent/__init__.py` 的 `__version__`，其余位置（打包、`/health`、OpenAPI、CLI）自动跟随 |
| 测试读配置 | 测试**不读 `.env`**（`tests/conftest.py` 的 `hermetic_settings`）。本机填了真实密钥也不该改变 `pytest` 的结果 |
| 解释器路径 | 不写死。文档里的路径是本机示例，代码里一律走 `sys.executable` 或环境 |
| 拒答策略 | 靠语料范围判据，不靠分数阈值（原因见 README 末尾「两条被实测否掉的路线」） |
| 打分函数 | 不要改 `services/embeddings.py` 的 `tokenize`：既有向量由它生成，改了查询向量就与库里的错位 |

## 改了这些，必须一起改

| 改了什么 | 连带要改 |
|---|---|
| 新增或修改 CLI 子命令 | `cli.py` 的 `build_parser`、`tests/test_cli.py`、README「命令行」段 |
| 调整 `/chat` 出口分支顺序 | README 的 `status` 表、`docs/architecture.md`、`tests/test_evaluation.py`（评测判定复用同一条链路，会跟着变——这是有意的） |
| 新增一个工具 | `agent_loop.py` 的注册表与 `local_model`（要让本地规则模型也能选中）、README 架构图、`tests/test_tools.py` |
| 换向量后端或维度 | 必须重建库并重导语料：`scripts/ingest_smartpv.py --source <目录> --reset`；同步 README「向量后端」段 |
| 改列名或加列 | 「`create_all` 不改已存在表的列名」——Docker 模式的 PG 卷会停在旧结构，需要显式 `ALTER`；改完用 `scripts/check_schema.py` 两侧各验一次 |
| 改内置页面的行为 | 三个客户端入口都要看：`static/index.html`、`scripts/start_client.py`、`scripts/create_desktop_launcher.py` |
| 改静态资源打包 | `pyproject.toml` 的 `force-include` + `Dockerfile` 的 `COPY static` 顺序 + CI 的 wheel 冒烟断言 |
| 改配置项 | `config.py`、`.env.example`、`docker-compose.yml` 的 `environment`、README 相关段落 |
| 改抽取规则或行业标签 | 元数据只能重导才更新（导入按校验和去重，内容没变会整份跳过），命令同上 |
| 改版本号 | README 顶部徽章与 `CHANGELOG.md` 顶部新增一段（版本位怎么选见 README「版本与发布」） |

## 怎么加一个工具

工具定义集中在 `services/agent_loop.py` 的 `build_tool_registry()`，照着现有条目加：

```python
registry["my_tool"] = ToolSpec(
    name="my_tool",
    description="给模型看的一句话：它做什么、什么时候该用它。写法直接影响模型选不选它。",
    parameters={
        "type": "object",
        "properties": {"arg": {"type": "string", "description": "参数含义"}},
        "required": ["arg"],
        "additionalProperties": False,      # 未知参数要拒绝，不是忽略
    },
    handler=lambda arguments: my_function(arguments["arg"]),
    writes=False,                            # 写操作设 True，会被拦下走人工确认
    timeout_seconds=10,                      # 慢工具（查库、调外部接口）单独放宽
)
```

要点：

- `handler` 可以是同步函数也可以是协程。**同步函数会被丢进线程再等**，所以超时是真的（直接
  `await wait_for` 一个同步函数会占住事件循环，超时形同虚设）。
- `writes=True` 的工具不会被执行，而是返回 `pending_confirmation` 与一次性令牌。
- 别把执行细节写进 `description`：那是给模型的说明书，模型看不到 `handler`。
- 同一个「工具 + 参数」连续失败 2 次后服务端不再放行（`repeated_failure`），这是防模型死循环，不用自己处理。

## 怎么加一个接口

放在 `main.py`，依赖用已有的类型别名（`DbDep` / `SettingsDep` 等）。一个硬约束：

**`GET /` 与 `/static` 的挂载必须排在所有 API 之后注册**，否则会抢先匹配把接口吃掉。

新增接口后补两条：`tests/test_api.py` 的用例，以及 README 的 API 表。

## 怎么加一条评测样本

评测集不进仓库，运行评测时由 `dataset_path` 指定。样本是 JSONL，**声明哪层就评哪层**：

```json
{"id": "tool-07", "question": "SN-2024-000123 这台设备现在什么状态",
 "retrieval": {"expected_keywords": ["SUN2000"]},
 "tools": {"expected": ["query_device"], "forbidden": ["calculator"]},
 "answer": {"status": "completed", "answer_source": ["tool"], "must_not_contain": ["抱歉"]}}
```

- 只声明 `retrieval` 的样本不调用模型，跑得快，适合大批量。
- 一旦声明 `tools` 或 `answer`，就会真的跑一轮 Agent Loop。
- 判定不另写一份：检索层调 `SupportAgent.retrieve`，其余调 `SupportAgent.run_turn`，与 `/chat` 同一份代码。
  自己抄一份判定，两边迟早会漂移，最后「评测通过」和「线上正确」说的不是一回事。

## 提交与发布

改动默认留在本地，需要时再提交。发布一次的动作是固定的四步，见 README「版本与发布」：
改 `__version__` → 写 `CHANGELOG.md` → `python -m build` → `git tag vX.Y.Z`。

CI 会在每次推送时跑：规范检查、三个 Python 版本的全量测试、打包后在干净环境里的安装冒烟、
以及 Docker 镜像构建与启动。所以「本地全绿」不等于「CI 全绿」——打包和镜像这两条路径只有 CI 会覆盖。
