import json
import os

# 读取原始数据
with open('data\patients.json', 'r', encoding='utf-8') as file:
    patients = json.load(file)

# 计算需要生成的文件数量
num_patients = len(patients)
num_files = (num_patients + 99) // 100  # 向上取整

# 创建输出目录（如果不存在）
output_dir = 'split_patients'
os.makedirs(output_dir, exist_ok=True)

# 切分数据并保存到不同的文件
for i in range(num_files):
    start_idx = i * 100
    end_idx = min(start_idx + 100, num_patients)
    file_name = os.path.join(output_dir, f'patients({i+1}).json')
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(patients[start_idx:end_idx], file, ensure_ascii=False, indent=4)

print(f"数据已成功切分为 {num_files} 个文件，保存在 {output_dir} 目录下。")