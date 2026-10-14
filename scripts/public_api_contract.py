"""Collect the public-interface baseline without freezing runtime annotations.

Used by the v1.0 preparation script and its compatibility tests. Importing
this helper does not write a baseline. Tests read the saved JSON; they never
regenerate it. Calculation results continue to be checked by the existing
model and artifact tests.
"""

from __future__ import annotations

from collections.abc import Mapping
import importlib
import inspect
import math
from numbers import Integral, Real

import pandas as pd


NAMESPACES = ("blastdesign", "blastdesign_ai")
ANALYSES = (
    ("diameter", "build_gole_gohar_diameter_sensitivity_table", "build_diameter_ensemble_summary", "build_model_diameter_response_summary"),
    ("ucs", "build_gole_gohar_ucs_sensitivity_table", "build_ucs_ensemble_summary", "build_model_ucs_response_summary"),
    ("explosive_density", "build_gole_gohar_explosive_density_sensitivity_table", "build_explosive_density_ensemble_summary", "build_model_explosive_density_response_summary"),
    ("rock_density", "build_gole_gohar_rock_density_sensitivity_table", "build_rock_density_ensemble_summary", "build_model_rock_density_response_summary"),
    ("ash_burden_ratio", "build_gole_gohar_ash_burden_ratio_sensitivity_table", "build_ash_burden_ratio_ensemble_summary", "build_model_ash_burden_ratio_response_summary"),
    ("joint_density", "build_gole_gohar_joint_density_sensitivity_table", "build_joint_density_ensemble_summary", "build_model_joint_density_response_summary"),
)
DIRECT_DATAFRAMES = (
    "build_integrated_sensitivity_summary",
    "build_model_parameter_dependency_matrix",
    "build_konya_density_elasticity_summary",
    "build_gole_gohar_konya_density_elasticity_table",
)


def normalize(value):
    """Serialize only deterministic JSON-compatible public defaults."""
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, Real):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("Non-finite public default cannot enter the contract.")
        return number
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise TypeError("Public mapping defaults must use string keys.")
        return {key: normalize(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [normalize(item) for item in value]
    if hasattr(value, "item"):
        scalar = value.item()
        if scalar is not value:
            return normalize(scalar)
    raise TypeError(f"Unsupported public default type: {type(value).__name__}")


def describe_parameters(function) -> list[dict]:
    parameters = []
    for parameter in inspect.signature(function).parameters.values():
        record = {"name": parameter.name, "kind": parameter.kind.name}
        record["has_default"] = parameter.default is not inspect.Parameter.empty
        if record["has_default"]:
            record["default"] = normalize(parameter.default)
        parameters.append(record)
    return parameters


def describe_function(function) -> dict:
    signature = inspect.signature(function)
    display = signature.replace(
        parameters=[p.replace(annotation=inspect.Parameter.empty) for p in signature.parameters.values()],
        return_annotation=inspect.Signature.empty,
    )
    origin = getattr(function, "__module__", "")
    function_name = getattr(function, "__name__", "")
    alias = f"{origin}.{function_name}"
    if origin not in NAMESPACES and not origin.startswith(("blastdesign.", "blastdesign_ai.")):
        raise ValueError(f"Unexpected public function origin: {alias}")
    return {
        "kind": "function",
        "parameters": describe_parameters(function),
        "display_signature": str(display),
        "source_alias": alias,
    }


def describe_dataframe(frame) -> dict:
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("A documented DataFrame builder returned a different type.")
    columns = frame.columns.tolist()
    if not all(isinstance(column, str) for column in columns):
        raise TypeError("Contract DataFrame columns must be strings.")
    if len(columns) != len(set(columns)):
        raise ValueError("Contract DataFrame columns must be unique.")
    return {
        "columns": columns,
        "decision_gate": normalize(frame.attrs.get("decision_gate")),
    }


def collect_contract() -> dict:
    result = {
        "contract_schema_version": 1,
        "target_release": "1.0.0",
        "namespaces": {},
        "reference_scenario_inputs": {},
        "dataframes": {},
    }
    for namespace in NAMESPACES:
        module = importlib.import_module(namespace)
        names = module.__all__
        if not isinstance(names, (list, tuple)) or not all(isinstance(name, str) for name in names):
            raise TypeError(f"Invalid public export list in {namespace}.")
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate public exports in {namespace}.")
        exports = {}
        for name in sorted(names):
            value = getattr(module, name)
            if inspect.isfunction(value):
                exports[name] = describe_function(value)
            else:
                exports[name] = {
                    "kind": "constant",
                    "container_type": type(value).__name__,
                    "value": normalize(value),
                }
        result["namespaces"][namespace] = exports

    blastdesign = importlib.import_module("blastdesign")
    required = "build_gole_gohar_konya_density_elasticity_table"
    if required not in blastdesign.__all__:
        raise ValueError("Export the elasticity-grid builder before collecting the v1.0 contract.")
    reference = blastdesign.gole_gohar_reference_inputs()
    result["reference_scenario_inputs"] = normalize(reference)
    for _, table_name, ensemble_name, model_name in ANALYSES:
        table = getattr(blastdesign, table_name)()
        for name, frame in (
            (table_name, table),
            (ensemble_name, getattr(blastdesign, ensemble_name)(table)),
            (model_name, getattr(blastdesign, model_name)(table)),
        ):
            result["dataframes"][f"blastdesign.{name}"] = describe_dataframe(frame)
    for name in DIRECT_DATAFRAMES:
        result["dataframes"][f"blastdesign.{name}"] = describe_dataframe(getattr(blastdesign, name)())
    result["dataframes"]["blastdesign.evaluate_conventional_burden_models"] = describe_dataframe(
        blastdesign.evaluate_conventional_burden_models(**reference)
    )
    return result


def render_reference(contract: dict) -> str:
    lines = [
        "# Public API reference for v1.0.0", "",
        "This reference records the candidate v1.0 public interface. It is paired with",
        "[the compatibility policy](API_COMPATIBILITY.md) and the saved machine-readable",
        "baseline at `data/processed/public_api_contract.json`.", "",
        "Type annotations are omitted here so interpreter-specific annotation formatting",
        "does not define compatibility. Argument names, kinds, and defaults are recorded.", "",
    ]
    for namespace, exports in contract["namespaces"].items():
        lines += [f"## {namespace}", ""]
        for name, description in exports.items():
            if description["kind"] == "function":
                lines += [
                    f"- `{namespace}.{name}{description['display_signature']}`",
                    f"  Existing direct import: `{description['source_alias']}`.", "",
                ]
            else:
                lines += [f"- `{namespace}.{name}`: `{description['value']!r}` ({description['container_type']}).", ""]
    lines += ["## Default research DataFrame schemas", "", "Column order and the recorded decision-gate metadata are part of this baseline.", ""]
    for name, description in contract["dataframes"].items():
        lines += [f"### {name}", "", "```text", *description["columns"], "```", ""]
        if description["decision_gate"] is not None:
            lines += [f"Decision gate: `{description['decision_gate']}`.", ""]
    lines += [
        "## Units and interpretation", "",
        "- Fields ending in `_mm` use millimetres; `_mpa` uses MPa; `_g_cm3` uses g/cm3.",
        "- Geometric burden and range fields ending in `_m` use metres.",
        "- Fields ending in `_percent` use percent.",
        "- Density ratios, the Ash burden ratio, and elasticities are dimensionless.",
        "- The integrated-summary `unit` field identifies each varied parameter's unit.",
        "- Counts, response flags, identifiers, and JSON list fields are not physical measurements.",
        "- Low-level numerical outputs and model disagreement remain research comparisons.", "",
    ]
    return "\n".join(lines)
