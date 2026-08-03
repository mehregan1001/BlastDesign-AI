import math

from blastdesign import calculate_blast_metrics


def test_first_notebook_blast_metrics():
    result = calculate_blast_metrics(
        bench_height_m=10.0,
        hole_diameter_mm=102.0,
        burden_m=3.0,
        spacing_m=3.6,
        subdrilling_m=0.8,
        stemming_m=2.5,
        explosive_density_kg_m3=1100.0,
        number_of_holes=40,
    )
    assert math.isclose(result["explosive_mass_per_hole_kg"], 74.60380915184177)
    assert math.isclose(result["total_explosive_mass_kg"], 2984.152366073671)
    assert math.isclose(result["powder_factor_kg_m3"], 0.6907760106652017)
