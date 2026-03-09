"""
应力场数据分析工具
用于后处理和进一步分析生成的应力场数据
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib
matplotlib.use('Agg')


class StressAnalyzer:
    """应力场数据分析器"""
    
    def __init__(self, statistics_csv):
        """
        初始化分析器
        
        Args:
            statistics_csv: stress_statistics.csv 文件路径
        """
        self.df = pd.read_csv(statistics_csv)
        print(f"✅ 加载统计数据: {statistics_csv}")
        print(f"   数据行数: {len(self.df)}")
        print(f"   数据列数: {len(self.df.columns)}\n")
    
    def plot_stress_distribution(self, output_file='stress_distribution.png'):
        """绘制应力分布直方图"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('全样本应力分布统计', fontsize=14, fontweight='bold')
        
        # von Mises应力分布
        axes[0, 0].hist(self.df['s_mises_mean'], bins=50, color='blue', alpha=0.7)
        axes[0, 0].set_title('平均von Mises应力分布')
        axes[0, 0].set_xlabel('应力 (Pa)')
        axes[0, 0].set_ylabel('频数')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 最大应力分布
        axes[0, 1].hist(self.df['s_mises_max'], bins=50, color='red', alpha=0.7)
        axes[0, 1].set_title('最大von Mises应力分布')
        axes[0, 1].set_xlabel('应力 (Pa)')
        axes[0, 1].set_ylabel('频数')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 正应力σxx分布
        axes[1, 0].hist(self.df['sxx_mean'], bins=50, color='green', alpha=0.7)
        axes[1, 0].set_title('平均正应力σxx分布')
        axes[1, 0].set_xlabel('应力 (Pa)')
        axes[1, 0].set_ylabel('频数')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 正应力σyy分布
        axes[1, 1].hist(self.df['syy_mean'], bins=50, color='orange', alpha=0.7)
        axes[1, 1].set_title('平均正应力σyy分布')
        axes[1, 1].set_xlabel('应力 (Pa)')
        axes[1, 1].set_ylabel('频数')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✅ 分布图已保存: {output_file}\n")
    
    def plot_stress_evolution(self, output_file='stress_evolution.png'):
        """绘制应力随CT层数的演化"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('应���沿CT深度的演化', fontsize=14, fontweight='bold')
        
        x = np.arange(len(self.df))
        
        # von Mises应力演化
        axes[0, 0].plot(x, self.df['s_mises_mean'], label='平均值', linewidth=2, color='blue')
        axes[0, 0].fill_between(x, self.df['s_mises_min'], self.df['s_mises_max'], 
                               alpha=0.3, color='blue', label='最大-最小范围')
        axes[0, 0].set_title('von Mises应力演化')
        axes[0, 0].set_xlabel('CT切片序号')
        axes[0, 0].set_ylabel('应力 (Pa)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # σxx应力演化
        axes[0, 1].plot(x, self.df['sxx_mean'], label='平均值', linewidth=2, color='green')
        axes[0, 1].fill_between(x, self.df['sxx_min'], self.df['sxx_max'], 
                               alpha=0.3, color='green')
        axes[0, 1].set_title('正应力σxx演化')
        axes[0, 1].set_xlabel('CT切片序号')
        axes[0, 1].set_ylabel('应力 (Pa)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # σyy应力演化
        axes[1, 0].plot(x, self.df['syy_mean'], label='平均值', linewidth=2, color='orange')
        axes[1, 0].fill_between(x, self.df['syy_min'], self.df['syy_max'], 
                               alpha=0.3, color='orange')
        axes[1, 0].set_title('正应力σyy演化')
        axes[1, 0].set_xlabel('CT切片序号')
        axes[1, 0].set_ylabel('应力 (Pa)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 应力范围演化
        stress_range = self.df['s_mises_max'] - self.df['s_mises_min']
        axes[1, 1].plot(x, stress_range, linewidth=2, color='red', label='应力范围')
        axes[1, 1].fill_between(x, 0, stress_range, alpha=0.3, color='red')
        axes[1, 1].set_title('应力范围(max-min)演化')
        axes[1, 1].set_xlabel('CT切片序号')
        axes[1, 1].set_ylabel('应力差 (Pa)')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✅ 演化图已保存: {output_file}\n")
    
    def identify_critical_regions(self, percentile=90, output_file='critical_regions.csv'):
        """
        识别高应力区域
        
        Args:
            percentile: 百分位数阈值（默认90%表示应力最高的10%）
            output_file: 输出CSV文件
        """
        threshold = np.percentile(self.df['s_mises_max'], percentile)
        critical = self.df[self.df['s_mises_max'] >= threshold].copy()
        critical = critical.sort_values('s_mises_max', ascending=False)
        
        critical.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"🔴 高应力区域识别 (百分位数 > {percentile}%)")
        print(f"{'='*60}")
        print(f"应力阈值: {threshold:.2e} Pa")
        print(f"识别区域数: {len(critical)}/{len(self.df)}")
        print(f"结果已保存: {output_file}\n")
        
        print("前10个高应力区域:")
        print(critical[['file_name', 's_mises_mean', 's_mises_max']].head(10).to_string())
        print()
        
        return critical
    
    def generate_summary_report(self, output_file='stress_analysis_report.txt'):
        """生成分析报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("应力场分析报告\n")
            f.write("="*60 + "\n\n")
            
            f.write("1. 数据概览\n")
            f.write("-"*60 + "\n")
            f.write(f"总样本数: {len(self.df)}\n")
            f.write(f"数据列数: {len(self.df.columns)}\n\n")
            
            f.write("2. von Mises应力统计\n")
            f.write("-"*60 + "\n")
            f.write(f"平均值的平均: {self.df['s_mises_mean'].mean():.2e} Pa\n")
            f.write(f"平均值的标准差: {self.df['s_mises_mean'].std():.2e} Pa\n")
            f.write(f"全局最大应力: {self.df['s_mises_max'].max():.2e} Pa\n")
            f.write(f"全局最小应力: {self.df['s_mises_min'].min():.2e} Pa\n")
            f.write(f"应力变化范围: {self.df['s_mises_max'].max() - self.df['s_mises_min'].min():.2e} Pa\n\n")
            
            f.write("3. 正应力σxx统计\n")
            f.write("-"*60 + "\n")
            f.write(f"平均值的平均: {self.df['sxx_mean'].mean():.2e} Pa\n")
            f.write(f"最大值的平均: {self.df['sxx_max'].mean():.2e} Pa\n")
            f.write(f"最小值的平均: {self.df['sxx_min'].mean():.2e} Pa\n\n")
            
            f.write("4. 正应力σyy统计\n")
            f.write("-"*60 + "\n")
            f.write(f"平均值的平均: {self.df['syy_mean'].mean():.2e} Pa\n")
            f.write(f"最大值的平均: {self.df['syy_max'].mean():.2e} Pa\n")
            f.write(f"最小值的平均: {self.df['syy_min'].mean():.2e} Pa\n\n")
            
            f.write("5. 高应力区域识别\n")
            f.write("-"*60 + "\n")
            threshold_90 = np.percentile(self.df['s_mises_max'], 90)
            high_stress = self.df[self.df['s_mises_max'] >= threshold_90]
            f.write(f"90%分位数阈值: {threshold_90:.2e} Pa\n")
            f.write(f"超过阈值的样本: {len(high_stress)} 个\n")
            f.write(f"所占比例: {100*len(high_stress)/len(self.df):.1f}%\n\n")
            
            f.write("6. 关键统计信息\n")
            f.write("-"*60 + "\n")
            f.write(self.df.describe().to_string())
        
        print(f"✅ 分析报告已保存: {output_file}\n")


if __name__ == "__main__":
    # 使用示例
    analyzer = StressAnalyzer('./stress_output/stress_statistics.csv')
    
    # 生成各类分析图表
    analyzer.plot_stress_distribution(output_file='./stress_output/stress_distribution.png')
    analyzer.plot_stress_evolution(output_file='./stress_output/stress_evolution.png')
    
    # 识别高应力区域
    critical = analyzer.identify_critical_regions(
        percentile=90,
        output_file='./stress_output/critical_regions.csv'
    )
    
    # 生成总结报告
    analyzer.generate_summary_report(
        output_file='./stress_output/analysis_report.txt'
    )