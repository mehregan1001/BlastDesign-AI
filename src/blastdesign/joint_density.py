"""Joint density-grid comparison of reconstructed burden equations."""

from __future__ import annotations

from collections.abc import Iterable
from math import isfinite

import numpy as np
import pandas as pd

from .audit import gole_gohar_reference_inputs
from .comparison import evaluate_conventional_burden_models
from .sensitivity import (
    DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3,
    DEFAULT_ROCK_DENSITY_GRID_G_CM3,
)
from .validation import positive_float


def _validated_density_grid(
    values: Iterable[float] | None,
    default_values: Iterable[float],
    parameter_name: str,
) -> list[float]:
    """Return a sorted, nonempty grid of unique positive densities."""
    if values is None:
        raw_values = list(default_values)
    else:
        if isinstance(values, (str, bytes)):
            raise TypeError(
                f"{parameter_name} must be an iterable of numerical values."
            )
        try:
            raw_values = list(values)
        except TypeError as error:
            raise TypeError(
                f"{parameter_name} must be an iterable of numerical values."
            ) from error

    if not raw_values:
        raise ValueError(f"At least one {parameter_name} value is required.")

    try:
        density_values = [
            positive_float(value, parameter_name)
            for value in raw_values
        ]
    except OverflowError as error:
        raise ValueError(
            f"{parameter_name} must contain finite positive values."
        ) from error

    if len(set(density_values)) != len(density_values):
        raise ValueError(f"{parameter_name} values must be unique.")

    return sorted(density_values)


def build_gole_gohar_joint_density_sensitivity_table(
    explosive_densities_g_cm3: Iterable[float] | None = None,
    rock_densities_g_cm3: Iterable[float] | None = None,
) -> pd.DataFrame:
    """Evaluate seven equations at every pair of sampled densities.

    Both density grids vary while all other reconstructed reference
    inputs remain fixed. The grids are exploratory computational
    intervals, not probability distributions or validated domains.

    In the current Konya implementations, both densities enter through
    their ratio. Sampling two inputs does not establish two independent
    physical mechanisms or provide calibrated predictive uncertainty.
    """
    explosive_values = _validated_density_grid(
        explosive_densities_g_cm3,
        DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3,
        "explosive_density_g_cm3",
    )
    rock_values = _validated_density_grid(
        rock_densities_g_cm3,
        DEFAULT_ROCK_DENSITY_GRID_G_CM3,
        "rock_density_g_cm3",
    )

    reference_inputs = gole_gohar_reference_inputs()
    fixed_inputs = reference_inputs.copy()
    reference_explosive_density = positive_float(
        fixed_inputs.pop("explosive_density_g_cm3"),
        "reference_explosive_density_g_cm3",
    )
    reference_rock_density = positive_float(
        fixed_inputs.pop("rock_density_g_cm3"),
        "reference_rock_density_g_cm3",
    )

    tables = []

    for explosive_density in explosive_values:
        for rock_density in rock_values:
            density_ratio = positive_float(
                explosive_density / rock_density,
                "explosive_to_rock_density_ratio",
            )
            scenario_inputs = reference_inputs.copy()
            scenario_inputs["explosive_density_g_cm3"] = explosive_density
            scenario_inputs["rock_density_g_cm3"] = rock_density

            model_table = evaluate_conventional_burden_models(
                **scenario_inputs
            )

            if any(
                not isfinite(value) or value <= 0.0
                for value in model_table["burden_m"].to_numpy(dtype=float)
            ):
                raise ValueError(
                    "The density pair produced a nonfinite or nonpositive "
                    "burden; use values within floating-point limits."
                )

            model_table.attrs.clear()
            model_table.insert(
                0, "explosive_density_g_cm3", explosive_density
            )
            model_table.insert(1, "rock_density_g_cm3", rock_density)
            model_table.insert(
                2, "explosive_to_rock_density_ratio", density_ratio
            )
            tables.append(model_table)

    result = pd.concat(tables, ignore_index=True)
    result.attrs.clear()
    result.attrs.update(
        {
            "analysis_type": "two_factor_grid",
            "varied_parameters": (
                "explosive_density_g_cm3",
                "rock_density_g_cm3",
            ),
            "reference_explosive_density_g_cm3": reference_explosive_density,
            "reference_rock_density_g_cm3": reference_rock_density,
            "reference_explosive_to_rock_density_ratio": (
                reference_explosive_density / reference_rock_density
            ),
            "fixed_inputs": fixed_inputs,
            "grid_shape": (len(explosive_values), len(rock_values)),
            "scenario_count": len(explosive_values) * len(rock_values),
            "sampled_intervals_g_cm3": {
                "explosive_density_g_cm3": {
                    "minimum": explosive_values[0],
                    "maximum": explosive_values[-1],
                },
                "rock_density_g_cm3": {
                    "minimum": rock_values[0],
                    "maximum": rock_values[-1],
                },
            },
            "decision_gate": "RESEARCH_COMPARATOR_ONLY",
            "density_warning": (
                "The Cartesian grid is an exploratory computational "
                "experiment, not a probability distribution, recommended "
                "operational range, or universal model-validation domain. "
                "Its endpoints include uncommon geological endmembers. "
                "Mineral, grain, dry-bulk, saturated-bulk, and in-situ "
                "densities must not be treated as interchangeable. "
                "The fixed explosive-type label does not establish that "
                "every sampled density describes a realizable product."
            ),
            "interpretation_warning": (
                "Both densities enter the current Konya equations through "
                "the same explosive-to-rock density ratio. Numerical "
                "responses represent equation structure and model-form "
                "disagreement, not independent physical mechanisms, "
                "predictive accuracy, or calibrated uncertainty."
            ),
        }
    )
    return result


_JOINT_PAIR_COLUMNS = [
    "explosive_density_g_cm3",
    "rock_density_g_cm3",
]
_REQUIRED_JOINT_DENSITY_COLUMNS = {
    *_JOINT_PAIR_COLUMNS,
    "explosive_to_rock_density_ratio",
    "model_id",
    "model_name",
    "burden_m",
}
_CANONICAL_MODEL_IDS = {
    "CONV_ASH",
    "CONV_BHANDARI",
    "CONV_JIMENO",
    "CONV_KONYA_1972",
    "CONV_KONYA_1983",
    "CONV_RUSTAN",
    "CONV_TATIYA",
}


def _validate_joint_density_table(sensitivity_table: pd.DataFrame) -> None:
    """Validate a complete Cartesian grid of the seven canonical models."""
    if not isinstance(sensitivity_table, pd.DataFrame):
        raise TypeError("sensitivity_table must be a pandas DataFrame.")
    if not sensitivity_table.columns.is_unique:
        raise ValueError("The joint-density table has duplicate column names.")

    missing = _REQUIRED_JOINT_DENSITY_COLUMNS.difference(
        sensitivity_table.columns
    )
    if missing:
        raise ValueError(f"Missing joint-density columns: {sorted(missing)}")
    if sensitivity_table.empty:
        raise ValueError("The joint-density table must not be empty.")

    numeric_columns = [
        *_JOINT_PAIR_COLUMNS,
        "explosive_to_rock_density_ratio",
        "burden_m",
    ]
    numeric_values = {}
    for column in numeric_columns:
        series = sensitivity_table[column]
        if (
            not pd.api.types.is_numeric_dtype(series.dtype)
            or pd.api.types.is_bool_dtype(series.dtype)
            or pd.api.types.is_complex_dtype(series.dtype)
        ):
            raise ValueError(f"{column} must contain real numerical values.")
        values = series.to_numpy(dtype=float, na_value=np.nan)
        if not np.isfinite(values).all() or not (values > 0.0).all():
            raise ValueError(f"{column} must contain finite positive values.")
        numeric_values[column] = values

    if set(sensitivity_table["model_id"]) != _CANONICAL_MODEL_IDS:
        raise ValueError("The table must contain the seven canonical model IDs.")
    if not all(
        isinstance(name, str) and bool(name.strip())
        for name in sensitivity_table["model_name"]
    ):
        raise ValueError("Every model name must be a nonempty string.")

    if sensitivity_table.duplicated(
        _JOINT_PAIR_COLUMNS + ["model_id"]
    ).any():
        raise ValueError("The table contains duplicate density-pair/model rows.")

    groups = sensitivity_table.groupby(_JOINT_PAIR_COLUMNS)
    for _, group in groups:
        if set(group["model_id"]) != _CANONICAL_MODEL_IDS:
            raise ValueError("Every density pair must contain all seven models.")
        if group["explosive_to_rock_density_ratio"].nunique() != 1:
            raise ValueError("Each density pair must have exactly one ratio.")

    expected_pair_count = (
        sensitivity_table["explosive_density_g_cm3"].nunique()
        * sensitivity_table["rock_density_g_cm3"].nunique()
    )
    if groups.ngroups != expected_pair_count:
        raise ValueError("The table must contain a complete Cartesian grid.")
    if not sensitivity_table.groupby("model_id")["model_name"].nunique().eq(1).all():
        raise ValueError("A model ID has inconsistent model names.")

    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        expected_ratios = (
            numeric_values["explosive_density_g_cm3"]
            / numeric_values["rock_density_g_cm3"]
        )
    if (
        not np.isfinite(expected_ratios).all()
        or not (expected_ratios > 0.0).all()
        or not np.allclose(
            numeric_values["explosive_to_rock_density_ratio"],
            expected_ratios,
            rtol=1e-12,
            atol=0.0,
        )
    ):
        raise ValueError("Density ratios must equal explosive density / rock density.")


def _joint_summary_metadata(analysis_type: str) -> dict:
    """Create summary metadata without inheriting scenario-specific attrs."""
    return {
        "analysis_type": analysis_type,
        "varied_parameters": tuple(_JOINT_PAIR_COLUMNS),
        "decision_gate": "RESEARCH_COMPARATOR_ONLY",
        "density_warning": (
            "Sampled density pairs are exploratory computational settings, "
            "not a probability distribution, a recommended operational "
            "range, or a universal validation domain. Density measurement "
            "bases must not be treated as interchangeable."
        ),
        "interpretation_warning": (
            "The current Konya implementations depend on the "
            "explosive-to-rock density ratio. These summaries describe "
            "deterministic equation responses and structural model "
            "disagreement, not calibrated predictive uncertainty, physical "
            "parameter importance, or an optimized blast design."
        ),
    }


def build_joint_density_ensemble_summary(
    sensitivity_table: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize seven-model disagreement at each sampled density pair."""
    _validate_joint_density_table(sensitivity_table)
    summary = (
        sensitivity_table.groupby(_JOINT_PAIR_COLUMNS, as_index=False)
        .agg(
            model_count=("model_id", "nunique"),
            mean_burden_m=("burden_m", "mean"),
            median_burden_m=("burden_m", "median"),
            minimum_burden_m=("burden_m", "min"),
            maximum_burden_m=("burden_m", "max"),
        )
        .sort_values(_JOINT_PAIR_COLUMNS)
        .reset_index(drop=True)
    )
    summary.insert(
        2,
        "explosive_to_rock_density_ratio",
        summary["explosive_density_g_cm3"] / summary["rock_density_g_cm3"],
    )
    summary["range_m"] = (
        summary["maximum_burden_m"] - summary["minimum_burden_m"]
    )
    if not np.isfinite(summary.select_dtypes(include="number").to_numpy()).all():
        raise ValueError("The ensemble summary contains nonfinite statistics.")
    summary.attrs.clear()
    summary.attrs.update(_joint_summary_metadata("joint_density_ensemble_summary"))
    return summary


def _burden_at_ratio_endpoint(group: pd.DataFrame, ratio: float) -> float:
    """Resolve a ratio endpoint without arbitrarily choosing unequal outputs."""
    values = group.loc[
        group["explosive_to_rock_density_ratio"].eq(ratio), "burden_m"
    ].to_numpy(dtype=float)
    if not np.allclose(values, values[0], rtol=1e-12, atol=1e-12):
        raise ValueError(
            "A model has inconsistent burdens at a density-ratio endpoint."
        )
    return float(values[0])


def build_model_joint_density_response_summary(
    sensitivity_table: pd.DataFrame,
    reference_explosive_density_g_cm3: float | None = None,
    reference_rock_density_g_cm3: float | None = None,
) -> pd.DataFrame:
    """Summarize each model's sampled response and ratio-endpoint change.

    Reference values default to the centralized Gole Gohar inputs. The
    corresponding pair must be present in the supplied table. Ratio
    endpoints describe the sampled minimum and maximum rho_e/rho_r;
    they do not describe varying either density alone.
    """
    _validate_joint_density_table(sensitivity_table)
    reference_inputs = gole_gohar_reference_inputs()
    reference_explosive_density = positive_float(
        reference_inputs["explosive_density_g_cm3"]
        if reference_explosive_density_g_cm3 is None
        else reference_explosive_density_g_cm3,
        "reference_explosive_density_g_cm3",
    )
    reference_rock_density = positive_float(
        reference_inputs["rock_density_g_cm3"]
        if reference_rock_density_g_cm3 is None
        else reference_rock_density_g_cm3,
        "reference_rock_density_g_cm3",
    )
    reference_ratio = positive_float(
        reference_explosive_density / reference_rock_density,
        "reference_explosive_to_rock_density_ratio",
    )
    reference_rows = sensitivity_table.loc[
        sensitivity_table["explosive_density_g_cm3"].eq(reference_explosive_density)
        & sensitivity_table["rock_density_g_cm3"].eq(reference_rock_density)
    ]
    if len(reference_rows) != 7:
        raise ValueError(
            "The table must contain the reference density pair "
            f"({reference_explosive_density}, {reference_rock_density}) g/cm3."
        )
    reference_burdens = reference_rows.set_index("model_id")["burden_m"]
    rows = []

    for model_id, group in sensitivity_table.groupby("model_id", sort=False):
        burdens = group["burden_m"].astype(float)
        distinct_count = int(burdens.nunique())
        minimum_ratio = float(group["explosive_to_rock_density_ratio"].min())
        maximum_ratio = float(group["explosive_to_rock_density_ratio"].max())
        lower_burden = _burden_at_ratio_endpoint(group, minimum_ratio)
        upper_burden = _burden_at_ratio_endpoint(group, maximum_ratio)
        endpoint_change = upper_burden - lower_burden
        rows.append(
            {
                "model_id": str(model_id),
                "model_name": group["model_name"].iloc[0],
                "distinct_burden_count": distinct_count,
                "responds_to_joint_density_grid": distinct_count > 1,
                "reference_explosive_density_g_cm3": reference_explosive_density,
                "reference_rock_density_g_cm3": reference_rock_density,
                "reference_density_ratio": reference_ratio,
                "reference_burden_m": float(reference_burdens.loc[model_id]),
                "minimum_sampled_density_ratio": minimum_ratio,
                "maximum_sampled_density_ratio": maximum_ratio,
                "burden_at_minimum_density_ratio_m": lower_burden,
                "burden_at_maximum_density_ratio_m": upper_burden,
                "ratio_endpoint_change_m": endpoint_change,
                "ratio_endpoint_change_percent": endpoint_change / lower_burden * 100.0,
                "minimum_burden_m": float(burdens.min()),
                "maximum_burden_m": float(burdens.max()),
                "burden_range_m": float(burdens.max() - burdens.min()),
            }
        )

    summary = pd.DataFrame(rows)
    if not np.isfinite(summary.select_dtypes(include="number").to_numpy()).all():
        raise ValueError("The model response summary contains nonfinite statistics.")
    summary.attrs.clear()
    summary.attrs.update(
        _joint_summary_metadata("model_joint_density_response_summary")
    )
    summary.attrs.update(
        {
            "reference_explosive_density_g_cm3": reference_explosive_density,
            "reference_rock_density_g_cm3": reference_rock_density,
            "reference_explosive_to_rock_density_ratio": reference_ratio,
            "endpoint_change_definition": (
                "Burden at maximum sampled density ratio minus burden at "
                "minimum sampled density ratio; percentage change uses "
                "the burden at the minimum sampled ratio as its baseline."
            ),
        }
    )
    return summary
