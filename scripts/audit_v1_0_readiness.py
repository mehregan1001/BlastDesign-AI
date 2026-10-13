"""Read-only inventory before choosing the BlastDesign-AI 1.0 API.

Run from the repository root with its normal Python environment:
    python -B scripts/audit_v1_0_readiness.py

This script imports interfaces but does not call calculation functions,
install packages, modify files, run tests, or change the version. It is
an inventory, not a release-readiness certificate. Use --json for full
function signatures and structured output.
"""

from __future__ import annotations

import argparse
import importlib
from importlib import metadata
import inspect
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True

NAMESPACES = ("blastdesign", "blastdesign_ai")
ANALYSIS_MODULES = (
    "blastdesign.sensitivity",
    "blastdesign.synthesis",
    "blastdesign.joint_density",
    "blastdesign.density_elasticity",
)


def read_text(root: Path, relative: str) -> str | None:
    path = root / relative
    return path.read_text(encoding="utf-8-sig") if path.is_file() else None


def project_literal(text: str | None, key: str) -> str | None:
    """Read the current project's simple quoted TOML fields conservatively."""
    if text is None:
        return None
    section = re.search(
        r"(?ms)^\[project\]\s*$\n(.*?)(?=^\[|\Z)", text
    )
    if section is None:
        return None
    value = re.search(
        rf"(?m)^{re.escape(key)}\s*=\s*([\"'])([^\r\n]*?)\1\s*(?:#.*)?$",
        section.group(1),
    )
    return value.group(2) if value else None


def function_info(value) -> dict:
    info = {"kind": type(value).__name__}
    if inspect.isfunction(value) or inspect.isbuiltin(value):
        info["module"] = getattr(value, "__module__", None)
        try:
            info["signature"] = str(inspect.signature(value))
        except (TypeError, ValueError):
            info["signature"] = "<unavailable>"
    return info


def collect(root: Path) -> dict:
    config = read_text(root, "pyproject.toml")
    citation = read_text(root, "CITATION.cff")
    citation_version = (
        re.search(r"(?m)^version:\s*[\"']?([^\s\"']+)", citation)
        if citation else None
    )
    report = {
        "scope": "Read-only inventory; installation and release readiness are not certified.",
        "project_root": str(root),
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "versions": {
            "pyproject": project_literal(config, "version"),
            "citation": citation_version.group(1) if citation_version else None,
        },
        "package_metadata": {},
        "namespaces": {},
        "analysis_modules": {},
        "status_markers": [],
        "configuration": {
            "pyproject.toml": config,
            ".github/workflows/tests.yml": read_text(root, ".github/workflows/tests.yml"),
        },
        "issues": [],
    }
    try:
        installed = metadata.metadata("blastdesign-ai")
        report["versions"]["installed"] = installed.get("Version")
        report["package_metadata"] = {
            key: installed.get(key)
            for key in ("Name", "Version", "Requires-Python", "License-Expression")
        }
        report["package_metadata"]["Requires-Dist"] = installed.get_all("Requires-Dist", [])
    except metadata.PackageNotFoundError:
        report["issues"].append("No installed blastdesign-ai distribution was found.")

    declared_functions = set()
    for name in NAMESPACES:
        try:
            module = importlib.import_module(name)
        except Exception as error:
            report["issues"].append(f"Import {name}: {type(error).__name__}: {error}")
            continue
        exports = getattr(module, "__all__", None)
        if not isinstance(exports, (list, tuple)) or not all(isinstance(x, str) for x in exports):
            report["issues"].append(f"{name} has no valid list/tuple of public export names.")
            continue
        duplicates = sorted({x for x in exports if exports.count(x) > 1})
        missing = sorted(x for x in exports if not hasattr(module, x))
        interface = {
            "loaded_file": getattr(module, "__file__", None),
            "exports": list(exports),
            "duplicates": duplicates,
            "missing": missing,
            "objects": {x: function_info(getattr(module, x)) for x in exports if hasattr(module, x)},
        }
        report["namespaces"][name] = interface
        declared_functions.update(
            (info.get("module"), exported_name)
            for exported_name, info in interface["objects"].items()
        )
        if duplicates or missing:
            report["issues"].append(f"{name}: duplicate exports={duplicates}; missing exports={missing}.")
        if name == "blastdesign_ai":
            report["versions"]["imported"] = getattr(module, "__version__", None)

    for name in ANALYSIS_MODULES:
        try:
            module = importlib.import_module(name)
            functions = {
                function_name: function_info(value)
                for function_name, value in vars(module).items()
                if not function_name.startswith("_")
                and inspect.isfunction(value)
                and value.__module__ == name
            }
            report["analysis_modules"][name] = {
                "functions": functions,
                "not_reexported_at_package_level": [
                    x for x in functions if (name, x) not in declared_functions
                ],
            }
        except Exception as error:
            report["issues"].append(f"Import {name}: {type(error).__name__}: {error}")

    for relative in ("README.md", "docs/burden_model_research_note.md"):
        text = read_text(root, relative)
        if text is None:
            report["issues"].append(f"Missing {relative}.")
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if re.search(r"alpha|preliminary public research prototype|software status|passing tests|passing automated tests", line, re.I):
                report["status_markers"].append(f"{relative}:{number}: {line}")
    values = report["versions"]
    report["version_alignment"] = (
        "MATCH" if len(values) == 4 and all(values.values()) and len(set(values.values())) == 1
        else "REVIEW REQUIRED"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="Print the complete structured inventory.")
    args = parser.parse_args()
    root = args.root.resolve()
    if not (root / "pyproject.toml").is_file() or not (root / "src" / "blastdesign").is_dir():
        parser.error("Run from the BlastDesign-AI repository root, or supply --root.")
    report = collect(root)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=True))
        return 0
    print(report["scope"])
    print("Project:", report["project_root"])
    print("Python:", report["python_executable"], "|", report["python_version"])
    print("Versions:", report["versions"], "|", report["version_alignment"])
    print("Installed metadata:", report["package_metadata"])
    for name, interface in report["namespaces"].items():
        print("\nNAMESPACE:", name)
        print("Loaded file:", interface["loaded_file"])
        print("Declared exports:", ", ".join(interface["exports"]))
        print("Duplicate exports:", interface["duplicates"], "| Missing exports:", interface["missing"])
    for name, interface in report["analysis_modules"].items():
        print("\nSUBMODULE:", name)
        print("Public functions without package-level reexport:", interface["not_reexported_at_package_level"])
    print("\nDOCUMENTATION STATUS MARKERS")
    print("\n".join(report["status_markers"]) or "None found.")
    print("\nISSUES REQUIRING REVIEW")
    print("\n".join(report["issues"]) or "No import/export inventory issues found.")
    for relative, text in report["configuration"].items():
        print("\nFILE:", relative)
        print(text if text is not None else "<not found at this path>")
    print("Still required: API/schema compatibility policy, a fresh non-editable installation check,")
    print("artifact/notebook reproduction review, and review of the latest CI results.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
