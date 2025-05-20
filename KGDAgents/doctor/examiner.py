# 检查员  由gpt3.5 驱动

import openai
from openai import OpenAI

class Examiner():
    def __init__(self,examiner_data,openai_api_key,openai_api_base,temperture=0,max_tokens=1024, top_p=1, frequency_penalty=0, presence_penalty=0):
        openai_model='gpt-3.5-turbo'
        self.openai_api_key = openai_api_key
        self.openai_api_base = openai_api_base
        self.openai_model = openai_model
        self.temperture = temperture
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        # 等数据加载了之后要去掉
        self.examiner_message = examiner_data
        self.system_message = {
            "role":"system",
            "content":(
                "你是医院负责医学检查的人员，这是你获得的资料：\n"
                f"{self.examiner_message}\n"
                "接下来会有患者向你寻求检查，你需要：\n"
                "(1)从病人的检查申请中解析出指向明确的专业医学检查项目。\n"
                "(2)只提供病人要求的检查项目，不要提供其他检查项目。\n"
                "(3)你需要从你获得的资料中，查询是否有相关检查项目的结果，\n"
                "如果有，请按照下面的格式输出，并且不要包含任何日期信息：\n"
                "#检查项目#\n- xxx\n"
                "#检查结果#\n- xxx\n"
                "(4)如果没有找到具体的医学检查项目，请输出：\n"
                "#检查项目#\n- xxx\n"
                "#检查结果#\n- 无异常\n"
                "(5)在输出检查结果时，请去掉所有的日期信息，直接给出检查结果。\n"
                "(6)例如，原始数据中如果有'心电图显示快速型房颤（2020-06-05于我院）'，"
                "你应该只输出'心电图显示快速型房颤'。\n"
            )
        }
        self.client = OpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_api_base
        )
        self.memory = [self.system_message]
    
    def get_response(self,patient_info):
        self.memory.append({"role":"user","content":patient_info})
        # print(f"examiner:{self.memory}")
        examiner_response = self.client.chat.completions.create(
            model=self.openai_model,
            messages=self.memory,
            temperature=self.temperture,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty
        )
        examiner_response_content = examiner_response.choices[0].message.content
        return examiner_response_content