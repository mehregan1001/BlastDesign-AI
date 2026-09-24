import math

import pytest

from blastdesign import (
    DEFAULT_ROCK_DENSITY_GRID_G_CM3,
    build_gole_gohar_rock_density_sensitivity_table,
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


def test_default_grid_has_seven_models_per_density():
    table = build_gole_gohar_rock_density_sensitivity_table()

    assert table.shape == (
        7 * len(DEFAULT_ROCK_DENSITY_GRID_G_CM3),
        5,
    )

    assert table.columns.tolist() == [
        "rock_density_g_cm3",
        "explosive_to_rock_density_ratio",
        "model_id",
        "model_name",
        "burden_m",
    ]

    assert (
        table["rock_density_g_cm3"]
        .drop_duplicates()
        .tolist()
        == list(DEFAULT_ROCK_DENSITY_GRID_G_CM3)
    )

    assert set(table["model_id"]) == MODEL_IDS

    model_counts = table.groupby(
        "rock_density_g_cm3"
    )["model_id"].nunique()

    assert model_counts.eq(7).all()


def test_density_ratio_is_calculated_consistently():
    table = build_gole_gohar_rock_density_sensitivity_table()

    for row in table.itertuples():
        expected_ratio = 0.85 / row.rock_density_g_cm3

        assert math.isclose(
            row.explosive_to_rock_density_ratio,
            expected_ratio,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )


def test_reference_density_reproduces_known_konya_outputs():
    table = build_gole_gohar_rock_density_sensitivity_table()

    reference_rows = table[
        table["rock_density_g_cm3"] == 4.37
    ].set_index("model_id")

    assert reference_rows.loc[
        "CONV_KONYA_1972",
        "burden_m",
    ] == pytest.approx(
        5.5273236163425565,
        rel=1e-12,
        abs=1e-12,
    )

    assert reference_rows.loc[
        "CONV_KONYA_1983",
        "burden_m",
    ] == pytest.approx(
        5.689716247139588,
        rel=1e-12,
        abs=1e-12,
    )


def test_only_konya_models_change_with_rock_density():
    table = build_gole_gohar_rock_density_sensitivity_table()

    unique_burdens = table.groupby(
        "model_id"
    )["burden_m"].nunique()

    changing_models = set(
        unique_burdens[unique_burdens > 1].index
    )

    assert changing_models == {
        "CONV_KONYA_1972",
        "CONV_KONYA_1983",
    }


def test_konya_burdens_decrease_as_rock_density_increases():
    table = build_gole_gohar_rock_density_sensitivity_table()

    for model_id in (
        "CONV_KONYA_1972",
        "CONV_KONYA_1983",
    ):
        model_rows = (
            table[table["model_id"] == model_id]
            .sort_values("rock_density_g_cm3")
        )

        assert model_rows[
            "burden_m"
        ].is_monotonic_decreasing


@pytest.mark.parametrize(
    "values",
    [
        [],
        [2.75, 2.75],
        [0.0, 2.75],
        [-1.0, 2.75],
    ],
)
def test_invalid_density_grids_are_rejected(values):
    with pytest.raises(ValueError):
        build_gole_gohar_rock_density_sensitivity_table(
            values
        )


def test_string_density_grid_is_rejected():
    with pytest.raises(TypeError):
        build_gole_gohar_rock_density_sensitivity_table(
            "2.75"
        )


def test_custom_density_grid_is_sorted():
    table = build_gole_gohar_rock_density_sensitivity_table(
        [5.30, 2.75, 4.37]
    )

    assert (
        table["rock_density_g_cm3"]
        .drop_duplicates()
        .tolist()
        == [2.75, 4.37, 5.30]
    )


def test_research_safety_metadata_is_recorded():
    table = build_gole_gohar_rock_density_sensitivity_table()

    assert table.attrs["analysis_type"] == (
        "one_factor_at_a_time"
    )

    assert table.attrs["varied_parameter"] == (
        "rock_density_g_cm3"
    )

    assert table.attrs["reference_rock_density_g_cm3"] == (
        pytest.approx(4.37)
    )

    assert table.attrs["sampled_interval_g_cm3"] == {
        "minimum": 1.8,
        "maximum": 5.3,
    }

    assert table.attrs["decision_gate"] == (
        "RESEARCH_COMPARATOR_ONLY"
    )

    assert (
        "must not be treated as interchangeable"
        in table.attrs["density_warning"]
    )