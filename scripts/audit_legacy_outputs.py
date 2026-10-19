"""Read-only inventory of ten legacy BlastDesign research CSV outputs.

Save in scripts/ and run with python -B scripts/audit_legacy_outputs.py.
Only the Python standard library and a local Git executable are required.
No project modules or notebooks are imported or executed. Nothing is restored,
staged, generated, fetched, or written to the project by this script.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


LEGACY_NAMES = (
    "burden_aggregation_comparison_step_24_15.csv",
    "burden_applicability_ledger_step_24_16.csv",
    "burden_decision_readiness_step_24_20.csv",
    "burden_evidence_tiers_step_24_17.csv",
    "burden_leave_one_out_step_24_14.csv",
    "burden_results_step_24_11.csv",
    "burden_robust_spread_step_24_15.csv",
    "burden_screening_scenarios_step_24_17.csv",
    "burden_structural_uncertainty_step_24_18.csv",
    "model_registry_step_24_11.csv",
)


def find_git() -> str:
    located = shutil.which("git")
    if located:
        return located
    candidates = []
    if os.name == "nt":
        for key in ("ProgramFiles", "ProgramFiles(x86)"):
            if os.environ.get(key):
                candidates.append(Path(os.environ[key]) / "Git/cmd/git.exe")
        if os.environ.get("LOCALAPPDATA"):
            local = Path(os.environ["LOCALAPPDATA"])
            candidates.append(local / "Programs/Git/cmd/git.exe")
            candidates.extend(sorted(
                (local / "GitHubDesktop").glob("app-*/resources/app/git/cmd/git.exe"),
                reverse=True,
            ))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise ValueError("Git was not found. Run in a terminal with Git available.")


def git_result(git: str, root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [git, "--no-pager", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"},
        timeout=60,
    )


def git_bytes(git: str, root: Path, *args: str) -> bytes:
    result = git_result(git, root, *args)
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def path_set(data: bytes) -> set[str]:
    return {item.decode("utf-8") for item in data.split(b"\0") if item}


def read_release_manifest(git: str, root: Path) -> dict[str, str]:
    result = git_result(git, root, "show", "v1.0.0:CHECKSUMS.sha256")
    if result.returncode:
        print("Release manifest unavailable in fetched refs; hash comparison skipped.")
        return {}
    manifest = {}
    for line in result.stdout.decode("utf-8-sig").splitlines():
        if not line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match or match[2] in manifest:
            raise ValueError("The v1.0.0 manifest has an invalid or duplicate entry.")
        manifest[match[2]] = match[1]
    return manifest


def compare_recorded_hash(data: bytes, expected: str | None) -> str:
    if not expected:
        return "not recorded in available v1.0.0 manifest"
    if hashlib.sha256(data).hexdigest() == expected:
        return "exact byte match"
    # Diagnostic variants only. The local file and historical manifest stay intact.
    lf = data.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    if any(hashlib.sha256(candidate).hexdigest() == expected for candidate in (lf, crlf)):
        return "matches after LF/CRLF conversion only"
    return "DIFFERS; content/encoding needs review"


def csv_shape(data: bytes) -> str:
    try:
        text = data.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = next(reader, None)
        if header is None:
            return "empty CSV"
        rows = 0
        irregular = False
        for row in reader:
            if not row:
                continue
            rows += 1
            irregular |= len(row) != len(header)
        suffix = "; irregular row widths" if irregular else ""
        return f"{rows} data rows, {len(header)} columns{suffix}"
    except (UnicodeError, csv.Error) as error:
        return f"CSV inspection failed: {error}"


def inspect_recipe_references(root: Path, missing: set[str]) -> None:
    print("\nTEXT REFERENCES TO MISSING OUTPUTS IN CODE")
    print("Notebook indices below are zero-based. References are leads, not verified recipes.")
    found = set()
    paths = set()
    for directory, pattern in (("notebooks", "*.ipynb"), ("scripts", "*.py"), ("src", "*.py")):
        paths.update((root / directory).rglob(pattern))
    own_path = Path(__file__).resolve()
    for path in sorted(paths):
        if path.resolve() == own_path or any(
            part in {".ipynb_checkpoints", "__pycache__"} for part in path.parts
        ):
            continue
        relative = path.relative_to(root).as_posix()
        try:
            source = path.read_text(encoding="utf-8-sig")
            if path.suffix == ".ipynb":
                cells = json.loads(source)["cells"]
                chunks = [
                    (f"code cell {index}", "".join(cell.get("source", [])))
                    for index, cell in enumerate(cells)
                    if cell.get("cell_type") == "code"
                ]
            else:
                chunks = [("Python source", source)]
            for location, chunk in chunks:
                matches = {name for name in missing if Path(name).stem in chunk}
                if matches:
                    found.update(matches)
                    print(f"  {relative} | {location}")
                    for name in sorted(matches):
                        print(f"    {name}")
        except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
            print(f"  Could not inspect {relative}: {error}")
    for name in sorted(missing - found):
        print(f"  No literal code reference found: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        root = args.project_root.resolve()
        if not (root / "pyproject.toml").is_file():
            raise ValueError("Expected the BlastDesign-AI project root containing pyproject.toml.")
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            if os.environ.get(key):
                raise ValueError(f"Unset {key} before auditing this checkout.")
        git = find_git()
        actual_root = Path(git_bytes(git, root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
        if actual_root != root:
            raise ValueError("The requested directory is not the Git checkout root.")
        print("READ-ONLY LEGACY OUTPUT INVENTORY")
        print(f"Project: {root}")
        print("No files or Git state are changed; no notebooks are executed.")
        paths = [f"data/processed/{name}" for name in LEGACY_NAMES]
        tracked = path_set(git_bytes(git, root, "ls-files", "-z", "--", *paths))
        ignored = path_set(git_bytes(
            git, root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--", *paths,
        ))
        manifest = read_release_manifest(git, root)
        missing = set()
        present_count = 0
        for name, relative in zip(LEGACY_NAMES, paths):
            path = root / relative
            print(f"\n{name}")
            state = "tracked" if relative in tracked else "untracked"
            state += ", ignored" if relative in ignored else ""
            print(f"  Git index: {state}")
            if path.is_symlink():
                raise ValueError(f"Inspect symlink manually: {relative}")
            if path.is_file():
                present_count += 1
                data = path.read_bytes()
                print(f"  Local: present; {csv_shape(data)}")
                print(f"  v1.0.0 hash: {compare_recorded_hash(data, manifest.get(relative))}")
            else:
                missing.add(name)
                print("  Local: ABSENT")
                print(f"  Recorded v1.0.0 SHA-256: {manifest.get(relative, 'unavailable')}")
            history = git_bytes(
                git, root, "log", "--all", "--full-history", "-1", "--format=%h %s", "--", relative,
            ).decode("utf-8", errors="replace").strip()
            print(f"  Latest path history in fetched refs: {history or 'none found'}")
        print(f"\nTotals: {present_count} present; {len(missing)} absent; {len(tracked)} tracked paths.")
        if missing:
            inspect_recipe_references(root, missing)
        print("\nInventory complete. Presence, hash matching, and code references do not establish scientific validity.")
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"Inventory stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
