from pathlib import Path

from blastdesign_ai.__main__ import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REFERENCE_REPORT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "burden_decision_report_step_24_21.json"
)


def test_cli_validates_reference_research_report(capsys):
    exit_code = main([str(REFERENCE_REPORT)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Contract validation: PASSED" in captured.out
    assert "research-comparator safeguards enforced" in captured.out


def test_cli_rejects_missing_report(tmp_path, capsys):
    missing_report = tmp_path / "missing_report.json"

    exit_code = main([str(missing_report)])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Contract validation: FAILED" in captured.out


def test_cli_rejects_invalid_json(tmp_path, capsys):
    invalid_report = tmp_path / "invalid_report.json"

    invalid_report.write_text(
        "{ this is not valid JSON }",
        encoding="utf-8",
    )

    exit_code = main([str(invalid_report)])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Contract validation: FAILED" in captured.out