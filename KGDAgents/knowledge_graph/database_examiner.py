# 数据库检索员

from openai import OpenAI
from knowledge_graph.neo4j_api import fetch_diseases_for_symptom

class DatabaseExaminer:
    def __init__(self,api_key,api_base):
        self.client = OpenAI(api_key=api_key,base_url=api_base)
        self.system_message = {
            "role":"system",
            "content":
            (
            "你是一个专业的数据库检索员，下面你会得到患者的叙述，你需要:\n"
            "1. 你需要根据患者的描述，用几个词简要描述患者的症状。\n"
            "2. 症状前面不要加表示程度的形容词，如'轻微胸闷'，只需要'胸闷'即可。\n"
            "3. 请注意患者的回复，如果患者说'没有头痛、恶心或其他不适症状。'，请不要返回任何症状。\n"
            "请按照以下格式返回:\n"
            "症状1\n症状2\n症状3\n..."
        )}
        self.model = 'gpt-3.5-turbo'
        self.memory = [self.system_message]
    def get_response(self,patient_message):
        self.memory.append({"role":"user","content":f"患者回复:{patient_message}"})
        patient_response = self.client.chat.completions.create(
            model=self.model,
            messages=self.memory,
            temperature=0
        )
        reponse_content = patient_response.choices[0].message.content
        # print(f"知识图谱检索员分析出的症状：{reponse_content}")
        
        disease_count = {}  # 存储每个疾病出现的次数

        for line in reponse_content.split("\n"):  # 逐个症状交给知识图谱
            diseases = fetch_diseases_for_symptom(line)
            for disease in diseases:
                if disease in disease_count:
                    disease_count[disease] += 1
                else:
                    disease_count[disease] = 1
        disease_count = dict(sorted(disease_count.items(), key=lambda item: item[1], reverse=True))  # 按出现次数排序
        return disease_count  # 返回的是一次对话中的症状共同的疾病



