import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# 数据
models = ['OpenCSP-L6', 'OpenCSP-L12', 'OpenCSP-L24', 'MACE-MPA-0', 'MatterSim v1 5M', 'GRACE-2L-OAM','DPA-3.1-3M-FT']
e_mae = [20.7, 17.2, 15.6, 25.0, 33.6,20.8, 19.5 ]
e_rmse = [27.7, 23.1, 21.4, 123.5, 124.8, 123.5, 123.4]
#e_mae = [20.7, 17.2, 15.6, 100.1, 109.2,96.0, 94.7 ]
#e_rmse = [27.7, 23.1, 21.4, 205.7, 206.8, 203.3, 201.6]

# 设置绘图风格
plt.rcParams['font.size'] = 14
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['xtick.major.width'] = 1.5
plt.rcParams['ytick.major.width'] = 1.5
plt.rcParams['xtick.major.size'] = 6  # x轴刻度线长度
plt.rcParams['ytick.major.size'] = 6  # y轴刻度线长度
plt.rcParams['xtick.minor.size'] = 4  # x轴次要刻度线长度
plt.rcParams['ytick.minor.size'] = 4  # y轴次要刻度线长度
plt.rcParams['xtick.minor.width'] = 1.5  # x轴次要刻度线宽度
plt.rcParams['ytick.minor.width'] = 1.5  # y轴次要刻度线宽度

# 创建图形
fig, ax = plt.subplots(figsize=(8, 8))

# 使用与参考代码相似的配色方案
colors = ['#DA6C6C', '#FFCCB3', '#FFD23F', '#98D2C0', '#4F959D', '#205781']
bar_width = 0.35
x_pos = np.arange(len(models))

# 绘制柱状图
bars1 = ax.bar(x_pos - bar_width/2, e_mae, bar_width, 
               label='${\mathrm{E_{MAE}}}$ ', color=colors[0], alpha=0.8, edgecolor='white', linewidth=1)
bars2 = ax.bar(x_pos + bar_width/2, e_rmse, bar_width, 
               label='${\mathrm{E_{RMSE}}}$ ', color=colors[3], alpha=0.8, edgecolor='white', linewidth=1)

# 设置y轴范围 - 最小值为10，最大值自动调整
y_min = 10
y_max = max(max(e_mae), max(e_rmse)) * 1.23  # 增加15%的边距
ax.set_ylim(y_min, y_max)

# 设置标签和标题
#ax.set_xlabel('Models', fontsize=20)
ax.set_ylabel('Error (meV/atom)', fontsize=20)
ax.set_title('Energy Errors ', fontsize=22)

# 设置x轴刻度
ax.set_xticks(x_pos)
ax.set_xticklabels(models, rotation=30, ha='right', fontsize=16)
ax.set_yscale('log')

# 设置y轴格式和刻度
ax.tick_params(axis='y', which='major', labelsize=16, width=2, size=8)  # 增加刻度线宽度和长度
ax.tick_params(axis='x', which='major', width=2, size=8)  # 也增强x轴刻度线

# 添加网格
ax.grid(axis='y', alpha=0.3, linestyle='--')

# 添加图例
ax.legend(fontsize=16, framealpha=0.9, frameon=False)

# 在每个柱子上添加数值标签
def add_value_labels(bars):
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height * 1.02,
                f'{height:.1f}', ha='center', va='bottom', fontsize=16, rotation=0)

add_value_labels(bars1)
add_value_labels(bars2)

# 调整布局
plt.tight_layout()

# 保存图像
plt.savefig('E-new.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Saved E.png")