"""Automated tests for the burden decision contract."""

import copy
import json
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

from blastdesign_ai.decision_contract import (
    validate_burden_decision_contract,
)


REPORT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "burden_decision_report_step_24_21.json"
)


@pytest.fixture
def valid_report():
    """Load a fresh report for every test."""

    assert REPORT_PATH.exists(), (
        f"Required report not found: {REPORT_PATH}"
    )

    with REPORT_PATH.open(
        "r",
        encoding="utf-8",
    ) as report_file:
        return json.load(report_file)


def test_valid_report_passes_30_checks(
    valid_report,
):
    checks = validate_burden_decision_contract(
        valid_report
    )

    assert len(checks) == 30


def test_non_null_recommendation_is_rejected(
    valid_report,
):
    altered_report = copy.deepcopy(valid_report)

    altered_report["decision"][
        "recommended_burden_m"
    ] = 6.10

    with pytest.raises(
        AssertionError,
        match="recommended burden remains null",
    ):
        validate_burden_decision_contract(
            altered_report
        )


def test_duplicate_model_id_is_rejected(
    valid_report,
):
    altered_report = copy.deepcopy(valid_report)

    altered_report["model_outputs"][1][
        "model_id"
    ] = altered_report["model_outputs"][0][
        "model_id"
    ]

    with pytest.raises(
        AssertionError,
        match="model identifiers are unique",
    ):
        validate_burden_decision_contract(
            altered_report
        )


def test_inconsistent_range_is_rejected(
    valid_report,
):
    altered_report = copy.deepcopy(valid_report)

    altered_report["scenario_summaries"][
        "audited_only"
    ]["range_m"] += 0.25

    with pytest.raises(
        AssertionError,
        match="audited_only range is internally consistent",
    ):
        validate_burden_decision_contract(
            altered_report
        )