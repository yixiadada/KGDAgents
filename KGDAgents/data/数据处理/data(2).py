import json

# 读取原始JSON文件
with open('data\数据处理\patients(2).json', 'r', encoding='utf-8') as file:
    patients = json.load(file)

# 处理每个患者的数据
for patient in patients:
    raw_medical_record = patient.pop('raw_medical_record')
    
    # 重新组织数据
    patient['symptom'] = {
        "一般资料": raw_medical_record.get("一般资料"),
        "主诉": raw_medical_record.get("主诉"),
        "现病史": raw_medical_record.get("现病史"),
        "既往史": raw_medical_record.get("既往史")
    }
    
    patient['examine'] = {
        "查体": raw_medical_record.get("查体"),
        "辅助检查": raw_medical_record.get("辅助检查")
    }
    
    patient['diagnosis'] = {
        "初步诊断": raw_medical_record.get("初步诊断"),
        "诊断依据": raw_medical_record.get("诊断依据"),
        "鉴别诊断": raw_medical_record.get("鉴别诊断"),
        "诊断结果": raw_medical_record.get("诊断结果")
    }
    
    patient['cure'] = raw_medical_record.get("诊治经过")

# 将处理后的数据写回JSON文件
with open('patients(3).json', 'w', encoding='utf-8') as file:
    json.dump(patients, file, ensure_ascii=False, indent=4)

print("处理完成，结果已保存到 processed_patients(2).json 文件中。")