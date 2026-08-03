"""Basic blast-pattern calculations developed in the first learning notebook."""

from __future__ import annotations

import math

from .validation import positive_float


def calculate_blast_metrics(
    bench_height_m,
    hole_diameter_mm,
    burden_m,
    spacing_m,
    subdrilling_m,
    stemming_m,
    explosive_density_kg_m3,
    number_of_holes,
):
    """Calculate elementary geometry, explosive mass and powder factor."""
    bench_height_m = positive_float(bench_height_m, "bench_height_m")
    hole_diameter_mm = positive_float(hole_diameter_mm, "hole_diameter_mm")
    burden_m = positive_float(burden_m, "burden_m")
    spacing_m = positive_float(spacing_m, "spacing_m")
    subdrilling_m = positive_float(subdrilling_m, "subdrilling_m")
    stemming_m = positive_float(stemming_m, "stemming_m")
    explosive_density_kg_m3 = positive_float(
        explosive_density_kg_m3, "explosive_density_kg_m3"
    )
    number_of_holes_float = positive_float(number_of_holes, "number_of_holes")
    if not number_of_holes_float.is_integer():
        raise ValueError("number_of_holes must be a whole number.")
    number_of_holes = int(number_of_holes_float)

    hole_length_m = bench_height_m + subdrilling_m
    charge_length_m = hole_length_m - stemming_m
    if charge_length_m <= 0:
        raise ValueError("stemming_m must be shorter than the total hole length.")

    hole_diameter_m = hole_diameter_mm / 1000.0
    hole_area_m2 = math.pi * hole_diameter_m**2 / 4.0
    explosive_volume_per_hole_m3 = hole_area_m2 * charge_length_m
    explosive_mass_per_hole_kg = (
        explosive_volume_per_hole_m3 * explosive_density_kg_m3
    )
    total_explosive_mass_kg = explosive_mass_per_hole_kg * number_of_holes
    rock_volume_per_hole_m3 = bench_height_m * burden_m * spacing_m
    total_rock_volume_m3 = rock_volume_per_hole_m3 * number_of_holes
    powder_factor_kg_m3 = total_explosive_mass_kg / total_rock_volume_m3

    return {
        "bench_height_m": bench_height_m,
        "hole_diameter_mm": hole_diameter_mm,
        "hole_diameter_m": hole_diameter_m,
        "burden_m": burden_m,
        "spacing_m": spacing_m,
        "subdrilling_m": subdrilling_m,
        "stemming_m": stemming_m,
        "hole_length_m": hole_length_m,
        "charge_length_m": charge_length_m,
        "hole_area_m2": hole_area_m2,
        "explosive_density_kg_m3": explosive_density_kg_m3,
        "explosive_volume_per_hole_m3": explosive_volume_per_hole_m3,
        "explosive_mass_per_hole_kg": explosive_mass_per_hole_kg,
        "number_of_holes": number_of_holes,
        "total_explosive_mass_kg": total_explosive_mass_kg,
        "rock_volume_per_hole_m3": rock_volume_per_hole_m3,
        "total_rock_volume_m3": total_rock_volume_m3,
        "powder_factor_kg_m3": powder_factor_kg_m3,
    }
