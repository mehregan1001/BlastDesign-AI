import blastdesign_ai


def test_package_version_is_defined():
    assert blastdesign_ai.__version__ == "0.3.0"


def test_public_api_exposes_report_builder():
    assert callable(blastdesign_ai.build_burden_decision_report)


def test_public_api_exposes_contract_validator():
    assert callable(blastdesign_ai.validate_burden_decision_contract)


def test_public_api_is_explicitly_declared():
    assert set(blastdesign_ai.__all__) == {
        "build_burden_decision_report",
        "validate_burden_decision_contract",
    }