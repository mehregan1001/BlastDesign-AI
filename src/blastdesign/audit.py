"""Reproducible Gole Gohar burden-model benchmark fixture."""

from __future__ import annotations

import pandas as pd

from .burden import (
    ash_burden,
    bhandari_burden,
    konya_1972_burden,
    konya_1983_burden,
    lopez_jimeno_burden,
    rustan_burden,
    tatiya_al_ajmi_burden,
)


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

    diameter = inputs["hole_diameter_mm"]
    ucs = inputs["ucs_mpa"]
    explosive_density = inputs["explosive_density_g_cm3"]
    rock_density = inputs["rock_density_g_cm3"]
    explosive_type = inputs["explosive_type"]
    ash_ratio = inputs["ash_burden_ratio"]

    rows = [
        (
            "CONV_ASH",
            "Ash",
            ash_burden(diameter, ash_ratio),
            6.27,
        ),
        (
            "CONV_BHANDARI",
            "Bhandari",
            bhandari_burden(diameter),
            6.87,
        ),
        (
            "CONV_JIMENO",
            "Lopez Jimeno",
            lopez_jimeno_burden(
                diameter,
                ucs,
                explosive_type,
            ),
            5.77,
        ),
        (
            "CONV_KONYA_1972",
            "Konya 1972",
            konya_1972_burden(
                diameter,
                explosive_density,
                rock_density,
            ),
            5.52,
        ),
        (
            "CONV_KONYA_1983",
            "Konya 1983",
            konya_1983_burden(
                diameter,
                explosive_density,
                rock_density,
            ),
            5.69,
        ),
        (
            "CONV_RUSTAN",
            "Rustan",
            rustan_burden(diameter),
            6.98,
        ),
        (
            "CONV_TATIYA",
            "Tatiya–Al-Ajmi",
            tatiya_al_ajmi_burden(
                diameter,
                ucs,
                explosive_type,
            ),
            5.84,
        ),
    ]

    result = pd.DataFrame(
        rows,
        columns=[
            "model_id",
            "model_name",
            "burden_m",
            "thesis_reported_m",
        ],
    )

    result["absolute_difference_m"] = (
        result["burden_m"] - result["thesis_reported_m"]
    ).abs()

    result.attrs["inputs"] = inputs

    return result