"""Align the verified interface milestone with version 1.0.0.

Save in scripts/ and run with the planned release date:
    python -B scripts/prepare_v1_0_0_release.py --release-date YYYY-MM-DD

The API baseline and stability files must already be present. All metadata
and documentation edits are validated before writes; original files are
backed up outside the repository. Equations, API exports, data tables, and
published release history are preserved. Use --dry-run to inspect changes.
"""

from __future__ import annotations

import argparse
from datetime import date
import difflib
import json
from pathlib import Path
import re
import tempfile


VERSION = "1.0.0"
PREVIOUS_VERSION = "0.9.0"
TEST_COUNT = 218
SUBTEST_COUNT = 228
REPOSITORY = "https://github.com/mehregan1001/BlastDesign-AI"
OLD_STATUS = "## Status note: Preliminary public research prototype (alpha)."
NEW_STATUS = "## Status: Stable research software interface (v1.0.0)"
STATUS_EXPLANATION = (
    "Version 1.0.0 establishes the documented public software interface for\n"
    "reproducible comparisons of the reconstructed equations. Independent\n"
    "field validation and operational blast-design suitability remain outside\n"
    "the current research scope.\n"
)


def replace_version(text: str, pattern: str, label: str) -> str:
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    if len(matches) != 1:
        raise ValueError(f"Expected one version field in {label}; found {len(matches)}.")
    match = matches[0]
    observed = match.group("version")
    if observed not in (PREVIOUS_VERSION, VERSION):
        raise ValueError(f"Unexpected version {observed!r} in {label}.")
    return text[:match.start("version")] + VERSION + text[match.end("version"):]


def replace_count(text: str, pattern: str, label: str, required: bool = True) -> str:
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    if len(matches) > 1 or (required and len(matches) != 1):
        raise ValueError(f"Expected {'one' if required else 'at most one'} current {label} field.")
    if not matches:
        return text
    match = matches[0]
    observed = int(match.group("count"))
    if observed not in (215, TEST_COUNT):
        raise ValueError(f"Unexpected current test count {observed} in {label}.")
    return text[:match.start("count")] + str(TEST_COUNT) + text[match.end("count"):]


def update_readme(text: str) -> str:
    old = list(re.finditer(r"(?m)^" + re.escape(OLD_STATUS) + r"[ \t]*$", text))
    new = list(re.finditer(r"(?m)^" + re.escape(NEW_STATUS) + r"[ \t]*$", text))
    if len(old) + len(new) != 1:
        raise ValueError("Expected one reviewed README software-status heading.")
    if old:
        match = old[0]
        text = text[:match.start()] + NEW_STATUS + "\n\n" + STATUS_EXPLANATION.rstrip() + text[match.end():]
    text = replace_count(
        text, r"A full test suite with\s+(?:\*\*)?(?P<count>\d+)(?= passing tests)",
        "README test-suite",
    )
    output = list(re.finditer(
        r"(?m)^(?P<count>\d+) passed(?:, (?P<subtests>\d+) subtests passed)?(?: in [\d.]+s)?[ \t]*$", text,
    ))
    if len(output) != 1:
        raise ValueError("Expected one README test-output example.")
    match = output[0]
    if int(match.group("count")) not in (215, TEST_COUNT):
        raise ValueError("Unexpected current README test-output count.")
    if match.group("subtests") and int(match.group("subtests")) != SUBTEST_COUNT:
        raise ValueError("Unexpected README subtest count.")
    return text[:match.start()] + f"{TEST_COUNT} passed, {SUBTEST_COUNT} subtests passed" + text[match.end():]


def update_research_note(text: str) -> str:
    for pattern, label in (
        (r"Python packages? with (?P<count>\d+)(?= passing automated tests)", "research-note software-status"),
        (r"A complete automated test suite containing (?P<count>\d+)(?= passing tests)", "research-note test-suite"),
    ):
        text = replace_count(text, pattern, label)
    return replace_count(
        text, r"The project suite currently passes (?P<count>\d+)(?= tests and 228 subtests\.)",
        "research-note current-suite prose", required=False,
    )


def add_release_count(body: str) -> str:
    bullet = f"- Increased the complete automated test suite from 215 to {TEST_COUNT} passing tests, with {SUBTEST_COUNT} passing subtests."
    if bullet in body.splitlines():
        return body
    headings = list(re.finditer(r"(?m)^### Changed[ \t]*$", body))
    if len(headings) != 1:
        raise ValueError("Expected one Changed subsection in the v1.0 stability changelog.")
    match = headings[0]
    following = re.search(r"(?m)^### ", body[match.end():])
    stop = match.end() + following.start() if following else len(body)
    return body[:stop].rstrip() + "\n" + bullet + "\n\n" + body[stop:]


def update_changelog(text: str, release_date: str) -> str:
    unreleased = list(re.finditer(r"(?m)^## \[Unreleased\][ \t]*$", text))
    if len(unreleased) != 1:
        raise ValueError("Expected one Unreleased changelog heading.")
    releases = list(re.finditer(r"(?m)^## \[1\.0\.0\] - (?P<date>\d{4}-\d{2}-\d{2})[ \t]*$", text))
    if len(releases) > 1:
        raise ValueError("Duplicate v1.0.0 changelog headings.")
    if releases:
        if releases[0].group("date") != release_date:
            raise ValueError("v1.0.0 already has a different changelog date; no files written.")
    else:
        if re.search(r"(?m)^## \[1\.0\.0\]", text):
            raise ValueError("Malformed existing v1.0.0 changelog heading.")
        match = unreleased[0]
        following = re.search(r"(?m)^## ", text[match.end():])
        if following is None:
            raise ValueError("Cannot locate previous release history.")
        stop = match.end() + following.start()
        body = text[match.end():stop].strip()
        for evidence in ("compatibility policy", "Three compatibility tests", "installed wheels"):
            if evidence not in body:
                raise ValueError(f"Missing verified stability changelog entry: {evidence}")
        body = add_release_count(body)
        text = text[:match.end()] + f"\n\n## [{VERSION}] - {release_date}\n\n" + body.rstrip() + "\n\n" + text[stop:]
    link = f"[Unreleased]: {REPOSITORY}/compare/v{VERSION}...HEAD"
    matches = list(re.finditer(r"(?m)^\[Unreleased\]:[^\n]*$", text))
    if len(matches) != 1:
        raise ValueError("Expected one Unreleased comparison link.")
    match = matches[0]
    text = text[:match.start()] + link + text[match.end():]
    release_link = f"[{VERSION}]: {REPOSITORY}/compare/v{PREVIOUS_VERSION}...v{VERSION}"
    matches = list(re.finditer(r"(?m)^\[1\.0\.0\]:[^\n]*$", text))
    if len(matches) > 1:
        raise ValueError("Duplicate v1.0.0 comparison links.")
    if matches:
        match = matches[0]
        text = text[:match.start()] + release_link + text[match.end():]
    else:
        text = text.replace(link, link + "\n" + release_link, 1)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--release-date", required=True, help="Planned release date, YYYY-MM-DD.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    date.fromisoformat(args.release_date)
    root = args.project_root.resolve()
    baseline = json.loads((root / "data" / "processed" / "public_api_contract.json").read_text(encoding="utf-8-sig"))
    if (baseline.get("contract_schema_version") != 1 or baseline.get("target_release") != VERSION
            or sum(len(exports) for exports in baseline.get("namespaces", {}).values()) != 46
            or len(baseline.get("dataframes", {})) != 23):
        raise ValueError("The verified 46-export, 23-schema stability baseline is required.")
    for relative in ("docs/API_COMPATIBILITY.md", "tests/test_api_compatibility.py", "scripts/check_wheel_installation.py"):
        if not (root / relative).is_file():
            raise ValueError(f"Missing stability preparation file: {relative}")
    workflow = (root / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8-sig")
    if "python scripts/check_wheel_installation.py" not in workflow or "windows-latest" not in workflow:
        raise ValueError("The reviewed installed-wheel CI configuration is required.")
    filenames = (
        "pyproject.toml", "src/blastdesign_ai/__init__.py", "tests/test_public_api.py",
        "CITATION.cff", "CHANGELOG.md", "README.md", "docs/burden_model_research_note.md",
        "docs/PUBLIC_API_REFERENCE.md",
    )
    originals = {}
    updated = {}
    for relative in filenames:
        raw = (root / relative).read_bytes()
        text = raw.decode("utf-8-sig")
        originals[relative] = (raw, "\r\n" if "\r\n" in text else "\n")
        updated[relative] = text.replace("\r\n", "\n")
    quoted = r'(?P<quote>[\"\x27])(?P<version>[^\"\x27\n]+)(?P=quote)'
    for relative, prefix in (
        ("pyproject.toml", r"^version[ \t]*=[ \t]*"),
        ("src/blastdesign_ai/__init__.py", r"^__version__[ \t]*=[ \t]*"),
        ("tests/test_public_api.py", r"^[ \t]*assert[ \t]+blastdesign_ai\.__version__[ \t]*==[ \t]*"),
    ):
        updated[relative] = replace_version(updated[relative], prefix + quoted + r"[ \t]*$", relative)
    updated["CITATION.cff"] = replace_version(
        updated["CITATION.cff"], r"^version:[ \t]*(?P<version>[^ \t\n]+)[ \t]*$", "CITATION.cff",
    )
    pattern = r"(?m)^date-released:[ \t]*(?P<date>\d{4}-\d{2}-\d{2})[ \t]*$"
    matches = list(re.finditer(pattern, updated["CITATION.cff"]))
    if len(matches) != 1:
        raise ValueError("Expected one ISO release-date field in CITATION.cff.")
    match = matches[0]
    date.fromisoformat(match.group("date"))
    text = updated["CITATION.cff"]
    updated["CITATION.cff"] = text[:match.start("date")] + args.release_date + text[match.end("date"):]
    updated["CHANGELOG.md"] = update_changelog(updated["CHANGELOG.md"], args.release_date)
    updated["README.md"] = update_readme(updated["README.md"])
    updated["docs/burden_model_research_note.md"] = update_research_note(updated["docs/burden_model_research_note.md"])
    reference = updated["docs/PUBLIC_API_REFERENCE.md"]
    old_sentence = "This reference records the candidate v1.0 public interface."
    new_sentence = "This reference records the v1.0 public interface."
    if reference.count(old_sentence) + reference.count(new_sentence) != 1:
        raise ValueError("Expected one reviewed API-reference status sentence.")
    updated["docs/PUBLIC_API_REFERENCE.md"] = reference.replace(old_sentence, new_sentence, 1)
    for relative in ("src/blastdesign_ai/__init__.py", "tests/test_public_api.py"):
        compile(updated[relative], str(root / relative), "exec")
    changes = {}
    for relative in filenames:
        raw, newline = originals[relative]
        prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
        content = prefix + updated[relative].replace("\n", newline).encode("utf-8")
        if content != raw:
            changes[relative] = content
    if args.dry_run:
        for relative in changes:
            print("".join(difflib.unified_diff(
                originals[relative][0].decode("utf-8-sig").splitlines(keepends=True),
                changes[relative].decode("utf-8-sig").splitlines(keepends=True),
                fromfile=relative + " (current)", tofile=relative + " (proposed)",
            )), end="")
        print("Dry run: no files written.")
        return
    if changes:
        backup = Path(tempfile.mkdtemp(prefix="blastdesign_v1_release_backup_"))
        for relative in changes:
            target = backup / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(originals[relative][0])
        for relative, content in changes.items():
            (root / relative).write_bytes(content)
            print("Updated:", relative)
        print("Original-file backups:", backup)
    else:
        print("v1.0.0 metadata and documentation are already aligned; no files changed.")
    print(f"Prepared {VERSION}; planned release date {args.release_date}.")
    print(f"Documented validation: {TEST_COUNT} tests and {SUBTEST_COUNT} subtests.")
    print("The API baseline, equations, exports, research data, and previous release history were preserved.")


if __name__ == "__main__":
    main()
