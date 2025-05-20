import json

def split_symptom(symptom_str):
    # 分割字符串获取一般资料和既往史
    parts = symptom_str.split("既往史：")
    
    if len(parts) != 2:
        return {
            "一般资料": symptom_str,
            "既往史": ""
        }
    
    general_info = parts[0]
    history = "既往史：" + parts[1]
    
    return {
        "一般资料": general_info,
        "既往史": history
    }

def transform_data(input_file, output_file):
    # 读取原始JSON文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换每个记录
    for record in data:
        if "symptom" in record and isinstance(record["symptom"], str):
            record["symptom"] = split_symptom(record["symptom"])
    
    # 写入新的JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 执行转换
transform_data('data/final.json', 'data/final_transformed.json')