# 第 6 周：生产化、安全与开始投递

主资源：DeepLearning.AI Agentic AI Module 4、OpenAI Evals 指南、LangChain Academy 当前 LangSmith Essentials、OWASP Top 10 for LLM and GenAI 2025。

## 日程

- Day 1：结构化日志、Trace ID、Token 与成本记录。
- Day 2：超时、重试、限流、缓存和幂等。
- Day 3：学习 OWASP 2025 的 Prompt Injection、Improper Output Handling、Excessive Agency、Vector/Embedding Weaknesses 和 Unbounded Consumption。
- Day 4：权限隔离、敏感信息脱敏和审计日志。
- Day 5：CI、Docker Compose 和健康检查。
- Day 6：整理第一版简历，完成第一批 8–10 个岗位投递。
- Day 7：完成剩余投递并总结 JD 高频词。

## 必做故障演练

- 模型返回 429、超时和非法 JSON。
- 数据库不可用、文件为空、PDF 无文本层。
- 伪造确认令牌、重复提交、跨用户读取会话。
- 知识库没有答案和知识库包含提示词攻击文本。

评测要求分三层记录：检索组件、工具选择/参数、最终回答。不要用一个总分掩盖错误来源。
