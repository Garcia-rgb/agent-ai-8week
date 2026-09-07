# 第 2 周：后端、数据库与测试

## 日程

- Day 1：SQL 增删改查、主键、外键、唯一约束。
- Day 2：索引、事务、隔离级别；用 `EXPLAIN` 观察查询。
- Day 3：SQLAlchemy Session、提交、回滚和连接池。
- Day 4：FastAPI 分层、依赖注入、配置和异常映射。
- Day 5：pytest Fixture、Mock、API 测试。
- Day 6：Dockerfile、Compose、健康检查；启动 PostgreSQL 与 Redis。
- Day 7：无 AI 写会话和消息查询，运行全部测试并复盘。

## 仓库练习

- 阅读 `models.py`，手画所有表的关系。
- 给会话列表增加分页，但先写测试再实现。
- 人为制造一次事务失败，验证没有产生半条数据。

## 验收问题

1. 为什么数据库唯一约束不能只靠接口校验替代？
2. Session 生命周期过长有什么风险？
3. 单元测试和接口测试分别保护什么？
4. Redis 不可用时哪些功能应该降级，哪些应该失败？

