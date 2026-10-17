"""Hash the staged Git contents of reproducibility-critical project files.

Stage intended inputs first. Generate, stage CHECKSUMS.sha256, then run
this script with --check. Digests describe stored Git blob contents,
not the LF/CRLF presentation of files in a working directory.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "CHECKSUMS.sha256"
ROOT_FILES = (
    ".gitattributes", ".gitignore", "CHANGELOG.md", "CITATION.cff", "LICENSE",
    "README.md", "environment.yml", "project_checkpoint.json", "pyproject.toml",
    "requirements.txt", "start_jupyterlab.bat",
)
FILE_PATTERNS = (
    ".github/workflows/*.yml", ".github/workflows/*.yaml",
    "data/processed/*.csv", "data/processed/*.json", "docs/*.md",
    "docs/sources/*", "notebooks/*.ipynb", "scripts/*.py", "src/**/*.py",
    "tests/*.py",
)
EXCLUDED_DIRECTORY_NAMES = {".ipynb_checkpoints", "__pycache__"}


def find_git() -> str:
    """Find Git on PATH or in standard Windows Git/Desktop installations."""
    located = shutil.which("git")
    if located:
        return located
    if os.name == "nt":
        candidates = []
        for key in ("ProgramFiles", "ProgramFiles(x86)"):
            if os.environ.get(key):
                candidates.append(Path(os.environ[key]) / "Git/cmd/git.exe")
        if os.environ.get("LOCALAPPDATA"):
            local = Path(os.environ["LOCALAPPDATA"])
            candidates.append(local / "Programs/Git/cmd/git.exe")
            desktop = local / "GitHubDesktop"
            candidates.extend(sorted(
                desktop.glob("app-*/resources/app/git/cmd/git.exe"),
                reverse=True,
            ))
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
    raise ValueError("Git could not be found. Run from a terminal with Git available.")


def git_bytes(git: str, *args: str, optional: bool = False) -> bytes:
    result = subprocess.run(
        [git, "-C", str(PROJECT_ROOT), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    )
    if result.returncode and not optional:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"Git failed: {message}")
    return b"" if result.returncode else result.stdout


def matches_parts(parts: tuple[str, ...], pattern: tuple[str, ...]) -> bool:
    if not pattern:
        return not parts
    if pattern[0] == "**":
        return matches_parts(parts, pattern[1:]) or (
            bool(parts) and matches_parts(parts[1:], pattern)
        )
    return bool(parts) and fnmatch.fnmatchcase(parts[0], pattern[0]) and (
        matches_parts(parts[1:], pattern[1:])
    )


def eligible(name: str) -> bool:
    parts = PurePosixPath(name).parts
    if any(part in EXCLUDED_DIRECTORY_NAMES for part in parts):
        return False
    return name in ROOT_FILES or any(
        matches_parts(parts, PurePosixPath(pattern).parts)
        for pattern in FILE_PATTERNS
    )


def decode_paths(data: bytes) -> set[str]:
    return {part.decode("utf-8") for part in data.split(b"\0") if part}


def read_index(git: str) -> dict[str, tuple[str, str]]:
    entries = {}
    for record in git_bytes(git, "ls-files", "--stage", "-z").split(b"\0"):
        if not record:
            continue
        metadata, raw_name = record.split(b"\t", 1)
        mode, oid, stage = metadata.decode("ascii").split()
        name = raw_name.decode("utf-8")
        if not eligible(name) and name != MANIFEST_NAME:
            continue
        if stage != "0":
            raise ValueError(f"Resolve the merge conflict first: {name}")
        if mode not in {"100644", "100755"}:
            raise ValueError(f"Expected a regular tracked file: {name} (mode {mode})")
        if any(c in name for c in "\r\n\\"):
            raise ValueError(f"Unsupported manifest pathname: {name!r}")
        entries[name] = (mode, oid)
    return entries


def validate_inputs(git: str, entries: dict, check: bool) -> None:
    if not entries:
        raise ValueError("No staged project inputs were found.")
    required = set(entries) - {MANIFEST_NAME}
    missing = sorted(name for name in required if not (PROJECT_ROOT / name).is_file())
    unstaged = decode_paths(git_bytes(
        git, "diff", "--no-ext-diff", "--name-only", "-z", "--",
    ))
    relevant = required | ({MANIFEST_NAME} if check else set())
    changed = sorted(unstaged & relevant)
    untracked = sorted(name for name in decode_paths(git_bytes(
        git, "ls-files", "--others", "--exclude-standard", "-z",
    )) if eligible(name))
    problems = []
    if missing:
        problems.append("Missing tracked inputs:\n  " + "\n  ".join(missing))
    if changed:
        problems.append("Stage the intended edits/deletions first:\n  " + "\n  ".join(changed))
    if untracked:
        problems.append("Review and stage these new inputs first:\n  " + "\n  ".join(untracked))
    if problems:
        raise ValueError("\n".join(problems))
    if not required:
        raise ValueError("No staged project inputs were found.")


def hash_blobs(git: str, entries: dict) -> dict[str, str]:
    """Stream raw blob bytes without applying working-tree filters."""
    hashes = {}
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(
            [git, "-C", str(PROJECT_ROOT), "cat-file", "--batch"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        )
        try:
            for name in sorted(set(entries) - {MANIFEST_NAME}):
                oid = entries[name][1]
                process.stdin.write(oid.encode("ascii") + b"\n")
                process.stdin.flush()
                header = process.stdout.readline().split()
                if len(header) != 3 or header[0].decode("ascii") != oid or header[1] != b"blob":
                    raise ValueError(f"Cannot read the staged blob: {name}")
                remaining = int(header[2])
                digest = hashlib.sha256()
                prefix = b""
                while remaining:
                    chunk = process.stdout.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise ValueError(f"Truncated Git blob: {name}")
                    if len(prefix) < 128:
                        prefix += chunk[:128 - len(prefix)]
                    digest.update(chunk)
                    remaining -= len(chunk)
                if process.stdout.read(1) != b"\n":
                    raise ValueError(f"Invalid Git batch response: {name}")
                if prefix.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
                    raise ValueError(f"LFS pointers need a separate artifact checksum policy: {name}")
                hashes[name] = digest.hexdigest()
            process.stdin.close()
            if process.wait(timeout=30):
                errors.seek(0)
                raise ValueError(errors.read().decode("utf-8", errors="replace"))
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            if not process.stdin.closed:
                process.stdin.close()
            process.stdout.close()
    return hashes


def manifest_paths(data: bytes) -> set[str]:
    result = set()
    for line in data.decode("utf-8-sig").splitlines():
        if not line:
            continue
        match = re.fullmatch(r"[0-9a-f]{64}  (.+)", line)
        if not match or match[1] in result:
            raise ValueError("The previous manifest contains an invalid or duplicate entry.")
        result.add(match[1])
    return result


def report_inventory(git: str, selected: set[str]) -> None:
    previous = manifest_paths(git_bytes(git, "show", "HEAD:" + MANIFEST_NAME, optional=True))
    ignored = {name for name in decode_paths(git_bytes(
        git, "ls-files", "--others", "--ignored", "--exclude-standard", "-z",
    )) if eligible(name)}
    excluded = sorted((previous | ignored) - selected)
    print("Hash basis: raw staged Git blob contents (not working-directory bytes).")
    if excluded:
        print("Outside this version-controlled inventory:")
        for name in excluded:
            state = "present locally" if (PROJECT_ROOT / name).is_file() else "absent locally"
            print(f"  {name} [{state}]")
        print("Retain/recover and explicitly version any research outputs that need archival coverage.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Verify the staged manifest against staged inputs.")
    mode.add_argument("--dry-run", action="store_true", help="Report and hash inputs without writing a manifest.")
    args = parser.parse_args()
    try:
        for variable in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            if os.environ.get(variable):
                raise ValueError(f"Unset {variable} before running this project command.")
        git = find_git()
        root = Path(os.fsdecode(git_bytes(git, "rev-parse", "--show-toplevel").rstrip(b"\r\n")))
        if root.resolve() != PROJECT_ROOT.resolve():
            raise ValueError("Run the script from its own project checkout.")
        entries = read_index(git)
        validate_inputs(git, entries, args.check)
        hashes = hash_blobs(git, entries)
        if read_index(git) != entries:
            raise ValueError("The Git index changed during hashing; rerun after staging is complete.")
        validate_inputs(git, entries, args.check)
        data = "".join(f"{digest}  {name}\n" for name, digest in hashes.items()).encode("utf-8")
        report_inventory(git, set(hashes))
        if args.check:
            if MANIFEST_NAME not in entries:
                raise ValueError("Stage CHECKSUMS.sha256 before using --check.")
            recorded = git_bytes(git, "cat-file", "blob", entries[MANIFEST_NAME][1])
            if recorded != data:
                raise ValueError("The staged manifest is stale. Regenerate it, stage it, then rerun --check.")
            print(f"Staged checksum manifest PASSED: {len(hashes)} files.")
        elif args.dry_run:
            print(f"Dry run: {len(hashes)} staged inputs; no manifest written.")
        else:
            output = PROJECT_ROOT / MANIFEST_NAME
            # All validation and hashing finish before the existing manifest is replaced.
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=PROJECT_ROOT, prefix=".checksums-", delete=False) as stream:
                    temporary = Path(stream.name)
                    stream.write(data)
                temporary.replace(output)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
            print(f"Wrote {len(hashes)} SHA-256 checksums to {output}")
            print("Next: git add CHECKSUMS.sha256, then rerun this command with --check.")
        return 0
    except (OSError, ValueError, UnicodeError, subprocess.SubprocessError) as error:
        print(f"Checksum generation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
