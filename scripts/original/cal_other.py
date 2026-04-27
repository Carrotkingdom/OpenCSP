import os
import numpy as np
import pandas as pd
from pathlib import Path
from ase.io import read
from collections import Counter

# GNoME 官方校正值 (E_corrected = E_raw + correction)
# 还原回 raw 需要减去这些值
PP_CORR = {
    "Ga": -0.0028805,
    "Ge": 0.10417085,
    "Li": -0.00301278,
    "Mg": 0.0924014,
    "Na": -0.00447437
}

def get_poscar_info(poscar_path):
    """稳健读取 POSCAR 并获取原子数与成分"""
    try:
        atoms = read(poscar_path)
        num_atoms = len(atoms)
        composition = dict(Counter(atoms.get_chemical_symbols()))
        return num_atoms, composition
    except Exception as e:
        print(f"Warning: Failed to read {poscar_path}: {e}")
        return None, None

def process_gnome_benchmarks():
    #models = ['dpa3.1']
    models = ['mace', 'grace', 'mattersim', 'dpa3.1']
    base_path = Path(".")
    all_data = []

    for model_name in models:
        model_dir = base_path / model_name
        if not model_dir.exists(): continue
        
        print(f"Processing model: {model_name}")
        task_folders = list(model_dir.glob("task.*"))
        
        for task in task_folders:
            f_energy = task / "energy"        # 模型预测值 (eV/atom)
            f_gnome = task / "energy_GNoME"   # 参考值 (Corrected Total Energy)
            f_poscar = task / "POSCAR"
            
            if not (f_energy.exists() and f_gnome.exists() and f_poscar.exists()):
                continue
                
            n_atoms, comp = get_poscar_info(f_poscar)
            if n_atoms is None: continue
            
            try:
                e_model = float(f_energy.read_text().strip()) # 已经是 eV/atom
                e_gnome_total_corr = float(f_gnome.read_text().strip())
            except ValueError: continue
            
            # 1. 计算总校正量
            total_correction = sum(comp.get(elem, 0) * val for elem, val in PP_CORR.items())
            
            # 2. 按照你的要求：将 GNoME 还原回 correct 之前 (Raw Reference)
            # E_raw = E_corrected - Correction
            e_ref_total_raw = e_gnome_total_corr - total_correction
            
            # 3. 归一化为单原子能量
            e_ref_atom_raw = e_ref_total_raw / n_atoms
            
            # 4. 计算误差
            error = e_model - e_ref_atom_raw
            
            # 物理检查：如果误差大于 2.0 eV/atom，通常说明单位依然不对（比如 e_model 其实是总能）
            if abs(error) > 2.0:
                 # 尝试自动修正：如果 e_model 实际上是总能
                 e_model_atom = e_model / n_atoms
                 error = e_model_atom - e_ref_atom_raw
            
            all_data.append({
                'Model': model_name,
                'Task': task.name,
                'Formula': "".join([f"{k}{int(v)}" for k, v in comp.items()]),
                'E_Model_Raw': e_model if abs(e_model - e_ref_atom_raw) < 2.0 else e_model/n_atoms,
                'E_Ref_Raw': e_ref_atom_raw,
                'Error': error
            })

    df = pd.DataFrame(all_data)
    if df.empty: return

    # 计算指标
    summary = []
    for model in df['Model'].unique():
        m_df = df[df['Model'] == model]
        mae = m_df['Error'].abs().mean()
        rmse = np.sqrt((m_df['Error']**2).mean())
        summary.append({
            'Model': model,
            'MAE (meV/atom)': mae * 1000, # 转换为 meV 方便查看
            'RMSE (meV/atom)': rmse * 1000,
            'Count': len(m_df)
        })
    
    summary_df = pd.DataFrame(summary)
    print("\n--- Benchmark Metrics (meV/atom) ---")
    print(summary_df.to_string(index=False))
    
    df.to_csv('gnome_comparison_raw_basis.csv', index=False)
    summary_df.to_csv('gnome_metrics_summary.csv', index=False)

if __name__ == "__main__":
    process_gnome_benchmarks()