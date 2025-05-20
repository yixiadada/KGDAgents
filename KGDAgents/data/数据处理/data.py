import json

# 假设json_data是你的原始数据
# 读取JSON文件
with open('data\数据处理\patients(1).json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# 定义需要移除的字段
fields_to_remove = ["medical_record","reformed_text_medical_record","department","profile"]

# 移除指定字段
cleaned_data = []
for record in json_data:
    cleaned_record = {key: value for key, value in record.items() if key not in fields_to_remove}
    cleaned_data.append(cleaned_record)

# 打印清理后的数据
print(json.dumps(cleaned_data, ensure_ascii=False, indent=4))

# 将清理后的数据保存为patients(1).json
with open('data\数据处理\patients(2).json', 'w', encoding='utf-8') as file:
    json.dump(cleaned_data, file, ensure_ascii=False, indent=4)