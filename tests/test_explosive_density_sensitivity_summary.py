import pandas as pd
import pytest

from blastdesign import (
    build_explosive_density_ensemble_summary,
    build_gole_gohar_explosive_density_sensitivity_table,
    build_model_explosive_density_response_summary,
    gole_gohar_burden_results,
)


def test_density_ensemble_summary_quantifies_disagreement():
    sensitivity_table = (
        build_gole_gohar_explosive_density_sensitivity_table()
    )

    summary = build_explosive_density_ensemble_summary(
        sensitivity_table
    )

    assert len(summary) == 7
    assert summary["model_count"].eq(7).all()

    indexed = summary.set_index(
        "explosive_density_g_cm3"
    )

    assert indexed.loc[
        0.70, "range_m"
    ] == pytest.approx(
        1.7989019838673785
    )

    assert indexed.loc[
        0.85, "range_m"
    ] == pytest.approx(
        1.4558649429218482
    )

    assert indexed.loc[
        1.00, "range_m"
    ] == pytest.approx(
        1.210188559264405
    )

    assert (
        summary.attrs["decision_gate"]
        == "RESEARCH_COMPARATOR_ONLY"
    )


def test_model_density_summary_identifies_responsive_models():
    sensitivity_table = (
        build_gole_gohar_explosive_density_sensitivity_table()
    )

    summary = (
        build_model_explosive_density_response_summary(
            sensitivity_table
        )
    )

    responsive_models = set(
        summary.loc[
            summary[
                "responds_to_explosive_density"
            ],
            "model_id",
        ]
    )

    assert responsive_models == {
        "CONV_KONYA_1972",
        "CONV_KONYA_1983",
    }

    indexed = summary.set_index("model_id")

    assert indexed.loc[
        "CONV_KONYA_1972",
        "endpoint_change_m",
    ] == pytest.approx(
        0.6475674809985943
    )

    assert indexed.loc[
        "CONV_KONYA_1983",
        "endpoint_change_m",
    ] == pytest.approx(
        0.41354691075514793
    )

    benchmark = (
        gole_gohar_burden_results()
        .set_index("model_id")["burden_m"]
    )

    pd.testing.assert_series_equal(
        indexed["reference_burden_m"],
        benchmark,
        check_names=False,
    )


def test_density_summaries_reject_invalid_tables():
    sensitivity_table = (
        build_gole_gohar_explosive_density_sensitivity_table()
    )

    duplicate_table = pd.concat(
        [
            sensitivity_table,
            sensitivity_table.iloc[[0]],
        ],
        ignore_index=True,
    )

    with pytest.raises(ValueError):
        build_explosive_density_ensemble_summary(
            duplicate_table
        )

    incomplete_table = sensitivity_table.iloc[1:].copy()

    with pytest.raises(ValueError):
        build_model_explosive_density_response_summary(
            incomplete_table
        )

    inconsistent_ratio_table = sensitivity_table.copy()

    inconsistent_ratio_table.loc[
        0,
        "explosive_to_rock_density_ratio",
    ] += 0.01

    with pytest.raises(ValueError):
        build_explosive_density_ensemble_summary(
            inconsistent_ratio_table
        )