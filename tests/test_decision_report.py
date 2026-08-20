"""Automated tests for the burden decision-report builder."""

import sys
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

from blastdesign_ai.decision_contract import (
    validate_burden_decision_contract,
)
from blastdesign_ai.decision_report import (
    build_burden_decision_report,
)


@pytest.fixture
def model_table():
    """Create representative audited burden-model data."""

    return pd.DataFrame(
        [
            {
                "model_id": "CONV_ASH",
                "model_name": "Ash",
                "burden_m": 6.275000,
                "evidence_tier": "B",
                "audit_domain_status": (
                    "PARTIAL_BRANCH_MATCH"
                ),
                "independent_validation_established": False,
            },
            {
                "model_id": "CONV_BHANDARI",
                "model_name": "Bhandari",
                "burden_m": 6.874000,
                "evidence_tier": "C",
                "audit_domain_status": "DOMAIN_UNRESOLVED",
                "independent_validation_established": False,
            },
            {
                "model_id": "CONV_JIMENO",
                "model_name": "Lopez Jimeno",
                "burden_m": 5.773000,
                "evidence_tier": "A",
                "audit_domain_status": (
                    "AUDITED_BRANCH_MATCH"
                ),
                "independent_validation_established": False,
            },
            {
                "model_id": "CONV_KONYA_1972",
                "model_name": "Konya 1972",
                "burden_m": 5.527324,
                "evidence_tier": "C",
                "audit_domain_status": "DOMAIN_UNRESOLVED",
                "independent_validation_established": False,
            },
            {
                "model_id": "CONV_KONYA_1983",
                "model_name": "Konya 1983",
                "burden_m": 5.689716,
                "evidence_tier": "C",
                "audit_domain_status": "DOMAIN_UNRESOLVED",
                "independent_validation_established": False,
            },
            {
                "model_id": "CONV_RUSTAN",
                "model_name": "Rustan",
                "burden_m": 6.983189,
                "evidence_tier": "A",
                "audit_domain_status": (
                    "AUDITED_BRANCH_MATCH"
                ),
                "independent_validation_established": False,
            },
            {
                "model_id": "CONV_TATIYA",
                "model_name": "Tatiya-Al-Ajmi",
                "burden_m": 5.839370,
                "evidence_tier": "B",
                "audit_domain_status": (
                    "PARTIAL_BRANCH_MATCH"
                ),
                "independent_validation_established": False,
            },
        ]
    )


@pytest.fixture
def scenario_table():
    """Create representative structural-uncertainty scenarios."""

    return pd.DataFrame(
        [
            {
                "scenario_id": "ALL_LEGACY_COMPARATOR",
                "model_count": 7,
                "mean_burden_m": 6.137371,
                "median_burden_m": 5.839370,
                "minimum_burden_m": 5.527324,
                "maximum_burden_m": 6.983189,
                "range_m": 1.455865,
            },
            {
                "scenario_id": "AUDITED_PLUS_PARTIAL",
                "model_count": 4,
                "mean_burden_m": 6.217640,
                "median_burden_m": 6.057185,
                "minimum_burden_m": 5.773000,
                "maximum_burden_m": 6.983189,
                "range_m": 1.210189,
            },
            {
                "scenario_id": "AUDITED_ONLY",
                "model_count": 2,
                "mean_burden_m": 6.378094,
                "median_burden_m": 6.378094,
                "minimum_burden_m": 5.773000,
                "maximum_burden_m": 6.983189,
                "range_m": 1.210189,
            },
        ]
    )


def test_builder_creates_valid_report(
    model_table,
    scenario_table,
):
    report = build_burden_decision_report(
        model_table,
        scenario_table,
    )

    checks = validate_burden_decision_contract(
        report
    )

    assert len(checks) == 30


def test_builder_keeps_recommendation_null(
    model_table,
    scenario_table,
):
    report = build_burden_decision_report(
        model_table,
        scenario_table,
    )

    assert (
        report["decision"]["recommended_burden_m"]
        is None
    )


def test_builder_rejects_missing_model_column(
    model_table,
    scenario_table,
):
    incomplete_models = model_table.drop(
        columns=["evidence_tier"]
    )

    with pytest.raises(
        ValueError,
        match="Missing model-table columns",
    ):
        build_burden_decision_report(
            incomplete_models,
            scenario_table,
        )


def test_builder_rejects_missing_scenario(
    model_table,
    scenario_table,
):
    incomplete_scenarios = scenario_table[
        scenario_table["scenario_id"]
        != "AUDITED_ONLY"
    ]

    with pytest.raises(
        ValueError,
        match="Missing scenarios",
    ):
        build_burden_decision_report(
            model_table,
            incomplete_scenarios,
        )


def test_builder_rejects_unexpected_validation(
    model_table,
    scenario_table,
):
    altered_models = model_table.copy()

    altered_models.loc[
        0,
        "independent_validation_established",
    ] = True

    with pytest.raises(
        ValueError,
        match="expects zero independently validated models",
    ):
        build_burden_decision_report(
            altered_models,
            scenario_table,
        )