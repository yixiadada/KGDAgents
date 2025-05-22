'''
评估诊断报告
'''

from openai import OpenAI
import re

class Evaluate_Agent:
    def __init__(self,openai_api_key,openai_api_base):
        self.client = OpenAI(
            api_key=openai_api_key,
            base_url=openai_api_base
        )
        
        self.system_message = {
            "role":"system",
            "content":
           '''
            您是一位资深的医学专家。
            现在，您将获得患者的病历和其他医生的诊断报告。您的任务是根据患者的病历，评估其他医生的诊断报告。为此，您需要按照以下要求完成任务：
            诊断报告包含四个部分，分别对应患者病历的四个部分。请逐一评估这四个部分，并为每部分打分。评分标准如下：
                "- 第一档，当诊断报告与病历中对应信息完全不同时，需要从0-25中选择一个数字。\n"
                "- 第二档，当诊断报告与病历中对应信息部分一致时，需在26-50中选择一个数字。\n"
                "- 第三档，当诊断报告与病历中对应信息有部分差异时，需在51-75中选择一个数字。\n"
                "- 第四档，当诊断报告与病历中对应信息完全一致时，需要从76-100中选择一个不数字。\n"
            在症状中，病历中有1-2个症状没有在诊断报告中表述，则应属于第三档；当有3-4个症状没有在诊断报告中表述，则应属于第二档；有更多症状没有表述，则应属于第一档。
            在相关检查结果中，病历中有1个医学检查项目没有在诊断报告中表述，则应属于第三档；当有2个症状没有在诊断报告中表述，则应属于第二档；有更多症状没有表述，则应属于第一档。
            在诊断结果中，病历中有1个结果没有在诊断报告中表述，则应属于第三档；当有2个症状没有在诊断报告中表述，则应属于第二档；有更多症状没有表述，则应属于第一档。
            在治疗建议中，评判治疗建议与病历中的治疗经过是否相符，不要求完全一致，诊断报告中说出一些治疗方式与病历中的治疗过程相似即可。
            请确保每个维度的评估清晰、准确，并根据实际情况给予合适的分数。
            评分完成后，请严格按照以下格式输出每部分的评估结果，并附上您的评估理由和具体分数：
            ###症状###
            评估理由：xx
            分数：xx
            ###相关检查结果###
            评估理由：xx
            分数：xx
            ###诊断结果###
            评估理由：xx
            分数：xx
            ###治疗建议###
            评估理由：xx
            分数：xx
            请确保每个部分的评估清晰、准确，并根据实际情况给予合适的分数。
            '''
        }
    #从评估文本中提取各个维度的分数
    def extract_scores(self,text):
        """
        从评估文本中提取各个维度的分数
        """
        patterns = {
        'symptoms': r'[#]+\s*症状.*[#]*[\s\S]*?分数[:：]?(\d+)',
        'exam': r'[#]+\s*相关检查.*[#]*[\s\S]*?分数[:：]?(\d+)',
        'diagnosis': r'[#]+\s*诊断.*[#]*[\s\S]*?分数[:：]?(\d+)',
        'treatment': r'[#]+\s*治疗.*[#]*[\s\S]*?分数[:：]?(\d+)'
        }
        scores = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                scores[f'{key}_score'] = int(match.group(1))
            else:
                print(f"No match found for {key} in the following text:")
                print(text)
                print("Pattern used:", pattern)
    
        return scores

    def get_response(self,medical_record,report):
        messages = []
        messages = [self.system_message]
        messages.append({"role":"user","content":f"原始病历{medical_record}"})
        messages.append({"role":"user","content":f"诊断报告{report}"})
    
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        response_text = response.choices[0].message.content
        score = self.extract_scores(response_text)
        return score,response_text


