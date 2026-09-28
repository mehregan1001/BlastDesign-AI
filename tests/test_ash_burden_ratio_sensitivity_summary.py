import pandas as pd
import pytest

from blastdesign import (
    build_ash_burden_ratio_ensemble_summary,
    build_gole_gohar_ash_burden_ratio_sensitivity_table,
    build_model_ash_burden_ratio_response_summary,
)


def build_table():
    return (
        build_gole_gohar_ash_burden_ratio_sensitivity_table()
    )


def test_ensemble_summary_structure_and_reference_values():
    summary = build_ash_burden_ratio_ensemble_summary(
        build_table()
    )

    assert summary.shape == (9, 7)
    assert summary.columns.tolist() == [
        "ash_burden_ratio",
        "model_count",
        "mean_burden_m",
        "median_burden_m",
        "minimum_burden_m",
        "maximum_burden_m",
        "range_m",
    ]
    assert summary["model_count"].eq(7).all()

    reference_row = summary[
        summary["ash_burden_ratio"].eq(25.0)
    ].iloc[0]

    assert reference_row["mean_burden_m"] == pytest.approx(
        6.137371203249507
    )
    assert reference_row["range_m"] == pytest.approx(
        1.4558649429218485
    )


def test_ensemble_summary_is_sorted():
    table = (
        build_gole_gohar_ash_burden_ratio_sensitivity_table(
            [40.0, 20.0, 25.0]
        )
    )

    summary = build_ash_burden_ratio_ensemble_summary(
        table
    )

    assert summary["ash_burden_ratio"].tolist() == [
        20.0,
        25.0,
        40.0,
    ]


def test_model_summary_identifies_only_ash_response():
    summary = (
        build_model_ash_burden_ratio_response_summary(
            build_table()
        )
    )

    responsive_models = summary.loc[
        summary["responds_to_ash_burden_ratio"],
        "model_id",
    ].tolist()

    assert responsive_models == ["CONV_ASH"]
    assert len(summary) == 7


def test_ash_model_summary_preserves_endpoint_behavior():
    summary = (
        build_model_ash_burden_ratio_response_summary(
            build_table()
        )
    )

    ash_row = summary[
        summary["model_id"].eq("CONV_ASH")
    ].iloc[0]

    assert ash_row["lower_ash_burden_ratio"] == 20.0
    assert ash_row["upper_ash_burden_ratio"] == 40.0
    assert ash_row["burden_at_lower_endpoint_m"] == (
        pytest.approx(5.02)
    )
    assert ash_row["reference_burden_m"] == (
        pytest.approx(6.275)
    )
    assert ash_row["burden_at_upper_endpoint_m"] == (
        pytest.approx(10.04)
    )
    assert ash_row["endpoint_change_m"] == (
        pytest.approx(5.02)
    )
    assert ash_row["endpoint_change_percent"] == (
        pytest.approx(100.0)
    )
    assert ash_row["burden_range_m"] == (
        pytest.approx(5.02)
    )


def test_summaries_preserve_research_safety_metadata():
    table = build_table()

    ensemble = build_ash_burden_ratio_ensemble_summary(
        table
    )
    model_summary = (
        build_model_ash_burden_ratio_response_summary(
            table
        )
    )

    assert ensemble.attrs["decision_gate"] == (
        "RESEARCH_COMPARATOR_ONLY"
    )
    assert model_summary.attrs["decision_gate"] == (
        "RESEARCH_COMPARATOR_ONLY"
    )
    assert "not calibrated" in (
        ensemble.attrs["interpretation_warning"]
    )
    assert "not predictive accuracy" in (
        model_summary.attrs["interpretation_warning"]
    )


def test_model_summary_requires_reference_ratio():
    with pytest.raises(ValueError):
        build_model_ash_burden_ratio_response_summary(
            build_table(),
            reference_ash_burden_ratio=26.0,
        )


def test_model_summary_rejects_inconsistent_names():
    table = build_table()
    changed_row = table[
        table["model_id"].eq("CONV_ASH")
    ].index[0]

    table.loc[changed_row, "model_name"] = (
        "Inconsistent Ash name"
    )

    with pytest.raises(ValueError):
        build_model_ash_burden_ratio_response_summary(
            table
        )


def test_summary_rejects_non_dataframe_input():
    with pytest.raises(TypeError):
        build_ash_burden_ratio_ensemble_summary(
            []
        )


def test_summary_rejects_missing_columns():
    table = build_table().drop(
        columns=["burden_m"]
    )

    with pytest.raises(ValueError):
        build_ash_burden_ratio_ensemble_summary(
            table
        )


def test_summary_rejects_empty_table():
    empty_table = pd.DataFrame(
        columns=[
            "ash_burden_ratio",
            "model_id",
            "model_name",
            "burden_m",
        ]
    )

    with pytest.raises(ValueError):
        build_ash_burden_ratio_ensemble_summary(
            empty_table
        )


def test_summary_rejects_duplicate_ratio_model_rows():
    table = build_table()
    duplicated_table = pd.concat(
        [
            table,
            table.iloc[[0]],
        ],
        ignore_index=True,
    )

    with pytest.raises(ValueError):
        build_ash_burden_ratio_ensemble_summary(
            duplicated_table
        )


def test_summary_rejects_incomplete_model_sets():
    table = build_table().drop(
        index=build_table().index[0]
    )

    with pytest.raises(ValueError):
        build_ash_burden_ratio_ensemble_summary(
            table
        )