"""Verify the joint density grid and its mathematical invariants."""

from itertools import product

import numpy as np
import pandas as pd
import pytest

from blastdesign import (
    build_gole_gohar_explosive_density_sensitivity_table,
    build_gole_gohar_joint_density_sensitivity_table,
    build_gole_gohar_rock_density_sensitivity_table,
    evaluate_conventional_burden_models,
    gole_gohar_reference_inputs,
)
from blastdesign.sensitivity import (
    DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3,
    DEFAULT_ROCK_DENSITY_GRID_G_CM3,
)


MODEL_IDS = {
    "CONV_ASH",
    "CONV_BHANDARI",
    "CONV_JIMENO",
    "CONV_KONYA_1972",
    "CONV_KONYA_1983",
    "CONV_RUSTAN",
    "CONV_TATIYA",
}
KONYA_IDS = {"CONV_KONYA_1972", "CONV_KONYA_1983"}
PAIR_COLUMNS = ["explosive_density_g_cm3", "rock_density_g_cm3"]


@pytest.fixture(scope="module")
def joint_table():
    return build_gole_gohar_joint_density_sensitivity_table()


def _assert_same_model_outputs(actual, expected):
    columns = ["model_id", "model_name", "burden_m"]
    actual = actual[columns].sort_values("model_id").reset_index(drop=True)
    expected = expected[columns].sort_values("model_id").reset_index(drop=True)
    pd.testing.assert_frame_equal(
        actual,
        expected,
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )


def test_default_grid_contains_every_pair_and_canonical_model(joint_table):
    expected_pairs = set(
        product(
            DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3,
            DEFAULT_ROCK_DENSITY_GRID_G_CM3,
        )
    )
    observed_pairs = set(
        joint_table[PAIR_COLUMNS].itertuples(index=False, name=None)
    )
    assert observed_pairs == expected_pairs
    assert len(joint_table) == len(expected_pairs) * len(MODEL_IDS)
    assert not joint_table.duplicated(PAIR_COLUMNS + ["model_id"]).any()
    assert joint_table.columns.tolist() == [
        "explosive_density_g_cm3",
        "rock_density_g_cm3",
        "explosive_to_rock_density_ratio",
        "model_id",
        "model_name",
        "burden_m",
    ]
    for _, group in joint_table.groupby(PAIR_COLUMNS):
        assert set(group["model_id"]) == MODEL_IDS


def test_density_ratios_match_both_sampled_inputs(joint_table):
    expected = (
        joint_table["explosive_density_g_cm3"]
        / joint_table["rock_density_g_cm3"]
    )
    np.testing.assert_allclose(
        joint_table["explosive_to_rock_density_ratio"],
        expected,
        rtol=1e-12,
        atol=0.0,
    )


def test_reference_pair_reproduces_shared_evaluator(joint_table):
    reference = gole_gohar_reference_inputs()
    actual = joint_table.loc[
        joint_table["explosive_density_g_cm3"].eq(
            reference["explosive_density_g_cm3"]
        )
        & joint_table["rock_density_g_cm3"].eq(
            reference["rock_density_g_cm3"]
        )
    ]
    expected = evaluate_conventional_burden_models(**reference)
    _assert_same_model_outputs(actual, expected)


def test_reference_explosive_density_slice_matches_rock_density_sweep(
    joint_table,
):
    reference = gole_gohar_reference_inputs()
    actual = joint_table.loc[
        joint_table["explosive_density_g_cm3"].eq(
            reference["explosive_density_g_cm3"]
        )
    ]
    expected = build_gole_gohar_rock_density_sensitivity_table()
    sort_columns = ["rock_density_g_cm3", "model_id"]
    pd.testing.assert_frame_equal(
        actual[expected.columns].sort_values(sort_columns).reset_index(drop=True),
        expected.sort_values(sort_columns).reset_index(drop=True),
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )


def test_reference_rock_density_slice_matches_explosive_density_sweep(
    joint_table,
):
    reference = gole_gohar_reference_inputs()
    actual = joint_table.loc[
        joint_table["rock_density_g_cm3"].eq(
            reference["rock_density_g_cm3"]
        )
    ]
    expected = build_gole_gohar_explosive_density_sensitivity_table()
    sort_columns = ["explosive_density_g_cm3", "model_id"]
    pd.testing.assert_frame_equal(
        actual[expected.columns].sort_values(sort_columns).reset_index(drop=True),
        expected.sort_values(sort_columns).reset_index(drop=True),
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )


def test_only_konya_models_respond_to_joint_density_grid(joint_table):
    distinct_counts = joint_table.groupby("model_id")["burden_m"].nunique()
    assert set(distinct_counts[distinct_counts > 1].index) == KONYA_IDS


@pytest.mark.parametrize("model_id", sorted(KONYA_IDS))
def test_konya_response_direction_along_each_density_axis(joint_table, model_id):
    model_rows = joint_table.loc[joint_table["model_id"].eq(model_id)]
    for _, group in model_rows.groupby("rock_density_g_cm3"):
        ordered = group.sort_values("explosive_density_g_cm3")
        assert np.all(np.diff(ordered["burden_m"].to_numpy()) > 0.0)
    for _, group in model_rows.groupby("explosive_density_g_cm3"):
        ordered = group.sort_values("rock_density_g_cm3")
        assert np.all(np.diff(ordered["burden_m"].to_numpy()) < 0.0)


def test_proportional_density_pairs_preserve_each_models_burden():
    table = build_gole_gohar_joint_density_sensitivity_table(
        explosive_densities_g_cm3=[0.75, 0.90],
        rock_densities_g_cm3=[3.0, 3.6],
    )
    first = table.loc[
        table["explosive_density_g_cm3"].eq(0.75)
        & table["rock_density_g_cm3"].eq(3.0)
    ]
    second = table.loc[
        table["explosive_density_g_cm3"].eq(0.90)
        & table["rock_density_g_cm3"].eq(3.6)
    ]
    assert first["explosive_to_rock_density_ratio"].tolist() == [0.25] * 7
    assert second["explosive_to_rock_density_ratio"].tolist() == [0.25] * 7
    _assert_same_model_outputs(first, second)


def test_custom_grids_are_sorted_without_mutating_inputs():
    explosive_values = [0.90, 0.75]
    rock_values = [3.6, 3.0]
    table = build_gole_gohar_joint_density_sensitivity_table(
        explosive_values, rock_values
    )
    assert explosive_values == [0.90, 0.75]
    assert rock_values == [3.6, 3.0]
    assert table["explosive_density_g_cm3"].drop_duplicates().tolist() == [
        0.75, 0.90
    ]
    assert table["rock_density_g_cm3"].drop_duplicates().tolist() == [3.0, 3.6]
    assert len(table) == 28


def test_research_metadata_describes_both_varied_parameters(joint_table):
    reference = gole_gohar_reference_inputs()
    attrs = joint_table.attrs
    assert attrs["analysis_type"] == "two_factor_grid"
    assert attrs["varied_parameters"] == tuple(PAIR_COLUMNS)
    assert attrs["decision_gate"] == "RESEARCH_COMPARATOR_ONLY"
    assert attrs["reference_explosive_density_g_cm3"] == reference[
        "explosive_density_g_cm3"
    ]
    assert attrs["reference_rock_density_g_cm3"] == reference["rock_density_g_cm3"]
    assert attrs["reference_explosive_to_rock_density_ratio"] == pytest.approx(
        reference["explosive_density_g_cm3"] / reference["rock_density_g_cm3"]
    )
    assert attrs["fixed_inputs"] == {
        name: value for name, value in reference.items() if name not in PAIR_COLUMNS
    }
    assert attrs["grid_shape"] == (
        len(DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3),
        len(DEFAULT_ROCK_DENSITY_GRID_G_CM3),
    )
    assert attrs["scenario_count"] == 84
    assert attrs["sampled_intervals_g_cm3"] == {
        "explosive_density_g_cm3": {"minimum": 0.7, "maximum": 1.0},
        "rock_density_g_cm3": {"minimum": 1.8, "maximum": 5.3},
    }
    assert "inputs" not in attrs
    assert "varied_parameter" not in attrs
    assert "probability distribution" in attrs["density_warning"]
    assert "density ratio" in attrs["interpretation_warning"]


@pytest.mark.parametrize(
    "parameter_name",
    ["explosive_densities_g_cm3", "rock_densities_g_cm3"],
)
@pytest.mark.parametrize(
    "values, expected_error",
    [
        pytest.param([], ValueError, id="empty"),
        pytest.param(0.85, TypeError, id="scalar"),
        pytest.param("0.85", TypeError, id="string-grid"),
        pytest.param([True], TypeError, id="boolean"),
        pytest.param([0.0], ValueError, id="zero"),
        pytest.param([-1.0], ValueError, id="negative"),
        pytest.param([float("nan")], ValueError, id="nan"),
        pytest.param([float("inf")], ValueError, id="infinite"),
        pytest.param([0.85, 0.85], ValueError, id="duplicate"),
        pytest.param([object()], TypeError, id="nonnumeric"),
        pytest.param([10**400], ValueError, id="integer-overflow"),
    ],
)
def test_joint_grid_rejects_invalid_density_inputs(
    parameter_name, values, expected_error
):
    with pytest.raises(expected_error):
        build_gole_gohar_joint_density_sensitivity_table(
            **{parameter_name: values}
        )


@pytest.mark.parametrize(
    "explosive_density, rock_density",
    [
        pytest.param(1e308, 1e-308, id="ratio-overflow"),
        pytest.param(1e-308, 1e308, id="ratio-underflow"),
        pytest.param(1e308, 1.0, id="burden-overflow"),
    ],
)
def test_joint_grid_rejects_unrepresentable_ratios_or_burdens(
    explosive_density, rock_density
):
    with pytest.raises(ValueError):
        build_gole_gohar_joint_density_sensitivity_table(
            [explosive_density], [rock_density]
        )
