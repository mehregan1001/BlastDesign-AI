"""Shared evaluation of the seven conventional burden models."""

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


def evaluate_conventional_burden_models(
    hole_diameter_mm,
    ucs_mpa,
    explosive_density_g_cm3,
    rock_density_g_cm3,
    explosive_type="ANFO",
    ash_burden_ratio=25.0,
) -> pd.DataFrame:
    """Evaluate all seven reconstructed burden equations consistently."""

    rows = [
        (
            "CONV_ASH",
            "Ash",
            ash_burden(
                hole_diameter_mm,
                ash_burden_ratio,
            ),
        ),
        (
            "CONV_BHANDARI",
            "Bhandari",
            bhandari_burden(hole_diameter_mm),
        ),
        (
            "CONV_JIMENO",
            "Lopez Jimeno",
            lopez_jimeno_burden(
                hole_diameter_mm,
                ucs_mpa,
                explosive_type,
            ),
        ),
        (
            "CONV_KONYA_1972",
            "Konya 1972",
            konya_1972_burden(
                hole_diameter_mm,
                explosive_density_g_cm3,
                rock_density_g_cm3,
            ),
        ),
        (
            "CONV_KONYA_1983",
            "Konya 1983",
            konya_1983_burden(
                hole_diameter_mm,
                explosive_density_g_cm3,
                rock_density_g_cm3,
            ),
        ),
        (
            "CONV_RUSTAN",
            "Rustan",
            rustan_burden(hole_diameter_mm),
        ),
        (
            "CONV_TATIYA",
            "Tatiya–Al-Ajmi",
            tatiya_al_ajmi_burden(
                hole_diameter_mm,
                ucs_mpa,
                explosive_type,
            ),
        ),
    ]

    result = pd.DataFrame(
        rows,
        columns=[
            "model_id",
            "model_name",
            "burden_m",
        ],
    )

    result.attrs["inputs"] = {
        "hole_diameter_mm": float(hole_diameter_mm),
        "ucs_mpa": float(ucs_mpa),
        "explosive_density_g_cm3": float(
            explosive_density_g_cm3
        ),
        "rock_density_g_cm3": float(
            rock_density_g_cm3
        ),
        "explosive_type": str(explosive_type),
        "ash_burden_ratio": float(ash_burden_ratio),
    }

    return result