import math

import pandas as pd
import pytest

from blastdesign import (
    DEFAULT_ASH_BURDEN_RATIO_GRID,
    build_gole_gohar_ash_burden_ratio_sensitivity_table,
)


def test_default_grid_has_seven_models_per_ratio():
    table = (
        build_gole_gohar_ash_burden_ratio_sensitivity_table()
    )

    assert isinstance(table, pd.DataFrame)
    assert table.shape == (
        7 * len(DEFAULT_ASH_BURDEN_RATIO_GRID),
        4,
    )
    assert table.columns.tolist() == [
        "ash_burden_ratio",
        "model_id",
        "model_name",
        "burden_m",
    ]

    model_counts = table.groupby(
        "ash_burden_ratio"
    )["model_id"].nunique()

    assert model_counts.eq(7).all()


def test_reference_ratio_reproduces_ash_benchmark():
    table = (
        build_gole_gohar_ash_burden_ratio_sensitivity_table()
    )

    reference_rows = table[
        table["ash_burden_ratio"].eq(25.0)
    ].set_index("model_id")

    assert len(reference_rows) == 7
    assert math.isclose(
        reference_rows.loc["CONV_ASH", "burden_m"],
        6.275,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )


def test_only_ash_responds_to_burden_ratio():
    table = (
        build_gole_gohar_ash_burden_ratio_sensitivity_table()
    )

    distinct_counts = table.groupby(
        "model_id"
    )["burden_m"].nunique()

    assert (
        distinct_counts.loc["CONV_ASH"]
        == len(DEFAULT_ASH_BURDEN_RATIO_GRID)
    )
    assert distinct_counts.drop("CONV_ASH").eq(1).all()


def test_ash_response_is_linear_and_increasing():
    table = (
        build_gole_gohar_ash_burden_ratio_sensitivity_table()
    )

    ash_rows = (
        table[
            table["model_id"].eq("CONV_ASH")
        ]
        .sort_values("ash_burden_ratio")
        .reset_index(drop=True)
    )

    assert math.isclose(
        ash_rows.iloc[0]["burden_m"],
        5.02,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
    assert math.isclose(
        ash_rows.iloc[-1]["burden_m"],
        10.04,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )

    burdens = ash_rows["burden_m"].tolist()

    assert all(
        later > earlier
        for earlier, later in zip(
            burdens,
            burdens[1:],
        )
    )


def test_custom_grid_is_sorted_without_mutating_input():
    supplied_values = [40.0, 20.0, 25.0]
    original_values = supplied_values.copy()

    table = (
        build_gole_gohar_ash_burden_ratio_sensitivity_table(
            supplied_values
        )
    )

    assert supplied_values == original_values
    assert (
        table["ash_burden_ratio"]
        .drop_duplicates()
        .tolist()
        == [20.0, 25.0, 40.0]
    )


def test_sensitivity_metadata_preserves_research_safeguards():
    table = (
        build_gole_gohar_ash_burden_ratio_sensitivity_table()
    )

    assert table.attrs["analysis_type"] == (
        "one_factor_at_a_time"
    )
    assert table.attrs["varied_parameter"] == (
        "ash_burden_ratio"
    )
    assert table.attrs["reference_ash_burden_ratio"] == 25.0
    assert table.attrs["sampled_interval"] == {
        "minimum": 20.0,
        "maximum": 40.0,
    }
    assert table.attrs["decision_gate"] == (
        "RESEARCH_COMPARATOR_ONLY"
    )
    assert (
        "ash_burden_ratio"
        not in table.attrs["fixed_inputs"]
    )
    assert "not calibrated" in (
        table.attrs["parameter_warning"]
    )


@pytest.mark.parametrize(
    ("values", "error_type"),
    [
        ([], ValueError),
        ([25.0, 25.0], ValueError),
        ([19.9], ValueError),
        ([40.1], ValueError),
        ("25.0", TypeError),
        (25.0, TypeError),
    ],
)
def test_invalid_ratio_grids_are_rejected(
    values,
    error_type,
):
    with pytest.raises(error_type):
        build_gole_gohar_ash_burden_ratio_sensitivity_table(
            values
        )