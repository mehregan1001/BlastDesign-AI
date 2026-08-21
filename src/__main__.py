"""Command-line entry point for BlastDesign-AI research-report validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .decision_contract import validate_burden_decision_contract


def main(argv=None):
    """Validate a saved BlastDesign-AI burden decision report."""

    parser = argparse.ArgumentParser(
        prog="python -m blastdesign_ai",
        description=(
            "Validate a BlastDesign-AI burden decision report "
            "against its research-use decision contract."
        ),
    )

    parser.add_argument(
        "report",
        type=Path,
        help="Path to a burden decision-report JSON file.",
    )

    args = parser.parse_args(argv)
    report_path = args.report.expanduser().resolve()

    try:
        report_text = report_path.read_text(encoding="utf-8")
        report = json.loads(report_text)

        validate_burden_decision_contract(report)

    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        AssertionError,
        ValueError,
        TypeError,
        KeyError,
    ) as error:

        print("Contract validation: FAILED")
        print(f"Report: {report_path}")
        print(f"Reason: {error}")

        return 1

    print("Contract validation: PASSED")
    print(f"Report: {report_path}")
    print("Decision policy: research-comparator safeguards enforced")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())