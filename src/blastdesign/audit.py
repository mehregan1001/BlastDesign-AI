"""Reproducible Gole Gohar burden-model benchmark fixture."""

from __future__ import annotations

import pandas as pd

from .comparison import evaluate_conventional_burden_models


def gole_gohar_reference_inputs() -> dict:
    """Return a fresh copy of the audited reference-scenario inputs."""
    return {
        "hole_diameter_mm": 251.0,
        "ucs_mpa": 85.0,
        "explosive_density_g_cm3": 0.85,
        "rock_density_g_cm3": 4.37,
        "explosive_type": "ANFO",
        "ash_burden_ratio": 25.0,
    }


def gole_gohar_burden_results() -> pd.DataFrame:
    """Return the seven audited burden outputs at full precision."""
    inputs = gole_gohar_reference_inputs()

    result = evaluate_conventional_burden_models(
        **inputs
    )

    thesis_reported_by_model = {
        "CONV_ASH": 6.27,
        "CONV_BHANDARI": 6.87,
        "CONV_JIMENO": 5.77,
        "CONV_KONYA_1972": 5.52,
        "CONV_KONYA_1983": 5.69,
        "CONV_RUSTAN": 6.98,
        "CONV_TATIYA": 5.84,
    }

    result["thesis_reported_m"] = (
        result["model_id"].map(
            thesis_reported_by_model
        )
    )

    result["absolute_difference_m"] = (
        result["burden_m"]
        - result["thesis_reported_m"]
    ).abs()

    result.attrs["inputs"] = inputs

    return result