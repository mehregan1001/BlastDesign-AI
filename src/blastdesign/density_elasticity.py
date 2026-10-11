"""Analytical local density elasticities of reconstructed Konya equations.

An elasticity is E_x = (x / B) * dB/dx, with the other inputs fixed.
It describes a differential, dimensionless equation response. It is not
a measured rock or explosive property or a calibrated uncertainty measure.
"""

from __future__ import annotations

from collections.abc import Iterable
from math import isfinite

import numpy as np
import pandas as pd

from .audit import gole_gohar_reference_inputs
from .burden import konya_1972_burden, konya_1983_burden
from .sensitivity import (
    DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3,
    DEFAULT_ROCK_DENSITY_GRID_G_CM3,
)
from .validation import positive_float


def _positive_real_input(value, name: str) -> float:
    """Validate a real numerical input before calling the burden models."""
    if isinstance(value, (str, bytes, bool, np.bool_, complex, np.complexfloating)):
        raise TypeError(f"{name} must be a real numerical value.")
    try:
        return positive_float(value, name)
    except OverflowError as error:
        raise ValueError(f"{name} must be finite and greater than zero.") from error


def build_konya_density_elasticity_summary(
    hole_diameter_mm: float | None = None,
    explosive_density_g_cm3: float | None = None,
    rock_density_g_cm3: float | None = None,
) -> pd.DataFrame:
    """Return the local density elasticities of both Konya implementations.

    Omitted inputs use the centralized reconstructed Gole Gohar values.
    Each supplied input must be a finite positive real numerical value.
    Densities are in g/cm3, diameter is in mm, and burden is returned in m.

    For q = rho_e / rho_r, the implemented equations give:

    * Konya 1972: E_rho_e = 0.33 and E_rho_r = -0.33. The exponent
      intentionally remains 0.33, matching the reconstructed equation.
    * Konya 1983: E_rho_e = 2q / (2q + 1.5) and E_rho_r = -E_rho_e.

    The percentage interpretation is local: dB/B = E_x * dx/x when only
    x changes. A finite percentage change generally requires evaluating
    the burden equation at the changed input instead of treating this
    differential approximation as exact.

    Density definitions must match the source equation. Numerical input
    acceptance does not establish geological or operational applicability.
    """
    reference = gole_gohar_reference_inputs()
    supplied_inputs = {
        "hole_diameter_mm": hole_diameter_mm,
        "explosive_density_g_cm3": explosive_density_g_cm3,
        "rock_density_g_cm3": rock_density_g_cm3,
    }
    inputs = {
        name: _positive_real_input(
            reference[name] if value is None else value,
            name,
        )
        for name, value in supplied_inputs.items()
    }

    diameter = inputs["hole_diameter_mm"]
    explosive_density = inputs["explosive_density_g_cm3"]
    rock_density = inputs["rock_density_g_cm3"]
    density_ratio = positive_float(
        explosive_density / rock_density,
        "explosive_to_rock_density_ratio",
    )

    # This equivalent form avoids unnecessary multiplication of q by 2.
    konya_1983_elasticity = density_ratio / (density_ratio + 0.75)

    models = (
        ("CONV_KONYA_1972", "Konya 1972", konya_1972_burden, 0.33),
        (
            "CONV_KONYA_1983",
            "Konya 1983",
            konya_1983_burden,
            konya_1983_elasticity,
        ),
    )

    rows = []
    for model_id, model_name, burden_function, explosive_elasticity in models:
        burden = burden_function(diameter, explosive_density, rock_density)
        if not isfinite(burden) or burden <= 0.0:
            raise ValueError(
                f"{model_id} produced a nonfinite or nonpositive burden; "
                "use inputs within floating-point limits."
            )
        rows.append(
            {
                "model_id": model_id,
                "model_name": model_name,
                **inputs,
                "explosive_to_rock_density_ratio": density_ratio,
                "burden_m": float(burden),
                "explosive_density_elasticity": float(explosive_elasticity),
                "rock_density_elasticity": float(-explosive_elasticity),
            }
        )

    summary = pd.DataFrame(rows)
    summary.attrs.update(
        {
            "analysis_type": "analytical_local_density_elasticity",
            "scenario_inputs": inputs.copy(),
            "elasticity_definition": "E_x = (x/B) * dB/dx, with other inputs fixed.",
            "elasticity_units": "dimensionless",
            "model_scope": ("CONV_KONYA_1972", "CONV_KONYA_1983"),
            "decision_gate": "RESEARCH_COMPARATOR_ONLY",
            "interpretation_warning": (
                "Elasticities describe local fractional responses of the "
                "reconstructed equations. They do not establish field "
                "sensitivity, causal influence, predictive accuracy, "
                "calibrated uncertainty, or an operational recommendation. "
                "The differential approximation is not generally an exact "
                "response to a finite percentage change."
            ),
            "density_warning": (
                "Use the density definition intended by the source equation. "
                "Mineral, grain, dry-bulk, saturated-bulk, and in-situ "
                "densities must not be treated as interchangeable."
            ),
        }
    )
    return summary


def _validated_elasticity_density_grid(
    values: Iterable[float] | None,
    default_values: Iterable[float],
    parameter_name: str,
) -> list[float]:
    """Return a sorted, nonempty grid of unique positive real densities."""
    if values is None:
        raw_values = list(default_values)
    else:
        if isinstance(values, (str, bytes)):
            raise TypeError(f"{parameter_name} must be an iterable of numbers.")
        try:
            raw_values = list(values)
        except TypeError as error:
            raise TypeError(
                f"{parameter_name} must be an iterable of numbers."
            ) from error

    if not raw_values:
        raise ValueError(f"At least one {parameter_name} value is required.")
    validated = [_positive_real_input(value, parameter_name) for value in raw_values]
    if len(set(validated)) != len(validated):
        raise ValueError(f"{parameter_name} values must be unique.")
    return sorted(validated)


def build_gole_gohar_konya_density_elasticity_table(
    explosive_densities_g_cm3: Iterable[float] | None = None,
    rock_densities_g_cm3: Iterable[float] | None = None,
) -> pd.DataFrame:
    """Evaluate analytical local elasticities at every sampled density pair.

    The default Cartesian grid is the same as the joint-density analysis.
    Both densities vary while the centralized reference diameter stays
    fixed. Each pair has one row for each reconstructed Konya equation.

    A custom grid need not include the reference density pair. Its
    presence is explicitly recorded in the output metadata.

    Elasticities are dimensionless local derivatives evaluated at each
    pair. The grid is not a probability distribution, a calibrated
    uncertainty model, or a validated geological or operational domain.
    """
    explosive_values = _validated_elasticity_density_grid(
        explosive_densities_g_cm3,
        DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3,
        "explosive_density_g_cm3",
    )
    rock_values = _validated_elasticity_density_grid(
        rock_densities_g_cm3,
        DEFAULT_ROCK_DENSITY_GRID_G_CM3,
        "rock_density_g_cm3",
    )
    reference = gole_gohar_reference_inputs()
    diameter = _positive_real_input(reference["hole_diameter_mm"], "hole_diameter_mm")
    reference_pair = {
        name: _positive_real_input(reference[name], name)
        for name in ("explosive_density_g_cm3", "rock_density_g_cm3")
    }

    tables = []
    common_metadata = {}
    for rho_e in explosive_values:
        for rho_r in rock_values:
            point = build_konya_density_elasticity_summary(diameter, rho_e, rho_r)
            if not common_metadata:
                common_metadata = {
                    name: point.attrs[name]
                    for name in (
                        "elasticity_definition",
                        "elasticity_units",
                        "model_scope",
                        "decision_gate",
                        "interpretation_warning",
                    )
                }
            # A single scenario's attributes do not describe the entire grid.
            point.attrs.clear()
            tables.append(point)

    result = pd.concat(tables, ignore_index=True)
    result.attrs.clear()
    result.attrs.update(common_metadata)
    result.attrs.update(
        {
            "analysis_type": "analytical_local_density_elasticity_grid",
            "varied_parameters": (
                "explosive_density_g_cm3",
                "rock_density_g_cm3",
            ),
            "fixed_inputs": {"hole_diameter_mm": diameter},
            "reference_density_pair": reference_pair,
            "reference_density_pair_sampled": (
                reference_pair["explosive_density_g_cm3"] in explosive_values
                and reference_pair["rock_density_g_cm3"] in rock_values
            ),
            "grid_shape": (len(explosive_values), len(rock_values)),
            "scenario_count": len(explosive_values) * len(rock_values),
            "models_per_scenario": 2,
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
            "density_warning": (
                "The density grids are exploratory computational intervals, "
                "not probability distributions, recommended operational "
                "ranges, or universal model-validation domains. Numerical "
                "acceptance does not establish geological or product "
                "realizability. Use the density definition intended by the "
                "source equation; mineral, grain, dry-bulk, saturated-bulk, "
                "and in-situ densities are not interchangeable."
            ),
        }
    )
    return result
