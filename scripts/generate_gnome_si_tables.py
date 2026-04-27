#!/usr/bin/env python3
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data" / "foundation_gnome_energies.csv"
OUTDIR = BASE / "generated"
OUTDIR.mkdir(exist_ok=True)

MODEL_LABELS = {
    "mace": "MACE-MPA-0",
    "mattersim": "MatterSim v1 5M",
    "grace": "GRACE-2L-OAM",
    "dpa3.1": "DPA-3.1-3M-FT",
}


def mae_rmse(x):
    x = np.asarray(x, dtype=float)
    return np.mean(np.abs(x)), np.sqrt(np.mean(x**2))


def main():
    df = pd.read_csv(DATA)
    df["err_gnome_raw_meV"] = (df["energy_model_eV_per_atom"] - df["energy_gnome_raw_eV_per_atom"]) * 1000
    df["err_vasp_relax_meV"] = (df["energy_model_eV_per_atom"] - df["energy_vasp_relax_eV_per_atom"]) * 1000
    df["ref_diff_meV"] = (df["energy_gnome_raw_eV_per_atom"] - df["energy_vasp_relax_eV_per_atom"]) * 1000
    df["formula_latex"] = df["formula"].str.replace(r'([A-Z][a-z]?)(\d+)', r'\1_{\2}', regex=True)

    task_mean = df.groupby(["task", "formula", "natoms", "contains_lanthanide", "contains_Gd", "formula_latex"], as_index=False).agg({
        "energy_model_eV_per_atom": "mean",
        "energy_gnome_raw_eV_per_atom": "first",
        "energy_vasp_relax_eV_per_atom": "first",
    })
    task_mean["err_gnome_raw_meV"] = (task_mean["energy_model_eV_per_atom"] - task_mean["energy_gnome_raw_eV_per_atom"]) * 1000
    task_mean["err_vasp_relax_meV"] = (task_mean["energy_model_eV_per_atom"] - task_mean["energy_vasp_relax_eV_per_atom"]) * 1000
    task_mean["ref_diff_meV"] = (task_mean["energy_gnome_raw_eV_per_atom"] - task_mean["energy_vasp_relax_eV_per_atom"]) * 1000

    spread = df.groupby("task")["energy_model_eV_per_atom"].agg(lambda s: (s.max() - s.min()) * 1000).rename("spread_meV")
    task_mean = task_mean.merge(spread, on="task")

    outlier_mask = (task_mean["err_gnome_raw_meV"].abs() < task_mean["err_vasp_relax_meV"].abs()) & (task_mean["ref_diff_meV"].abs() > 400)
    outliers = task_mean[outlier_mask].copy().sort_values("err_vasp_relax_meV", key=lambda s: s.abs(), ascending=False)

    rows_s1 = []
    for _, r in outliers.iterrows():
        rows_s1.append(
            f"$\\mathrm{{{r['formula_latex']}}}$ & {int(r['natoms'])} & {'Yes' if r['contains_lanthanide'] else 'No'} & ${r['energy_model_eV_per_atom']:.3f}$ & {r['spread_meV']:.1f} & {r['err_gnome_raw_meV']:.1f} & {r['err_vasp_relax_meV']:.1f} \\\\"
        )
    (OUTDIR / "table_s1_outliers.tex").write_text("\n".join(rows_s1))

    rows_s2 = []
    for subset_name, subset_df in [("All 1,008", df), (f"Excluding {len(outliers)} outliers", df[~df['task'].isin(outliers['task'])])]:
        for mdir, label in MODEL_LABELS.items():
            sub = subset_df[subset_df['model_dir'] == mdir]
            mae, rmse = mae_rmse(sub["err_vasp_relax_meV"])
            rows_s2.append(f"{subset_name} & {label} & {len(sub)} & {mae:.1f} & {rmse:.1f} \\\\")
    (OUTDIR / "table_s2_excluding_outliers.tex").write_text("\n".join(rows_s2))

    rows_s3 = []
    remaining = df[~df['task'].isin(outliers['task'])].copy()
    for mdir, label in MODEL_LABELS.items():
        sub = remaining[remaining['model_dir'] == mdir]
        gd = sub[sub['contains_Gd'] == True]
        other_ln = sub[(sub['contains_lanthanide'] == True) & (sub['contains_Gd'] == False)]
        no_ln = sub[sub['contains_lanthanide'] == False]
        mae1, rmse1 = mae_rmse(gd['err_vasp_relax_meV'])
        mae2, rmse2 = mae_rmse(other_ln['err_vasp_relax_meV'])
        mae3, rmse3 = mae_rmse(no_ln['err_vasp_relax_meV'])
        rows_s3.append(f"{label} & {gd['task'].nunique()} & {mae1:.1f} & {rmse1:.1f} & {other_ln['task'].nunique()} & {mae2:.1f} & {rmse2:.1f} & {no_ln['task'].nunique()} & {mae3:.1f} & {rmse3:.1f} \\\\")
    (OUTDIR / "table_s3_gd_ln_subsets.tex").write_text("\n".join(rows_s3))

    summary = [
        f"outlier_count={len(outliers)}",
        f"outliers_with_lanthanide={int(outliers['contains_lanthanide'].sum())}",
        f"outliers_with_Gd={int(outliers['contains_Gd'].sum())}",
        f"remaining_tasks={task_mean[~outlier_mask]['task'].nunique()}",
        f"remaining_Gd_tasks={task_mean[(~outlier_mask) & (task_mean['contains_Gd']==True)]['task'].nunique()}",
        f"remaining_other_ln_tasks={task_mean[(~outlier_mask) & (task_mean['contains_lanthanide']==True) & (task_mean['contains_Gd']==False)]['task'].nunique()}",
        f"remaining_no_ln_tasks={task_mean[(~outlier_mask) & (task_mean['contains_lanthanide']==False)]['task'].nunique()}",
    ]
    (OUTDIR / "si_summary.txt").write_text("\n".join(summary))
    print("Wrote generated LaTeX tables and summary text.")


if __name__ == "__main__":
    main()
