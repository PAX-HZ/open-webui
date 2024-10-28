import json
import io
import psycopg2
import os
from dotenv import load_dotenv
import datetime
from collections import Counter

def loadDB2Json():
    # 获取当前脚本文件所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取父级目录的上级目录路径
    parent_parent_dir = os.path.join(script_dir, '../../')
    # 构建 .env 文件的完整路径
    dotenv_path = os.path.normpath(os.path.join(parent_parent_dir, '.env'))
    # 从 .env 文件中加载环境变量
    load_dotenv(dotenv_path)

    # 从环境变量中获取数据库 URL
    database_url = os.getenv("DATABASE_URL")
    print(f"database_url:{database_url}")

    # 连接到 PostgreSQL 数据库
    conn = psycopg2.connect(database_url)
    print(conn)
    cursor = conn.cursor()

    # 执行 SQL 语句
    # SQLite
    # cursor.execute("SELECT json_extract(chat, '$.messages') FROM chat")
    # PostgreSQL
    cursor.execute("SELECT (replace(chat, '\\u0000', '')::json)->>'messages',id FROM chat")
    # 获取查询结果
    results = cursor.fetchall()

    # 创建一个 JSON 对象
    json_data = []

    for row in results:
        chat = row[0]
        try:
            messages = json.loads(chat)
        except Exception as e:  # JSON 解析错误时捕获异常
            print(f"JSON 解析失败：{e}\n{row}")

        json_data.append(messages)

    print(f"json_data len: {len(json_data)}")
    # 将结果保存为 JSON 文件
    with io.open('webui.json', 'w') as f:
        json.dump(json_data, f)

    # 关闭数据库连接
    conn.close()

loadDB2Json()

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
month_counts = {}

for timestamp in eval_timestamp_dicts:
    # Convert the timestamp to a date object
    date_obj = datetime.datetime.fromtimestamp(timestamp)

    # Get the day of the week (Monday to Sunday) as a string
    day_of_week = date_obj.strftime('%A')
    # Get the month (e.g., January, February) as a string
    month = date_obj.strftime('%B')

    # If the day is not already in the dictionary, add it with a count of 0
    if day_of_week not in day_counts:
        day_counts[day_of_week] = 0
    
    # If the month is not already in the dictionary, add it with a count of 0
    if month not in month_counts:
        month_counts[month] = 0

    # Increment the count for this day
    day_counts[day_of_week] += 1
    month_counts[month] += 1


fix = 1000000000
print("Model counts:", model_counts)
print("会话数:", len(data))
print("对话数:", len(info_dicts))
print(f"LLM加载总时长:{(total_duration_load/fix)/60}分钟")
print("处理token数（输入+输出）:", (total_count_in+total_count_out))
print("回复总时长:", (total_duration_out/fix)/60,"分钟")
print("回复token速度:", total_count_out/(total_duration_out/fix)," tokens/s")
print("赞:", len(rating1_dicts))
print("踩:", len(rating0_dicts))
print("按星期分组统计:", day_counts)
print("按月份分组统计:", month_counts)

# 2024年10月23日19点19分
# Model counts: {'CodeWizard:v1.5': 3, '代码解析': 61, 'llama3:70b-instruct': 1, 'llama3:8b': 698, '项目跟踪邮件助手': 3, 'llama2:13b': 10, 'qwen2.5:7b-instruct-q4_K_M': 4, 'qwen2.5:14b-instruct-q4_K_M': 589, '专业英语翻译': 638, 'CodeWizard-EMEA:v1.6': 1, 'command-r:35b': 2, 'CodeWizard:v1.2': 3, 'mistral:v0.2': 219, 'mistral:7b-instruct-v0.2-fp16': 19, 'llama3:8b-instruct-fp16': 13, '降低代码复杂度': 28, 'gemma:v1.1': 903, 'mistral:7b': 3, 'llama2-chinese:13b': 9, 'qwen2:7b-instruct-q4_K_M': 2678, 'qwen2:72b-instruct': 4, 'CodeWizard-EMEA:v1.7': 2, 'codellama:13b': 9, 'llama2:latest': 6, 'gemma:7b-instruct-v1.1-fp16': 24, '要点凝练': 51, 'qwen:14b': 6, 'CodeLlama3-8B-Python:latest': 4, 'llama3:8b-instruct-q4_K_M': 40, 'gemma:7b': 15, 'llama2:70b': 9}
# 会话数: 1725
# 对话数: 5971
# LLM加载总时长:127.10694012758333分钟
# 处理token数（输入+输出）: 12765856
# 回复总时长: 551.8516650166667 分钟
# 回复token速度: 192.77305855391492  tokens/s
# 赞: 20
# 踩: 26
# 按星期分组统计: {'Wednesday': 1173, 'Tuesday': 1064, 'Monday': 1089, 'Thursday': 1179, 'Friday': 1220, 'Saturday': 230, 'Sunday': 100}
# 按月份分组统计: {'April': 384, 'May': 1099, 'June': 917, 'September': 996, 'October': 476, 'August': 955, 'July': 1228}

# Model counts: {'专业英语翻译': 638, 'gemma:v1.1': 903, 'CodeWizard:v1.2': 3, 'CodeLlama3-8B-Python:latest': 4, '项目跟踪邮件助手': 3, 'qwen:14b': 6, 'gemma:7b-instruct-v1.1-fp16': 24, 'llama3:8b-instruct-fp16': 13, 'llama3:8b-instruct-q4_K_M': 40, 'qwen2:7b-instruct-q4_K_M': 2678, 'codellama:13b': 9, '代码解析': 61, '要点凝练': 51, 'llama2-chinese:13b': 9, 'qwen2.5:7b-instruct-q4_K_M': 4, 'CodeWizard-EMEA:v1.7': 2, 'CodeWizard:v1.5': 3, 'mistral:7b': 3, 'qwen2.5:14b-instruct-q4_K_M': 589, 'mistral:7b-instruct-v0.2-fp16': 19, 'gemma:7b': 15, 'qwen2:72b-instruct': 4, 'mistral:v0.2': 219, '降低代码复杂度': 28, 'llama2:latest': 6, 'llama2:70b': 9, 'llama3:8b': 698, 'llama3:70b-instruct': 1, 'CodeWizard-EMEA:v1.6': 1, 'command-r:35b': 2, 'llama2:13b': 10}
# 会话数: 1725
# 对话数: 5971
# LLM加载总时长:127.10694012758333分钟
# 处理token数（输入+输出）: 12765856
# 回复总时长: 551.8516650166667 分钟
# 回复token速度: 192.77305855391492  tokens/s
# 赞: 20
# 踩: 26
# 按星期分组统计: {'Wednesday': 2324, 'Tuesday': 2092, 'Monday': 2156, 'Thursday': 2340, 'Friday': 2409, 'Saturday': 456, 'Sunday': 199}
# 按月份分组统计: {'April': 752, 'May': 2194, 'June': 1829, 'September': 1967, 'October': 938, 'August': 1883, 'July': 2413}