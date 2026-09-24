from pathlib import Path

import pandas as pd

from blastdesign import (
    build_gole_gohar_rock_density_sensitivity_table,
    build_model_rock_density_response_summary,
    build_rock_density_ensemble_summary,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


def assert_saved_csv_matches(
    filename,
    expected,
):
    actual = pd.read_csv(
        DATA_DIRECTORY / filename
    )

    pd.testing.assert_frame_equal(
        actual,
        expected.reset_index(drop=True),
        check_dtype=False,
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )


def test_saved_model_outputs_match_generated_results():
    expected = (
        build_gole_gohar_rock_density_sensitivity_table()
    )

    assert_saved_csv_matches(
        "rock_density_sensitivity_model_outputs.csv",
        expected,
    )


def test_saved_ensemble_summary_matches_generated_results():
    table = (
        build_gole_gohar_rock_density_sensitivity_table()
    )

    expected = build_rock_density_ensemble_summary(
        table
    )

    assert_saved_csv_matches(
        "rock_density_sensitivity_ensemble_summary.csv",
        expected,
    )


def test_saved_model_response_summary_matches_generated_results():
    table = (
        build_gole_gohar_rock_density_sensitivity_table()
    )

    expected = (
        build_model_rock_density_response_summary(
            table
        )
    )

    assert_saved_csv_matches(
        "rock_density_sensitivity_model_response_summary.csv",
        expected,
    )