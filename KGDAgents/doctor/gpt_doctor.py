'''
GPT医生
'''
from openai import OpenAI
from tenacity import retry,stop_after_attempt,wait_fixed,retry_if_exception_type
import os
from .Main_Doctor import Doctor
from .nurse import Nurse  # 分诊医生
from patient.patient import Patient
from .create_report import Generate_diagnostic_report
import re

class GPTDoctor(Doctor):
    def __init__(self, doctor_name,doctor_api_key,doctor_api_base):
        super().__init__()
        self.doctor_name = doctor_name
        self.doctor_api_key = doctor_api_key
        self.doctor_api_base = doctor_api_base
        self.temperature = 0.0
        self.client = OpenAI(
            api_key=self.doctor_api_key, base_url=self.doctor_api_base
        )
        self.turn = 1  # 医患交流轮次
        self.MAX_TURNS = 10
        self.doctor_A_memory = []  # 医生A的记忆
        self.doctor_B_memory = []  # 医生B的记忆
        self.report_memory = []   # 给生成诊断报告医生的记录
        self.all_diseases = {}  # 所有疾病
        self.red_color = '\033[31m'
        self.init_color = '\033[0m'

    def memory_doctor_A(self,patient_response=None,doctor_A_response=None,doctor_B_response=None,system_messsage=None):
        if patient_response is not None:
            self.doctor_A_memory.append({"role":"user","content":f"患者:{patient_response}"})
            self.report_memory.append({"role":"user","content":f"患者:{patient_response}"})
        elif doctor_A_response is not None:
            self.doctor_A_memory.append({"role":"assistant","content":f"医生A:{doctor_A_response}"})
            self.report_memory.append({"role":"assistant","content":f"医生A:{doctor_A_response}"})
        elif doctor_B_response is not None:
            self.doctor_A_memory.append({"role":"user","content":f"医生B:{doctor_B_response}"})
            self.report_memory.append({"role":"user","content":f"医生B:{doctor_B_response}"})
        elif system_messsage is not None:
            self.doctor_A_memory.append({"role":"system","content":f"查体结果:{system_messsage}"})
            self.report_memory.append({"role":"system","content":f"查体结果:{system_messsage}"})
    
    def memory_doctor_B(self,patient_response=None,doctor_A_response=None,doctor_B_response=None):  # 医生B的记忆
        if patient_response is not None:
            self.doctor_B_memory.append({"role":"user","content":f"患者:{patient_response}"})
        elif doctor_A_response is not None:
            self.doctor_B_memory.append({"role":"user","content":f"医生A:{doctor_A_response}"})
        elif doctor_B_response is not None:
            self.doctor_B_memory.append({"role":"assistant","content":f"医生B:{doctor_B_response}"})
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
    def get_A_response(self):
        response = self.client.chat.completions.create(
            model=self.doctor_name,
            messages=self.doctor_A_memory,
            temperature=0
        )
        return response.choices[0].message.content
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
    def get_B_response(self):
        response = self.client.chat.completions.create(
            model=self.doctor_name,
            messages=self.doctor_B_memory,
            temperature=0
        )
        return response.choices[0].message.content
    
    def interact_with_patient(self,line_data,patient_api_key,patient_api_base):
        # 从环境变量中获取敏感信息
        api_key = self.doctor_api_key or os.getenv('API_KEY')
        api_base = self.doctor_api_base or os.getenv('API_BASE')

        # 记忆清空
        self.all_diseases = {}
        self.doctor_A_memory = []
        self.doctor_B_memory = []
        self.report_memory = []

        # 分割数据
        patient_info = line_data['symptom']
        examine = line_data['examine']
        if '体格检查' in examine:
            physical_examination = examine['体格检查']
        elif '查体' in examine:
            physical_examination = examine['查体']
        self.memory_doctor_A(system_messsage=physical_examination)
        medical_history = patient_info['既往史']

        # 分诊
        department_directory = ["内科", "外科", "妇产科", "儿科", "眼科", "耳鼻喉科", "皮肤科", "神经科", "牙科", "急诊科"]
        department_mapping = {dept: dept for dept in department_directory}
        department_mapping["其他"] = "其他"

        patient = Patient(patient_info, api_key=patient_api_key, api_base=patient_api_base)
        print("您好，请问您哪里不舒服呢？")
        try:
            first_patient_response = patient.get_first_patient_response()
        except Exception as e:
            print(f"Error getting first patient response: {e}")
            return

        print(f"{self.red_color}患者描述：{self.init_color}{first_patient_response}")
        nurse = Nurse(api_key=patient_api_key, api_base=patient_api_base, department_directory=department_directory)
        try:
            nurse_response = nurse.get_response(first_patient_response)
        except Exception as e:
            print(f"Error getting nurse response: {e}")
            return

        print(f"{self.red_color}分诊医生：{self.init_color}我推荐你去{nurse_response}就诊")

        specialty = department_mapping.get(nurse_response, "其他")

        doctor_a_message, doctor_b_message, report_system_message_A, report_system_message_B = Doctor.generate_doctor_prompt(specialty, medical_history)
        self.doctor_A_memory.append(doctor_a_message)
        self.doctor_B_memory.append(doctor_b_message)
        self.memory_doctor_A(patient_response=first_patient_response)
        self.memory_doctor_B(patient_response=first_patient_response)
        print("您好，我是您的主治医生，请告诉我您哪里不舒服。")
        

        # 缓存正则表达式
        pattern_doctor_b = re.compile(r'对医生B说|有什么意见|医生B')
        finish_pattern = re.compile(r'会话结束|<会话结束>|<再见>|再见|祝您')
        print("当前轮次：", self.turn)
        print(f"{self.red_color}患者主诉:{self.init_color}{first_patient_response}")
        try:
            doctor_a_response = self.get_A_response()  # 医生A的回答
        except Exception as e:
            print(f"Error getting doctor A response: {e}")
        print(f"{self.red_color}医生A回复:{self.init_color}{doctor_a_response}")
        self.memory_doctor_A(doctor_A_response=doctor_a_response)
        self.turn += 1
        # 医患交流
        while True:
            print("当前轮次：", self.turn)
            try:
                patient_response, one_turn_disease = patient.get_patient_response(doctor_response=doctor_a_response, examiner_info=examine)
            except Exception as e:
                print(f"Error getting patient response: {e}")
                break
            print(f"{self.red_color}患者回复:{self.init_color}{patient_response}")
            self.memory_doctor_A(patient_response=patient_response)
            self.memory_doctor_B(patient_response=patient_response)

            try:
                doctor_a_response = self.get_A_response()  # 医生A的回答
            except Exception as e:
                print(f"Error getting doctor A response: {e}")
                break

            print(f"{self.red_color}医生A回复:{self.init_color}{doctor_a_response}")
            self.memory_doctor_A(doctor_A_response=doctor_a_response)

            if pattern_doctor_b.search(doctor_a_response):  # 医生A需要医生B的意见
                try:
                    doctor_b_response = self.get_B_response()  # 医生B的回答
                except Exception as e:
                    print(f"Error getting doctor B response: {e}")
                    break

                print(f"{self.red_color}医生B回复:{self.init_color}{doctor_b_response}")
                self.memory_doctor_B()
                self.memory_doctor_A(doctor_B_response=doctor_b_response)

                try:
                    doctor_a_response = self.get_A_response()
                except Exception as e:
                    print(f"Error getting doctor A response: {e}")
                    break

                print(f"{self.red_color}医生A回复:{self.init_color}{doctor_a_response}")
                self.memory_doctor_A(doctor_A_response=doctor_a_response)
            if one_turn_disease:  # 如果检索到的疾病非空
                for disease, count in one_turn_disease.items():
                    if disease in self.all_diseases:
                        self.all_diseases[disease] += count
                    else:
                        self.all_diseases[disease] = count
            if finish_pattern.search(doctor_a_response):
                break
            if self.turn > self.MAX_TURNS:
                break
            self.turn += 1

            

        self.all_diseases = dict(sorted(self.all_diseases.items(), key=lambda item: item[1], reverse=True))  # 按出现次数排序
        print(f"所有对话中所有症状共有的疾病：{self.all_diseases}")
        print(f"会话结束，当前轮次：{self.turn}")  # 医患对话结束，生成诊断报告

        report_agent = Generate_diagnostic_report(
            report_system_message_A=report_system_message_A,
            report_system_message_B=report_system_message_B,
            medical_history=medical_history,
            patient_description=self.report_memory,
            api_key=api_key,
            api_base=api_base,
            model_name=self.doctor_name
        )
        five_disease = list(self.all_diseases.keys())[:5]
        report = report_agent.Generate_report(five_disease,physical_examination)
        print(report)
        return report
    

 