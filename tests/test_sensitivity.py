import pandas as pd
import pytest

from blastdesign import (
    DEFAULT_DIAMETER_GRID_MM,
    build_gole_gohar_diameter_sensitivity_table,
    gole_gohar_burden_results,
)


def test_default_sensitivity_grid_has_seven_models_per_diameter():
    result = (
        build_gole_gohar_diameter_sensitivity_table()
    )

    observed_diameters = (
        result["hole_diameter_mm"]
        .drop_duplicates()
        .tolist()
    )

    assert observed_diameters == list(
        DEFAULT_DIAMETER_GRID_MM
    )
    assert len(result) == (
        len(DEFAULT_DIAMETER_GRID_MM) * 7
    )
    assert (
        result.groupby("hole_diameter_mm")
        .size()
        .eq(7)
        .all()
    )
    assert (
        result.attrs["decision_gate"]
        == "RESEARCH_COMPARATOR_ONLY"
    )


def test_sensitivity_reference_row_matches_benchmark():
    result = (
        build_gole_gohar_diameter_sensitivity_table()
    )

    reference_rows = (
        result[
            result["hole_diameter_mm"].eq(
                251.0
            )
        ]
        .set_index("model_id")
        ["burden_m"]
    )

    benchmark_rows = (
        gole_gohar_burden_results()
        .set_index("model_id")
        ["burden_m"]
    )

    pd.testing.assert_series_equal(
        reference_rows,
        benchmark_rows,
    )


@pytest.mark.parametrize(
    "diameters",
    [
        [180.0],
        [312.0],
        [170.0, 251.0],
        [],
    ],
)
def test_sensitivity_rejects_invalid_comparison_grids(
    diameters,
):
    with pytest.raises(ValueError):
        build_gole_gohar_diameter_sensitivity_table(
            diameters
        )


def test_sensitivity_sorts_values_and_rejects_duplicates():
    result = (
        build_gole_gohar_diameter_sensitivity_table(
            [311.0, 181.0, 251.0]
        )
    )

    assert (
        result["hole_diameter_mm"]
        .drop_duplicates()
        .tolist()
        == [181.0, 251.0, 311.0]
    )

    with pytest.raises(ValueError):
        build_gole_gohar_diameter_sensitivity_table(
            [251.0, 251.0]
        )