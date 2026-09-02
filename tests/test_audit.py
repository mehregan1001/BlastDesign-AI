from blastdesign import (
    gole_gohar_burden_results,
    gole_gohar_reference_inputs,
)


EXPECTED_INPUTS = {
    "hole_diameter_mm": 251.0,
    "ucs_mpa": 85.0,
    "explosive_density_g_cm3": 0.85,
    "rock_density_g_cm3": 4.37,
    "explosive_type": "ANFO",
    "ash_burden_ratio": 25.0,
}


def test_reference_inputs_are_complete_and_defensive():
    inputs = gole_gohar_reference_inputs()

    assert inputs == EXPECTED_INPUTS

    inputs["ucs_mpa"] = 999.0

    assert gole_gohar_reference_inputs() == EXPECTED_INPUTS


def test_benchmark_records_reference_inputs_and_seven_models():
    result = gole_gohar_burden_results()

    assert result.attrs["inputs"] == EXPECTED_INPUTS
    assert len(result) == 7
    assert result["model_id"].is_unique
    assert set(result["model_id"]) == {
        "CONV_ASH",
        "CONV_BHANDARI",
        "CONV_JIMENO",
        "CONV_KONYA_1972",
        "CONV_KONYA_1983",
        "CONV_RUSTAN",
        "CONV_TATIYA",
    }