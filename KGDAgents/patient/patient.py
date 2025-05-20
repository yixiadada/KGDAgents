'''
    患者类,由gpt3.5 -turbo 驱动
'''
from openai import OpenAI
import re
from doctor.examiner import Examiner
from knowledge_graph.database_examiner import DatabaseExaminer  # 引入数据库检索员
class Patient:
    def __init__(self,patient_info,api_key,api_base):
        self.model_name = "gpt-3.5-turbo"
        self.patient_info = patient_info
        self.api_key = api_key
        self.api_base = api_base
        self.system_message = {
            "role":"system",
            "content": (
                "请牢牢记住你的角色是一个病人。不要充当其他角色.这是你的基本资料。\n" 
                f"{self.patient_info}\n"
                "你必须遵守以下规则：\n"
                "(1) 用日常口语，像普通人一样描述你的症状。不要用医学术语。\n"
                "(2) 你需要首先说出你的性别年龄以及来看病的原因。\n"
                "(3) 请严格遵守这条规定。在每次对话时，你都要分清对话对象是<医生>还是<检查员>。跟医生说话时用<对医生讲>开头，跟检查员说话时用<对检查员讲>开头。\n"
                "(4) 当医生问你的病史时，用简单的话回答，不要背诵病历。\n"
                "(5) 当医生要求你做任何检查时，你必须立即用以下格式向检查员询问结果：\n"
                "   <对检查员讲>医生让我做[检查名称]，能告诉我结果吗？\n"
                "(6) 从检查员那里得到结果后，你必须立即用以下格式告诉医生：\n"
                "   <对医生讲>#检查项目#\n- [检查名称]\n\n#检查结果#\n- [检查结果]\n"
                "(7) 请严格注意：当医生要求你进行医学检查时，不要只说'好的'或'我会去做'，必须立即执行上述第5条和第6条规则。否则你会收到惩罚。\n"
            )
        }
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        self.patient_message = []
        self.patient_message.append(self.system_message)
    def memory(self,patient_response=None,doctor_response=None,examiner_response=None):
        if patient_response is not None:
            self.patient_message.append({"role":"assistant","content":patient_response})
        if doctor_response is not None:
            self.patient_message.append({"role":"user","content":doctor_response})
        if examiner_response is not None:
            self.patient_message.append({"role":"user","content":examiner_response})

    def get_first_patient_response(self):  # 获取患者第一次回答，给到分诊医生,分诊医生分诊后，又给到医生
    # 添加初始消息，引导患者描述症状和来看病的原因
        initial_prompt = {
            "role": "user",
            "content": "请您用日常用语描述一下您的症状，告诉我来看病的原因。"
        }
        self.patient_message.append(initial_prompt)
        # print(self.patient_message)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.patient_message,
            temperature=0
        )
        self.memory(patient_response=response.choices[0].message.content)
        return response.choices[0].message.content
    
    def get_patient_response(self,doctor_response,examiner_info):  # 获取患者回答，给到医生
        try:
            self.memory(doctor_response=doctor_response)
        
            patient_response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.patient_message,
                temperature=0
            )
            patient_response_content = patient_response.choices[0].message.content if patient_response.choices else ""
        
            # 使用正则表达式匹配 "对检查员讲"
            if re.search(r"对检查员讲", patient_response_content):
                print(f"患者对检查员:{patient_response_content}")
                examiner = Examiner(examiner_info, self.api_key, self.api_base)
                examiner_response = examiner.get_response(patient_response_content)
                self.memory(examiner_response=examiner_response)
            
                # 获取最终回复
                final_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=self.patient_message,
                    temperature=0
                )
                patient_response_content = final_response.choices[0].message.content if final_response.choices else ""
                return patient_response_content, {}
            else:
                database_examiner = DatabaseExaminer(self.api_key, self.api_base)
                one_response_disease = database_examiner.get_response(patient_response_content)
                return patient_response_content, one_response_disease
        except Exception as e:
            print(f"Error occurred: {e}")
            return "", {}  # 返回空字符串和空字典作为默认值