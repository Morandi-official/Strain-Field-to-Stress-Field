"""
批量处理1000张CT - 严格对标文献版本
"""

from pathlib import Path
from dic_bts_strict_converter import DICBTSStrictConverter
import pandas as pd
import numpy as np


def batch_process_all_files_strict():
    """批量处理所有文件 - 严格版本"""
    
    print("\n" + "="*70)
    print(" "*10 + "DIC-BTS严格对标文献批量处理系统")
    print(" "*5 + "处理1000张CT，完整实现所有文献公式")
    print("="*70 + "\n")
    
    # 参数配置
    E = 5e10
    nu = 0.25
    D = 50.0
    t = 25.0
    
    input_dir = './strain_data'
    output_dir = './DIC_BTS_strict_batch_output'
    
    # 创建转换器
    converter = DICBTSStrictConverter(E, nu, D, t)
    
    # 获取所有Excel文件
    input_path = Path(input_dir)
    excel_files = sorted(input_path.glob('*.xlsx'))
    
    total_files = len(excel_files)
    print(f"找到 {total_files} 个Excel文件\n")
    print("="*70 + "\n")
    
    summary_results = []
    failed_files = []
    
    # 批量处理
    for file_idx, excel_file in enumerate(excel_files, 1):
        try:
            # 处理单个文件
            results_df = converter.process_dic_excel_strict(str(excel_file), output_dir)
            
            # 统计
            if len(results_df) > 0:
                # 计数Griffith准则分支
                branch1_count = (results_df['griffith_condition'] >= 0).sum()
                branch2_count = (results_df['griffith_condition'] < 0).sum()
                
                summary_results.append({
                    'file_name': excel_file.name,
                    'num_points': len(results_df),
                    # 三种方法的σt
                    'sigma_t_const_mean': results_df['sigma_t_const'].mean(),
                    'sigma_t_kirsch_mean': results_df['sigma_t_kirsch'].mean(),
                    'sigma_t_hondros_mean': results_df['sigma_t_hondros'].mean(),
                    # 应力范围
                    'sigma_yy_const_max': results_df['sigma_yy_const'].max(),
                    'sigma_yy_kirsch_max': results_df['sigma_yy_kirsch'].max(),
                    'sigma_yy_hondros_max': results_df['sigma_yy_hondros'].max(),
                    # Griffith准则分支统计
                    'griffith_branch1_count': branch1_count,
                    'griffith_branch1_percent': 100*branch1_count/len(results_df),
                    'griffith_branch2_count': branch2_count,
                    'griffith_branch2_percent': 100*branch2_count/len(results_df),
                    # 方法差异
                    'diff_const_kirsch_xx': (results_df['sigma_xx_const'] - results_df['sigma_xx_kirsch']).abs().mean(),
                    'diff_const_kirsch_yy': (results_df['sigma_yy_const'] - results_df['sigma_yy_kirsch']).abs().mean(),
                    'diff_kirsch_hondros_xx': (results_df['sigma_xx_kirsch'] - results_df['sigma_xx_hondros']).abs().mean(),
                    'diff_kirsch_hondros_yy': (results_df['sigma_yy_kirsch'] - results_df['sigma_yy_hondros']).abs().mean(),
                })
            
            # 显示进度
            if file_idx % max(1, total_files // 10) == 0 or file_idx == total_files:
                progress = 100 * file_idx / total_files
                print(f"进度: {progress:6.1f}% ({file_idx:4d}/{total_files})")
        
        except Exception as e:
            print(f"❌ 处理 {excel_file.name} 出错: {e}")
            failed_files.append(excel_file.name)
            continue
    
    # 保存汇总
    summary_df = pd.DataFrame(summary_results)
    summary_file = Path(output_dir) / 'DIC_BTS_strict_summary.csv'
    summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
    
    print(f"\n" + "="*70)
    print(f"✅ 批量处理完成！")
    print(f"="*70)
    print(f"✓ 成功处理: {len(summary_results)} 个文件")
    print(f"✗ 失败文件: {len(failed_files)} 个")
    print(f"✓ 汇总文件: {summary_file}\n")
    
    # 统计输出
    if len(summary_df) > 0:
        print("【全局统计】")
        print("-"*70)
        
        print(f"\n【抗拉强度 σt 统计】")
        print(f"本构关系：")
        print(f"  平均值: {summary_df['sigma_t_const_mean'].mean():.3f} MPa")
        print(f"  标准差: {summary_df['sigma_t_const_mean'].std():.3f} MPa")
        print(f"\nKirsch理论：")
        print(f"  平均值: {summary_df['sigma_t_kirsch_mean'].mean():.3f} MPa")
        print(f"  标准差: {summary_df['sigma_t_kirsch_mean'].std():.3f} MPa")
        print(f"\nHondros理论：")
        print(f"  平均值: {summary_df['sigma_t_hondros_mean'].mean():.3f} MPa")
        print(f"  标准差: {summary_df['sigma_t_hondros_mean'].std():.3f} MPa")
        
        print(f"\n【Griffith破坏准则统计】")
        total_branch1 = summary_df['griffith_branch1_count'].sum()
        total_branch2 = summary_df['griffith_branch2_count'].sum()
        total_points = total_branch1 + total_branch2
        print(f"  第一分支：{total_branch1} 个点 ({100*total_branch1/total_points:.1f}%)")
        print(f"  第二分支：{total_branch2} 个点 ({100*total_branch2/total_points:.1f}%)")
        
        print(f"\n【三种方法的平均差异】")
        print(f"本构关系 vs Kirsch：")
        print(f"  σxx: {summary_df['diff_const_kirsch_xx'].mean():.3f} MPa")
        print(f"  σyy: {summary_df['diff_const_kirsch_yy'].mean():.3f} MPa")
        print(f"\nKirsch vs Hondros：")
        print(f"  σxx: {summary_df['diff_kirsch_hondros_xx'].mean():.3f} MPa")
        print(f"  σyy: {summary_df['diff_kirsch_hondros_yy'].mean():.3f} MPa")
    
    print(f"\n" + "="*70 + "\n")


if __name__ == "__main__":
    batch_process_all_files_strict()