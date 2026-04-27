#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
METRICS = BASE / "generated" / "gnome_metrics_summary.csv"
OUT = BASE / "generated" / "Figure_GNoME_main.png"

models = [
    "OpenCSP-L6", "OpenCSP-L12", "OpenCSP-L24",
    "MACE-MPA-0", "MatterSim v1 5M", "GRACE-2L-OAM", "DPA-3.1-3M-FT"
]


def main():
    df = pd.read_csv(METRICS)
    mae_map = dict(zip(df["Model"], df["VASP_relax_SP_MAE_meV_per_atom"]))
    rmse_map = dict(zip(df["Model"], df["VASP_relax_SP_RMSE_meV_per_atom"]))
    e_mae = [float(mae_map[m]) for m in models]
    e_rmse = [float(rmse_map[m]) for m in models]

    plt.rcParams["font.size"] = 14
    plt.rcParams["axes.linewidth"] = 1.5
    plt.rcParams["xtick.major.width"] = 1.5
    plt.rcParams["ytick.major.width"] = 1.5
    plt.rcParams["xtick.major.size"] = 6
    plt.rcParams["ytick.major.size"] = 6
    plt.rcParams["xtick.minor.size"] = 4
    plt.rcParams["ytick.minor.size"] = 4
    plt.rcParams["xtick.minor.width"] = 1.5
    plt.rcParams["ytick.minor.width"] = 1.5

    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ["#DA6C6C", "#FFCCB3", "#FFD23F", "#98D2C0", "#4F959D", "#205781"]
    bar_width = 0.35
    x_pos = np.arange(len(models))

    bars1 = ax.bar(
        x_pos - bar_width / 2,
        e_mae,
        bar_width,
        label='${\\mathrm{E_{MAE}}}$',
        color=colors[0],
        alpha=0.8,
        edgecolor="white",
        linewidth=1,
    )
    bars2 = ax.bar(
        x_pos + bar_width / 2,
        e_rmse,
        bar_width,
        label='${\\mathrm{E_{RMSE}}}$',
        color=colors[3],
        alpha=0.8,
        edgecolor="white",
        linewidth=1,
    )

    y_min = 10
    y_max = max(max(e_mae), max(e_rmse)) * 1.23
    ax.set_ylim(y_min, y_max)
    ax.set_ylabel("Error (meV/atom)", fontsize=20)
    ax.set_title("Energy Errors", fontsize=22)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(models, rotation=30, ha="right", fontsize=16)
    ax.set_yscale("log")
    ax.tick_params(axis="y", which="major", labelsize=16, width=2, size=8)
    ax.tick_params(axis="x", which="major", width=2, size=8)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.legend(fontsize=16, framealpha=0.9, frameon=False)

    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height * 1.02,
                f"{height:.1f}",
                ha="center",
                va="bottom",
                fontsize=16,
                rotation=0,
            )

    add_value_labels(bars1)
    add_value_labels(bars2)
    plt.tight_layout()
    plt.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
