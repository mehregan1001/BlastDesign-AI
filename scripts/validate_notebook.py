"""Execute code cells from a notebook JSON file in one clean Python process.

This lightweight validator is useful when Jupyter/nbconvert is unavailable.
It does not save outputs back to the notebook.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def display(value):
    """Minimal replacement for IPython.display.display during validation."""
    print(value)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/validate_notebook.py NOTEBOOK.ipynb")
    path = Path(sys.argv[1]).resolve()
    notebook = json.loads(path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__notebook_validation__", "display": display}
    for index, cell in enumerate(notebook.get("cells", []), start=1):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        try:
            exec(compile(source, f"{path.name}:cell-{index}", "exec"), namespace)
        except Exception as exc:
            raise RuntimeError(f"Failure in {path.name}, cell {index}") from exc
    print(f"VALIDATION PASSED: {path.name}")


if __name__ == "__main__":
    main()
