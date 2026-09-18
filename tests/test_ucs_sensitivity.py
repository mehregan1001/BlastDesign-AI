import pandas as pd
import pytest

from blastdesign import (
    DEFAULT_UCS_GRID_MPA,
    build_gole_gohar_ucs_sensitivity_table,
    gole_gohar_burden_results,
)


def test_default_ucs_grid_has_seven_models_per_value():
    result = build_gole_gohar_ucs_sensitivity_table()

    observed_values = (
        result["ucs_mpa"]
        .drop_duplicates()
        .tolist()
    )

    assert observed_values == list(DEFAULT_UCS_GRID_MPA)
    assert len(result) == len(DEFAULT_UCS_GRID_MPA) * 7
    assert (
        result.groupby("ucs_mpa")
        .size()
        .eq(7)
        .all()
    )
    assert (
        result.attrs["decision_gate"]
        == "RESEARCH_COMPARATOR_ONLY"
    )


def test_ucs_reference_rows_match_benchmark():
    result = build_gole_gohar_ucs_sensitivity_table()

    reference_rows = (
        result[result["ucs_mpa"].eq(85.0)]
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


def test_only_strength_dependent_models_change_with_ucs():
    result = build_gole_gohar_ucs_sensitivity_table()

    unique_burdens = (
        result.groupby("model_id")["burden_m"]
        .nunique()
    )

    changing_models = set(
        unique_burdens[unique_burdens.gt(1)].index
    )

    assert changing_models == {
        "CONV_JIMENO",
        "CONV_TATIYA",
    }


def test_ucs_classification_boundaries_are_explicit():
    result = build_gole_gohar_ucs_sensitivity_table()

    table = result.pivot(
        index="ucs_mpa",
        columns="model_id",
        values="burden_m",
    )

    assert table.loc[
        69.999, "CONV_JIMENO"
    ] == pytest.approx(7.028)

    assert table.loc[
        70.0, "CONV_JIMENO"
    ] == pytest.approx(5.773)

    assert table.loc[
        180.0, "CONV_JIMENO"
    ] == pytest.approx(5.773)

    assert table.loc[
        180.001, "CONV_JIMENO"
    ] == pytest.approx(5.271)

    assert table.loc[
        54.999, "CONV_TATIYA"
    ] == pytest.approx(6.94086)

    assert table.loc[
        55.0, "CONV_TATIYA"
    ] == pytest.approx(5.83937)

    assert table.loc[
        110.0, "CONV_TATIYA"
    ] == pytest.approx(5.83937)

    assert table.loc[
        110.001, "CONV_TATIYA"
    ] == pytest.approx(5.08908)


@pytest.mark.parametrize(
    "values",
    [
        [],
        [0.0],
        [-1.0],
    ],
)
def test_ucs_sensitivity_rejects_invalid_numeric_grids(
    values,
):
    with pytest.raises(ValueError):
        build_gole_gohar_ucs_sensitivity_table(values)


def test_ucs_sensitivity_rejects_string_input():
    with pytest.raises(TypeError):
        build_gole_gohar_ucs_sensitivity_table("85")


def test_ucs_sensitivity_sorts_and_rejects_duplicates():
    result = build_gole_gohar_ucs_sensitivity_table(
        [180.001, 40.0, 85.0]
    )

    assert (
        result["ucs_mpa"]
        .drop_duplicates()
        .tolist()
        == [40.0, 85.0, 180.001]
    )

    with pytest.raises(ValueError):
        build_gole_gohar_ucs_sensitivity_table(
            [85.0, 85.0]
        )