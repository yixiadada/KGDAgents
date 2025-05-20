# 保存ABCD四个报告和它们的得分到csv文件中
import pandas as pd
import os
from datetime import datetime

num = 1
evaluation_num = 1
def create_output_dit(output_dir,model_name,data_name):
    current_time = datetime.now().strftime('%Y%m%d')
    output_dir = output_dir + '/' + f"output_{current_time}_{model_name}_{data_name}"
    return output_dir

def save_all_to_csv(report_A,report_B,report_C,report_D,report_total_A,report_total_B,report_total_C,report_total_D,output_dir,model_name):
    """
    保存报告内容和分数到CSV文件
    
    Args:
        report_A, report_B, report_C, report_D: 四份报告的内容
        report_total_list: 包含四份报告得分的列表
        output_dir: 输出目录，默认为'comparison_results'
        
    Returns:
        str: 保存的CSV文件路径
    """
    output_dir = create_output_dit(output_dir,model_name)
    global num # 全局变量
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取当前时间并格式化
    current_time = datetime.now().strftime('%Y%m%d')  # 只取年月和日

    # 准备数据
    if report_C is None:
        data = {    
            '序号':num,
            '报告A内容': [report_A],
            'A症状分数': [report_total_A['症状分数']],
            'A检查结果分数': [report_total_A['检查结果分数']],
            'A诊断结果分数': [report_total_A['诊断结果分数']],
            'A治疗建议分数': [report_total_A['治疗建议分数']],
            'A总分': [report_total_A['总分']],

            '报告B内容': [report_B],
            'B症状分数': [report_total_B['症状分数']],
            'B检查结果分数': [report_total_B['检查结果分数']],
            'B诊断结果分数': [report_total_B['诊断结果分数']],
            'B治疗建议分数': [report_total_B['治疗建议分数']],
            'B总分': [report_total_B['总分']]
        }
    else:
        data = {
            '序号':num,
            '报告A内容': [report_A],
            'A症状分数': [report_total_A['症状分数']],
            'A检查结果分数': [report_total_A['检查结果分数']],
            'A诊断结果分数': [report_total_A['诊断结果分数']],
            'A治疗建议分数': [report_total_A['治疗建议分数']],
            'A总分': [report_total_A['总分']],
            
            '报告B内容': [report_B],
            'B症状分数': [report_total_B['症状分数']],
            'B检查结果分数': [report_total_B['检查结果分数']],
            'B诊断结果分数': [report_total_B['诊断结果分数']],
            'B治疗建议分数': [report_total_B['治疗建议分数']],
            'B总分': [report_total_B['总分']],
            
            '报告C内容': [report_C],
            'C症状分数': [report_total_C['症状分数']],
            'C检查结果分数': [report_total_C['检查结果分数']],
            'C诊断结果分数': [report_total_C['诊断结果分数']],
            'C治疗建议分数': [report_total_C['治疗建议分数']],
            'C总分': [report_total_C['总分']],
            
            '报告D内容': [report_D],
            'D症状分数': [report_total_D['症状分数']],
            'D检查结果分数': [report_total_D['检查结果分数']],
            'D诊断结果分数': [report_total_D['诊断结果分数']],
            'D治疗建议分数': [report_total_D['治疗建议分数']],
            'D总分': [report_total_D['总分']]
        }

    # 创建DataFrame并保存
    df = pd.DataFrame(data)
    # 如果文件不存在，创建新文件并写入表头
    csv_all_path = os.path.join(output_dir, f'reports_and_scores_{current_time}_{model_name}.csv')
    if not os.path.exists(csv_all_path):
        df.to_csv(csv_all_path, index=False, encoding='utf-8-sig')
    else:
        # 如果文件已存在，追加数据不写入表头
        df.to_csv(csv_all_path, mode='a', header=False, index=False, encoding='utf-8-sig')
    num += 1
    return csv_all_path

def save_final_to_csv(final_report,output_dir,model_name,final_num,data_name):
    # 保存最终报告到csv文件中
    output_dir = create_output_dit(output_dir,model_name,data_name)
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
     # 获取当前时间并格式化
    current_time = datetime.now().strftime('%Y%m%d')
    data = {
        '序号':final_num,
        '最终报告':[final_report]
    }
    df = pd.DataFrame(data)
    csv_final_path = os.path.join(output_dir, f'final_report_{current_time}_{model_name}.csv')
    if not os.path.exists(csv_final_path):
        df.to_csv(csv_final_path, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(csv_final_path, mode='a', header=False, index=False, encoding='utf-8-sig')  # a表示追加,不覆盖原文件,header=False表示不重复写表头
    final_num += 1
    return csv_final_path

def save_evaluation_to_csv(evaluation,output_dir,model_name,evaluation_num,data_name):   
    '''
    保存评价结果到csv文件中
    '''
    # 获取当前时间并格式化
    current_time = datetime.now().strftime('%Y%m%d')
    output_dir = create_output_dit(output_dir,model_name,data_name)
    # print(f"output_dir: {output_dir}")
    # 添加以下代码来创建目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    
    data = {
        '序号':evaluation_num,
        '评价结果':[evaluation]
    }
    df = pd.DataFrame(data)
    csv_evaluation_path = os.path.join(output_dir, f'evaluation_results_{current_time}_{model_name}.csv')
    if not os.path.exists(csv_evaluation_path):
        df.to_csv(csv_evaluation_path, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(csv_evaluation_path, mode='a', header=False, index=False, encoding='utf-8-sig')  # a表示追加,不覆盖原文件,header=False表示不重复写表头
    evaluation_num += 1
    return csv_evaluation_path

