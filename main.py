"""
主程序入口
完整的工作流程：数据生成 → 数据转换 → 结果分析
"""

import os
import sys
from pathlib import Path

# 导入各个模块
from generate_sample_strain_data import generate_sample_strain_data
from strain_to_stress_converter import StrainToStressConverter
from analysis_tools import StressAnalyzer


def main():
    """主工作流程"""
    
    print("\n" + "="*70)
    print(" "*15 + "DIC应变场 → 应力场转换系统")
    print("="*70 + "\n")
    
    # ============ 第一步：生成模拟数据 ============
    print("【步骤1】生成模拟应变场数据\n")
    print("-" * 70)
    
    strain_data_dir = "./strain_data"
    
    # 检查是否已存在数据
    if not Path(strain_data_dir).exists() or len(list(Path(strain_data_dir).glob('*.xlsx'))) == 0:
        print(f"📊 正在生成模拟应变场数据到: {strain_data_dir}\n")
        
        # 改成1000个文件
        generate_sample_strain_data(num_files=1000, points_per_file=500, output_dir=strain_data_dir)
    else:
        file_count = len(list(Path(strain_data_dir).glob('*.xlsx')))
        print(f"✅ 应变场数据已存在 ({file_count} 个文件)\n")
    
    # ============ 第二步：转换为应力场 ============
    print("\n【步骤2】将应变场转换为应力场\n")
    print("-" * 70)
    
    stress_output_dir = "./stress_output"
    
    # 创建转换器（根据岩石材料类型调整参数）
    print("🔧 初始化应力转换器\n")
    converter = StrainToStressConverter(
        E=5e10,  # 花岗岩杨氏模量约50 GPa
        nu=0.25,  # 泊松比
        stress_type='plane_stress'
    )
    
    # 执行批量处理
    print("🔄 执行批量转换和云图生成\n")
    results_df = converter.process_batch(
        input_dir=strain_data_dir,
        output_dir=stress_output_dir,
        file_pattern='*.xlsx',
        generate_images=True  # 设为False可跳过云图生成（加快速度）
    )
    
    # ============ 第三步：分析结果 ============
    print("\n【步骤3】分析应力场数据\n")
    print("-" * 70)
    
    statistics_file = os.path.join(stress_output_dir, 'stress_statistics.csv')
    
    print("📈 开始应力场数据分析\n")
    analyzer = StressAnalyzer(statistics_file)
    
    # 生成分析图表
    print("🎨 生成分析图表\n")
    analyzer.plot_stress_distribution(
        output_file=os.path.join(stress_output_dir, 'stress_distribution.png')
    )
    analyzer.plot_stress_evolution(
        output_file=os.path.join(stress_output_dir, 'stress_evolution.png')
    )
    
    # 识别高应力区域
    print("🔍 识别高应力区域\n")
    critical_regions = analyzer.identify_critical_regions(
        percentile=90,
        output_file=os.path.join(stress_output_dir, 'critical_regions.csv')
    )
    
    # 生成总结报告
    print("📄 生成分析报告\n")
    analyzer.generate_summary_report(
        output_file=os.path.join(stress_output_dir, 'analysis_report.txt')
    )
    
    # ============ 最终总结 ============
    print("\n" + "="*70)
    print("✅ 所有处理完成！")
    print("="*70)
    print(f"\n📁 输出文件夹结构:\n")
    print(f"{stress_output_dir}/")
    print(f"├── stress_data/              # 应力场数据 (1000个Excel)")
    print(f"├── stress_images/            # 应力云图 (1000张PNG)")
    print(f"├── stress_statistics.csv     # 统计汇总表")
    print(f"├── stress_distribution.png   # 应力分布直方图")
    print(f"├── stress_evolution.png      # 应力演化曲线")
    print(f"├── critical_regions.csv      # 高应力区域列表")
    print(f"└── analysis_report.txt       # 分析报告")
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断了程序执行")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)