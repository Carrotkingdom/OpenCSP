import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ================= 1. 数据提取与标准化 =================

def get_natoms(poscar_path):
    try:
        with open(poscar_path, 'r') as f:
            lines = f.readlines()
            for line in lines[5:8]:
                parts = line.split()
                if parts and all(p.isdigit() for p in parts):
                    return sum(int(p) for p in parts)
    except: return None
    return None

def read_energy_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return float(f.read().strip().split()[0])
    except: return None

all_errors = []

# --- 处理 4 个大模型 (目录结构型) ---
model_dirs = {
    'mace': 'MACE-MPA-0',
    'mattersim': 'MatterSim v1 5M',
    'grace': 'GRACE-2L-OAM',
    'dpa3.1': 'DPA-3.1-3M-FT'
}

print("正在从目录提取大模型数据...")
for folder, display_name in model_dirs.items():
    if not os.path.isdir(folder): continue
    task_dirs = glob.glob(os.path.join(folder, 'task.*'))
    for task_path in task_dirs:
        task_name = os.path.basename(task_path) # 提取 task.74 这种名字
        n = get_natoms(os.path.join(task_path, 'POSCAR'))
        v_total = read_energy_file(os.path.join(task_path, 'energy_vasp_relax'))
        p_at = read_energy_file(os.path.join(task_path, 'energy'))
        
        if n and v_total is not None and p_at is not None:
            error = p_at - (v_total / n)
            all_errors.append({
                'Model': display_name, 
                'Error': error, 
                'Task': task_name,
                'Source': 'Foundation'
            })

# --- 处理 3 个 OpenCSP 模型 (文本文件型) ---
opencsp_files = {
    '0310.e_peratom_6.out': 'OpenCSP-L6',
    '0310.e_peratom_12.out': 'OpenCSP-L12',
    '0310.e_peratom_24.out': 'OpenCSP-L24'
}

print("正在从 .out 文件提取 OpenCSP 数据...")
for filename, display_name in opencsp_files.items():
    if not os.path.exists(filename): continue
    with open(filename, 'r') as f:
        line_idx = 1
        for line in f:
            if line.startswith('#') or not line.strip(): continue
            parts = line.split()
            if len(parts) >= 2:
                dft_e = float(parts[0])
                pred_e = float(parts[1])
                error = pred_e - dft_e
                all_errors.append({
                    'Model': display_name, 
                    'Error': error, 
                    'Task': f"Line_{line_idx}", # .out 文件没有文件夹，用行号标识
                    'Source': 'OpenCSP'
                })
            line_idx += 1

# 汇总到 DataFrame
df = pd.DataFrame(all_errors)
df['Abs_Error_meV'] = df['Error'].abs() * 1000

# ================= 2. 找出前 10 个误差最大的 Task =================

print("\n" + "="*50)
print("📊 4个基座模型绝对误差最大的前 10 个 Task")
print("="*50)

foundation_names = list(model_dirs.values())
for m_name in foundation_names:
    model_subset = df[df['Model'] == m_name]
    if not model_subset.empty:
        # 按绝对误差降序排列并取前 10
        top_10 = model_subset.sort_values(by='Abs_Error_meV', ascending=False).head(100)
        
        print(f"\n【模型: {m_name}】")
        print(f"{'Rank':<5} | {'Task Name':<15} | {'Error (meV/atom)':<20}")
        print("-" * 45)
        for i, (idx, row) in enumerate(top_10.iterrows(), 1):
            print(f"{i:<5} | {row['Task']:<15} | {row['Abs_Error_meV']:<20.4f}")

# ================= 3. 绘图部分 (保持原样) =================

model_order = [
    'MACE-MPA-0', 'GRACE-2L-OAM', 'MatterSim v1 5M', 'DPA-3.1-3M-FT',
    'OpenCSP-L6', 'OpenCSP-L12', 'OpenCSP-L24'
]
colors = ['#DA6C6C', '#FFCCB3', '#FFD23F', '#BA68C8', '#98D2C0', '#4F959D', '#205781']

plt.rcParams['font.size'] = 14
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams.update({'xtick.major.width': 1.5, 'ytick.major.width': 1.5, 'xtick.major.size': 6, 'ytick.major.size': 6})

fig, ax = plt.subplots(figsize=(12, 8))

sns.violinplot(data=df, x='Model', y='Abs_Error_meV', order=model_order, palette=colors, inner='box', linewidth=1.5, cut=0, ax=ax)

ax.set_xlabel('Model', fontsize=22)
ax.set_ylabel('Absolute Error (meV/atom)', fontsize=22)
ax.set_title('Energy Error Distribution Comparison', fontsize=22, pad=20)
ax.set_yscale('log')
ax.set_xticklabels([m.upper() for m in model_order], rotation=30, ha='right', fontsize=14)
ax.tick_params(axis='y', which='both', labelsize=16)
ax.grid(axis='y', alpha=0.3, linestyle='--', which='both')

plt.tight_layout()
plt.savefig('Full_Model_Comparison.png', dpi=300, bbox_inches='tight')

print("\nMAE Statistics (meV/atom):")
stats = df.groupby('Model')['Abs_Error_meV'].mean().reindex(model_order)
print(stats)