"""Regenerate Konya density-elasticity CSVs, metadata, and comparison figure.

Run from the project root with:
    python scripts/generate_konya_density_elasticity_artifacts.py

These outputs describe analytical local responses of the reconstructed
equations. They retain the RESEARCH_COMPARATOR_ONLY decision gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from blastdesign.density_elasticity import (
    build_gole_gohar_konya_density_elasticity_table,
    build_konya_density_elasticity_summary,
)


COLUMN_UNITS = {
    "model_id": "identifier",
    "model_name": "text",
    "hole_diameter_mm": "mm",
    "explosive_density_g_cm3": "g/cm3",
    "rock_density_g_cm3": "g/cm3",
    "explosive_to_rock_density_ratio": "dimensionless",
    "burden_m": "m",
    "explosive_density_elasticity": "dimensionless",
    "rock_density_elasticity": "dimensionless",
}


def build_elasticity_artifact_metadata(
    reference: pd.DataFrame,
    grid: pd.DataFrame,
) -> dict:
    """Preserve units and DataFrame attributes outside the plain CSVs."""
    metadata = {
        "schema_version": 1,
        "decision_gate": "RESEARCH_COMPARATOR_ONLY",
        "column_units": COLUMN_UNITS.copy(),
        "calculation_source": "blastdesign.density_elasticity",
        "artifacts": {
            "konya_density_elasticity_reference.csv": {
                "row_count": len(reference),
                "columns": reference.columns.tolist(),
                "attributes": reference.attrs,
            },
            "konya_density_elasticity_grid.csv": {
                "row_count": len(grid),
                "columns": grid.columns.tolist(),
                "attributes": grid.attrs,
            },
        },
    }
    # Normalize tuple-valued attributes to JSON arrays and reject NaN/Infinity.
    return json.loads(json.dumps(metadata, allow_nan=False))


def plot_konya_density_elasticity_comparison(
    reference: pd.DataFrame,
    grid: pd.DataFrame,
):
    """Plot the ratio response and Konya 1983 values at the sampled pairs.

    Lines in the left panel show the exact analytical elasticity formulas.
    Right-panel colors show sampled values, without contour interpolation.
    """
    konya_1983 = grid.loc[grid["model_id"].eq("CONV_KONYA_1983")]
    ratio = konya_1983["explosive_to_rock_density_ratio"]
    q = np.linspace(float(ratio.min()), float(ratio.max()), 400)
    q_reference = float(reference["explosive_to_rock_density_ratio"].iloc[0])
    reference_1983 = reference.loc[
        reference["model_id"].eq("CONV_KONYA_1983")
    ].iloc[0]
    heatmap = konya_1983.pivot(
        index="explosive_density_g_cm3",
        columns="rock_density_g_cm3",
        values="explosive_density_elasticity",
    ).sort_index().sort_index(axis=1)

    with plt.rc_context({"font.size": 10, "axes.titlesize": 11}):
        figure, axes = plt.subplots(1, 2, figsize=(12.5, 5.2))
        figure.subplots_adjust(left=0.075, right=0.91, bottom=0.22,
                               top=0.82, wspace=0.31)
        figure.suptitle("Analytical local density elasticities of Konya equations",
                         fontsize=14, y=0.97)
        figure.text(0.5, 0.91,
                    "Reconstructed equations at fixed hole diameter; research comparison only",
                    ha="center", fontsize=10, color="#444444")

        left, right = axes
        left.plot(q, np.full_like(q, 0.33), color="#1f77b4", linewidth=2,
                  label="Konya 1972: 0.33")
        left.plot(q, q / (q + 0.75), color="#d95f02", linewidth=2,
                  label="Konya 1983: q / (q + 0.75)")
        left.scatter(ratio, konya_1983["explosive_density_elasticity"],
                     s=12, color="#d95f02", alpha=0.65, zorder=3)
        left.axvline(q_reference, color="#555555", linestyle="--", linewidth=1)
        left.scatter([q_reference], [reference_1983["explosive_density_elasticity"]],
                     marker="*", s=170, color="#222222", zorder=5,
                     label="Reference density pair")
        left.set(title="(a) Exact analytical response and sampled ratios",
                 xlabel=r"Explosive-to-rock density ratio, $q = \rho_e / \rho_r$",
                 ylabel=r"Explosive-density elasticity, $E_{\rho_e}$",
                 xlim=(float(q.min()), float(q.max())), ylim=(0.12, 0.47))
        left.grid(alpha=0.2)
        left.legend(loc="upper left", fontsize=8.5, framealpha=0.95)

        rock = heatmap.columns.to_numpy(dtype=float)
        explosive = heatmap.index.to_numpy(dtype=float)
        mesh = right.pcolormesh(rock, explosive, heatmap.to_numpy(dtype=float),
                                shading="nearest", cmap="viridis",
                                vmin=float(heatmap.min().min()),
                                vmax=float(heatmap.max().max()))
        right.scatter(konya_1983["rock_density_g_cm3"],
                      konya_1983["explosive_density_g_cm3"],
                      s=5, color="white", alpha=0.7)
        right.scatter([reference_1983["rock_density_g_cm3"]],
                      [reference_1983["explosive_density_g_cm3"]],
                      marker="*", s=180, color="white", edgecolors="#222222",
                      linewidths=0.8, zorder=5)
        right.set(title="(b) Konya 1983 at sampled density pairs",
                  xlabel=r"Rock density, $\rho_r$ (g/cm$^3$)",
                  ylabel=r"Explosive density, $\rho_e$ (g/cm$^3$)",
                  xlim=(float(rock.min()), float(rock.max())),
                  ylim=(float(explosive.min()), float(explosive.max())))
        right.set_xticks([1.8, 2.75, 3.75, 4.37, 5.3])
        right.set_yticks(explosive)
        colorbar = figure.colorbar(mesh, ax=right, pad=0.025, fraction=0.045)
        colorbar.set_label(r"$E_{\rho_e}$ (dimensionless)")

        figure.text(0.075, 0.105,
                    r"For both equations: $E_{\rho_r} = -E_{\rho_e}$. "
                    "Elasticity describes a differential fractional response.",
                    fontsize=10)
        figure.text(0.075, 0.055,
                    "Exploratory density grid. No field validation, calibrated uncertainty, "
                    "or operational recommendation.", fontsize=9, color="#444444")
    return figure


def generate_artifacts(project_root: Path):
    """Build and save the default reference/grid outputs; return their paths."""
    project_root = Path(project_root).resolve()
    data_directory = project_root / "data" / "processed"
    figure_directory = project_root / "outputs" / "figures"
    data_directory.mkdir(parents=True, exist_ok=True)
    figure_directory.mkdir(parents=True, exist_ok=True)

    reference = build_konya_density_elasticity_summary()
    grid = build_gole_gohar_konya_density_elasticity_table()
    paths = {
        "reference": data_directory / "konya_density_elasticity_reference.csv",
        "grid": data_directory / "konya_density_elasticity_grid.csv",
        "metadata": data_directory / "konya_density_elasticity_metadata.json",
        "figure": figure_directory / "konya_density_elasticity_comparison.png",
    }
    reference.to_csv(paths["reference"], index=False, encoding="utf-8",
                     lineterminator="\n")
    grid.to_csv(paths["grid"], index=False, encoding="utf-8", lineterminator="\n")
    metadata = build_elasticity_artifact_metadata(reference, grid)
    with paths["metadata"].open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(metadata, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")

    figure = plot_konya_density_elasticity_comparison(reference, grid)
    try:
        figure.savefig(paths["figure"], dpi=300, facecolor="white")
    finally:
        plt.close(figure)
    return reference, grid, paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path,
                        default=Path(__file__).resolve().parents[1],
                        help="Project directory (defaults to this script's parent project).")
    arguments = parser.parse_args()
    reference, grid, paths = generate_artifacts(arguments.project_root)
    print(f"Reference table: {reference.shape}")
    print(f"Grid table: {grid.shape}")
    print(f"Density pairs: {grid.attrs['scenario_count']}")
    print("Decision gate: RESEARCH_COMPARATOR_ONLY")
    for path in paths.values():
        print(f"Wrote: {path}")


if __name__ == "__main__":
    main()
