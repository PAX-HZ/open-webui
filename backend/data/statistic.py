import json
import io
import psycopg2
import os
from dotenv import load_dotenv
import datetime
from collections import Counter



# 从 .env 文件中加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# 从环境变量中获取数据库 URL
database_url = os.getenv("DATABASE_URL")

# 连接到 PostgreSQL 数据库
conn = psycopg2.connect(database_url)
print(conn)
cursor = conn.cursor()

# 执行 SQL 语句
# SQLite
# cursor.execute("SELECT json_extract(chat, '$.messages') FROM chat")
# PostgreSQL
cursor.execute("SELECT (replace(chat, '\\u0000', '')::json)->>'messages' FROM chat")
# 获取查询结果
results = cursor.fetchall()

# 创建一个 JSON 对象
json_data = []

for row in results:
    chat = row[0]
    messages = json.loads(chat)
    json_data.append(messages)

# 将结果保存为 JSON 文件
with io.open('webui.json', 'w') as f:
    json.dump(json_data, f)

# 关闭数据库连接
conn.close()

# Load the JSON data
data = json.load(open('webui.json', 'r'))

# Initialize arrays to store model and info data
models = []
info_dicts = []
eval_timestamp_dicts = []
rating1_dicts = []
rating0_dicts = []

# Loop through each message
for messages in data:
    for message in messages:
        if message['role'] == "assistant":
            models.append(message['model'])
            if 'info' in message:
                info_dicts.append(message['info'])
            if 'timestamp' in message:
                eval_timestamp_dicts.append(message['timestamp'])
            if 'rating' in message:
                if(message['rating']==1):
                    rating1_dicts.append(message['rating'])
                elif(message['rating']==-1):
                    rating0_dicts.append(message['rating'])

# Group by model and count the occurrences
model_counts = {}
for model in set(models):
    model_counts[model] = models.count(model)

# Calculate the total duration for all info dictionaries
total_duration_in = 0
total_duration_out = 0
total_duration_load = 0
total_count_in = 0
total_count_out = 0
for info_dict in info_dicts:
    total_duration_in += info_dict.get('prompt_eval_duration', 0)
    total_duration_out += info_dict.get('eval_duration', 0)
    total_duration_load += info_dict.get('load_duration', 0)
    total_count_in += (info_dict.get('prompt_eval_count', 0))
    total_count_out += (info_dict.get('prompt_eval_count', 0))


# Initialize an empty dictionary to store the results
day_counts = {}

for timestamp in eval_timestamp_dicts:
    # Convert the timestamp to a date object
    date_obj = datetime.datetime.fromtimestamp(timestamp)

    # Get the day of the week (Monday to Sunday) as a string
    day_of_week = date_obj.strftime('%A')

    # If the day is not already in the dictionary, add it with a count of 0
    if day_of_week not in day_counts:
        day_counts[day_of_week] = 0

    # Increment the count for this day
    day_counts[day_of_week] += 1


fix = 1000000000
print("Model counts:", model_counts)
print("会话数:", len(results))
print("对话数:", len(info_dicts))
print(f"LLM加载总时长:{(total_duration_load/fix)/60}分钟")
print("处理token数（输入+输出）:", (total_count_in+total_count_out))
print("回复总时长:", (total_duration_out/fix)/60,"分钟")
print("回复token速度:", total_count_out/(total_duration_out/fix)," tokens/s")
print("赞:", len(rating1_dicts))
print("踩:", len(rating0_dicts))
print("按星期分组统计:", day_counts)