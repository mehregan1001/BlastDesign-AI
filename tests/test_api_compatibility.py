# The saved contract is an independent baseline, never regenerated here.
from functools import lru_cache
import importlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "blastdesign_public_api_contract_support", ROOT / "scripts" / "public_api_contract.py"
)
SUPPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUPPORT)


@lru_cache(maxsize=1)
def contracts():
    baseline = json.loads((ROOT / "data" / "processed" / "public_api_contract.json").read_text(encoding="utf-8-sig"))
    assert baseline["contract_schema_version"] == 1
    assert baseline["target_release"] == "1.0.0"
    return baseline, SUPPORT.collect_contract()


def test_public_export_names_and_constants_match_contract():
    expected, actual = contracts()
    assert actual["reference_scenario_inputs"] == expected["reference_scenario_inputs"]
    for namespace, exports in expected["namespaces"].items():
        assert set(actual["namespaces"][namespace]) == set(exports), namespace
        for name, record in exports.items():
            observed = actual["namespaces"][namespace][name]
            assert observed["kind"] == record["kind"], (namespace, name)
            if record["kind"] == "constant":
                assert observed == record, (namespace, name)


def test_public_function_parameters_and_aliases_match_contract():
    expected, actual = contracts()
    for namespace, exports in expected["namespaces"].items():
        for name, record in exports.items():
            if record["kind"] != "function":
                continue
            assert actual["namespaces"][namespace][name]["parameters"] == record["parameters"], (namespace, name)
            module_name, alias_name = record["source_alias"].rsplit(".", 1)
            alias = getattr(importlib.import_module(module_name), alias_name)
            assert SUPPORT.describe_parameters(alias) == record["parameters"], record["source_alias"]


def test_default_dataframe_schemas_match_contract():
    expected, actual = contracts()
    assert set(actual["dataframes"]) == set(expected["dataframes"])
    for name, schema in expected["dataframes"].items():
        assert actual["dataframes"][name] == schema, name
