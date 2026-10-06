"""Regenerate the default joint-density CSV research artifacts.

Run from the mining-ai environment:
    python scripts/generate_joint_density_artifacts.py
"""

from pathlib import Path

from blastdesign import (
    build_gole_gohar_joint_density_sensitivity_table,
    build_joint_density_ensemble_summary,
    build_model_joint_density_response_summary,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    output_directory = PROJECT_ROOT / "data" / "processed"
    output_directory.mkdir(parents=True, exist_ok=True)

    model_outputs = build_gole_gohar_joint_density_sensitivity_table()
    ensemble_summary = build_joint_density_ensemble_summary(model_outputs)
    model_response_summary = build_model_joint_density_response_summary(
        model_outputs
    )

    artifacts = (
        ("joint_density_sensitivity_model_outputs.csv", model_outputs),
        ("joint_density_sensitivity_ensemble_summary.csv", ensemble_summary),
        (
            "joint_density_sensitivity_model_response_summary.csv",
            model_response_summary,
        ),
    )

    for filename, table in artifacts:
        path = output_directory / filename
        table.to_csv(
            path,
            index=False,
            encoding="utf-8",
            lineterminator="\n",
        )
        print(
            f"Wrote {filename}: {len(table)} rows, "
            f"{len(table.columns)} columns"
        )

    print(f"Output directory: {output_directory}")
    print(f"Decision gate: {model_outputs.attrs['decision_gate']}")
    print(
        "CSV files store numerical tables; interpretation warnings "
        "are documented in the module and analysis notebook."
    )


if __name__ == "__main__":
    main()
