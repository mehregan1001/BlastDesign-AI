"""Controlled sensitivity analyses for reconstructed burden models."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from .audit import gole_gohar_reference_inputs
from .comparison import evaluate_conventional_burden_models
from .validation import positive_float


DEFAULT_DIAMETER_GRID_MM = tuple(
    float(value)
    for value in range(181, 312, 10)
)


def build_gole_gohar_diameter_sensitivity_table(
    hole_diameters_mm: Iterable[float] | None = None,
) -> pd.DataFrame:
    """Build a seven-model diameter-sensitivity comparison.

    The comparison window is greater than 180 mm through 311 mm.
    This selects the Lopez Jimeno large-hole branch and avoids
    extrapolating Rustan beyond its documented upper limit.

    The window is not a universal validation domain for all models.
    """

    if hole_diameters_mm is None:
        raw_diameters = list(
            DEFAULT_DIAMETER_GRID_MM
        )
    else:
        if isinstance(
            hole_diameters_mm,
            (str, bytes),
        ):
            raise TypeError(
                "hole_diameters_mm must be an iterable "
                "of numerical values."
            )

        try:
            raw_diameters = list(
                hole_diameters_mm
            )
        except TypeError as error:
            raise TypeError(
                "hole_diameters_mm must be an iterable "
                "of numerical values."
            ) from error

    if not raw_diameters:
        raise ValueError(
            "At least one hole diameter is required."
        )

    diameters = [
        positive_float(
            value,
            "hole_diameter_mm",
        )
        for value in raw_diameters
    ]

    if len(set(diameters)) != len(diameters):
        raise ValueError(
            "Hole-diameter values must be unique."
        )

    for diameter in diameters:
        if not 180.0 < diameter <= 311.0:
            raise ValueError(
                "Diameter sensitivity requires values "
                "greater than 180 mm and no greater "
                "than 311 mm."
            )

    diameters.sort()

    reference_inputs = (
        gole_gohar_reference_inputs()
    )

    tables = []

    for diameter in diameters:
        scenario_inputs = (
            reference_inputs.copy()
        )
        scenario_inputs[
            "hole_diameter_mm"
        ] = diameter

        model_table = (
            evaluate_conventional_burden_models(
                **scenario_inputs
            )
        )

        model_table.insert(
            0,
            "hole_diameter_mm",
            diameter,
        )

        tables.append(model_table)

    result = pd.concat(
        tables,
        ignore_index=True,
    )

    fixed_inputs = reference_inputs.copy()
    reference_diameter = fixed_inputs.pop(
        "hole_diameter_mm"
    )

    result.attrs["analysis_type"] = (
        "one_factor_at_a_time"
    )
    result.attrs["varied_parameter"] = (
        "hole_diameter_mm"
    )
    result.attrs["reference_hole_diameter_mm"] = (
        reference_diameter
    )
    result.attrs["fixed_inputs"] = fixed_inputs
    result.attrs["comparison_window_mm"] = {
        "lower_bound_exclusive": 180.0,
        "upper_bound_inclusive": 311.0,
    }
    result.attrs["decision_gate"] = (
        "RESEARCH_COMPARATOR_ONLY"
    )
    result.attrs["window_warning"] = (
        "The comparison window aligns the Lopez Jimeno "
        "large-hole branch with the documented Rustan "
        "upper limit; it is not a universal validation "
        "domain for all models."
    )

    return result

_REQUIRED_SENSITIVITY_COLUMNS = {
    "hole_diameter_mm",
    "model_id",
    "model_name",
    "burden_m",
}


def _validate_sensitivity_table(
    sensitivity_table: pd.DataFrame,
) -> None:
    """Validate the structure of a seven-model sensitivity table."""

    if not isinstance(
        sensitivity_table,
        pd.DataFrame,
    ):
        raise TypeError(
            "sensitivity_table must be a pandas DataFrame."
        )

    missing_columns = (
        _REQUIRED_SENSITIVITY_COLUMNS.difference(
            sensitivity_table.columns
        )
    )

    if missing_columns:
        raise ValueError(
            "Missing sensitivity-table columns: "
            f"{sorted(missing_columns)}"
        )

    if sensitivity_table.empty:
        raise ValueError(
            "The sensitivity table must not be empty."
        )

    if sensitivity_table.duplicated(
        subset=[
            "hole_diameter_mm",
            "model_id",
        ]
    ).any():
        raise ValueError(
            "The sensitivity table contains duplicate "
            "diameter-model combinations."
        )

    model_counts = (
        sensitivity_table.groupby(
            "hole_diameter_mm"
        )["model_id"]
        .nunique()
    )

    if not model_counts.eq(7).all():
        raise ValueError(
            "Every diameter must contain exactly seven "
            "unique burden models."
        )


def build_diameter_ensemble_summary(
    sensitivity_table: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize deterministic model disagreement by diameter."""

    _validate_sensitivity_table(
        sensitivity_table
    )

    summary = (
        sensitivity_table.groupby(
            "hole_diameter_mm",
            as_index=False,
        )
        .agg(
            model_count=(
                "model_id",
                "nunique",
            ),
            mean_burden_m=(
                "burden_m",
                "mean",
            ),
            median_burden_m=(
                "burden_m",
                "median",
            ),
            minimum_burden_m=(
                "burden_m",
                "min",
            ),
            maximum_burden_m=(
                "burden_m",
                "max",
            ),
        )
        .sort_values("hole_diameter_mm")
        .reset_index(drop=True)
    )

    summary["range_m"] = (
        summary["maximum_burden_m"]
        - summary["minimum_burden_m"]
    )

    summary.attrs["decision_gate"] = (
        "RESEARCH_COMPARATOR_ONLY"
    )
    summary.attrs["interpretation_warning"] = (
        "The reported ranges represent deterministic "
        "model-form disagreement, not confidence intervals."
    )

    return summary


def build_model_diameter_response_summary(
    sensitivity_table: pd.DataFrame,
    reference_diameter_mm: float = 251.0,
) -> pd.DataFrame:
    """Summarize each model's response across the diameter window."""

    _validate_sensitivity_table(
        sensitivity_table
    )

    reference_diameter = positive_float(
        reference_diameter_mm,
        "reference_diameter_mm",
    )

    rows = []

    for model_id, group in (
        sensitivity_table.groupby(
            "model_id",
            sort=False,
        )
    ):
        model_names = (
            group["model_name"]
            .drop_duplicates()
            .tolist()
        )

        if len(model_names) != 1:
            raise ValueError(
                f"Model {model_id!r} has inconsistent names."
            )

        ordered = (
            group.sort_values(
                "hole_diameter_mm"
            )
            .reset_index(drop=True)
        )

        reference_rows = ordered[
            ordered["hole_diameter_mm"].eq(
                reference_diameter
            )
        ]

        if len(reference_rows) != 1:
            raise ValueError(
                f"Model {model_id!r} must contain exactly "
                f"one row at {reference_diameter} mm."
            )

        lower_row = ordered.iloc[0]
        upper_row = ordered.iloc[-1]
        reference_row = reference_rows.iloc[0]

        lower_burden = float(
            lower_row["burden_m"]
        )
        upper_burden = float(
            upper_row["burden_m"]
        )
        endpoint_change = (
            upper_burden - lower_burden
        )

        rows.append(
            {
                "model_id": str(model_id),
                "model_name": model_names[0],
                "lower_diameter_mm": float(
                    lower_row[
                        "hole_diameter_mm"
                    ]
                ),
                "upper_diameter_mm": float(
                    upper_row[
                        "hole_diameter_mm"
                    ]
                ),
                "burden_at_lower_endpoint_m": (
                    lower_burden
                ),
                "reference_diameter_mm": (
                    reference_diameter
                ),
                "reference_burden_m": float(
                    reference_row["burden_m"]
                ),
                "burden_at_upper_endpoint_m": (
                    upper_burden
                ),
                "endpoint_change_m": (
                    endpoint_change
                ),
                "endpoint_change_percent": (
                    endpoint_change
                    / lower_burden
                    * 100.0
                ),
                "burden_range_m": float(
                    ordered["burden_m"].max()
                    - ordered["burden_m"].min()
                ),
            }
        )

    summary = pd.DataFrame(rows)

    summary.attrs["decision_gate"] = (
        "RESEARCH_COMPARATOR_ONLY"
    )
    summary.attrs["interpretation_warning"] = (
        "Endpoint changes describe deterministic equation "
        "responses and do not establish predictive accuracy."
    )

    return summary