import pandas as pd

from blastdesign import (
    evaluate_conventional_burden_models,
    gole_gohar_burden_results,
    gole_gohar_reference_inputs,
)


EXPECTED_MODEL_IDS = [
    "CONV_ASH",
    "CONV_BHANDARI",
    "CONV_JIMENO",
    "CONV_KONYA_1972",
    "CONV_KONYA_1983",
    "CONV_RUSTAN",
    "CONV_TATIYA",
]


def test_shared_evaluator_reproduces_reference_benchmark():
    inputs = gole_gohar_reference_inputs()

    comparison = evaluate_conventional_burden_models(
        **inputs
    )

    benchmark = gole_gohar_burden_results()

    pd.testing.assert_series_equal(
        comparison.set_index("model_id")["burden_m"],
        benchmark.set_index("model_id")["burden_m"],
    )

    assert comparison.attrs["inputs"] == inputs


def test_shared_evaluator_returns_canonical_model_ids():
    result = evaluate_conventional_burden_models(
        **gole_gohar_reference_inputs()
    )

    assert result["model_id"].tolist() == EXPECTED_MODEL_IDS
    assert result["model_id"].is_unique
    assert len(result) == 7