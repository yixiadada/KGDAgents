# 把id从1开始
import json

# 读取 JSON 文件
with open('data\patients(3).json', 'r', encoding='utf-8') as file:
    patients = json.load(file)

# 重新编号 id
for index, patient in enumerate(patients, start=1):
    patient['id'] = index

# 写回 JSON 文件
with open('data\patients(3).json', 'w', encoding='utf-8') as file:
    json.dump(patients, file, ensure_ascii=False, indent=4)