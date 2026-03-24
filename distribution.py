import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 加载数据
df = pd.read_csv('gnome_comparison_raw_basis.csv')

# 2. 预处理：计算绝对误差并转为 meV/atom
# 审稿人关心的是 MAE/RMSE 这种绝对偏差的来源
df['Abs_Error_meV'] = df['Error'].abs() * 1000

# 3. 设置绘图风格 (继承自你的参考代码)
plt.rcParams['font.size'] = 14
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['xtick.major.width'] = 1.5
plt.rcParams['ytick.major.width'] = 1.5
plt.rcParams['xtick.major.size'] = 6
plt.rcParams['ytick.major.size'] = 6
plt.rcParams['xtick.minor.size'] = 4
plt.rcParams['ytick.minor.size'] = 4

# 创建图形
fig, ax = plt.subplots(figsize=(10, 8))

# 配色方案 (按照你的参考颜色)
colors = ['#DA6C6C', '#FFCCB3', '#FFD23F', '#98D2C0', '#4F959D', '#205781', '#BA68C8']
model_order = ['MACE-MPA-0', 'GRACE-2L-OAM', 'MatterSim v1 5M', 'DPA-3.1-3M-FT'] # 你可以根据需要调整顺序

# 4. 绘制小提琴图 + 箱线图
# 使用 cut=0 防止小提琴图延伸到负数区域（因为是绝对误差）
sns.violinplot(
    data=df, 
    x='Model', 
    y='Abs_Error_meV', 
    order=model_order,
    palette=colors,
    inner='box',      # 在内部绘制箱线图
    linewidth=1.5,
    cut=0,
    ax=ax
)

# 5. 图形装饰
ax.set_xlabel('Model', fontsize=22)
ax.set_ylabel('Absolute Error (meV/atom)', fontsize=22)
ax.set_title('Distribution of Energy Errors (GNoME)', fontsize=22, pad=20)

# 设置对数坐标轴 (应对离群值，且符合你的参考风格)
# 如果误差跨度非常大，对数轴能更好地看清分布主体
ax.set_yscale('log')

# 设置x轴标签
ax.set_xticklabels([m.upper() for m in model_order], rotation=30, ha='right', fontsize=16)

# 设置y轴刻度线增强
ax.tick_params(axis='y', which='both', labelsize=16, width=1.5)
ax.tick_params(axis='x', which='major', width=1.5)

# 添加横向网格
ax.grid(axis='y', alpha=0.3, linestyle='--', which='both')

# 6. 保存和显示
plt.tight_layout()
plt.savefig('GNoME_Error_Distribution.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Saved GNoME_Error_Distribution.png")