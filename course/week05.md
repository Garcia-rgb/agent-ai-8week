# 第 5 周：LangGraph 与安全工作流

主资源：[LangGraph 当前官方文档](https://docs.langchain.com/oss/python/langgraph/overview)、Hugging Face Agents Course Unit 2.3、Hugging Face MCP Course Unit 1、[MCP latest specification](https://modelcontextprotocol.io/specification/latest)。

## 日程

- Day 1：State、Node、Edge 和条件路由。
- Day 2：阅读 `graph.py`，画出当前状态图。
- Day 3：加入 Checkpoint，并比较数据库会话与图状态；理解 durable execution 与 replay。
- Day 4：实现工具超时、最多重试次数和错误节点。
- Day 5：实现最小 MCP Server/Client，理解 Host、Client、Server、Tools、Resources 和 Prompts。
- Day 6：演示工单确认令牌、防篡改、防重放和过期。
- Day 7：用无 AI 方式实现一个新的只读工具。

## 验收问题

1. 哪些状态应持久化，哪些只存在于单次请求？
2. 为什么查询设备状态和创建工单的确认要求不同？
3. LangGraph 相比普通函数编排解决了什么问题？
4. MCP 工具返回内容为什么仍应视为不可信输入？
5. 当前 MCP 规范的 Authorization、用户同意和工具权限边界分别由谁负责？
