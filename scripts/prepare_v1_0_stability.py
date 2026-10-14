"""Prepare the API policy, compatibility baseline/tests, and wheel-testing CI.

Save this and public_api_contract.py in scripts/, then run:
    python -B scripts/prepare_v1_0_stability.py

No version or release-date fields are changed. All planned edits are validated
before writing. Existing files are backed up outside the repository. Repeating
the command is safe when the interface has not changed. A differing existing
baseline is rejected instead of silently regenerating it to hide a regression.
Use --dry-run for diffs and a summary without writes.
"""

from __future__ import annotations

import argparse
import ast
import difflib
import importlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile

sys.dont_write_bytecode = True


POLICY = """# Public API and compatibility policy

Starting with version 1.0.0, BlastDesign-AI commits to a documented software
interface for its reconstructed research comparator. Software-interface
stability does not establish independent field validation or operational
blast-design suitability.

## Supported interface

- Public exports declared by `blastdesign.__all__` and `blastdesign_ai.__all__`.
- Existing direct-import aliases listed in [the API reference](PUBLIC_API_REFERENCE.md).
- Documented argument names, positional/keyword kinds, and default values.
- Documented physical units, reference-scenario inputs, and default sampling grids.
- Column names and order for the recorded research DataFrame schemas.
- The existing `blastdesign-validate REPORT.json` command: zero exit status for
  successful validation and nonzero status for an invalid report or invocation.

The saved baseline is `data/processed/public_api_contract.json`. Three
compatibility tests compare it with the implementation. They do not regenerate
the baseline during a test run.

## Versioning commitments

- Patch releases contain compatible corrections. A numerical bug fix may alter
  computed values; the correction, affected outputs, and supporting reasoning
  must be documented, and dependent artifacts must be regenerated.
- Minor releases can add compatible functionality. Existing supported calls,
  units, and output schemas must retain their documented interpretation.
- Removing or renaming supported interfaces, changing required arguments, or
  making an incompatible unit/schema change requires a major release.
- Deprecations must be documented before removal.
- Published release tags and their recorded artifacts are not rewritten.

An intentional interface change requires reviewing the compatibility policy,
versioning impact, tests, reference, and saved baseline together. An unexpected
test failure is not resolved by automatically recapturing the baseline.

## What the baseline does not freeze

Private names beginning with `_`, internal code organisation, type-annotation
rendering, exact error-message text, incidental DataFrame attributes, pandas
storage dtypes, notebook execution counters, and figure bytes are outside this
interface contract. Documented direct-import aliases remain supported even if
implementation code is reorganised.

The baseline protects interfaces. Existing equation, decision-contract, and
saved-artifact tests protect numerical behaviour and research safeguards.
Passing software tests does not measure predictive accuracy against mine data.

## Installation and platform checks

`python scripts/check_wheel_installation.py` builds a normal wheel from a
temporary source copy, installs it with its declared dependencies into a fresh
virtual environment, checks package origins and metadata, runs the repository
suite against that wheel, and validates the saved research report with the
installed command-line entry point.

Release CI is configured for Linux on Python 3.10, 3.11, 3.12, 3.13, and 3.14,
plus Windows on Python 3.11. Review successful runs for the release commit;
configuration alone is not evidence that those environments passed. This
matrix does not test every allowed dependency combination or every future
Python release.

The wheel supplies the two Python packages and validator. Research notebooks,
saved CSV/JSON artifacts, figures, and documentation are obtained from the
source repository or release source archive.

## Reproducibility and research scope

Saved-artifact tests compare the recorded tables with regenerated calculations.
Retain units and interpretation metadata when exporting: CSV does not preserve
DataFrame attributes. Record Python and dependency versions when reproducing
research outputs. Re-run and save a modified notebook before committing its
outputs, and regenerate `CHECKSUMS.sha256` after the final file changes.

The existing `RESEARCH_COMPARATOR_ONLY` decision gate remains in force.
Structural model disagreement and local elasticities are deterministic
equation comparisons; they are not calibrated predictive uncertainty or
field-ready operational burden recommendations. No new field-validation
claim is introduced by the 1.0 software milestone.
"""

WORKFLOW = """name: BlastDesign-AI automated tests

"on":
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read

jobs:
  tests:
    name: ${{ matrix.os }} - Python ${{ matrix.python-version }} - installed wheel
    runs-on: ${{ matrix.os }}
    timeout-minutes: 30
    strategy:
      fail-fast: false
      matrix:
        os:
          - ubuntu-latest
        python-version:
          - "3.10"
          - "3.11"
          - "3.12"
          - "3.13"
          - "3.14"
        include:
          - os: windows-latest
            python-version: "3.11"
    steps:
      - name: Download repository
        uses: actions/checkout@v7
      - name: Configure Python
        uses: actions/setup-python@v7
        with:
          python-version: ${{ matrix.python-version }}
      - name: Build, install, and test the normal wheel and validator
        run: python scripts/check_wheel_installation.py
"""

PREVIOUS_WORKFLOW = r"""name: BlastDesign-AI automated tests

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read

jobs:
  tests:
    name: Python ${{ matrix.python-version }} - package and validator
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version:
          - "3.10"
          - "3.11"
          - "3.12"
          - "3.13"
          - "3.14"
    steps:
      - name: Download repository
        uses: actions/checkout@v7
      - name: Configure Python
        uses: actions/setup-python@v7
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install package and test dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e .
          python -m pip install pytest
      - name: Run complete automated test suite
        run: python -m pytest -v
      - name: Validate saved research decision report
        run: |
          blastdesign-validate \
            data/processed/burden_decision_report_step_24_21.json
"""

TESTS = '''# The saved contract is an independent baseline, never regenerated here.
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
'''

README_BLOCK = """<!-- BEGIN PUBLIC API COMPATIBILITY -->
## Public API and compatibility

The supported imports, arguments, defaults, physical units, and research-table
schemas are documented in the [compatibility policy](docs/API_COMPATIBILITY.md)
and [public API reference](docs/PUBLIC_API_REFERENCE.md). A saved JSON baseline
and compatibility tests make unexpected interface changes visible.

Test the normal installed package with:

```text
python scripts/check_wheel_installation.py
```

This creates a temporary environment, verifies wheel imports and metadata,
runs the suite against the installed package, and checks its validator.
Software-interface stability and scientific field validation are distinct;
the research-comparator scope remains in force.
<!-- END PUBLIC API COMPATIBILITY -->
"""

NOTE_BLOCK = """<!-- BEGIN PUBLIC API COMPATIBILITY -->
## Software-interface stability and reproducibility

The v1.0 interface baseline records the declared public imports, function
arguments and defaults, reference-scenario inputs, default grids, and
research DataFrame column schemas. Three compatibility tests check that
baseline; existing equation and saved-artifact tests continue to check the
calculations. The [compatibility policy](API_COMPATIBILITY.md) defines how
future changes are versioned.

The installed-wheel check uses a fresh temporary environment and verifies
that the tested package is imported from that environment rather than the
source checkout. Its result establishes software-installation and regression
evidence for the tested configuration. It does not establish predictive
accuracy or independent field validation. The existing
`RESEARCH_COMPARATOR_ONLY` decision gate and research limitations remain.
<!-- END PUBLIC API COMPATIBILITY -->
"""


def edit_block(text: str, block: str, before_heading: str | None = None) -> str:
    begin, end = "<!-- BEGIN PUBLIC API COMPATIBILITY -->", "<!-- END PUBLIC API COMPATIBILITY -->"
    if text.count(begin) != text.count(end) or text.count(begin) > 1:
        raise ValueError("Malformed existing compatibility documentation block.")
    if begin in text:
        start = text.index(begin)
        stop = text.index(end, start) + len(end)
        return text[:start] + block.rstrip() + text[stop:]
    if before_heading:
        matches = list(re.finditer(rf"(?m)^{re.escape(before_heading)}[ \t]*$", text))
        if len(matches) != 1:
            raise ValueError(f"Expected one {before_heading!r} heading.")
        offset = matches[0].start()
        return text[:offset] + block.rstrip() + "\n\n" + text[offset:]
    return text.rstrip() + "\n\n" + block.rstrip() + "\n"


def add_changelog(text: str) -> str:
    if re.search(r"(?m)^## \[1\.0\.0\] - \d{4}-\d{2}-\d{2}[ \t]*$", text):
        return text
    match = re.search(r"(?m)^## \[Unreleased\][ \t]*$", text)
    if match is None or len(re.findall(r"(?m)^## \[Unreleased\]", text)) != 1:
        raise ValueError("Expected one Unreleased changelog section.")
    following = re.search(r"(?m)^## ", text[match.end():])
    if following is None:
        raise ValueError("Cannot locate released changelog history.")
    stop = match.end() + following.start()
    body = text[match.end():stop].strip()
    sections = {
        "Added": [
            "Public package export of the existing Konya density-elasticity grid builder.",
            "Public API compatibility policy, generated reference, and saved machine-readable interface baseline.",
            "Three compatibility tests covering exports/defaults, function arguments/direct-import aliases, and research DataFrame schemas.",
            "Read-only release-readiness inventory and isolated normal-wheel installation, regression, and CLI checks.",
        ],
        "Changed": [
            "Configured CI to test installed wheels on Linux with Python 3.10 through 3.14 and on Windows with Python 3.11.",
            "Linked software-interface compatibility and reproducibility documentation from the README and research note.",
        ],
        "Research safeguards": [
            "Retains the RESEARCH_COMPARATOR_ONLY gate and distinguishes interface stability from independent field validation.",
        ],
    }
    for title, bullets in sections.items():
        missing = [f"- {bullet}" for bullet in bullets if f"- {bullet}" not in body]
        if not missing:
            continue
        heading = re.search(rf"(?m)^### {re.escape(title)}[ \t]*$", body)
        if heading is None:
            body = body.rstrip() + ("\n\n" if body else "") + f"### {title}\n\n" + "\n".join(missing)
        else:
            next_heading = re.search(r"(?m)^### ", body[heading.end():])
            insertion = heading.end() + next_heading.start() if next_heading else len(body)
            body = body[:insertion].rstrip() + "\n" + "\n".join(missing) + "\n\n" + body[insertion:]
    return text[:match.end()] + "\n\n" + body.rstrip() + "\n\n" + text[stop:]


def workflow_key(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def validate_previous_workflow(text: str) -> None:
    if workflow_key(text) in (workflow_key(WORKFLOW), workflow_key(PREVIOUS_WORKFLOW)):
        return
    raise ValueError("The CI workflow differs from the reviewed workflow; no files will be overwritten.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = args.project_root.resolve()
    for namespace in ("blastdesign", "blastdesign_ai"):
        module = importlib.import_module(namespace)
        expected = (root / "src" / namespace / "__init__.py").resolve()
        if Path(module.__file__).resolve() != expected:
            raise ValueError(f"{namespace} is not imported from this checkout: {module.__file__}")
    helper = root / "scripts" / "public_api_contract.py"
    spec = importlib.util.spec_from_file_location("blastdesign_public_api_preparation", helper)
    support = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(support)
    contract = support.collect_contract()
    contract_path = root / "data" / "processed" / "public_api_contract.json"
    if contract_path.exists():
        saved = json.loads(contract_path.read_text(encoding="utf-8-sig"))
        if saved != contract:
            raise ValueError("An existing API baseline differs. It will not be silently regenerated.")

    originals = {}
    normalized = {}
    for relative in ("README.md", "docs/burden_model_research_note.md", "CHANGELOG.md", ".gitignore", ".github/workflows/tests.yml"):
        raw = (root / relative).read_bytes()
        decoded = raw.decode("utf-8-sig")
        originals[relative] = (raw, "\r\n" if "\r\n" in decoded else "\n")
        normalized[relative] = decoded.replace("\r\n", "\n")
    validate_previous_workflow(normalized[".github/workflows/tests.yml"])
    planned = {
        "README.md": edit_block(normalized["README.md"], README_BLOCK, "## Decision safeguards"),
        "docs/burden_model_research_note.md": edit_block(normalized["docs/burden_model_research_note.md"], NOTE_BLOCK),
        "CHANGELOG.md": add_changelog(normalized["CHANGELOG.md"]),
        ".github/workflows/tests.yml": WORKFLOW,
        "docs/API_COMPATIBILITY.md": POLICY,
        "docs/PUBLIC_API_REFERENCE.md": support.render_reference(contract),
        "data/processed/public_api_contract.json": json.dumps(contract, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n",
        "tests/test_api_compatibility.py": TESTS,
    }
    ignore = normalized[".gitignore"]
    exception = "!data/processed/public_api_contract.json"
    if exception not in ignore.splitlines():
        ignore = ignore.rstrip() + "\n\n# Versioned public-interface baseline\n" + exception + "\n"
    planned[".gitignore"] = ignore
    for relative in ("docs/API_COMPATIBILITY.md", "docs/PUBLIC_API_REFERENCE.md", "tests/test_api_compatibility.py"):
        path = root / relative
        if path.exists():
            observed = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
            if observed != planned[relative]:
                raise ValueError(f"Existing {relative} differs from this preparation template; inspect before replacement.")
    compile(TESTS, "tests/test_api_compatibility.py", "exec")
    ast.parse(helper.read_text(encoding="utf-8-sig"))
    changes = []
    for relative, content in planned.items():
        path = root / relative
        if relative in originals:
            raw, newline = originals[relative]
        elif path.exists():
            raw = path.read_bytes()
            newline = "\r\n" if b"\r\n" in raw else "\n"
        else:
            raw, newline = b"", "\n"
        prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
        updated = prefix + content.replace("\n", newline).encode("utf-8")
        if updated != raw:
            changes.append((relative, raw, updated))
    if args.dry_run:
        for relative, raw, updated in changes:
            print("".join(difflib.unified_diff(
                raw.decode("utf-8-sig").splitlines(keepends=True),
                updated.decode("utf-8-sig").splitlines(keepends=True),
                fromfile=relative + " (current)", tofile=relative + " (proposed)",
            )), end="")
    elif changes:
        backup = Path(tempfile.mkdtemp(prefix="blastdesign_stability_backup_"))
        for relative, raw, _ in changes:
            if (root / relative).exists():
                copy = backup / relative
                copy.parent.mkdir(parents=True, exist_ok=True)
                copy.write_bytes(raw)
        for relative, _, updated in changes:
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(updated)
            print("Updated:", relative)
        print("Original-file backups:", backup)
    else:
        print("Stability preparation is already present; no files changed.")
    exports = sum(len(values) for values in contract["namespaces"].values())
    print(f"Contract: {exports} public exports; {len(contract['dataframes'])} DataFrame schemas.")
    print("Added compatibility tests: 3. Version and release dates are unchanged.")


if __name__ == "__main__":
    main()
