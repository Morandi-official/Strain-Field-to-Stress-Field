"""
DIC-BTS严格对标文献系统 - 主程序

完整实现文献式1-2, 1-3, 1-4, 1-5, 1-6
"""

from pathlib import Path
from dic_bts_strict_converter import DICBTSStrictConverter
import pandas as pd


def main():
    """主程序"""
    
    print("\n" + "="*70)
    print(" "*10 + "DIC-BTS严格对标文献完整系统")
    print(" "*5 + "实现式1-2, 1-3, 1-4, 1-5, 1-6")
    print("="*70 + "\n")
    
    # ========== 【参数配置】 ==========
    print("【第1步】配置材料和样本参数")
    print("-"*70)
    
    # 花岗岩
    E = 5e10
    nu = 0.25
    D = 50.0
    t = 25.0
    
    print(f"✓ 材料：花岗岩")
    print(f"✓ E = {E/1e9:.0f} GPa, ν = {nu}")
    print(f"✓ 样本：D = {D:.1f} mm, t = {t:.1f} mm\n")
    
    # ========== 【文件夹配置】 ==========
    print("【第2步】配置文件夹")
    print("-"*70)
    
    input_dir = './strain_data'
    output_dir = './DIC_BTS_strict_output'
    
    print(f"✓ 输入：{input_dir}")
    print(f"✓ 输出：{output_dir}\n")
    
    # ========== 【创建转换器】 ==========
    print("【第3步】创建严格版转换器")
    print("-"*70)
    
    converter = DICBTSStrictConverter(E, nu, D, t)
    
    # ========== 【处理单个文件】 ==========
    print("【第4步】处理示例文件")
    print("-"*70 + "\n")
    
    input_path = Path(input_dir)
    excel_files = sorted(input_path.glob('*.xlsx'))
    
    if len(excel_files) > 0:
        excel_file = excel_files[0]
        print(f"处理示例文件: {excel_file.name}\n")
        
        # 处理文件
        results = converter.process_dic_excel_strict(str(excel_file), output_dir)
        
        # 绘制各种对比图
        converter.plot_stress_comparison_three_methods(results, output_dir)
        converter.plot_griffith_criterion_analysis(results, output_dir)
        converter.plot_stress_along_diameter(results, output_dir)
        
        # 生成报告
        converter.generate_strict_report(results, excel_file, output_dir)
        
        # ========== 【显示结果】 ==========
        print("\n【第5步】统计结果")
        print("-"*70)
        
        print(f"\n【抗拉强度统计】")
        print(f"  本构关系: {results['sigma_t_const'].mean():.3f} ± "
              f"{results['sigma_t_const'].std():.3f} MPa")
        print(f"  Kirsch:   {results['sigma_t_kirsch'].mean():.3f} ± "
              f"{results['sigma_t_kirsch'].std():.3f} MPa")
        print(f"  Hondros:  {results['sigma_t_hondros'].mean():.3f} ± "
              f"{results['sigma_t_hondros'].std():.3f} MPa")
        
        print(f"\n【Griffith破坏准则分析】")
        branch1 = (results['griffith_condition'] >= 0).sum()
        branch2 = (results['griffith_condition'] < 0).sum()
        print(f"  第一分支（拉应力主导）: {branch1} 个点 ({100*branch1/len(results):.1f}%)")
        print(f"  第二分支（压应力主导）: {branch2} 个点 ({100*branch2/len(results):.1f}%)")
        
        print(f"\n【应力场特性】")
        print(f"  σxx范围: [{results['sigma_xx_kirsch'].min():.3f}, "
              f"{results['sigma_xx_kirsch'].max():.3f}] MPa")
        print(f"  σyy范围: [{results['sigma_yy_kirsch'].min():.3f}, "
              f"{results['sigma_yy_kirsch'].max():.3f}] MPa")
        
        print(f"\n【输出文件】")
        print(f"  ✓ *_strict.csv - 完整应力数据")
        print(f"  ✓ comparison_three_methods.png - 三方法对比")
        print(f"  ✓ griffith_criterion_analysis.png - 破坏准则分析")
        print(f"  ✓ stress_along_diameter.png - 直径应力分布")
        print(f"  ✓ *_strict_report.txt - 详细分析报告")
        
    else:
        print(f"❌ 在 {input_dir} 中没有找到Excel文件\n")
    
    print("\n" + "="*70)
    print("✅ 严格对标文献的分析完成！")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()