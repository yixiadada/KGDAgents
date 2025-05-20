'''
    分诊医生
'''

from openai import OpenAI

class Nurse:
    def __init__(self,api_key,api_base,department_directory):
        self.model_name = "gpt-3.5-turbo"
        self.api_key = api_key
        self.api_base = api_base
        self.client = OpenAI(api_key=self.api_key,base_url=self.api_base)
        self.department_directory = department_directory
        self.nurse_system_message = {
            "role":"system",
            "content":(
                "You are a triage doctor in a hospital.Your task is to guide the patient to which department for treatment based on the patient's chief complaint."
                f"The following is the department directory:\n{self.department_directory}"
                "Please strictly select the department from the directory given to you.Please do not enter any text outside the directory."
            )
        }

    def get_response(self,patient_info):
        message = [self.nurse_system_message]
        # print(message)
        message.append({
            "role":"user",
            "content":(
                f"患者信息:\n{patient_info}"
                "Please recommend the clinic that the patient should go to based on the department directory."
                "Please only reply to the text in the department directory. Please do not enter any text outside the directory."
                )
            })
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=message,
            temperature=0
        )
        return response.choices[0].message.content
