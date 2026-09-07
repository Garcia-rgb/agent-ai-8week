# 明天开始：Day 1

总时长约 2 小时 20 分钟。第一天不接模型 API、不学 LangGraph。

## 1. 环境确认（15 分钟）

```powershell
cd D:\agent1\projects\agent-ai-8week
conda run -n agent-ai-8week python --version
conda run -n agent-ai-8week python -m pytest -q
```

看到 Python 3.12 和 15 个测试通过即可。当前 PowerShell 禁止加载配置脚本，
因此这里使用 `conda run`，不要求先执行 `conda activate`。不要升级全部依赖。

## 2. Python 闭卷摸底（45 分钟，禁止使用 AI）

新建临时草稿，实现：

1. 输入一组字符串，去重并保持原顺序。
2. 统计一段中英文文本中的词/字频率。
3. 把任务列表保存为 JSON，再读取回来。
4. 对文件不存在和 JSON 损坏分别给出错误。

不会的地方先写 `TODO`，45 分钟结束后再查资料。目的是建立真实基线，不是第一天考满分。

## 3. 官方教程定向学习（35 分钟）

阅读 Python 官方教程中的列表、字典、函数和异常。只补摸底中暴露的问题，不从第一页顺序刷到最后。

## 4. 项目阅读（30 分钟）

阅读：

- `exercises/week01/task_cli.py`
- `src/support_agent/schemas.py`

回答：为什么 Task 使用 dataclass，而 API 输入输出使用 Pydantic？把答案写入 `docs/error_log.md` 下方或自己的学习笔记。

## 5. 收尾（15 分钟）

- 在 `docs/project_review.md` 记录今天不会的内容。
- 用自己的话口述今天写的代码 3 分钟。
- Git 提交建议：`study: complete day 1 python baseline`。

Day 1 的成功标准是明确真实短板，并完成一次无 AI 编码，不是看完很多视频。
