-- SELECT u.name, COUNT(chat.user_id) AS c
-- FROM chat
-- JOIN "user" AS u ON chat.user_id = u.id  -- 假设 user 表中有 id 字段
-- where u.role='user'
-- GROUP BY u.name
-- ORDER BY c DESC;

SELECT 
    u.name, 
    COUNT(chat.user_id) AS session_count,
    SUM(jsonb_array_length(REPLACE(chat.chat::text, '\u0000', '')::jsonb->'messages')) AS total_messages
FROM 
    chat
JOIN 
    "user" AS u ON chat.user_id = u.id  -- 假设 user 表中有 id 字段
WHERE
    u.role = 'user'
GROUP BY 
    u.name
ORDER BY 
    total_messages desc, session_count DESC;

-- SELECT (replace(c.chat, '\u0000', '')::json)->>'messages',c.id
-- from chat as c
-- where c.id NOT IN ('84dadf5a-315d-46a4-98da-17d0143037d5',
--                  '2006cec8-9ff1-44ee-91a6-2e150136e596',
--                  'b57c2e08-fca7-41c6-ade0-d72cdaaf2e5f',
--                  '9a8cbabb-aa8e-4876-90c3-df1c2362ebea')
