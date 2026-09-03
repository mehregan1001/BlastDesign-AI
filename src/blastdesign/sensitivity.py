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