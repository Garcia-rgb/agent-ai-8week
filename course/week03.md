# 第 3 周：LLM API 与手写 Agent

主资源：DeepLearning.AI Agentic AI Module 1、3；Hugging Face Agents Course Unit 1；OpenAI 官方 Agents SDK 总览与 Tools/Function Calling 文档。

## 日程

- Day 1：Token、上下文、采样参数和成本估算。
- Day 2：Developer/System Prompt、Few-shot、结构化输出；理解 Responses API 的 Output Items。
- Day 3：阅读 `examples/manual_agent.py`，理解工具白名单。
- Day 4：调用兼容 API，加入超时、重试和错误映射。
- Day 5：手写“模型—工具—结果—模型”的最多 5 轮循环；对照 Responses API Function Calling 流程。
- Day 6：加入会话记录、参数校验和未知工具处理。
- Day 7：关闭 AI 重写 `safe_calculate` 的核心递归逻辑。

## 验收问题

1. Tool Calling 为什么仍然需要服务端参数校验？
2. Agent Loop 为什么必须有最大轮数？
3. Temperature 降为 0 为什么也不能保证完全确定？
4. 模型超时、限流和业务校验失败应如何分别处理？
5. Responses API 与 Agents SDK 谁负责 Agent Loop？为什么本项目仍保留厂商中立适配层？
