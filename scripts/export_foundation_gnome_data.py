#!/usr/bin/env python3
import os
import csv
from collections import Counter
from pathlib import Path
from ase.io import read

BASE = Path(__file__).resolve().parents[2]  # 4_GNoME/
OUTBASE = Path(__file__).resolve().parents[1]
OUTCSV = OUTBASE / 'data' / 'foundation_gnome_energies.csv'
MODELS = ['mace', 'mattersim', 'grace', 'dpa3.1']
PP_CORR = {
    'Ga': -0.0028805,
    'Ge': 0.10417085,
    'Li': -0.00301278,
    'Mg': 0.0924014,
    'Na': -0.00447437,
}
LAN = {'La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu'}


def main():
    rows = []
    for model in MODELS:
        mdir = BASE / model
        if not mdir.is_dir():
            continue
        for task in sorted(p for p in mdir.iterdir() if p.is_dir() and p.name.startswith('task.')):
            poscar = task / 'POSCAR'
            f_model = task / 'energy'
            f_gnome = task / 'energy_GNoME'
            f_vasp_relax = task / 'energy_vasp_relax'
            if not (poscar.exists() and f_model.exists() and f_gnome.exists() and f_vasp_relax.exists()):
                continue
            atoms = read(str(poscar))
            natoms = len(atoms)
            comp = Counter(atoms.get_chemical_symbols())
            formula = ''.join(f'{el}{int(n)}' for el, n in comp.items())
            total_corr = sum(comp.get(el, 0) * val for el, val in PP_CORR.items())
            e_model = float(f_model.read_text().strip())
            e_gnome_total = float(f_gnome.read_text().strip())
            e_vasp_relax_total = float(f_vasp_relax.read_text().strip())
            e_gnome_raw_total = e_gnome_total - total_corr
            rows.append({
                'model_dir': model,
                'task': task.name,
                'formula': formula,
                'natoms': natoms,
                'elements': ' '.join(sorted(comp.keys())),
                'contains_lanthanide': any(el in LAN for el in comp),
                'contains_Gd': 'Gd' in comp,
                'gnome_correction_total_eV': total_corr,
                'energy_model_eV_per_atom': e_model,
                'energy_gnome_corrected_total_eV': e_gnome_total,
                'energy_gnome_raw_total_eV': e_gnome_raw_total,
                'energy_gnome_corrected_eV_per_atom': e_gnome_total / natoms,
                'energy_gnome_raw_eV_per_atom': e_gnome_raw_total / natoms,
                'energy_vasp_relax_total_eV': e_vasp_relax_total,
                'energy_vasp_relax_eV_per_atom': e_vasp_relax_total / natoms,
            })
    OUTCSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTCSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f'Wrote {len(rows)} rows to {OUTCSV}')


if __name__ == '__main__':
    main()
