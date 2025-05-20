

from openai import OpenAI
import re

class Generate_diagnostic_report:
    def __init__(self,report_system_message_A,report_system_message_B,medical_history,patient_description,api_key,api_base,model_name):
        self.report_system_message_A = report_system_message_A
        self.report_system_message_B = report_system_message_B
        self.medical_history = medical_history  # 既往史
        self.patient_description = patient_description  # 患者描述
        self.api_key = api_key
        self.api_base = api_base
        self.model_name = model_name
        self.doctor_A_memory = []
        self.doctor_A_memory.append(self.report_system_message_A)
        self.doctor_B_memory = []
        self.doctor_B_memory.append(self.report_system_message_B)
        self.red_color = '\033[31m'
        self.init_color = '\033[0m'
    def message_append(message,content,role):  # 添加历史消息
        messages = list(message)
        messages.append({"role":"user","content":f"{role}:{content}"})
        return messages
    
    def add_doctor_A_memory(self,paitent_message=None,doctor_a_message=None,doctor_b_message=None,turn=None):
        if paitent_message != None:
            self.doctor_A_memory.append(paitent_message)
        if doctor_a_message != None:
            self.doctor_A_memory.append({"role":"assistant", "content":f"医生C:{doctor_a_message}\n当前回合:{turn}"})
        if doctor_b_message != None:
            self.doctor_A_memory.append({"role":"user", "content":f"医生D:{doctor_a_message}"})

    def add_doctor_B_memory(self,paitent_message=None,doctor_a_message=None,doctor_b_message=None):
        if paitent_message != None:
            self.doctor_B_memory.append(paitent_message)
        if doctor_a_message != None:
            self.doctor_B_memory.append({"role":"user", "content":f"医生C:{doctor_a_message}"})
        if doctor_b_message != None:
            self.doctor_B_memory.append({"role":"assistant", "content":f"医生D:{doctor_a_message}"})
    def get_a_response(self):  # 获取医生A的响应
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base

        )
        response = client.chat.completions.create(
            model=self.model_name,
            messages=self.doctor_A_memory,
            temperature=0
        )
        return response.choices[0].message.content
    
    def get_b_response(self):  # 获取医生B的响应
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base

        )
        response = client.chat.completions.create(
            model=self.model_name,
            messages=self.doctor_B_memory,
            temperature=0
        )
        return response.choices[0].message.content
    
    def Generate_symptom_report(self,all_diseases):  # 生成症状报告
        patient_symptom_A = {
            "role":"user",
            "content":(
            f"患者信息：{self.medical_history}\n"
            f"患者描述：{self.patient_description}\n"
            f"可能的疾病:{all_diseases}\n"
            f"现在请根据要求,与医生D进行对话,最终目标是生成患者的诊断报告."
            )
        }
        patient_symptom_B = {
            "role":"user",
            "content":(
            f"患者信息：{self.medical_history}\n"
            f"患者描述：{self.patient_description}\n"
            f"可能的疾病:{all_diseases}\n"
            f"现在请根据要求,与医生C进行对话."
            )
        }
        self.add_doctor_A_memory(paitent_message=patient_symptom_A)
        self.add_doctor_B_memory(paitent_message=patient_symptom_B)
        doctor_a_response = self.get_a_response()
        self.add_doctor_A_memory(doctor_a_message=doctor_a_response)
        self.add_doctor_B_memory(doctor_a_message=doctor_a_response)
        turn = 1
        print(f"{self.red_color}生成诊断报告:{self.init_color}")
        finish_content = re.compile(r'会话结束|再见')
        while finish_content.search(doctor_a_response) == None:
            
            print(f"{self.red_color}当前轮次:{turn}{self.init_color}")
            print(f"{self.red_color}医生C:{self.init_color}{doctor_a_response}")
            doctor_b_response = self.get_b_response()
            self.add_doctor_A_memory(doctor_b_message=doctor_b_response,turn=turn)
            self.add_doctor_B_memory(doctor_b_message=doctor_b_response)
            print(f"{self.red_color}医生D:{self.init_color}{doctor_b_response}")
            doctor_a_response = self.get_a_response()
            self.add_doctor_A_memory(doctor_a_message=doctor_a_response)
            self.add_doctor_B_memory(doctor_a_message=doctor_a_response)
            if turn == 6:
                break
            turn += 1
        # print(f"{self.red_color}症状报告:{self.init_color}{doctor_a_response}")
        return doctor_a_response


    def Generate_report(self,all_disease,physical_examination):  # 生成报告
        self.doctor_A_memory = []
        self.doctor_A_memory.append(self.report_system_message_A)
        self.doctor_A_memory.append({"role":"user", "content":f"查体结果:{physical_examination}"})
        self.doctor_B_memory = []
        self.doctor_B_memory.append(self.report_system_message_B)
        symptom_report = self.Generate_symptom_report(all_diseases=all_disease)
        report = symptom_report
        return report



