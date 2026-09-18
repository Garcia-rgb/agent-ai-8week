# 第 4 周：RAG 与知识库

主资源：Hugging Face Agents Course Unit 3（Agentic RAG）和 LlamaIndex 当前文档的 Ingestion、Retriever、Evaluation；不要通读 LlamaIndex 所有 Agent 功能。

## 日程

- Day 1：PDF/Markdown 解析、清洗和元数据。
- Day 2：固定长度、按段落和语义切块的取舍。
- Day 3：Embedding、余弦相似度和 pgvector。
- Day 4：BM25 思想、混合检索和 Rerank。
- Day 5：引用溯源、Query Rewrite 和空结果降级。
- Day 6：导入本地知识库并运行离线评测。
- Day 7：修改切块参数，对比结果并写实验记录。

Full Stack LLM Bootcamp 仅选看 LLMOps/UX。它录制于 2023 年，不照抄其中 API 或框架代码。

## 必做实验

分别使用 300/50、700/100、1200/150 三组“块大小/重叠”，记录：通过率、平均 Top-1 分数、索引块数和主观引用完整度。不要只保留最好结果。

## 验收问题

1. 检索召回失败和模型幻觉如何区分？
2. 为什么向量相似不等于事实相关？
3. Chunk 太大和太小分别会发生什么？
4. 评测集为什么要固定版本？
