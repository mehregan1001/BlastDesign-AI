"""Align v0.9.0 metadata and move the elasticity changelog into its release.

Save in scripts/ and run from the project environment:
    python scripts/prepare_v0_9_0_release.py --release-date 2026-10-12

Use --dry-run to see the complete planned diff. All required edits are
validated before any file is written. Originals are backed up outside
the repository. Repeated runs with the same date do not duplicate entries.
"""

from __future__ import annotations

import argparse
from datetime import date
import difflib
from pathlib import Path
import re
import tempfile


VERSION = "0.9.0"
PREVIOUS_VERSION = "0.8.0"
REPOSITORY = "https://github.com/mehregan1001/BlastDesign-AI"


def replace_version(text: str, pattern: str, label: str) -> str:
    matches = list(re.finditer(pattern, text, flags=re.MULTILINE))
    if len(matches) != 1:
        raise ValueError(f"Expected one version field in {label}; found {len(matches)}.")
    match = matches[0]
    observed = match.group("version")
    if observed not in {PREVIOUS_VERSION, VERSION}:
        raise ValueError(f"Unexpected version {observed!r} in {label}.")
    return text[:match.start("version")] + VERSION + text[match.end("version"):]


def replace_citation_date(text: str, release_date: str) -> str:
    pattern = r"(?m)^date-released:[ \t]*(?P<date>\d{4}-\d{2}-\d{2})[ \t]*$"
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1:
        raise ValueError("Expected one ISO date-released field in CITATION.cff.")
    match = matches[0]
    date.fromisoformat(match.group("date"))
    return text[:match.start("date")] + release_date + text[match.end("date"):]


def update_changelog(text: str, release_date: str) -> str:
    unreleased_matches = list(re.finditer(r"(?m)^## \[Unreleased\][ \t]*$", text))
    if len(unreleased_matches) != 1:
        raise ValueError("Expected one Unreleased changelog heading.")
    release_matches = list(re.finditer(
        r"(?m)^## \[0\.9\.0\] - (?P<date>\d{4}-\d{2}-\d{2})[ \t]*$", text,
    ))
    if len(release_matches) > 1:
        raise ValueError("Duplicate v0.9.0 changelog headings.")
    if release_matches:
        if release_matches[0].group("date") != release_date:
            raise ValueError("v0.9.0 already has a different changelog date; no files written.")
    else:
        if re.search(r"(?m)^## \[0\.9\.0\]", text):
            raise ValueError("Malformed existing v0.9.0 changelog heading.")
        unreleased = unreleased_matches[0]
        following = re.search(r"(?m)^## ", text[unreleased.end():])
        if following is None:
            raise ValueError("Cannot locate previous changelog release history.")
        end = unreleased.end() + following.start()
        body = text[unreleased.end():end].strip()
        if "elasticity" not in body.lower() or "215 passing tests" not in body:
            raise ValueError("Unreleased must contain the verified elasticity work and 215-test count.")
        release = f"## [{VERSION}] - {release_date}\n\n{body}\n\n"
        text = text[:unreleased.end()] + "\n\n" + release + text[end:]

    unreleased_link = f"[Unreleased]: {REPOSITORY}/compare/v{VERSION}...HEAD"
    matches = list(re.finditer(r"(?m)^\[Unreleased\]:[^\n]*$", text))
    if len(matches) != 1:
        raise ValueError("Expected one Unreleased comparison-link definition.")
    match = matches[0]
    text = text[:match.start()] + unreleased_link + text[match.end():]
    release_link = f"[{VERSION}]: {REPOSITORY}/compare/v{PREVIOUS_VERSION}...v{VERSION}"
    matches = list(re.finditer(r"(?m)^\[0\.9\.0\]:[^\n]*$", text))
    if len(matches) > 1:
        raise ValueError("Duplicate v0.9.0 comparison-link definitions.")
    if matches:
        match = matches[0]
        text = text[:match.start()] + release_link + text[match.end():]
    else:
        text = text.replace(unreleased_link, unreleased_link + "\n" + release_link, 1)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument("--release-date", required=True, help="Planned release date, YYYY-MM-DD.")
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()
    date.fromisoformat(arguments.release_date)
    root = arguments.project_root.resolve()
    filenames = (
        "pyproject.toml", "src/blastdesign_ai/__init__.py",
        "tests/test_public_api.py", "CITATION.cff", "CHANGELOG.md",
    )
    documents = {}
    for filename in filenames:
        raw = (root / filename).read_bytes()
        decoded = raw.decode("utf-8-sig")
        documents[filename] = (raw, decoded.replace("\r\n", "\n"),
                               "\r\n" if "\r\n" in decoded else "\n")
    updated = {filename: document[1] for filename, document in documents.items()}
    quoted_version = r'(?P<quote>[\"\x27])(?P<version>[^\"\x27\n]+)(?P=quote)'
    for filename, prefix in (
        ("pyproject.toml", r"^version[ \t]*=[ \t]*"),
        ("src/blastdesign_ai/__init__.py", r"^__version__[ \t]*=[ \t]*"),
        ("tests/test_public_api.py", r"^[ \t]*assert[ \t]+blastdesign_ai\.__version__[ \t]*==[ \t]*"),
    ):
        updated[filename] = replace_version(
            updated[filename], prefix + quoted_version + r"[ \t]*$", filename,
        )
    updated["CITATION.cff"] = replace_version(
        updated["CITATION.cff"], r"^version:[ \t]*(?P<version>[^ \t\n]+)[ \t]*$",
        "CITATION.cff",
    )
    updated["CITATION.cff"] = replace_citation_date(
        updated["CITATION.cff"], arguments.release_date,
    )
    updated["CHANGELOG.md"] = update_changelog(updated["CHANGELOG.md"], arguments.release_date)
    for filename in ("src/blastdesign_ai/__init__.py", "tests/test_public_api.py"):
        compile(updated[filename], str(root / filename), "exec")

    planned_bytes = {}
    for filename in filenames:
        original, _, newline = documents[filename]
        bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
        content = bom + updated[filename].replace("\n", newline).encode("utf-8")
        if content != original:
            planned_bytes[filename] = content
    if not planned_bytes:
        print("v0.9.0 metadata already aligned; no files changed.")
        return
    if arguments.dry_run:
        for filename in planned_bytes:
            print("".join(difflib.unified_diff(
                documents[filename][1].splitlines(keepends=True),
                updated[filename].splitlines(keepends=True),
                fromfile=filename, tofile=filename,
            )), end="")
        print("Dry run: no files written.")
        return
    backup_directory = Path(tempfile.mkdtemp(prefix="blastdesign-v0-9-0-backup-"))
    for filename in planned_bytes:
        backup = backup_directory / filename
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(documents[filename][0])
    for filename, content in planned_bytes.items():
        (root / filename).write_bytes(content)
        print(f"Updated: {root / filename}")
    print(f"Original-file backup: {backup_directory}")
    print(f"Prepared version {VERSION} with release date {arguments.release_date}.")


if __name__ == "__main__":
    main()
