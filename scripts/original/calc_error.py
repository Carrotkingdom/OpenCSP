#!/usr/bin/env python3
"""
Compare model-predicted energy (per atom) against 5 reference energies.
For each model and each reference, compute MAE and RMSE (meV/atom).

Usage: cd /root/calypso/hand/step2/valid/4_GNoME && python calc_error.py
"""

import os
import glob
import numpy as np
from ase.io import read

MODELS = ["mace", "mattersim", "grace", "dpa3.1"]
REF_FILES = {
    "energy_GNoME":    "GNoME (raw)",
    "energy_vasp":     "VASP (static)",
    "energy_vasp_relax": "VASP (relax)",
}


def get_natoms(poscar_path):
    atoms = read(poscar_path)
    return len(atoms)


def calc_metrics(errors):
    errors = np.array(errors)
    mae = np.mean(np.abs(errors))
    rmse = np.sqrt(np.mean(errors**2))
    return mae, rmse


def main():
    results = {}

    for model in MODELS:
        model_dir = model
        if not os.path.isdir(model_dir):
            continue

        task_dirs = sorted(glob.glob(os.path.join(model_dir, "task.*")))
        errors_by_ref = {ref: [] for ref in REF_FILES}

        for task_dir in task_dirs:
            energy_file = os.path.join(task_dir, "energy")
            poscar_file = os.path.join(task_dir, "POSCAR")

            if not os.path.exists(energy_file) or not os.path.exists(poscar_file):
                continue

            try:
                e_model = float(open(energy_file).read().strip())  # per atom
                natoms = get_natoms(poscar_file)
            except Exception:
                continue

            for ref_name in REF_FILES:
                ref_path = os.path.join(task_dir, ref_name)
                if not os.path.exists(ref_path):
                    continue
                try:
                    e_ref_total = float(open(ref_path).read().strip())
                    e_ref_atom = e_ref_total / natoms
                    errors_by_ref[ref_name].append(e_model - e_ref_atom)
                except Exception:
                    continue

        results[model] = errors_by_ref

    # Print results
    header = f"{'Model':<12} {'Reference':<20} {'Count':>6} {'MAE(meV/atom)':>14} {'RMSE(meV/atom)':>15}"
    print("=" * len(header))
    print(header)
    print("=" * len(header))

    for model in MODELS:
        if model not in results:
            continue
        for ref_name, label in REF_FILES.items():
            errs = results[model][ref_name]
            if not errs:
                continue
            mae, rmse = calc_metrics(errs)
            print(f"{model:<12} {label:<20} {len(errs):>6} {mae*1000:>14.2f} {rmse*1000:>15.2f}")
        print("-" * len(header))

    print("\nDone.")


if __name__ == "__main__":
    main()
