import json
import io
import psycopg2
import os
from dotenv import load_dotenv
import datetime
from collections import Counter
import csv
from collections import defaultdict

# 获取当前脚本文件所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前日期，格式为 YYYYMMDD
date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# 生成带日期戳的 CSV 文件名
csv_file_name = f'weekly_statistic_{date_str}.csv'
csv_file_path = os.path.join(script_dir, csv_file_name)
json_file_path = os.path.join(script_dir, 'statistic.json')

def loadDB2Json():
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
    cursor.execute("SELECT (replace(chat::text, '\\u0000', '')::json)->>'messages',user_id FROM chat where user_id not like 'shared%'")
    # 获取查询结果
    results = cursor.fetchall()

    # 创建一个 JSON 对象
    json_data = []

    for row in results:
        chat = row[0]
        user_id = row[1]
        try:
            messages = json.loads(chat)
            # 确保 messages 是列表
            if isinstance(messages, list):
                for message in messages:
                    # 将 user_id 添加到每条消息
                    message['user_id'] = user_id
            else:
                print(f"Unexpected format for messages: {messages}")
        except Exception as e:  # JSON 解析错误时捕获异常
            print(f"JSON 解析失败：{e}\n{row}")

        json_data.append(messages)

    print(f"json_data len: {len(json_data)}")
    # 将结果保存为 JSON 文件
    with io.open(json_file_path, 'w') as f:
        json.dump(json_data, f)

    # 关闭数据库连接
    conn.close()

loadDB2Json()

# Load the JSON data
data = json.load(open(json_file_path, 'r'))

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
        # if 'timestamp' in message:
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
    total_count_out += (info_dict.get('eval_count', 0))


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
print("处理字符数（输入+输出）:", (total_count_in+total_count_out))
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
# 处理字符数（输入+输出）: 12765856
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
# 处理字符数（输入+输出）: 12765856
# 回复总时长: 551.8516650166667 分钟
# 回复token速度: 192.77305855391492  tokens/s
# 赞: 20
# 踩: 26
# 按星期分组统计: {'Wednesday': 2324, 'Tuesday': 2092, 'Monday': 2156, 'Thursday': 2340, 'Friday': 2409, 'Saturday': 456, 'Sunday': 199}
# 按月份分组统计: {'April': 752, 'May': 2194, 'June': 1829, 'September': 1967, 'October': 938, 'August': 1883, 'July': 2413}

# 初始化字典存储按周统计数据
weekly_stats = defaultdict(lambda: {
    '会话数': 0,
    '对话数': 0,
    '处理字符数': 0,
    '降低代码复杂度': 0,
    '专业英语翻译': 0,
    '代码解析': 0,
    '要点凝练': 0,
    '项目跟踪邮件助手': 0
})
weekly_active_users = defaultdict(set)  # 用于存储每周的活跃用户集合

# 遍历每条数据，根据每周累加各项统计
for i, messages in enumerate(data):
    for msg in messages:
        # 从每条消息中提取 timestamp 和 user_id
        timestamp = msg.get('timestamp')
        user_id = msg.get('user_id')

        if timestamp is not None and user_id is not None:
            # 根据 timestamp 计算所属周
            week_of_year = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%W')
            
            # 记录用户活跃
            weekly_active_users[week_of_year].add(user_id)
            
            # # 打印特定周的活跃用户（如需要）
            # if week_of_year == "2024-47":
            #     print(week_of_year, user_id)
            # 更新统计数据
            weekly_stats[week_of_year]['对话数'] += 1
            weekly_stats[week_of_year]['处理字符数'] += int((
                msg.get('info', {}).get('prompt_eval_count', 0) +
                msg.get('info', {}).get('eval_count', 0)
            )/1000)

    # 查找第一个包含有效 timestamp 的消息
    reference_timestamp = next(
        (msg.get('timestamp') for msg in messages if msg.get('timestamp') is not None),
        None  # 如果找不到有效的 timestamp，返回 None
    )
    
    if reference_timestamp is not None:
        # 计算所属周
        week_of_year = datetime.datetime.fromtimestamp(reference_timestamp).strftime('%Y-%W')
        
        # 基于整组消息更新会话数
        weekly_stats[week_of_year]['会话数'] += 1



    # week_of_year = datetime.datetime.fromtimestamp(eval_timestamp_dicts[i]).strftime('%Y-%W')
    # # user_id = messages[0]['user_id']  # 假设 user_id_dict 存储每条消息的对应 user_id
    # # if(str(week_of_year)==("2024-47")):
    # #     print(week_of_year, user_id)
    # # weekly_active_users[week_of_year].add(user_id)  # 记录该用户在对应周活跃过
    
    # weekly_stats[week_of_year]['会话数'] += 1
    # # Count only messages with 'role' == "assistant"
    # weekly_stats[week_of_year]['对话数'] += sum(1 for message in messages if message['role'] == "assistant")
    # # weekly_stats[week_of_year]['处理字符数'] += sum(
    # #     msg.get('token_count', 0) for msg in messages if 'token_count' in msg
    # # )
    # weekly_stats[week_of_year]['处理字符数'] += int(sum(
    #     msg['info'].get('prompt_eval_count', 0) + msg['info'].get('eval_count', 0)
    #     for msg in messages if 'info' in msg
    # )/1000)

    # 按模型统计使用频次
    for message in messages:
        model = message.get('model', "")
        if model == '降低代码复杂度':
            weekly_stats[week_of_year]['降低代码复杂度'] += 1
        elif model == '专业英语翻译':
            weekly_stats[week_of_year]['专业英语翻译'] += 1
        elif model == '代码解析':
            weekly_stats[week_of_year]['代码解析'] += 1
        elif model == '要点凝练':
            weekly_stats[week_of_year]['要点凝练'] += 1
        elif model == '项目跟踪邮件助手':
            weekly_stats[week_of_year]['项目跟踪邮件助手'] += 1

# 导出为 CSV 文件
with open(csv_file_path, 'w', newline='') as csvfile:
    fieldnames = ['周数', '会话数', '对话数', '处理字符数', '降低代码复杂度', '专业英语翻译', '代码解析', '要点凝练', '项目跟踪邮件助手', '活跃用户数']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for week, stats in sorted(weekly_stats.items()):
        row = {'周数': week}
        row.update(stats)
        writer.writerow(row)

# 新增一个变量来保存累积的处理 token 总数
cumulative_token_count = 0
# Example for converting week-based keys to a 'yyyy/MM/dd' format when exporting to CSV
with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as csv_file:
    fieldnames = ['Week Start Date', '会话数', '对话数', '处理字符数', '累计处理字符总数', 
                  '降低代码复杂度', '专业英语翻译', '代码解析', '要点凝练', '项目跟踪邮件助手', '活跃用户数']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for week, stats in sorted(weekly_stats.items()):
        # Convert week to the first day of the week, formatted as 'yyyy/MM/dd'
        year, week_number = map(int, week.split('-'))
        week_start_date = datetime.datetime.strptime(f'{year}-W{week_number}-1', "%Y-W%W-%w").strftime('%Y/%m/%d')
        # 累加每周的处理 token 数到累积总数中
        cumulative_token_count += stats['处理字符数']
        # 获取对应周的活跃用户数
        # if(str(week_start_date)=="2024/11/18"):
        #     print(week_start_date, weekly_active_users[week])
        active_user_count = len(weekly_active_users[week])
        
        # Write the row with formatted week_start_date
        row = {
            'Week Start Date': week_start_date,
            '会话数': stats['会话数'],
            '对话数': stats['对话数'],
            '处理字符数': stats['处理字符数'],
            '累计处理字符总数': cumulative_token_count,
            '降低代码复杂度': stats['降低代码复杂度'],
            '专业英语翻译': stats['专业英语翻译'],
            '代码解析': stats['代码解析'],
            '要点凝练': stats['要点凝练'],
            '项目跟踪邮件助手': stats['项目跟踪邮件助手'],
            '活跃用户数': active_user_count
        }
        writer.writerow(row)