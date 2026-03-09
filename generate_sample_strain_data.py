"""
生成模拟DIC应变场数据（用于测试）
模拟1000张CT切面的应变场数据
"""

import numpy as np
import pandas as pd
from pathlib import Path


def generate_sample_strain_data(num_files=1000, points_per_file=500, output_dir="./strain_data"):
    """
    生成模拟应变场数据
    
    Args:
        num_files: 生成多少个Excel文件（模拟多少张CT切面）
        points_per_file: 每个文件有多少个测量点
        output_dir: 输出文件夹
    """
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"正在生成 {num_files} 个模拟应变场数据文件...")
    print(f"每个��件包含 {points_per_file} 个测量点\n")
    
    for file_idx in range(1, num_files + 1):
        # 生成测量点坐标（随机生成而不是网格）
        x = np.random.uniform(0, 100, points_per_file)
        y = np.random.uniform(0, 100, points_per_file)
        
        # 生成位移场（模拟单轴拉伸试验）
        # 位移随着x方向逐渐增加
        u = 0.005 * (x / 100) + np.random.normal(0, 0.0001, points_per_file)
        v = -0.0025 * (x / 100) + np.random.normal(0, 0.00005, points_per_file)
        
        # 生成应变场
        # 基础均匀应变
        exx = 0.0001 + np.random.normal(0, 0.000005, points_per_file)
        eyy = -0.00003 + np.random.normal(0, 0.000003, points_per_file)
        exy = np.random.normal(0, 0.000003, points_per_file)
        
        # 添加空间变化（模拟真实岩石内部缺陷）
        # 设置���干个应变集中区（模拟微裂纹、��隙等）
        num_defects = np.random.randint(3, 8)
        for _ in range(num_defects):
            # 随机缺陷位置
            defect_x = np.random.uniform(0, 100)
            defect_y = np.random.uniform(0, 100)
            defect_radius = np.random.uniform(5, 15)
            
            # 缺陷周围应变增强
            distance = np.sqrt((x - defect_x)**2 + (y - defect_y)**2)
            concentration = np.exp(-distance / defect_radius) * np.random.uniform(0.3, 0.8)
            
            exx += 0.00008 * concentration
            eyy += 0.00004 * concentration
            exy += 0.000005 * concentration
        
        # 确保应变值在合理范围内
        exx = np.clip(exx, -0.0003, 0.0005)
        eyy = np.clip(eyy, -0.0003, 0.0005)
        exy = np.clip(exy, -0.0002, 0.0002)
        
        # 创建DataFrame
        df = pd.DataFrame({
            'x': x,
            'y': y,
            'u': u,
            'v': v,
            'exx': exx,
            'eyy': eyy,
            'exy': exy
        })
        
        # 保存为Excel
        output_file = Path(output_dir) / f"CT_{file_idx:06d}.xlsx"
        df.to_excel(output_file, index=False, sheet_name='Sheet1')
        
        # 进度显示
        if file_idx % 100 == 0 or file_idx == 1 or file_idx == num_files:
            print(f"  已生成 {file_idx}/{num_files} 个文件 "
                  f"({100*file_idx/num_files:.1f}%)")
    
    print(f"\n✅ 模拟数据生成完成！")
    print(f"文件位置: {Path(output_dir).absolute()}")
    
    # 显示样本数据
    print(f"\n📄 样本数据预览 (CT_000001.xlsx):")
    sample_file = Path(output_dir) / "CT_000001.xlsx"
    sample_df = pd.read_excel(sample_file)
    print(sample_df.head(15))
    print(f"\n数据统计:")
    print(sample_df.describe())
    
    return sample_df


if __name__ == "__main__":
    # ============ 配置参数 ============
    num_files = 1000
    points_per_file = 500
    
    # ============ 生成数据 ============
    sample_data = generate_sample_strain_data(
        num_files=num_files,
        points_per_file=points_per_file,
        output_dir="./strain_data"
    )