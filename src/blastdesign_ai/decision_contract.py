"""Validation of BlastDesign-AI burden decision reports."""

from collections import Counter
from typing import Any

import numpy as np


def validate_burden_decision_contract(
    report: dict[str, Any],
) -> list[str]:
    """Validate the burden decision-report data contract."""

    passed_checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(
                "Decision-contract validation failed: "
                f"{label}"
            )

        passed_checks.append(label)

    check(
        report.get("schema_version") == "1.0",
        "schema version is 1.0",
    )

    check(
        report.get("module")
        == "conventional_burden_comparison",
        "module identifier is correct",
    )

    decision = report.get("decision")

    check(
        isinstance(decision, dict),
        "decision section exists",
    )

    check(
        decision.get("decision_gate")
        == "RESEARCH_COMPARATOR_ONLY",
        "decision gate is research-only",
    )

    check(
        decision.get("software_output_mode")
        == "COMPARATIVE_RANGE_WITH_EVIDENCE_WARNING",
        "software output mode is comparative",
    )

    check(
        decision.get("recommended_burden_m") is None,
        "recommended burden remains null",
    )

    check(
        decision.get("site_calibration_required") is True,
        "site calibration is required",
    )

    check(
        decision.get(
            "independently_validated_model_count"
        ) == 0,
        "validated-model count remains zero",
    )

    scenarios = report.get("scenario_summaries")

    expected_scenario_keys = {
        "all_legacy_models",
        "audited_plus_partial",
        "audited_only",
    }

    check(
        set(scenarios) == expected_scenario_keys,
        "all required scenarios are present",
    )

    expected_model_counts = {
        "all_legacy_models": 7,
        "audited_plus_partial": 4,
        "audited_only": 2,
    }

    for scenario_name, expected_count in (
        expected_model_counts.items()
    ):
        scenario = scenarios[scenario_name]

        minimum = float(
            scenario["minimum_burden_m"]
        )

        maximum = float(
            scenario["maximum_burden_m"]
        )

        mean = float(
            scenario["mean_burden_m"]
        )

        median = float(
            scenario["median_burden_m"]
        )

        reported_range = float(
            scenario["range_m"]
        )

        check(
            scenario["model_count"] == expected_count,
            f"{scenario_name} model count",
        )

        check(
            minimum <= median <= maximum,
            f"{scenario_name} median lies inside range",
        )

        check(
            minimum <= mean <= maximum,
            f"{scenario_name} mean lies inside range",
        )

        check(
            np.isclose(
                reported_range,
                maximum - minimum,
                atol=2e-6,
            ),
            f"{scenario_name} range is internally consistent",
        )

    model_outputs = report.get("model_outputs")

    check(
        isinstance(model_outputs, list),
        "model outputs are stored as a list",
    )

    check(
        len(model_outputs) == 7,
        "seven model outputs are present",
    )

    model_ids = [
        model["model_id"]
        for model in model_outputs
    ]

    check(
        len(model_ids) == len(set(model_ids)),
        "model identifiers are unique",
    )

    tier_counts = Counter(
        model["evidence_tier"]
        for model in model_outputs
    )

    check(
        tier_counts
        == Counter({"A": 2, "B": 2, "C": 3}),
        "evidence-tier distribution is correct",
    )

    check(
        all(
            model["independently_validated"] is False
            for model in model_outputs
        ),
        "all model validation flags remain false",
    )

    check(
        all(
            np.isfinite(float(model["burden_m"]))
            and float(model["burden_m"]) > 0
            for model in model_outputs
        ),
        "all burden values are finite and positive",
    )

    warnings = report.get("warnings")

    check(
        isinstance(warnings, list),
        "warnings are stored as a list",
    )

    check(
        len(warnings) == 4,
        "four evidence warnings are present",
    )

    check(
        all(
            isinstance(warning, str)
            and warning.strip()
            for warning in warnings
        ),
        "all warnings contain text",
    )

    return passed_checks