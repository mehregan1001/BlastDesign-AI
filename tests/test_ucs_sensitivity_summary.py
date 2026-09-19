import pandas as pd
import pytest

from blastdesign import (
    build_gole_gohar_ucs_sensitivity_table,
    build_model_ucs_response_summary,
    build_ucs_ensemble_summary,
    gole_gohar_burden_results,
)


def test_ucs_ensemble_summary_quantifies_disagreement():
    sensitivity_table = (
        build_gole_gohar_ucs_sensitivity_table()
    )

    summary = build_ucs_ensemble_summary(
        sensitivity_table
    )

    assert len(summary) == 11
    assert summary["model_count"].eq(7).all()

    reference_row = (
        summary[summary["ucs_mpa"].eq(85.0)]
        .iloc[0]
    )

    assert reference_row["range_m"] == pytest.approx(
        1.455864942921849
    )
    assert (
        summary.attrs["decision_gate"]
        == "RESEARCH_COMPARATOR_ONLY"
    )


def test_model_ucs_summary_identifies_responsive_models():
    sensitivity_table = (
        build_gole_gohar_ucs_sensitivity_table()
    )

    summary = build_model_ucs_response_summary(
        sensitivity_table
    )

    responsive_models = set(
        summary.loc[
            summary["responds_to_ucs"],
            "model_id",
        ]
    )

    assert responsive_models == {
        "CONV_JIMENO",
        "CONV_TATIYA",
    }

    indexed = summary.set_index("model_id")

    assert indexed.loc[
        "CONV_JIMENO", "burden_range_m"
    ] == pytest.approx(1.757)

    assert indexed.loc[
        "CONV_TATIYA", "burden_range_m"
    ] == pytest.approx(1.85178)

    benchmark = (
        gole_gohar_burden_results()
        .set_index("model_id")
        ["burden_m"]
    )

    pd.testing.assert_series_equal(
        indexed["reference_burden_m"],
        benchmark,
        check_names=False,
    )


def test_ucs_summaries_reject_invalid_tables():
    sensitivity_table = (
        build_gole_gohar_ucs_sensitivity_table()
    )

    duplicate_table = pd.concat(
        [
            sensitivity_table,
            sensitivity_table.iloc[[0]],
        ],
        ignore_index=True,
    )

    with pytest.raises(ValueError):
        build_ucs_ensemble_summary(
            duplicate_table
        )

    incomplete_table = sensitivity_table.iloc[1:].copy()

    with pytest.raises(ValueError):
        build_model_ucs_response_summary(
            incomplete_table
        )