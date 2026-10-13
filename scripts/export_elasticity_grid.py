"""Add the existing elasticity-grid builder to blastdesign's public exports.

Run from the project environment:
    python scripts/export_elasticity_grid.py

This changes only src/blastdesign/__init__.py. Existing exports, equations,
and version fields are preserved. Validation precedes the write; an original
copy is backed up outside the repository. Use --dry-run to inspect the diff.
"""

from __future__ import annotations

import argparse
import ast
import difflib
from pathlib import Path
import tempfile


NAME = "build_gole_gohar_konya_density_elasticity_table"


def plan_update(text: str) -> str:
    tree = ast.parse(text)
    declarations = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
    ]
    if len(declarations) != 1:
        raise ValueError("Expected exactly one top-level __all__ assignment.")
    declaration = declarations[0]
    if len(declaration.targets) != 1 or not isinstance(declaration.value, ast.List):
        raise ValueError("Expected __all__ to be a literal list assigned on its own.")
    exports = ast.literal_eval(declaration.value)
    if not all(isinstance(value, str) for value in exports) or len(exports) != len(set(exports)):
        raise ValueError("Existing export names must be unique strings.")
    if "build_konya_density_elasticity_summary" not in exports:
        raise ValueError("Expected the existing point-elasticity summary export.")

    direct_import = any(
        isinstance(node, ast.ImportFrom)
        and node.level == 1
        and node.module == "density_elasticity"
        and any(alias.name == NAME and alias.asname in (None, NAME) for alias in node.names)
        for node in tree.body
    )
    if NAME in exports and direct_import:
        return text

    lines = text.splitlines(keepends=True)
    if NAME not in exports:
        closing_line = declaration.value.end_lineno - 1
        if lines[closing_line].strip() != "]":
            raise ValueError("Expected the closing __all__ bracket on its own line.")
        if exports:
            last = declaration.value.elts[-1]
            last_line = lines[last.end_lineno - 1]
            trailing = last_line.encode("utf-8")[last.end_col_offset:].decode("utf-8").strip()
            if not trailing.startswith(","):
                raise ValueError("Expected a trailing comma after the last existing export.")
        lines.insert(closing_line, f'    "{NAME}",\n')
    if not direct_import:
        lines.insert(
            declaration.lineno - 1,
            f"from .density_elasticity import {NAME}\n\n",
        )
    updated = "".join(lines)
    compile(updated, "src/blastdesign/__init__.py", "exec")
    new_tree = ast.parse(updated)
    new_declaration = next(
        node for node in new_tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
    )
    expected_exports = exports if NAME in exports else exports + [NAME]
    if ast.literal_eval(new_declaration.value) != expected_exports:
        raise ValueError("Unexpected change to the existing export list.")
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()
    root = arguments.project_root.resolve()
    source = root / "src" / "blastdesign" / "density_elasticity.py"
    source_tree = ast.parse(source.read_text(encoding="utf-8-sig"))
    if not any(isinstance(node, ast.FunctionDef) and node.name == NAME for node in source_tree.body):
        raise ValueError(f"{NAME} is not defined in {source}.")
    filename = root / "src" / "blastdesign" / "__init__.py"
    raw = filename.read_bytes()
    original = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in original else "\n"
    normalized = original.replace("\r\n", "\n")
    updated = plan_update(normalized)
    if updated == normalized:
        print("Already exported:", NAME)
        return
    if arguments.dry_run:
        print("".join(difflib.unified_diff(
            normalized.splitlines(keepends=True), updated.splitlines(keepends=True),
            fromfile="src/blastdesign/__init__.py (current)",
            tofile="src/blastdesign/__init__.py (proposed)",
        )), end="")
        return
    backup = Path(tempfile.mkdtemp(prefix="blastdesign_api_backup_")) / "__init__.py"
    backup.write_bytes(raw)
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    filename.write_bytes(prefix + updated.replace("\n", newline).encode("utf-8"))
    print("Updated:", filename)
    print("Original backup:", backup)
    print("Existing exports, equations, and version fields were preserved.")


if __name__ == "__main__":
    main()