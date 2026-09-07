-- 先根据 src/support_agent/models.py 手画表结构，再完成下面练习。

-- 1. 每个用户的会话数量
SELECT user_id, COUNT(*) AS session_count
FROM conversations
GROUP BY user_id
ORDER BY session_count DESC;

-- 2. 最近 7 天每个会话的消息数量
SELECT c.id AS session_id, COUNT(m.id) AS message_count
FROM conversations AS c
LEFT JOIN messages AS m ON m.session_id = c.id
WHERE c.created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY c.id
ORDER BY message_count DESC;

-- 3. 差评消息及对应助手回答
SELECT f.rating, f.comment, m.content, m.created_at
FROM feedback AS f
JOIN messages AS m ON m.id = f.message_id
WHERE f.rating < 0
ORDER BY f.created_at DESC;

-- 思考：应在哪些列上建立索引？为什么不要给每一列都建索引？

