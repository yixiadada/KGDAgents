from dataloader import dataload
from doctor.gpt_doctor import GPTDoctor
from doctor.evaluate_report import Evaluate_Agent
import re
from tqdm import tqdm
from plot_true import HistoricalScorePlotter
from save_to_csv import save_evaluation_to_csv,save_final_to_csv,create_output_dit
# from plot import plot_data


def main():
    data_address = ""
    data_name = ""
    doctor_model_name = ''
    doctor_api_key = ''    
    doctor_api_base = ''
    patient_api_key = ''  
    patient_api_base = ''
    eva_openai_api_key = ''
    eva_openai_api_base = ''
    output_dir = ""
    data = dataload(data_address)
    red_color = '\033[31m'
    init_color = '\033[0m'
    num = 1
    model_name = re.compile(r'gpt-3.5-turbo|gpt-4|gpt-3.5-turbo-1106|qwen-max|qwen-turbo')
    if model_name.search(doctor_model_name):
        #  plotter = ScorePlotter()  # 创建初始图表
        for line_data in tqdm(data,desc="processing patients"):  # 每条病历
            doctor = GPTDoctor(doctor_model_name,doctor_api_key,doctor_api_base)
            report = doctor.interact_with_patient(line_data,patient_api_key,patient_api_base)
            print(f"{red_color}第{num}个患者诊断报告:{init_color}{report}")
            report_sava_path = save_final_to_csv(report,output_dir,doctor_model_name,num,data_name)
            print(f"{red_color}诊断报告已保存到:{init_color}{report_sava_path}")

            # 评估诊断报告
            evaluate_agent = Evaluate_Agent(eva_openai_api_key,eva_openai_api_base)
            score,evaluate_text = evaluate_agent.get_response(line_data,report)
            print(f"{red_color}第{num}个患者诊断报告评估分数:{init_color}{score}")
            print("--------------------------------------")
            print(f"{red_color}第{num}个患者诊断报告评估结果:{init_color}{evaluate_text}")
            evaluation_sava_path = save_evaluation_to_csv(evaluate_text,output_dir,doctor_model_name,num,data_name)
            print(f"{red_color}评估报告已保存到:{init_color}{evaluation_sava_path}")
            num += 1
        # 保存最终图表
        # plotter.save_plot("final_scores_plot.png",output_dir,doctor_model_name)
        # 绘图
        csv_file_path = evaluation_sava_path
        image_path = create_output_dit(output_dir,doctor_model_name,data_name)
        plotter = HistoricalScorePlotter()
        plotter.plot_scores(csv_file_path,image_path)






if __name__ == "__main__":
    main()
