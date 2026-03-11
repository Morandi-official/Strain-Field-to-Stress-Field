# Strain-Field-to-Stress-Field
整份程序运行的具体过程，包括数学公式和物理知识。（可能有错误）

## 📚 完整程序运行过程

---

## 【第一阶段】数据生成 `generate_sample_strain_data.py`

### **物理背景：DIC技术**

DIC（Digital Image Correlation，数字图像相关技术）是一种**无损、非接触**的测量方法：

1. **CT机扫描**：对岩石样本进行CT扫描，得到1000张连续的切面图像
2. **图像处理**：分析相邻两张图的图像变化
3. **位移计算**：根据斑点移动距离，计算每个点的位移 (u, v)
4. **应变计算**：通过位移求导得到应变分量

```
原始图像 ──CT扫描──> 1000张切面 ──DIC处理──> 位移场(u,v) ──求导──> 应变场(εxx, εyy, εxy)
```

### **应变的定义**

应变是**相对形变**，定义为：

```
εxx = ∂u/∂x   (X方向的相对伸长)
εyy = ∂v/∂y   (Y方向的相对伸长)
γxy = ∂u/∂y + ∂v/∂x   (剪切变形)
```

其中：
- **u, v** = 点在X、Y方向的位移（单位：mm）
- **εxx, εyy** = 正应变（无量纲，通常 10^-4 数量级）
- **γxy** = 工程剪切应变

### **程序中的模拟数据生成过程**

```python
# 【第1步】生成随机测量点坐标
x = np.random.uniform(0, 100, 500)  # 500个点的X坐标 (0-100mm)
y = np.random.uniform(0, 100, 500)  # 500个点的Y坐标 (0-100mm)

# 【第2步】生成位移场（模拟拉伸试验）
u = 0.005 * (x / 100) + np.random.normal(0, 0.0001, 500)
v = -0.0025 * (x / 100) + np.random.normal(0, 0.00005, 500)
```

**物理意义**：
- `u = 0.005 * (x/100)` ：模拟单轴拉伸，X方向位移与位置成正比（越往右拉得越多）
- `v = -0.0025 * (x/100)` ：由泊松效应，Y方向会收缩（负值表示压缩）
- `np.random.normal(...)` ：加入测量噪声

### **【第3步】生成应变场**

```python
# 基础均匀应变
exx = 0.0001 + np.random.normal(0, 0.000005, 500)  # 背景：均匀拉伸
eyy = -0.00003 + np.random.normal(0, 0.000003, 500)  # 背景：均匀压缩
exy = np.random.normal(0, 0.000003, 500)  # 背景：无剪切
```

### **【第4步】添加缺陷效应（应变集中）**

```python
# 模拟岩石内部缺陷（孔隙、微裂纹等）
for _ in range(num_defects):  # 随机生成3-8个缺陷
    defect_x = np.random.uniform(0, 100)  # 随机缺陷位置
    defect_y = np.random.uniform(0, 100)
    
    # 计算到缺陷的距离
    distance = np.sqrt((x - defect_x)**2 + (y - defect_y)**2)
    
    # 应变集中函数（高斯分布）
    concentration = np.exp(-distance / defect_radius) * 0.5
    
    # 缺陷周围应变增强
    exx += 0.00008 * concentration
    eyy += 0.00004 * concentration
    exy += 0.000005 * concentration
```

**物理含义**：缺陷附近应力集中，导致应变增加。这就是为什��岩石更容易从缺陷处开始破裂。

### **【结果】1000个Excel文件**

每个文件有500行数据：
```
x(mm)    y(mm)    u(mm)    v(mm)    exx        eyy        exy
0.5      2.3      0.0025   -0.0012  0.0001     -0.00002   0.000001
1.2      5.6      0.0060   -0.0030  0.0001     -0.00003   -0.000002
...      ...      ...      ...      ...        ...        ...
```

---

## 【第二阶段】应变→应力转换 `strain_to_stress_converter.py`

### **物理基础：胡克定律（本构关系）**

应力与应变的关系由材料的弹性模量决定。对于**各向同性线性弹性材料**：

#### **1️⃣ 平面应力情况** (plane_stress)

**假设条件**：σz = 0（表面薄层，如CT扫描切面）

**本构关系**：

$$\sigma_{xx} = \frac{E}{1-\nu^2}(\varepsilon_{xx} + \nu\varepsilon_{yy})$$

$$\sigma_{yy} = \frac{E}{1-\nu^2}(\varepsilon_{yy} + \nu\varepsilon_{xx})$$

$$\tau_{xy} = G\gamma_{xy} = \frac{E}{2(1+\nu)}\varepsilon_{xy}$$

其中：
- **E**：杨氏模量（弹性模量，单位：Pa）= 材料抵抗形变的能力
- **ν**：泊松比（无量纲，通常0.2-0.4）= 侧向收缩与纵向伸长的比值
- **G**：剪切模量 = E / [2(1+ν)]

**物理意义**：
- 如果材料拉伸（εxx > 0），会产生正应力σxx
- 同时也会对垂直方向产生应力（νεyy项）
- 这个关系是线性的，这就是"线性弹性"

#### **2️⃣ 平面应变情况** (plane_strain)

**假设条件**：εz = 0（深部岩石，受约束）

**本构关系**：

$$\sigma_{xx} = \frac{E}{(1-\nu)(1+\nu)}[(1-\nu)\varepsilon_{xx} + \nu\varepsilon_{yy}]$$

$$\sigma_{yy} = \frac{E}{(1-\nu)(1+\nu)}[\nu\varepsilon_{xx} + (1-\nu)\varepsilon_{yy}]$$

$$\tau_{xy} = G\gamma_{xy}$$

### **程序实现**

```python
class StrainToStressConverter:
    def strain_to_stress(self, strain_data):
        exx = strain_data['exx']
        eyy = strain_data['eyy']
        exy = strain_data['exy']
        
        # 平面应力情况
        if self.stress_type == 'plane_stress':
            factor = self.E / (1 - self.nu**2)
            sxx = factor * (exx + self.nu * eyy)
            syy = factor * (eyy + self.nu * exx)
        
        # 剪应力
        sxy = self.G * exy
        
        # von Mises等效应力
        s_mises = np.sqrt(sxx**2 + syy**2 - sxx*syy + 3*sxy**2)
```

### **具体计算例子**

假设一个数据点的应变为：
```
εxx = 0.0001    (拉伸0.01%)
εyy = -0.00003  (压缩0.003%)
εxy = 0.000005  (剪切)
```

材料参数（花岗岩）：
```
E = 5e10 Pa (50 GPa)
ν = 0.25
```

**计算过程**：

```
factor = 5e10 / (1 - 0.25²) 
       = 5e10 / 0.9375 
       = 5.33e10

σxx = 5.33e10 × (0.0001 + 0.25×(-0.00003))
    = 5.33e10 × (0.0001 - 0.0000075)
    = 5.33e10 × 0.0000925
    = 4.93e6 Pa = 4.93 MPa  (拉应力)

σyy = 5.33e10 × (-0.00003 + 0.25×0.0001)
    = 5.33e10 × (-0.00003 + 0.000025)
    = 5.33e10 × (-0.000005)
    = -2.67e5 Pa = -0.267 MPa  (压应力)

G = 5e10 / (2×1.25) = 2e10

τxy = 2e10 × 0.000005 = 1e5 Pa = 0.1 MPa
```

### **von Mises等效应力**

这是一个**标量值**，用来判断材料是否会破坏：

$$\sigma_{Mises} = \sqrt{\sigma_{xx}^2 + \sigma_{yy}^2 - \sigma_{xx}\sigma_{yy} + 3\tau_{xy}^2}$$

**物理意义**：
- 将复杂的三维应力状态简化为一个等效标量
- 当 σMises > 材料强度 时，材料开始塑性变形或破裂
- 这是最常用的材料失效判据（von Mises准则）

**继续上面的例子**：

```
σMises = √(4.93e6)² + (-2.67e5)² - 4.93e6×(-2.67e5) + 3×(1e5)²
       = √(24.3×10¹² + 0.71×10¹² + 1.32×10¹² + 3×10¹⁰)
       = √(26.3×10¹²)
       = 5.13e6 Pa = 5.13 MPa
```

### **【结果】1000个应力数据Excel**

每个文件有500行数据：
```
x(mm)    y(mm)    sxx(Pa)      syy(Pa)      sxy(Pa)      s_mises(Pa)
0.5      2.3      4.93e6       -2.67e5      1e5          5.13e6
1.2      5.6      5.20e6       -3.15e5      1.2e5        5.42e6
...      ...      ...          ...          ...          ...
```

---

## 【第三阶段】生成云图可视化

### **云图的物理意义**

云图是一种**等高线图**，用颜色表示应力的空间分布：

```
红色区 ─── 高应力（>0.8σMises_max）── 危险区，易破裂 🔴
黄色区 ─── 中应力 ── 中等危险
蓝色区 ─── 低应力（<0.2σMises_max）── 安全区 🔵
```

### **插值过程**

原始DIC数据是**离散的点**（500个点），需要插值得到**连续的场**：

```python
# 原始数据点
x = [0.5, 1.2, 2.3, ...]  (500个点)
y = [2.3, 5.6, 3.1, ...]
stress_values = [5.13e6, 5.42e6, 4.98e6, ...]

# 创建规则网格（50×50=2500个点）
xi = linspace(0, 100, 50)  # X轴分成50份
yi = linspace(0, 100, 50)  # Y轴分成50份
Xi, Yi = meshgrid(xi, yi)

# 三次样条插值（cubic interpolation）
Zi = griddata((x, y), stress_values, (Xi, Yi), method='cubic')
```

**插值公式**（三次样条）：

$$f(x,y) = \sum_{i,j} c_{ij} \cdot B_i(x) \cdot B_j(y)$$

其中 $B_i(x)$ 是三次B样条基函数。

**物理意义**：根据周围已知点的应力，推断网格点的应力值，生成光滑的应力场分布。

### **云图生成代码**

```python
def _plot_stress_field(self, stress_data, output_file):
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # 四个子图：σxx, σyy, τxy, σMises
    for key, title, ax in stress_components:
        stress_values = stress_data[key]
        x = stress_data['x']
        y = stress_data['y']
        
        # 创建网格
        Xi, Yi = np.meshgrid(np.linspace(x.min(), x.max(), 50),
                            np.linspace(y.min(), y.max(), 50))
        
        # 插值
        Zi = griddata((x, y), stress_values, (Xi, Yi), method='cubic')
        
        # 等高线填充（contourf = contour + fill）
        im = ax.contourf(Xi, Yi, Zi, levels=20, cmap='jet')
        
        # 添加原始数据点
        ax.scatter(x, y, c=stress_values, cmap='jet', s=20, alpha=0.6)
        
        # 颜色条
        cbar = plt.colorbar(im, ax=ax)
```

---

## 【第四阶段】数据分析

### **1. 应力分布直方图**

统计所有1000个切面的**应力值分布**：

```python
plt.hist(df['s_mises_mean'], bins=50)
```

**物理意义**：
- 如果分布集中（窄峰），说明应力分布均匀
- 如果分布分散（宽峰），说明应力分布不均匀，存在应力集中

### **2. 应力演化曲线**

```python
x = np.arange(len(df))  # CT切片序号 0-999
plt.plot(x, df['s_mises_mean'])  # 平均应力随深度变化
plt.fill_between(x, df['s_mises_min'], df['s_mises_max'])  # 应力范围
```

**物理意义**：
- 应力从顶部到底部如何变化
- 找到**应力集中区**（峰值位置）
- 这可能对应裂纹、孔隙等缺陷位置

### **3. 高应力区域识别**

```python
percentile_90 = np.percentile(df['s_mises_max'], 90)
critical = df[df['s_mises_max'] >= percentile_90]
```

找出**最高应力的10%**（超过90百分位数），这些是最危险的区域。

---

## 📊 完整数据流动图

```
【输入】岩石样本
   │
   ├─> CT扫描 ──> 1000张切面图像
   │
   └─> DIC处理 ──> 1000个应变场数据 (exx, eyy, exy)
                    ↓
        【generate_sample_strain_data.py】
        生成1000个 CT_001.xlsx ~ CT_1000.xlsx
        
【转换】应变 ──> 应力
   │
   ├─> 本构关系：σ = f(ε, E, ν)
   │
   └─> von Mises应力：σMises = √(σxx² + σyy² - σxx·σyy + 3τxy²)
        
        【strain_to_stress_converter.py】
        生成1000个 CT_001_stress.xlsx ~ CT_1000_stress.xlsx
        
【可视化】应力 ──> 云图
   │
   ├─> 插值：离散点 ──cubic spline──> 连续场
   │
   └─> 等高线填充：应力值 ──color map(jet)──> RGB颜色
                                (蓝 -> 绿 -> 红)
        
        【regenerate_images.py】
        生成1000张 CT_001_stress_field.png ~ CT_1000_stress_field.png
        
【分析】统计和识别
   │
   ├─> 分布直方图：应力值出现频率
   │
   ├─> 演化曲线：应力随深度变化
   │
   └─> 高应力区：找危险区域
   
        【analysis_tools.py】
        生成 stress_statistics.csv
        生成 stress_distribution.png
        生成 stress_evolution.png
        生成 critical_regions.csv
```

---

## 🎯 关键物理量总结表

| 物理量 | 符号 | 单位 | 范围 | 物理意义 |
|--------|------|------|------|---------|
| 应变 | ε | 无量纲 | 10⁻⁵ ~ 10⁻³ | 相对形变大小 |
| 应力 | σ | Pa (帕斯卡) | 10⁶ ~ 10⁸ Pa | 单位面积受力 |
| 杨氏模量 | E | Pa | 10¹⁰ ~ 10¹¹ Pa | 材料抵抗形变能力 |
| 泊松比 | ν | 无量纲 | 0.2 ~ 0.4 | 侧向收缩比 |
| von Mises应力 | σMises | Pa | 10⁶ ~ 10⁸ Pa | 等效应力，判断破坏 |

---

## 💡 一个完整的计算示例

假设你扫描一个**花岗岩样本**，CT得到1000张切面。第500张切面的某个测量点数据为：

### **第1步：DIC测量（已有）**
```
位置：x = 50mm, y = 50mm（样本中心）
位移：u = 0.5mm, v = -0.15mm
计算应变（数值微分）：
εxx = ∂u/∂x ≈ 0.0001
εyy = ∂v/∂y ≈ -0.00003
εxy = 0.000005
```

### **第2步：应变→应力转换**
```
花岗岩参数：
E = 5×10¹⁰ Pa (50 GPa)
ν = 0.25
G = E/[2(1+ν)] = 2×10¹⁰ Pa

计算：
factor = 5×10¹⁰ / (1 - 0.25²) = 5.33×10¹⁰

σxx = 5.33×10¹⁰ × (0.0001 + 0.25×(-0.00003))
    = 5.33×10¹⁰ × 0.0000925
    = 4.93 MPa  ✓ 拉应力

σyy = 5.33×10¹⁰ × (-0.00003 + 0.25×0.0001)
    = 5.33×10¹⁰ × (-0.000005)
    = -0.267 MPa  ✓ 压应力（泊松效应）

τxy = 2×10¹⁰ × 0.000005
    = 0.1 MPa
```

### **第3步：计算von Mises应力**
```
σMises = √(4.93² + 0.267² - 4.93×0.267 + 3×0.1²)
       = √(24.3 + 0.071 - 1.32 + 0.03)
       = √23.08
       = 4.8 MPa  ✓ 等效应力
```

### **第4步：判断安全性**
```
花岗岩抗压强度 fc ≈ 100-200 MPa
本点应力 = 4.8 MPa << 200 MPa
结论：✓ 安全，远未达到破坏应力
```

---

## 🔍 为什么有缺陷的地方应力更高？

这涉及**应力集中**现象：

```
无缺陷状况：
│════════════════════════════════════════│
│  应力分布均匀                         │
│  σ_avg = 10 MPa                       │
│════════════════════════════════════════│

有孔洞缺陷：
│═════════════╱═╲═════════════════════│
│  应力绕过孔洞，密集分布在孔周围     │
│  局部应力可达 σ_local = 30 MPa      │
│  应力集中因子 K = 30/10 = 3          │
│═════════════╱═╲═════════════════════│
```

**应力集中系数**：
$$K_t = \frac{\sigma_{local}}{\sigma_{avg}}$$

- K_t = 1：无应力集中
- K_t = 2-5：常见孔隙缺陷
- K_t > 5：严重缺陷，易破裂

这就是为什么我们需要找到高应力区域——那些地方最容易裂开！

---

## ✅ 总结

整个程序的逻辑就是：

```
1️⃣ 生成应变数据
   模拟DIC测量结果
   
2️⃣ 应变转换为应力
   使用胡克定律（本构关系）
   σ = f(ε, E, ν)
   
3️⃣ 计算等效应力
   von Mises公式
   判断材料是否会破坏
   
4️⃣ 可视化和分析
   生成云图显示应力分布
   找出高应力危险区域
   指导工程设计和风险评估
```

从**岩石扫描→应变测量→应力计算→风险评估**的完整过程
