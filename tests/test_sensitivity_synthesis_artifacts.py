from pathlib import Path

import pandas as pd

from blastdesign import (
    build_integrated_sensitivity_summary,
    build_model_parameter_dependency_matrix,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data" / "processed"


def assert_saved_csv_matches(filename, expected):
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


def test_saved_integrated_summary_matches_generated_results():
    expected = build_integrated_sensitivity_summary()

    assert_saved_csv_matches(
        "integrated_sensitivity_summary.csv",
        expected,
    )


def test_saved_dependency_matrix_matches_generated_results():
    expected = (
        build_model_parameter_dependency_matrix()
    )

    assert_saved_csv_matches(
        "model_parameter_dependency_matrix.csv",
        expected,
    )