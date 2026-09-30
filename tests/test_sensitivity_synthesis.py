import json

import pytest

from blastdesign import (
    build_integrated_sensitivity_summary,
    build_model_parameter_dependency_matrix,
)


@pytest.fixture(scope="module")
def integrated_summary():
    return build_integrated_sensitivity_summary()


@pytest.fixture(scope="module")
def dependency_matrix():
    return build_model_parameter_dependency_matrix()


def test_integrated_summary_schema(integrated_summary):
    assert integrated_summary.shape == (5, 17)

    assert integrated_summary.columns.tolist() == [
        "analysis_id",
        "parameter_name",
        "parameter_label",
        "unit",
        "reference_value",
        "sampled_minimum",
        "sampled_maximum",
        "sample_count",
        "responding_model_count",
        "responding_model_ids_json",
        "reference_mean_burden_m",
        "reference_range_m",
        "minimum_ensemble_range_m",
        "minimum_range_parameter_values_json",
        "maximum_ensemble_range_m",
        "maximum_range_parameter_values_json",
        "ensemble_range_span_m",
    ]

    assert integrated_summary["analysis_id"].tolist() == [
        "diameter",
        "ucs",
        "explosive_density",
        "rock_density",
        "ash_burden_ratio",
    ]


def test_reference_metrics_are_consistent(
    integrated_summary,
):
    assert integrated_summary[
        "reference_mean_burden_m"
    ].tolist() == pytest.approx(
        [6.137371203249507] * 5
    )

    assert integrated_summary[
        "reference_range_m"
    ].tolist() == pytest.approx(
        [1.4558649429218485] * 5
    )


def test_responding_model_counts(
    integrated_summary,
):
    observed = dict(
        zip(
            integrated_summary["analysis_id"],
            integrated_summary[
                "responding_model_count"
            ],
        )
    )

    assert observed == {
        "diameter": 7,
        "ucs": 2,
        "explosive_density": 2,
        "rock_density": 2,
        "ash_burden_ratio": 1,
    }


def test_minimum_range_parameter_values(
    integrated_summary,
):
    rows = integrated_summary.set_index(
        "analysis_id"
    )

    assert json.loads(
        rows.loc[
            "diameter",
            "minimum_range_parameter_values_json",
        ]
    ) == [271.0]

    assert json.loads(
        rows.loc[
            "ucs",
            "minimum_range_parameter_values_json",
        ]
    ) == [70.0, 85.0, 110.0]

    assert json.loads(
        rows.loc[
            "explosive_density",
            "minimum_range_parameter_values_json",
        ]
    ) == [1.0]

    assert json.loads(
        rows.loc[
            "rock_density",
            "minimum_range_parameter_values_json",
        ]
    ) == [
        2.4,
        2.6,
        2.75,
        3.0,
        3.3,
        3.75,
    ]

    assert json.loads(
        rows.loc[
            "ash_burden_ratio",
            "minimum_range_parameter_values_json",
        ]
    ) == [22.5, 25.0, 27.5]


def test_maximum_range_parameter_values(
    integrated_summary,
):
    rows = integrated_summary.set_index(
        "analysis_id"
    )

    assert json.loads(
        rows.loc[
            "diameter",
            "maximum_range_parameter_values_json",
        ]
    ) == [311.0]

    assert json.loads(
        rows.loc[
            "ucs",
            "maximum_range_parameter_values_json",
        ]
    ) == [
        110.001,
        180.0,
        180.001,
        220.0,
    ]

    assert json.loads(
        rows.loc[
            "explosive_density",
            "maximum_range_parameter_values_json",
        ]
    ) == [0.7]

    assert json.loads(
        rows.loc[
            "rock_density",
            "maximum_range_parameter_values_json",
        ]
    ) == [5.3]

    assert json.loads(
        rows.loc[
            "ash_burden_ratio",
            "maximum_range_parameter_values_json",
        ]
    ) == [40.0]


def test_responding_model_identifiers_are_json(
    integrated_summary,
):
    rows = integrated_summary.set_index(
        "analysis_id"
    )

    assert json.loads(
        rows.loc[
            "ucs",
            "responding_model_ids_json",
        ]
    ) == [
        "CONV_JIMENO",
        "CONV_TATIYA",
    ]

    assert json.loads(
        rows.loc[
            "explosive_density",
            "responding_model_ids_json",
        ]
    ) == [
        "CONV_KONYA_1972",
        "CONV_KONYA_1983",
    ]

    assert json.loads(
        rows.loc[
            "ash_burden_ratio",
            "responding_model_ids_json",
        ]
    ) == ["CONV_ASH"]


def test_integrated_summary_safety_metadata(
    integrated_summary,
):
    assert set(integrated_summary.attrs) == {
        "decision_gate",
        "analysis_type",
        "comparison_warning",
    }
    assert integrated_summary.attrs[
        "decision_gate"
    ] == "RESEARCH_COMPARATOR_ONLY"
    assert "must not be interpreted" in (
        integrated_summary.attrs[
            "comparison_warning"
        ]
    )


def test_dependency_matrix_schema(
    dependency_matrix,
):
    assert dependency_matrix.shape == (7, 8)

    assert dependency_matrix.columns.tolist() == [
        "model_id",
        "model_name",
        "hole_diameter_mm",
        "ucs_mpa",
        "explosive_density_g_cm3",
        "rock_density_g_cm3",
        "ash_burden_ratio",
        "responsive_parameter_count",
    ]


def test_dependency_matrix_response_patterns(
    dependency_matrix,
):
    expected_responders = {
        "hole_diameter_mm": {
            "CONV_ASH",
            "CONV_BHANDARI",
            "CONV_JIMENO",
            "CONV_KONYA_1972",
            "CONV_KONYA_1983",
            "CONV_RUSTAN",
            "CONV_TATIYA",
        },
        "ucs_mpa": {
            "CONV_JIMENO",
            "CONV_TATIYA",
        },
        "explosive_density_g_cm3": {
            "CONV_KONYA_1972",
            "CONV_KONYA_1983",
        },
        "rock_density_g_cm3": {
            "CONV_KONYA_1972",
            "CONV_KONYA_1983",
        },
        "ash_burden_ratio": {
            "CONV_ASH",
        },
    }

    for parameter, expected in (
        expected_responders.items()
    ):
        observed = set(
            dependency_matrix.loc[
                dependency_matrix[parameter],
                "model_id",
            ]
        )
        assert observed == expected

    observed_counts = dict(
        zip(
            dependency_matrix["model_id"],
            dependency_matrix[
                "responsive_parameter_count"
            ],
        )
    )

    assert observed_counts == {
        "CONV_ASH": 2,
        "CONV_BHANDARI": 1,
        "CONV_JIMENO": 2,
        "CONV_KONYA_1972": 3,
        "CONV_KONYA_1983": 3,
        "CONV_RUSTAN": 1,
        "CONV_TATIYA": 2,
    }


def test_dependency_matrix_safety_metadata(
    dependency_matrix,
):
    assert set(dependency_matrix.attrs) == {
        "decision_gate",
        "analysis_type",
        "interpretation_warning",
    }
    assert dependency_matrix.attrs[
        "decision_gate"
    ] == "RESEARCH_COMPARATOR_ONLY"
    assert "does not establish" in (
        dependency_matrix.attrs[
            "interpretation_warning"
        ]
    )