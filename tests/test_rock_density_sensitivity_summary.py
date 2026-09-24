import pandas as pd
import pytest

from blastdesign import (
    build_gole_gohar_rock_density_sensitivity_table,
    build_model_rock_density_response_summary,
    build_rock_density_ensemble_summary,
)


RESPONDING_MODELS = {
    "CONV_KONYA_1972",
    "CONV_KONYA_1983",
}


def test_ensemble_summary_structure_and_reference_values():
    table = build_gole_gohar_rock_density_sensitivity_table()
    summary = build_rock_density_ensemble_summary(table)

    assert summary.shape == (12, 8)

    assert summary.columns.tolist() == [
        "rock_density_g_cm3",
        "explosive_to_rock_density_ratio",
        "model_count",
        "mean_burden_m",
        "median_burden_m",
        "minimum_burden_m",
        "maximum_burden_m",
        "range_m",
    ]

    assert summary["model_count"].eq(7).all()

    reference = summary[
        summary["rock_density_g_cm3"].eq(4.37)
    ].iloc[0]

    assert reference["mean_burden_m"] == pytest.approx(
        6.137371203249507
    )

    assert reference["median_burden_m"] == pytest.approx(
        5.839369999999999
    )

    assert reference["minimum_burden_m"] == pytest.approx(
        5.5273236163425565
    )

    assert reference["maximum_burden_m"] == pytest.approx(
        6.983188559264405
    )

    assert reference["range_m"] == pytest.approx(
        1.4558649429218482
    )


def test_model_summary_identifies_density_responses():
    table = build_gole_gohar_rock_density_sensitivity_table()

    summary = build_model_rock_density_response_summary(
        table
    )

    assert summary.shape == (7, 14)

    responding = set(
        summary.loc[
            summary["responds_to_rock_density"],
            "model_id",
        ]
    )

    assert responding == RESPONDING_MODELS


def test_model_summary_preserves_reference_outputs():
    table = build_gole_gohar_rock_density_sensitivity_table()

    summary = build_model_rock_density_response_summary(
        table
    ).set_index("model_id")

    reference_rows = table[
        table["rock_density_g_cm3"].eq(4.37)
    ].set_index("model_id")

    for model_id in reference_rows.index:
        assert summary.loc[
            model_id,
            "reference_burden_m",
        ] == pytest.approx(
            reference_rows.loc[
                model_id,
                "burden_m",
            ]
        )


def test_density_responding_models_have_negative_endpoint_change():
    table = build_gole_gohar_rock_density_sensitivity_table()

    summary = build_model_rock_density_response_summary(
        table
    ).set_index("model_id")

    responding = summary.loc[list(RESPONDING_MODELS)]

    assert responding["endpoint_change_m"].lt(0).all()
    assert responding["burden_range_m"].gt(0).all()

    nonresponding = summary.drop(
        index=list(RESPONDING_MODELS)
    )

    assert nonresponding[
        "endpoint_change_m"
    ].eq(0).all()

    assert nonresponding[
        "burden_range_m"
    ].eq(0).all()


def test_summaries_preserve_research_safety_metadata():
    table = build_gole_gohar_rock_density_sensitivity_table()

    ensemble = build_rock_density_ensemble_summary(table)

    model_summary = (
        build_model_rock_density_response_summary(
            table
        )
    )

    assert ensemble.attrs["decision_gate"] == (
        "RESEARCH_COMPARATOR_ONLY"
    )

    assert model_summary.attrs["decision_gate"] == (
        "RESEARCH_COMPARATOR_ONLY"
    )

    assert (
        "not calibrated predictive uncertainty"
        in ensemble.attrs["interpretation_warning"]
    )

    assert (
        "not predictive accuracy"
        in model_summary.attrs[
            "interpretation_warning"
        ]
    )


def test_model_summary_requires_reference_density():
    table = (
        build_gole_gohar_rock_density_sensitivity_table(
            [2.75, 5.30]
        )
    )

    with pytest.raises(ValueError):
        build_model_rock_density_response_summary(
            table
        )


def test_model_summary_rejects_inconsistent_names():
    table = (
        build_gole_gohar_rock_density_sensitivity_table()
        .copy()
    )

    first_ash_row = table[
        table["model_id"].eq("CONV_ASH")
    ].index[0]

    table.loc[
        first_ash_row,
        "model_name",
    ] = "Inconsistent Ash name"

    with pytest.raises(ValueError):
        build_model_rock_density_response_summary(
            table
        )


def test_summary_rejects_non_dataframe_input():
    with pytest.raises(TypeError):
        build_rock_density_ensemble_summary(
            []
        )


def test_summary_rejects_missing_columns():
    table = (
        build_gole_gohar_rock_density_sensitivity_table()
        .drop(columns=["burden_m"])
    )

    with pytest.raises(ValueError):
        build_rock_density_ensemble_summary(
            table
        )


def test_summary_rejects_duplicate_density_model_rows():
    table = build_gole_gohar_rock_density_sensitivity_table()

    duplicated = pd.concat(
        [
            table,
            table.iloc[[0]],
        ],
        ignore_index=True,
    )

    with pytest.raises(ValueError):
        build_rock_density_ensemble_summary(
            duplicated
        )


def test_summary_rejects_incomplete_model_sets():
    table = (
        build_gole_gohar_rock_density_sensitivity_table()
        .drop(index=0)
    )

    with pytest.raises(ValueError):
        build_rock_density_ensemble_summary(
            table
        )


def test_summary_rejects_inconsistent_density_ratios():
    table = (
        build_gole_gohar_rock_density_sensitivity_table()
        .copy()
    )

    table.loc[
        table.index[0],
        "explosive_to_rock_density_ratio",
    ] = 999.0

    with pytest.raises(ValueError):
        build_rock_density_ensemble_summary(
            table
        )