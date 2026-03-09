"""
DIC应变场转应力场并生成云图
从应变场Excel表格计算应力场，并输出可视化云图
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from matplotlib import cm
from pathlib import Path
import warnings
from scipy.interpolate import griddata

warnings.filterwarnings('ignore')


class StrainToStressConverter:
    """将应变场转换为应力场的转换器"""
    
    def __init__(self, E=1e11, nu=0.3, stress_type='plane_stress'):
        """
        初始化转换器
        
        Args:
            E: 杨氏模量 (Pa)
            nu: 泊松比
            stress_type: 应力类型 ('plane_stress' 平面应力 或 'plane_strain' 平面应变)
        """
        self.E = E  # 杨氏模量
        self.nu = nu  # 泊松比
        self.G = E / (2 * (1 + nu))  # 剪切模量
        self.stress_type = stress_type
        
        print(f"✅ 转换器初始化:")
        print(f"   杨氏模量 E = {E:.2e} Pa")
        print(f"   泊松比 ν = {nu}")
        print(f"   剪切模量 G = {self.G:.2e} Pa")
        print(f"   应力类型 = {stress_type}\n")
        
    def strain_to_stress(self, strain_data):
        """
        根据应变场计算应力场
        
        Args:
            strain_data: dict 或 DataFrame，包含 'exx', 'eyy', 'exy' 的应变数据
        
        Returns:
            dict: 包含 'sxx', 'syy', 'sxy', 's_mises' 的应力数据
        """
        
        if isinstance(strain_data, pd.DataFrame):
            exx = strain_data['exx'].values
            eyy = strain_data['eyy'].values
            exy = strain_data['exy'].values
            coords_x = strain_data['x'].values if 'x' in strain_data.columns else None
            coords_y = strain_data['y'].values if 'y' in strain_data.columns else None
        else:
            exx = strain_data['exx']
            eyy = strain_data['eyy']
            exy = strain_data['exy']
            coords_x = strain_data.get('x', None)
            coords_y = strain_data.get('y', None)
        
        # 根据应力类型选择本构关系
        if self.stress_type == 'plane_stress':
            # 平面应力：σz = 0
            factor = self.E / (1 - self.nu**2)
            sxx = factor * (exx + self.nu * eyy)
            syy = factor * (eyy + self.nu * exx)
        else:  # plane_strain
            # 平面应变：εz = 0
            factor = self.E / ((1 - self.nu) * (1 + self.nu))
            sxx = factor * ((1 - self.nu) * exx + self.nu * eyy)
            syy = factor * (self.nu * exx + (1 - self.nu) * eyy)
        
        # 剪应力计算（两种应力状态相同）
        sxy = self.G * exy
        
        # 计算von Mises应力（等效应力）
        # σ_mises = sqrt(σxx² + σyy² - σxx*σyy + 3*τxy²)
        s_mises = np.sqrt(sxx**2 + syy**2 - sxx*syy + 3*sxy**2)
        
        stress_data = {
            'sxx': sxx,
            'syy': syy,
            'sxy': sxy,
            's_mises': s_mises
        }
        
        if coords_x is not None:
            stress_data['x'] = coords_x
        if coords_y is not None:
            stress_data['y'] = coords_y
            
        return stress_data
    
    def read_strain_excel(self, excel_file):
        """
        读取应变场Excel表格
        
        Args:
            excel_file: Excel文件路径
        
        Returns:
            DataFrame: 包含应变数据的表格，失败时返回None
        """
        try:
            df = pd.read_excel(excel_file)
            return df
        except Exception as e:
            print(f"❌ 读取文件 {excel_file} 失败: {e}")
            return None
    
    def process_batch(self, input_dir, output_dir, E=None, nu=None, 
                      file_pattern='*.xlsx', stress_type=None, 
                      generate_images=True, verbose=False):
        """
        批量处理应变场Excel文件
        
        Args:
            input_dir: 输入文件夹（包含所有应变场Excel文件）
            output_dir: 输出文件夹（保存应力场数据和云图）
            E: 杨氏模量（覆盖初始化值）
            nu: 泊松比（覆盖初始化值）
            file_pattern: 文件匹配模式
            stress_type: 应力类型（覆盖初始化值）
            generate_images: 是否生成云图
            verbose: 是否输出详细信息
        
        Returns:
            DataFrame: 统计结果汇总表
        """
        
        if E is not None:
            self.E = E
            self.G = E / (2 * (1 + nu))
        if nu is not None:
            self.nu = nu
            self.G = self.E / (2 * (1 + nu))
        if stress_type is not None:
            self.stress_type = stress_type
        
        # 创建输出文件夹
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        stress_dir = os.path.join(output_dir, 'stress_data')
        image_dir = os.path.join(output_dir, 'stress_images') if generate_images else None
        Path(stress_dir).mkdir(parents=True, exist_ok=True)
        if generate_images:
            Path(image_dir).mkdir(parents=True, exist_ok=True)
        
        # 获取所有Excel文件
        input_path = Path(input_dir)
        excel_files = sorted(input_path.glob(file_pattern))
        
        total_files = len(excel_files)
        print(f"{'='*60}")
        print(f"开始批量处理应变场数据")
        print(f"{'='*60}")
        print(f"📁 输入文件夹: {input_dir}")
        print(f"📊 找到 {total_files} 个应变场文件")
        print(f"📁 输出文件夹: {output_dir}")
        print(f"{'='*60}\n")
        
        results = []
        failed_files = []
        
        for idx, excel_file in enumerate(excel_files, 1):
            try:
                # 读取应变场数据
                strain_df = self.read_strain_excel(excel_file)
                
                if strain_df is None or strain_df.empty:
                    failed_files.append(excel_file.name)
                    continue
                
                # 转换为应力场
                stress_data = self.strain_to_stress(strain_df)
                
                # 保存应力数据为Excel
                stress_output_file = os.path.join(
                    stress_dir, 
                    f"{excel_file.stem}_stress.xlsx"
                )
                self._save_stress_to_excel(stress_data, stress_output_file)
                
                # 生成应力云图
                if generate_images:
                    image_output_file = os.path.join(
                        image_dir,
                        f"{excel_file.stem}_stress_field.png"
                    )
                    self._plot_stress_field(stress_data, image_output_file, idx, excel_file.stem)
                
                # 记录结果统计
                results.append({
                    'file_name': excel_file.name,
                    'file_stem': excel_file.stem,
                    'sxx_mean': np.mean(stress_data['sxx']),
                    'sxx_max': np.max(stress_data['sxx']),
                    'sxx_min': np.min(stress_data['sxx']),
                    'syy_mean': np.mean(stress_data['syy']),
                    'syy_max': np.max(stress_data['syy']),
                    'syy_min': np.min(stress_data['syy']),
                    'sxy_mean': np.mean(stress_data['sxy']),
                    'sxy_max': np.max(np.abs(stress_data['sxy'])),
                    's_mises_mean': np.mean(stress_data['s_mises']),
                    's_mises_max': np.max(stress_data['s_mises']),
                    's_mises_min': np.min(stress_data['s_mises'])
                })
                
                # 进度显示
                if idx % max(1, total_files // 10) == 0 or idx == 1 or idx == total_files:
                    progress = 100 * idx / total_files
                    bar_length = 40
                    filled = int(bar_length * idx / total_files)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    print(f"  进度: [{bar}] {progress:.1f}% ({idx}/{total_files})")
                
            except Exception as e:
                print(f"❌ 处理文件 {excel_file.name} 出错: {e}")
                failed_files.append(excel_file.name)
                continue
        
        # 保存统计结果
        results_df = pd.DataFrame(results)
        results_csv = os.path.join(output_dir, 'stress_statistics.csv')
        results_df.to_csv(results_csv, index=False, encoding='utf-8-sig')
        
        # 输出总结
        print(f"\n{'='*60}")
        print(f"✅ 处理完成！")
        print(f"{'='*60}")
        print(f"✓ 成功处理: {len(results)} 个文件")
        print(f"✗ 失败文件: {len(failed_files)} 个")
        print(f"\n📁 应力场数据: {stress_dir}")
        if generate_images:
            print(f"📁 应力场云图: {image_dir}")
        print(f"📊 统计数据: {results_csv}")
        print(f"{'='*60}\n")
        
        # 显示统计信息
        print("📈 应力场统计摘要:")
        print("-" * 60)
        print(results_df[['s_mises_mean', 's_mises_max', 's_mises_min']].describe())
        
        # 找出最大应力位置
        max_idx = results_df['s_mises_max'].idxmax()
        print(f"\n🔴 最大应力位置:")
        print(f"   文件: {results_df.iloc[max_idx]['file_name']}")
        print(f"   最大von Mises应力: {results_df.iloc[max_idx]['s_mises_max']:.2e} Pa")
        
        # 找出最小应力位置
        min_idx = results_df['s_mises_max'].idxmin()
        print(f"\n🔵 最小应力位置:")
        print(f"   文件: {results_df.iloc[min_idx]['file_name']}")
        print(f"   最大von Mises应力: {results_df.iloc[min_idx]['s_mises_max']:.2e} Pa")
        
        print(f"\n{'='*60}\n")
        
        return results_df
    
    def _save_stress_to_excel(self, stress_data, output_file):
        """保存应力数据为Excel"""
        df = pd.DataFrame({
            'sxx': stress_data['sxx'],
            'syy': stress_data['syy'],
            'sxy': stress_data['sxy'],
            's_mises': stress_data['s_mises']
        })
        
        if 'x' in stress_data:
            df.insert(0, 'x', stress_data['x'])
        if 'y' in stress_data:
            df.insert(1, 'y', stress_data['y'])
        
        df.to_excel(output_file, index=False, sheet_name='Sheet1')
    
    def _plot_stress_field(self, stress_data, output_file, file_idx, file_name):
        """绘制应力场云图"""
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(14, 12))
            fig.suptitle(f'应力场分布 ({file_name})', 
                        fontsize=14, fontweight='bold', y=0.995)
            
            # 提取坐标和应力数据
            if 'x' in stress_data and 'y' in stress_data:
                x = stress_data['x']
                y = stress_data['y']
                has_coords = True
            else:
                has_coords = False
            
            stress_components = [
                ('sxx', '正应力 σxx (Pa)', axes[0, 0]),
                ('syy', '正应力 σyy (Pa)', axes[0, 1]),
                ('sxy', '剪应力 τxy (Pa)', axes[1, 0]),
                ('s_mises', 'von Mises应力 σMises (Pa)', axes[1, 1])
            ]
            
            for key, title, ax in stress_components:
                stress_values = stress_data[key]
                
                if has_coords:
                    # 创建网格进行插值
                    try:
                        xi = np.linspace(x.min(), x.max(), 50)
                        yi = np.linspace(y.min(), y.max(), 50)
                        Xi, Yi = np.meshgrid(xi, yi)
                        
                        # 插值
                        Zi = griddata((x, y), stress_values, (Xi, Yi), method='cubic')
                        
                        # 绘制等高线云图
                        im = ax.contourf(Xi, Yi, Zi, levels=20, cmap='jet')
                        # 添加散点
                        scatter = ax.scatter(x, y, c=stress_values, cmap='jet', 
                                           s=20, alpha=0.6, edgecolors='none')
                    except:
                        # 如果插值失败，直接使用散点图
                        im = ax.scatter(x, y, c=stress_values, cmap='jet', s=30, alpha=0.8)
                else:
                    # 没有坐标信息时，绘制直方图
                    im = ax.hist(stress_values, bins=50, color='blue', alpha=0.7)
                
                ax.set_title(title, fontsize=11, fontweight='bold')
                if has_coords:
                    ax.set_xlabel('X (mm)', fontsize=10)
                    ax.set_ylabel('Y (mm)', fontsize=10)
                    ax.set_aspect('equal')
                else:
                    ax.set_xlabel('应力值', fontsize=10)
                    ax.set_ylabel('频数', fontsize=10)
                
                # 添加颜色条
                cbar = plt.colorbar(im, ax=ax)
                cbar.set_label('应力值 (Pa)', rotation=270, labelpad=20, fontsize=9)
                
                # 添加统计信息
                mean_val = np.mean(stress_values)
                max_val = np.max(stress_values)
                min_val = np.min(stress_values)
                stats_text = f'μ={mean_val:.2e}\nMax={max_val:.2e}\nMin={min_val:.2e}'
                ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                       fontsize=8, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=120, bbox_inches='tight')
            plt.close(fig)
            
        except Exception as e:
            print(f"⚠️ 绘制图像失败 {output_file}: {e}")