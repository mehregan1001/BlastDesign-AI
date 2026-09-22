import pandas as pd
import pytest

from blastdesign import (
    DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3,
    build_gole_gohar_explosive_density_sensitivity_table,
    gole_gohar_burden_results,
)


def test_default_density_grid_has_seven_models_per_value():
    result = (
        build_gole_gohar_explosive_density_sensitivity_table()
    )

    observed_values = (
        result["explosive_density_g_cm3"]
        .drop_duplicates()
        .tolist()
    )

    assert observed_values == list(
        DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3
    )

    assert (
        len(result)
        == len(DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3) * 7
    )

    assert (
        result.groupby("explosive_density_g_cm3")
        .size()
        .eq(7)
        .all()
    )

    expected_ratios = (
        result["explosive_density_g_cm3"] / 4.37
    )

    pd.testing.assert_series_equal(
        result["explosive_to_rock_density_ratio"],
        expected_ratios,
        check_names=False,
    )

    assert (
        result.attrs["decision_gate"]
        == "RESEARCH_COMPARATOR_ONLY"
    )


def test_density_reference_rows_match_benchmark():
    result = (
        build_gole_gohar_explosive_density_sensitivity_table()
    )

    reference_rows = (
        result[
            result["explosive_density_g_cm3"].eq(0.85)
        ]
        .set_index("model_id")["burden_m"]
    )

    benchmark_rows = (
        gole_gohar_burden_results()
        .set_index("model_id")["burden_m"]
    )

    pd.testing.assert_series_equal(
        reference_rows,
        benchmark_rows,
    )


def test_only_density_dependent_models_change():
    result = (
        build_gole_gohar_explosive_density_sensitivity_table()
    )

    unique_burdens = (
        result.groupby("model_id")["burden_m"]
        .nunique()
    )

    changing_models = set(
        unique_burdens[
            unique_burdens.gt(1)
        ].index
    )

    assert changing_models == {
        "CONV_KONYA_1972",
        "CONV_KONYA_1983",
    }


def test_konya_density_responses_match_equations():
    result = (
        build_gole_gohar_explosive_density_sensitivity_table()
    )

    table = result.pivot(
        index="explosive_density_g_cm3",
        columns="model_id",
        values="burden_m",
    )

    assert table.loc[
        0.70, "CONV_KONYA_1972"
    ] == pytest.approx(
        5.184286575397026
    )

    assert table.loc[
        1.00, "CONV_KONYA_1972"
    ] == pytest.approx(
        5.8318540563956205
    )

    assert table.loc[
        0.70, "CONV_KONYA_1983"
    ] == pytest.approx(
        5.482942791762014
    )

    assert table.loc[
        1.00, "CONV_KONYA_1983"
    ] == pytest.approx(
        5.896489702517162
    )

    assert table[
        "CONV_KONYA_1972"
    ].is_monotonic_increasing

    assert table[
        "CONV_KONYA_1983"
    ].is_monotonic_increasing


@pytest.mark.parametrize(
    "values",
    [
        [],
        [0.0],
        [-1.0],
    ],
)
def test_density_sensitivity_rejects_invalid_numeric_grids(
    values,
):
    with pytest.raises(ValueError):
        build_gole_gohar_explosive_density_sensitivity_table(
            values
        )


def test_density_sensitivity_rejects_string_input():
    with pytest.raises(TypeError):
        build_gole_gohar_explosive_density_sensitivity_table(
            "0.85"
        )


def test_density_sensitivity_sorts_and_rejects_duplicates():
    result = (
        build_gole_gohar_explosive_density_sensitivity_table(
            [1.00, 0.70, 0.85]
        )
    )

    assert (
        result["explosive_density_g_cm3"]
        .drop_duplicates()
        .tolist()
        == [0.70, 0.85, 1.00]
    )

    with pytest.raises(ValueError):
        build_gole_gohar_explosive_density_sensitivity_table(
            [0.85, 0.85]
        )