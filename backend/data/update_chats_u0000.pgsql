select c.user_id,c.chat from chat as c where c.chat::text LIKE '%\\u0000%';
-- UPDATE chat
-- SET chat = REPLACE(chat::text, '\u0000', '')::json
-- WHERE chat::text LIKE '%\u0000%';