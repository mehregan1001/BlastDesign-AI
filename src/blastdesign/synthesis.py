"""Integrated synthesis of deterministic sensitivity analyses.

The functions in this module combine existing one-factor-at-a-time
analyses without treating their different sampled intervals as directly
comparable probability distributions or validation domains.
"""

from __future__ import annotations

import json

import pandas as pd

from .sensitivity import (
    build_ash_burden_ratio_ensemble_summary,
    build_diameter_ensemble_summary,
    build_explosive_density_ensemble_summary,
    build_gole_gohar_ash_burden_ratio_sensitivity_table,
    build_gole_gohar_diameter_sensitivity_table,
    build_gole_gohar_explosive_density_sensitivity_table,
    build_gole_gohar_rock_density_sensitivity_table,
    build_gole_gohar_ucs_sensitivity_table,
    build_rock_density_ensemble_summary,
    build_ucs_ensemble_summary,
)


_ANALYSIS_SPECS = (
    {
        "analysis_id": "diameter",
        "parameter_name": "hole_diameter_mm",
        "parameter_label": "Hole diameter",
        "unit": "mm",
        "reference_attr": "reference_hole_diameter_mm",
        "table_builder": (
            build_gole_gohar_diameter_sensitivity_table
        ),
        "ensemble_builder": (
            build_diameter_ensemble_summary
        ),
    },
    {
        "analysis_id": "ucs",
        "parameter_name": "ucs_mpa",
        "parameter_label": (
            "Uniaxial compressive strength"
        ),
        "unit": "MPa",
        "reference_attr": "reference_ucs_mpa",
        "table_builder": (
            build_gole_gohar_ucs_sensitivity_table
        ),
        "ensemble_builder": (
            build_ucs_ensemble_summary
        ),
    },
    {
        "analysis_id": "explosive_density",
        "parameter_name": (
            "explosive_density_g_cm3"
        ),
        "parameter_label": "Explosive density",
        "unit": "g/cm3",
        "reference_attr": (
            "reference_explosive_density_g_cm3"
        ),
        "table_builder": (
            build_gole_gohar_explosive_density_sensitivity_table
        ),
        "ensemble_builder": (
            build_explosive_density_ensemble_summary
        ),
    },
    {
        "analysis_id": "rock_density",
        "parameter_name": "rock_density_g_cm3",
        "parameter_label": "Rock density",
        "unit": "g/cm3",
        "reference_attr": (
            "reference_rock_density_g_cm3"
        ),
        "table_builder": (
            build_gole_gohar_rock_density_sensitivity_table
        ),
        "ensemble_builder": (
            build_rock_density_ensemble_summary
        ),
    },
    {
        "analysis_id": "ash_burden_ratio",
        "parameter_name": "ash_burden_ratio",
        "parameter_label": "Ash burden ratio",
        "unit": "dimensionless",
        "reference_attr": (
            "reference_ash_burden_ratio"
        ),
        "table_builder": (
            build_gole_gohar_ash_burden_ratio_sensitivity_table
        ),
        "ensemble_builder": (
            build_ash_burden_ratio_ensemble_summary
        ),
    },
)


def _build_analysis_results():
    """Generate and validate the five sensitivity analyses."""

    results = []

    for spec in _ANALYSIS_SPECS:
        table = spec["table_builder"]()
        ensemble = spec["ensemble_builder"](
            table
        )

        parameter_name = spec["parameter_name"]

        required_table_columns = {
            parameter_name,
            "model_id",
            "model_name",
            "burden_m",
        }

        missing_table_columns = (
            required_table_columns.difference(
                table.columns
            )
        )

        if missing_table_columns:
            raise ValueError(
                f"{spec['analysis_id']!r} is missing "
                "table columns: "
                f"{sorted(missing_table_columns)}"
            )

        required_ensemble_columns = {
            parameter_name,
            "mean_burden_m",
            "range_m",
        }

        missing_ensemble_columns = (
            required_ensemble_columns.difference(
                ensemble.columns
            )
        )

        if missing_ensemble_columns:
            raise ValueError(
                f"{spec['analysis_id']!r} is missing "
                "ensemble columns: "
                f"{sorted(missing_ensemble_columns)}"
            )

        if table["model_id"].nunique() != 7:
            raise ValueError(
                f"{spec['analysis_id']!r} must contain "
                "exactly seven models."
            )

        inconsistent_names = (
            table.groupby("model_id")["model_name"]
            .nunique()
            .ne(1)
        )

        if inconsistent_names.any():
            raise ValueError(
                f"{spec['analysis_id']!r} contains "
                "inconsistent model names."
            )

        reference_attr = spec["reference_attr"]

        if reference_attr not in table.attrs:
            raise ValueError(
                f"{spec['analysis_id']!r} is missing "
                f"metadata attribute {reference_attr!r}."
            )

        results.append(
            {
                "spec": spec,
                "table": table,
                "ensemble": ensemble,
            }
        )

    return results


def build_integrated_sensitivity_summary() -> pd.DataFrame:
    """Summarize all five deterministic sensitivity analyses.

    The returned metrics describe only the preselected grid used by
    each existing analysis. They must not be interpreted as a global
    ranking of physical importance or predictive uncertainty.
    """

    rows = []

    for analysis in _build_analysis_results():
        spec = analysis["spec"]
        table = analysis["table"]
        ensemble = analysis["ensemble"]

        parameter_name = spec["parameter_name"]

        parameter_values = sorted(
            table[parameter_name]
            .astype(float)
            .drop_duplicates()
            .tolist()
        )

        reference_value = float(
            table.attrs[spec["reference_attr"]]
        )

        reference_rows = ensemble[
            (
                ensemble[parameter_name].astype(float)
                - reference_value
            ).abs()
            <= 1e-12
        ]

        if len(reference_rows) != 1:
            raise ValueError(
                f"{spec['analysis_id']!r} must contain "
                "exactly one ensemble row at its "
                "reference value."
            )

        reference_row = reference_rows.iloc[0]

        distinct_counts = table.groupby(
            "model_id"
        )["burden_m"].nunique()

        model_order = (
            table["model_id"]
            .drop_duplicates()
            .tolist()
        )

        responding_model_ids = [
            model_id
            for model_id in model_order
            if distinct_counts.loc[model_id] > 1
        ]

        minimum_range = float(
            ensemble["range_m"].min()
        )
        maximum_range = float(
            ensemble["range_m"].max()
        )

        minimum_parameter_values = (
            ensemble.loc[
                (
                    ensemble["range_m"]
                    - minimum_range
                ).abs()
                <= 1e-12,
                parameter_name,
            ]
            .astype(float)
            .tolist()
        )

        maximum_parameter_values = (
            ensemble.loc[
                (
                    ensemble["range_m"]
                    - maximum_range
                ).abs()
                <= 1e-12,
                parameter_name,
            ]
            .astype(float)
            .tolist()
        )

        rows.append(
            {
                "analysis_id": spec["analysis_id"],
                "parameter_name": parameter_name,
                "parameter_label": (
                    spec["parameter_label"]
                ),
                "unit": spec["unit"],
                "reference_value": reference_value,
                "sampled_minimum": (
                    parameter_values[0]
                ),
                "sampled_maximum": (
                    parameter_values[-1]
                ),
                "sample_count": len(
                    parameter_values
                ),
                "responding_model_count": len(
                    responding_model_ids
                ),
                "responding_model_ids_json": (
                    json.dumps(
                        responding_model_ids
                    )
                ),
                "reference_mean_burden_m": float(
                    reference_row["mean_burden_m"]
                ),
                "reference_range_m": float(
                    reference_row["range_m"]
                ),
                "minimum_ensemble_range_m": (
                    minimum_range
                ),
                "minimum_range_parameter_values_json": (
                    json.dumps(
                        minimum_parameter_values
                    )
                ),
                "maximum_ensemble_range_m": (
                    maximum_range
                ),
                "maximum_range_parameter_values_json": (
                    json.dumps(
                        maximum_parameter_values
                    )
                ),
                "ensemble_range_span_m": (
                    maximum_range - minimum_range
                ),
            }
        )

    summary = pd.DataFrame(rows)

    summary.attrs["decision_gate"] = (
        "RESEARCH_COMPARATOR_ONLY"
    )
    summary.attrs["analysis_type"] = (
        "cross_analysis_synthesis"
    )
    summary.attrs["comparison_warning"] = (
        "Each sensitivity analysis uses a different "
        "preselected grid, physical unit, empirical domain, "
        "and model response structure. Cross-analysis values "
        "must not be interpreted as a universal ranking of "
        "physical importance, uncertainty, or predictive "
        "accuracy."
    )

    return summary


def build_model_parameter_dependency_matrix() -> pd.DataFrame:
    """Build a seven-model by five-parameter response matrix."""

    analyses = _build_analysis_results()

    first_table = analyses[0]["table"]

    matrix = (
        first_table[
            [
                "model_id",
                "model_name",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    matrix.attrs.clear()

    canonical_ids = set(matrix["model_id"])
    canonical_names = dict(
        zip(
            matrix["model_id"],
            matrix["model_name"],
        )
    )

    parameter_columns = []

    for analysis in analyses:
        spec = analysis["spec"]
        table = analysis["table"]
        parameter_name = spec["parameter_name"]

        observed_ids = set(table["model_id"])

        if observed_ids != canonical_ids:
            raise ValueError(
                f"{spec['analysis_id']!r} contains a "
                "different model set."
            )

        observed_names = (
            table.groupby("model_id")["model_name"]
            .first()
            .to_dict()
        )

        if observed_names != canonical_names:
            raise ValueError(
                f"{spec['analysis_id']!r} contains "
                "model-name mappings inconsistent with "
                "the canonical comparison."
            )

        distinct_counts = table.groupby(
            "model_id"
        )["burden_m"].nunique()

        response_map = (
            distinct_counts.gt(1).to_dict()
        )

        matrix[parameter_name] = (
            matrix["model_id"]
            .map(response_map)
            .astype(bool)
        )

        parameter_columns.append(
            parameter_name
        )

    matrix["responsive_parameter_count"] = (
        matrix[parameter_columns]
        .sum(axis=1)
        .astype(int)
    )

    matrix.attrs["decision_gate"] = (
        "RESEARCH_COMPARATOR_ONLY"
    )
    matrix.attrs["analysis_type"] = (
        "model_parameter_dependency_matrix"
    )
    matrix.attrs["interpretation_warning"] = (
        "A True value means that a reconstructed model's "
        "numerical output changes somewhere on the sampled "
        "grid. It does not establish predictive importance, "
        "field sensitivity, causal influence, or validation."
    )

    return matrix