#!/usr/bin/env python3
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'data' / 'foundation_gnome_energies.csv'
OUT = BASE / 'generated' / 'gnome_metrics_summary.csv'

OPENCSP = {
    'OpenCSP-L6':  {'VASP_MAE': 20.7, 'VASP_RMSE': 27.7},
    'OpenCSP-L12': {'VASP_MAE': 17.2, 'VASP_RMSE': 23.1},
    'OpenCSP-L24': {'VASP_MAE': 15.6, 'VASP_RMSE': 21.4},
}
MODEL_LABELS = {
    'mace': 'MACE-MPA-0',
    'mattersim': 'MatterSim v1 5M',
    'grace': 'GRACE-2L-OAM',
    'dpa3.1': 'DPA-3.1-3M-FT',
}


def metrics(err):
    err = np.asarray(err, dtype=float)
    return np.mean(np.abs(err)), np.sqrt(np.mean(err**2)), np.mean(err)


def main():
    df = pd.read_csv(DATA)
    rows = []
    for mdir, label in MODEL_LABELS.items():
        sub = df[df['model_dir'] == mdir].copy()
        err_raw = (sub['energy_model_eV_per_atom'] - sub['energy_gnome_raw_eV_per_atom']) * 1000
        err_vasp = (sub['energy_model_eV_per_atom'] - sub['energy_vasp_relax_eV_per_atom']) * 1000
        mae_raw, rmse_raw, mean_raw = metrics(err_raw)
        mae_vasp, rmse_vasp, mean_vasp = metrics(err_vasp)
        rows.append({
            'Model': label,
            'Count': len(sub),
            'GNoME_raw_MAE_meV_per_atom': round(mae_raw, 1),
            'GNoME_raw_RMSE_meV_per_atom': round(rmse_raw, 1),
            'GNoME_raw_MeanErr_meV_per_atom': round(mean_raw, 1),
            'VASP_relax_SP_MAE_meV_per_atom': round(mae_vasp, 1),
            'VASP_relax_SP_RMSE_meV_per_atom': round(rmse_vasp, 1),
            'VASP_relax_SP_MeanErr_meV_per_atom': round(mean_vasp, 1),
        })
    for model, vals in OPENCSP.items():
        rows.append({
            'Model': model,
            'Count': 1008,
            'GNoME_raw_MAE_meV_per_atom': '',
            'GNoME_raw_RMSE_meV_per_atom': '',
            'GNoME_raw_MeanErr_meV_per_atom': '',
            'VASP_relax_SP_MAE_meV_per_atom': vals['VASP_MAE'],
            'VASP_relax_SP_RMSE_meV_per_atom': vals['VASP_RMSE'],
            'VASP_relax_SP_MeanErr_meV_per_atom': '',
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    print(out.to_string(index=False))
    print(f'Wrote {OUT}')


if __name__ == '__main__':
    main()
