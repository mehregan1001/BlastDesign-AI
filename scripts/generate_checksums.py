"""Generate SHA-256 checksums for reproducibility-critical project files."""

from __future__ import annotations

import hashlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "CHECKSUMS.sha256"

ROOT_FILES = (
    ".gitignore",
    "CHANGELOG.md",
    "CITATION.cff",
    "LICENSE",
    "README.md",
    "environment.yml",
    "project_checkpoint.json",
    "pyproject.toml",
    "requirements.txt",
    "start_jupyterlab.bat",
)

FILE_PATTERNS = (
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
    "data/processed/*.csv",
    "data/processed/*.json",
    "docs/*.md",
    "docs/sources/*",
    "notebooks/*.ipynb",
    "scripts/*.py",
    "src/**/*.py",
    "tests/*.py",
)

EXCLUDED_DIRECTORY_NAMES = {
    ".ipynb_checkpoints",
    "__pycache__",
}


def calculate_sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file."""

    digest = hashlib.sha256()

    with path.open("rb") as file_handle:
        for chunk in iter(
            lambda: file_handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def collect_project_files() -> list[Path]:
    """Collect reproducibility-critical files deterministically."""

    selected_files: set[Path] = set()

    for filename in ROOT_FILES:
        path = PROJECT_ROOT / filename

        if path.is_file():
            selected_files.add(path)

    for pattern in FILE_PATTERNS:
        for path in PROJECT_ROOT.glob(pattern):
            if not path.is_file():
                continue

            relative_path = path.relative_to(PROJECT_ROOT)

            if any(
                part in EXCLUDED_DIRECTORY_NAMES
                for part in relative_path.parts
            ):
                continue

            selected_files.add(path)

    return sorted(
        selected_files,
        key=lambda path: path.relative_to(
            PROJECT_ROOT
        ).as_posix(),
    )


def main() -> int:
    """Write the deterministic checksum manifest."""

    project_files = collect_project_files()

    lines = [
        (
            f"{calculate_sha256(path)}  "
            f"{path.relative_to(PROJECT_ROOT).as_posix()}"
        )
        for path in project_files
    ]

    OUTPUT_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        f"Wrote {len(project_files)} SHA-256 checksums "
        f"to {OUTPUT_PATH}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())