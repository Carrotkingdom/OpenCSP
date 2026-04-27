# GNoME benchmark upload package

This folder contains the data and scripts needed to reproduce the revised GNoME analysis for the four foundation models:
- MACE-MPA-0
- MatterSim v1 5M
- GRACE-2L-OAM
- DPA-3.1-3M-FT

## Directory structure

- `data/foundation_gnome_energies.csv`
  Consolidated per-task energy table for all four foundation models.
- `scripts/export_foundation_gnome_data.py`
  Rebuilds `foundation_gnome_energies.csv` directly from the original model folders under `../`.
- `scripts/compute_gnome_metrics.py`
  Computes MAE/RMSE against:
  1. raw GNoME reference (after undoing the element corrections), and
  2. the recomputed VASP single-point reference (`energy_vasp_relax`, generated with `MPRelaxSet`, `NSW=0`).
- `scripts/plot_main_gnome_figure.py`
  Reproduces the main-text GNoME bar plot (MAE/RMSE).
- `scripts/generate_gnome_si_tables.py`
  Reproduces the Supplementary Information tables for the reference-sensitivity / outlier analysis.
- `scripts/original/`
  Original scripts kept for provenance:
  - `cal_other.py`
  - `calc_error.py`
  - `plot_energy.py`
  - `plot_distribution.py`

## Important note on the GNoME reference energies

The file `energy_GNoME` stored in each task directory is the **corrected total energy**. For the revised benchmark, the comparison against the original GNoME reference is performed on the **raw** energy basis, following the logic in `cal_other.py`.

The elemental corrections that are removed are:
- Ga: -0.0028805 eV
- Ge: 0.10417085 eV
- Li: -0.00301278 eV
- Mg: 0.0924014 eV
- Na: -0.00447437 eV

In `foundation_gnome_energies.csv` both corrected and raw GNoME energies are stored:
- `energy_gnome_corrected_total_eV`
- `energy_gnome_raw_total_eV`
- `energy_gnome_corrected_eV_per_atom`
- `energy_gnome_raw_eV_per_atom`

## Reproducing the data package from the original task folders

From this `upload/` directory:

```bash
python3 scripts/export_foundation_gnome_data.py
```

This regenerates:

```bash
data/foundation_gnome_energies.csv
```

The script reads the original task folders from:
- `../mace/task.*`
- `../mattersim/task.*`
- `../grace/task.*`
- `../dpa3.1/task.*`

and extracts:
- model-predicted energy (`energy`, already in eV/atom)
- original GNoME total energy (`energy_GNoME`)
- recomputed VASP total energies (`energy_vasp_relax`)
- POSCAR composition / number of atoms

## Reproducing the main-text GNoME figure

First compute the summary metrics:

```bash
python3 scripts/compute_gnome_metrics.py
```

This generates:

```bash
generated/gnome_metrics_summary.csv
```

Then make the main figure:

```bash
python3 scripts/plot_main_gnome_figure.py
```

This generates:

```bash
generated/Figure_GNoME_main.png
```

Notes:
- The foundation-model bars use the recomputed VASP single-point reference (`energy_vasp_relax`).
- The OpenCSP-L6/L12/L24 values are hard-coded from the manuscript because those results were unchanged in this revision.

## Reproducing the Supplementary Information tables

Run:

```bash
python3 scripts/generate_gnome_si_tables.py
```

This generates:

```bash
generated/table_s1_outliers.tex
generated/table_s2_excluding_outliers.tex
generated/table_s3_gd_ln_subsets.tex
generated/si_summary.txt
```

### SI definitions used in the current revision

Outliers are defined using the **mean prediction of the four foundation models** for each task.
A structure is classified as an outlier if both conditions are satisfied:

1. the original raw GNoME energy is closer to the mean foundation-model prediction than the recomputed VASP reference, and
2. the absolute difference between the original raw GNoME energy and the recomputed VASP reference exceeds **400 meV/atom**.

Under this criterion, the revised SI identifies 13 outlier structures.

## Files used for the manuscript

### Main text
- Figure 2 / GNoME benchmark bar chart:
  - `generated/Figure_GNoME_main.png`
  - `generated/gnome_metrics_summary.csv`

### Supplementary Information
- Reference sensitivity / outlier tables:
  - `generated/table_s1_outliers.tex`
  - `generated/table_s2_excluding_outliers.tex`
  - `generated/table_s3_gd_ln_subsets.tex`
  - `generated/si_summary.txt`

## Provenance

The updated scripts were written to reproduce the revised analysis in a cleaner and more transparent way.
The original working scripts are kept in `scripts/original/` for traceability and comparison with the updated workflow.
