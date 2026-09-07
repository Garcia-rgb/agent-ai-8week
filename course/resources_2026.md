# 2026 Agent 课程与框架核对报告

核对日期：2026-09-03。以下结论来自各项目官方页面；课程开始前不需要把所有资源都看完。

## 核心结论

1. 原路线的 `Python → 手写循环 → RAG → LangGraph → 评测/安全` 顺序仍然合理。
2. Agent 学习不能只等于学 LangChain。当前主线应覆盖工具、状态、持久化、人工确认、评测和安全。
3. OpenAI 官方目前明确区分：想自己控制工具循环和分支时使用 Responses API；希望 SDK 管理循环、会话、Tracing、Guardrails 和可恢复审批时使用 Agents SDK。
4. LangGraph 当前定位是低层编排运行时，核心优势是 durable execution、streaming、human-in-the-loop 和 persistence，适合作为本项目的主框架。
5. MCP 已经不是“了解名词”即可。官方当前最新规范入口显示版本为 `2026-07-28`，需要至少完成一次 Client/Server 实践，并理解授权和信任边界。
6. 多 Agent 不是入门必需品。能用普通函数或确定性工作流解决的问题，不应强行拆成多个 Agent。
7. Full Stack LLM Bootcamp 是 2023 年录制，产品与 API 内容可能过时；它仍适合建立 LLM 产品、UX、LLMOps 的整体认识，但不再作为代码主教材。

## 课程比较

| 资源 | 当前状态与覆盖 | 优点 | 局限 | 本课程用法 |
|---|---|---|---|---|
| [DeepLearning.AI: Agentic AI](https://www.deeplearning.ai/courses/agentic-ai/) | 当前页面标注 New Course；约 9h55m，覆盖 Reflection、Tool Use、Planning、Multi-Agent、Evals | 从第一性原理讲模式，项目和错误分析较完整 | 中级 Python；部分作业/证书需要 PRO | 第 3、6 周主课，优先 Module 1、3、4，Module 5 选学 |
| [Hugging Face Agents Course](https://huggingface.co/learn/agents-course/unit0/introduction) | Living project；涵盖基础、smolagents、LlamaIndex、LangGraph、Agentic RAG、Final Project、评测 | 免费、有中文入口、有作业和认证路径 | 框架覆盖较多，容易平均用力 | 第 3–5 周主课；只做 Unit 1、2.3、3 和评测 Bonus |
| [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course/unit0/introduction) | 与 Anthropic 合作；覆盖架构、端到端应用、部署 | 免费，Client/Server 实践完整 | 全部完成约需多周 | 第 5 周做 Unit 1，并完成一个最小 Server/Client |
| [LangGraph 官方文档](https://docs.langchain.com/oss/python/langgraph/overview) | 当前文档强调长运行、有状态 Agent；含持久化、故障恢复、Interrupt、Time Travel、测试 | 与本项目匹配，生产概念清楚 | 偏低层，对初学者认知负担较高 | 第 5 周唯一要求熟练的框架资料 |
| [LangChain Academy](https://academy.langchain.com/) | 当前首页重点已经转向 Deep Agents、LangSmith、部署和认证 | 自学课程结构清晰，适合补观测和 Agent Harness | 产品内容较多，部分能力依赖平台 | 第 6 周选学 LangSmith Essentials；不依赖旧的 Intro to LangGraph 链接 |
| [OpenAI Agents SDK](https://developers.openai.com/api/docs/guides/agents) | 官方文档覆盖 SDK Loop、Sessions、Handoffs、Guardrails、审批与 Observability | 能清楚理解 SDK 管循环与应用自管循环的差别 | 厂商生态专项，不应替代通用工程能力 | 第 3 周阅读比较；第 5 周做可选 Quickstart |
| [OpenAI Tools](https://developers.openai.com/api/docs/guides/tools) | 当前工具体系包含 Function Calling、内置工具、Tool Search、Programmatic Tool Calling、Remote MCP | 能看到现代工具调用完整形态 | 部分能力与模型/平台绑定 | 第 3 周掌握 Function Calling；其余只建立地图 |
| [OpenAI Evals](https://developers.openai.com/api/docs/guides/evals) | 官方 Evals 使用数据源与 Grader 组合，并强调固定测试集 | 适合学习系统化评测设计 | 使用平台评测会产生调用成本 | 第 6 周与本地 JSONL 评测做概念对照 |
| [LlamaIndex 文档](https://docs.llamaindex.ai/en/stable/) | 同时覆盖 RAG、数据摄取、Agent、状态、HITL、评测和 MCP | 文档处理与 RAG 组件丰富 | 与 LangGraph 功能有重叠 | 第 4 周只学 Ingestion、Retriever、Evaluation |
| [Full Stack LLM Bootcamp](https://fullstackdeeplearning.com/llm-bootcamp/) | 官方页面明确为 2023 年 4 月录制 | 产品、UX、LLMOps 全局视角仍有价值 | API、Agent 框架与工具生态明显老化 | 周末选看 LLMOps/UX，不照抄代码 |

## 当前框架地图

| 框架/平台 | 官方当前定位 | 是否主学 | 判断 |
|---|---|---|---|
| LangGraph | 低层、有状态、可持久化的 Agent 编排运行时 | 是 | 最适合展示确定性步骤与 LLM 步骤混合、人工确认和失败恢复 |
| OpenAI Agents SDK | SDK 托管 Agent Loop、Sessions、Tracing、Guardrails、Handoffs | 次主线 | 应会解释并做最小实验，但作品项目保持厂商中立 |
| Google ADK 2.0 | Python/TS/Go/Java/Kotlin，多 Agent、Graph Workflow、MCP、A2A、评测与确认 | 了解 | Google/Java/云岗位可加学；两个月内不与 LangGraph双主修 |
| Microsoft Agent Framework | .NET/Python/Go 的 Agent 与 Workflow；官方称其为 AutoGen 和 Semantic Kernel 的后继 | 了解 | Azure/.NET 企业岗位优先；不要再把 AutoGen 当微软最新主线 |
| PydanticAI | Python 类型优先、模型无关的 Agent 框架 | 了解 | 与 FastAPI/Pydantic 心智一致，适合小型强类型服务，但当前项目不换框架 |
| LlamaIndex | 以数据、RAG、摄取、检索和评测见长，也提供 Agent/Workflow | 局部学习 | 重点吸收 RAG 方法，不与 LangGraph 重复造两套工作流 |
| CrewAI | 以 Crews + Flows 组织多 Agent 和事件工作流 | 了解 | Demo 快，但容易角色扮演多于工程控制；只用于面试比较 |
| Dify | 可视化构建 Agent、Workflow、知识库并通过 API 发布 | 2–3 小时体验 | 中小团队落地常有价值，但不能替代 Python、测试和系统设计能力 |
| Deep Agents | LangGraph 上层 Agent Harness，包含规划、子 Agent、文件系统和上下文管理 | 第 8 周后 | 当前不是入门必需，完成主项目后再学 |

## 两个月内的取舍

必须完成：

- DeepLearning.AI Agentic AI 的 Module 1、3、4。
- Hugging Face Agents Course 的 Unit 1、Unit 2.3、Unit 3。
- LangGraph 官方文档中的 Quickstart、Thinking in LangGraph、Persistence、Interrupts、Testing。
- Hugging Face MCP Course Unit 1，以及官方最新规范的 Architecture、Tools、Authorization/Security 概览。
- OpenAI Agents SDK 总览中“Responses API vs Agents SDK”部分和 Tools 文档的 Function Calling 流程。

只需了解：

- Google ADK、Microsoft Agent Framework、PydanticAI、CrewAI、Dify 各做什么。
- 多 Agent、A2A、Agent Harness、Voice Agent。

暂不学习：

- 同时实现 3–4 套 Agent 框架。
- 微调 Function Calling 模型。
- 为了展示炫技而加入浏览器操作、自动付款或不受控 Shell。
- 直接照搬 2023 年课程中的 API 和框架代码。

## 资料新鲜度维护

- 每两周只检查一次主框架 Changelog，不在每天学习时追版本。
- 代码依文档记录 Python 包版本；课程链接记录最后核对日期。
- 本仓库已将 LangGraph 依赖更新为 `>=1,<2`，避免继续安装旧的 0.x 系列。
- 遇到教程与官方文档冲突，以官方当前文档为准。
- MCP 实现以 [latest specification](https://modelcontextprotocol.io/specification/latest) 为准；当前核对到 `2026-07-28`。
- 安全主线使用 [OWASP Top 10 for LLM and GenAI 2025](https://genai.owasp.org/llm-top-10/)，并额外关注 Agentic Security 项目。
