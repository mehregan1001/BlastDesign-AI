import pandas as pd
import pytest

from blastdesign import (
    DEFAULT_DIAMETER_GRID_MM,
    build_diameter_ensemble_summary,
    build_gole_gohar_diameter_sensitivity_table,
    build_model_diameter_response_summary,
    gole_gohar_burden_results,
)


def test_ensemble_summary_quantifies_disagreement_by_diameter():
    sensitivity = (
        build_gole_gohar_diameter_sensitivity_table()
    )
    summary = build_diameter_ensemble_summary(
        sensitivity
    )

    assert len(summary) == len(
        DEFAULT_DIAMETER_GRID_MM
    )
    assert summary["model_count"].eq(7).all()
    assert summary["range_m"].gt(0).all()

    reference = summary[
        summary["hole_diameter_mm"].eq(251.0)
    ].iloc[0]

    benchmark = gole_gohar_burden_results()

    assert reference["mean_burden_m"] == pytest.approx(
        benchmark["burden_m"].mean()
    )
    assert reference["range_m"] == pytest.approx(
        benchmark["burden_m"].max()
        - benchmark["burden_m"].min()
    )


def test_model_summary_preserves_reference_outputs():
    sensitivity = (
        build_gole_gohar_diameter_sensitivity_table()
    )
    summary = (
        build_model_diameter_response_summary(
            sensitivity
        )
    )

    observed = (
        summary.set_index("model_id")
        ["reference_burden_m"]
        .sort_index()
    )
    expected = (
        gole_gohar_burden_results()
        .set_index("model_id")
        ["burden_m"]
        .sort_index()
    )

    pd.testing.assert_series_equal(
        observed,
        expected,
        check_names=False,
    )

    assert len(summary) == 7
    assert summary["endpoint_change_m"].gt(0).all()
    assert (
        summary.attrs["decision_gate"]
        == "RESEARCH_COMPARATOR_ONLY"
    )


def test_summary_rejects_duplicate_or_incomplete_tables():
    sensitivity = (
        build_gole_gohar_diameter_sensitivity_table()
    )

    duplicate = pd.concat(
        [
            sensitivity,
            sensitivity.iloc[[0]],
        ],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError,
        match="duplicate",
    ):
        build_diameter_ensemble_summary(
            duplicate
        )

    incomplete = (
        sensitivity.drop(index=0)
        .reset_index(drop=True)
    )

    with pytest.raises(
        ValueError,
        match="exactly seven",
    ):
        build_diameter_ensemble_summary(
            incomplete
        )