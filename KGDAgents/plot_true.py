
import pandas as pd
import matplotlib.pyplot as plt
import re
import os

class HistoricalScorePlotter:
    def __init__(self):
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建图形
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        
    def extract_scores(self, text):
        """从评价结果文本中提取分数"""
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
        
        # 计算总分
        scores['total_score'] = sum(scores.values())
        scores['total_score'] = scores['total_score'] / 4
        return scores
    
    def process_csv_file(self, file_path):
        """处理CSV文件并提取所有分数"""
        df = pd.read_csv(file_path)
        all_scores = []
        
        for _, row in df.iterrows():
            scores = self.extract_scores(row['评价结果'])
            all_scores.append(scores)
            
        return pd.DataFrame(all_scores)
    
    def plot_scores(self, csv_file, output_dir):
        """绘制单个CSV文件的分数对比图"""
        df = self.process_csv_file(csv_file)
        x = range(1, len(df) + 1)
        
        # 绘制各维度的折线
        lines = [
            self.ax.plot(x, df['symptoms_score'], 'o-', label='症状评分', linewidth=2)[0],
            self.ax.plot(x, df['exam_score'], 's-', label='检查结果评分', linewidth=2)[0],
            self.ax.plot(x, df['diagnosis_score'], '^-', label='诊断结果评分', linewidth=2)[0],
            self.ax.plot(x, df['treatment_score'], 'D-', label='治疗建议评分', linewidth=2)[0]
        ]
        
        # 在最后一个点标注值
        last_x = x[-1]
        for line in lines:
            y_data = line.get_ydata()
            last_y = y_data[-1]
            self.ax.annotate(f'{last_y:.1f}', 
                            xy=(last_x, last_y),
                            xytext=(5, 5),
                            textcoords='offset points')
        
        # 计算累积平均分
        score_columns = ['symptoms_score', 'exam_score', 'diagnosis_score', 'treatment_score']
        cumulative_avg = []
        for i in range(len(df)):
            # 截取到当前位置的所有数据
            current_data = df.iloc[:i+1][score_columns]
            # 计算所有维度得分的总和除以维度数量
            avg = current_data.sum().sum() / (len(score_columns) * (i + 1))
            cumulative_avg.append(avg)
        
        # 绘制累积平均分
        self.ax.plot(x, cumulative_avg, '*-', label='累积平均分', linewidth=2)
        
        # 为累积平均分也添加标注
        last_avg = cumulative_avg[-1]
        self.ax.annotate(f'{last_avg:.1f}', 
                        xy=(last_x, last_avg),
                        xytext=(5, 5),
                        textcoords='offset points')
        
        # 设置图形属性
        self.ax.set_xlabel('病历数量')
        self.ax.set_ylabel('分数')
        self.ax.set_title('各维度评分随病历数量的变化')
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend(loc='best', bbox_to_anchor=(1.05, 1))
        self.ax.set_ylim(0, 100)
        
        # 调整布局以显示完整的图例
        plt.tight_layout()
        
        # 保存图片
        save_path = os.path.join(output_dir, 'historical_scores_comparison.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图片已保存至: {save_path}")
        
        # 保存数据
        data_path = os.path.join(output_dir, 'historical_scores_data.json')
        date = re.search(r'(\d{8})', csv_file).group(1)
        df = self.process_csv_file(csv_file)
        all_data = {date: df.to_dict('records')}
            
        import json
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)
        print(f"数据已保存至: {data_path}")
