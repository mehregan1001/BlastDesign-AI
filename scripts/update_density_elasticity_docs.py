"""Update documentation for the verified Konya density-elasticity additions.

Run from the project root:
    python scripts/update_density_elasticity_docs.py

All three edits are prepared before any file is written. Original bytes
are backed up outside the repository, and UTF-8 BOM/newline style is kept.
Repeat runs do not add duplicate sections or changelog bullets.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import tempfile


README_SECTION = r"""## Analytical Konya density elasticities

The reconstructed Konya equations are also compared through dimensionless
local density elasticities, holding other inputs fixed. For the density
ratio `q = explosive_density / rock_density`, Konya 1972 has explosive-density
elasticity `0.33`, while Konya 1983 has elasticity `q / (q + 0.75)`.
Rock-density elasticity is the negative of explosive-density elasticity
for both equations.

| Model | Reference explosive-density elasticity | Reference rock-density elasticity |
|---|---:|---:|
| Konya 1972 | +0.330000 | -0.330000 |
| Konya 1983 | +0.205936 | -0.205936 |

The reference pair is 0.85 g/cm3 explosive density and 4.37 g/cm3 rock
density, at a hole diameter of 251 mm. The existing 7-by-12 density grid
contains 84 pairs and produces 168 rows for these two equations. Sampled
Konya 1983 explosive-density elasticities range from approximately
0.149733 to 0.425532.

Elasticity describes a differential fractional equation response. Its
percentage interpretation is local. A finite input change generally
requires reevaluating the burden equation. These results do not establish
field sensitivity, predictive accuracy, calibrated uncertainty, or an
operational recommendation.

The [comparison notebook](notebooks/konya_density_elasticity_comparison.ipynb)
shows the analytical ratio response and the sampled density-pair values.
Regenerate the two CSV tables, metadata JSON file, and figure with:

```text
python scripts/generate_konya_density_elasticity_artifacts.py
```

The JSON sidecar preserves units, scenario inputs, sampled intervals,
and interpretation warnings that CSV does not retain. All outputs keep
the `RESEARCH_COMPARATOR_ONLY` decision gate.
"""


RESEARCH_SECTION = r"""## Analytical local density elasticities of the Konya equations

The density-grid comparison is extended with analytical local
elasticities of the two reconstructed Konya burden equations. This
analysis describes their implemented mathematical structure.

Let $q = \rho_e / \rho_r$, with both densities expressed in g/cm3 using
the density definitions intended by the source equations. For diameter
$d$ in metres and burden $B$ in metres, the implementations are:

$$
B_{1972} = 37.8\,d\,q^{0.33},
\qquad
B_{1983} = 12\,d\,(2q + 1.5).
$$

The exponent remains 0.33, matching the reconstructed implementation.
It is not replaced with one third.

For an input $x$, local elasticity is defined by

$$
E_x = \frac{x}{B}\frac{\partial B}{\partial x},
$$

with the other inputs held fixed. Differentiation gives

$$
E_{\rho_e}^{1972} = 0.33,
\qquad E_{\rho_r}^{1972} = -0.33,
$$

$$
E_{\rho_e}^{1983} = \frac{2q}{2q + 1.5}
= \frac{q}{q + 0.75},
\qquad E_{\rho_r}^{1983} = -E_{\rho_e}^{1983}.
$$

At the reference density pair, 0.85 and 4.37 g/cm3, the ratio is
approximately 0.194508. The reference results are:

| Model | Explosive-density elasticity | Rock-density elasticity |
|---|---:|---:|
| Konya 1972 | +0.330000 | -0.330000 |
| Konya 1983 | +0.205936 | -0.205936 |

The Cartesian grid uses the existing 7 explosive-density values from
0.70 to 1.00 g/cm3 and 12 rock-density values from 1.80 to 5.30 g/cm3.
At fixed reference diameter, 251 mm, it evaluates 84 pairs and returns
168 rows for the two equations. The sampled Konya 1983
explosive-density elasticity has minimum approximately 0.149733 at
0.70/5.30 g/cm3 and maximum approximately 0.425532 at 1.00/1.80 g/cm3.
Konya 1972 retains constant elasticities throughout this grid.

For Konya 1983, explosive-density elasticity increases with the density
ratio. At fixed rock density it therefore increases with explosive
density, and at fixed explosive density it decreases with rock density.
The diameter factor cancels from both equations' density elasticities.

The differential relation $\mathrm{d}B/B = E_x\,\mathrm{d}x/x$ describes
small fractional changes when only $x$ varies. At the reference pair,
for example, a small 1% increase in explosive density corresponds to
approximately a 0.33% burden increase for Konya 1972 and a 0.206%
increase for Konya 1983. This is a local approximation, not a general
exact rule for finite changes. The changed-input equation should be
evaluated when a finite response is required.

Opposite density-elasticity signs arise because both implementations
depend on the same density ratio. They do not establish two separately
validated physical mechanisms. Larger elasticity means a stronger local
fractional response of the reconstructed equation. It does not establish
greater predictive importance, field sensitivity, causal influence,
model accuracy, or calibrated uncertainty.

The sampled density pairs remain exploratory computational scenarios.
Their numerical acceptance does not establish geological or explosive-
product feasibility. Mineral, grain, dry-bulk, saturated-bulk, and
in-situ densities must not be treated as interchangeable.

Reproducible outputs are:

- `data/processed/konya_density_elasticity_reference.csv`
- `data/processed/konya_density_elasticity_grid.csv`
- `data/processed/konya_density_elasticity_metadata.json`
- `outputs/figures/konya_density_elasticity_comparison.png`

The [comparison notebook](../notebooks/konya_density_elasticity_comparison.ipynb)
and `scripts/generate_konya_density_elasticity_artifacts.py` use the same
export routine. CSV numbers retain computational precision, while the
JSON sidecar preserves column units and analysis attributes.

Automated checks cover analytical derivatives against numerical finite
differences, ratio invariance, reference reproduction, complete grid
structure, input validation, metadata, and saved-data consistency.
The project suite currently passes 215 tests and 228 subtests.

The analysis retains `RESEARCH_COMPARATOR_ONLY` and provides no
operational burden recommendation.
"""


def replace_or_insert_section(text: str, section: str, before: str | None = None) -> str:
    heading = section.splitlines()[0]
    matches = list(re.finditer(r"(?m)^" + re.escape(heading) + r"[ \t]*$", text))
    if len(matches) > 1:
        raise ValueError(f"Duplicate section heading: {heading}")
    if matches:
        start = matches[0].start()
        following = re.search(r"(?m)^## ", text[matches[0].end():])
        end = matches[0].end() + following.start() if following else len(text)
        separator = "\n\n" if following else "\n"
        return text[:start] + section.rstrip() + separator + text[end:]
    if before is None:
        return text.rstrip() + "\n\n" + section.rstrip() + "\n"
    anchors = list(re.finditer(r"(?m)^" + re.escape(before) + r"[ \t]*$", text))
    if len(anchors) != 1:
        raise ValueError(f"Expected one insertion heading: {before}")
    index = anchors[0].start()
    return text[:index] + section.rstrip() + "\n\n" + text[index:]


def update_count(text: str, pattern: str, label: str) -> str:
    updated, count = re.subn(pattern, r"\g<1>215\g<2>", text)
    if count != 1:
        raise ValueError(f"Expected one current {label} field; found {count}.")
    return updated


def add_changelog_bullets(section: str, heading: str, bullets: list[str]) -> str:
    matches = list(re.finditer(r"(?m)^" + re.escape(heading) + r"[ \t]*$", section))
    if len(matches) > 1:
        raise ValueError(f"Duplicate Unreleased subsection: {heading}")
    if not matches:
        return section.rstrip() + "\n\n" + heading + "\n\n" + "\n".join(bullets) + "\n\n"
    match = matches[0]
    following = re.search(r"(?m)^### ", section[match.end():])
    end = match.end() + following.start() if following else len(section)
    body = section[match.end():end]
    additions = [bullet for bullet in bullets if bullet not in body.splitlines()]
    if not additions:
        return section
    return (section[:match.end()] + body.rstrip() + "\n" + "\n".join(additions)
            + "\n\n" + section[end:])


def update_changelog(text: str) -> str:
    matches = list(re.finditer(r"(?m)^## \[Unreleased\][ \t]*$", text))
    if len(matches) != 1:
        raise ValueError("Expected exactly one Unreleased changelog heading.")
    match = matches[0]
    following = re.search(r"(?m)^## ", text[match.end():])
    end = match.end() + following.start() if following else len(text)
    section = text[match.start():end]
    # Replace any current-suite count bullet only within Unreleased.
    section = re.sub(
        r"(?m)^- (?:Increased|Expanded|Updated)\b[^\n]*"
        r"(?:test suite|test count|automated-test count)[^\n]*\n?", "", section,
    )
    section = add_changelog_bullets(section, "### Added", [
        "- Analytical Konya density-elasticity grid across 84 explosive-density and rock-density pairs.",
        "- Reproducible elasticity reference/grid CSV tables, metadata JSON sidecar, comparison notebook, and two-panel figure.",
        "- Eight grid tests and three saved-artifact regression tests for the density-elasticity additions.",
    ])
    section = add_changelog_bullets(section, "### Changed", [
        "- Expanded the README and research note with analytical density-elasticity definitions, findings, and interpretation limits.",
        "- Increased the complete automated test suite from 192 to 215 passing tests, with 228 passing subtests.",
    ])
    section = add_changelog_bullets(section, "### Research safeguards", [
        "- Distinguishes local differential equation response from finite-change predictions, field sensitivity, and calibrated uncertainty.",
        "- Preserves units and research-safety metadata alongside CSV exports and retains RESEARCH_COMPARATOR_ONLY.",
    ])
    return text[:match.start()] + section.rstrip() + "\n\n" + text[end:]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Show planned files without writing.")
    arguments = parser.parse_args()
    root = arguments.project_root.resolve()
    relative_paths = ("README.md", "docs/burden_model_research_note.md", "CHANGELOG.md")
    documents = {}
    for relative in relative_paths:
        path = root / relative
        raw = path.read_bytes()
        decoded = raw.decode("utf-8-sig")
        documents[relative] = (raw, decoded.replace("\r\n", "\n"),
                               "\r\n" if "\r\n" in decoded else "\n")

    readme = update_count(documents["README.md"][1],
                          r"(A full test suite with\s+(?:\*\*)?)\d+( passing tests(?:\*\*)?)",
                          "README test-count")
    readme = re.sub(r"(?m)^\d+ passed(?:, \d+ subtests passed)?(?: in [\d.]+s)?[ \t]*$",
                    "215 passed, 228 subtests passed", readme)
    readme = replace_or_insert_section(readme, README_SECTION, "## Decision safeguards")
    note = update_count(documents["docs/burden_model_research_note.md"][1],
                        r"(Python packages? with )\d+( passing automated tests)",
                        "research-note software-status")
    note = update_count(note, r"(A complete automated test suite containing )\d+( passing tests)",
                        "research-note test-count")
    note = replace_or_insert_section(note, RESEARCH_SECTION)
    updated_text = {
        "README.md": readme,
        "docs/burden_model_research_note.md": note,
        "CHANGELOG.md": update_changelog(documents["CHANGELOG.md"][1]),
    }
    changed = {}
    for relative, text in updated_text.items():
        original, _, newline = documents[relative]
        bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
        updated = bom + text.replace("\n", newline).encode("utf-8")
        if updated != original:
            changed[relative] = updated
    if not changed:
        print("Documentation already updated; no files changed.")
        return
    if arguments.check:
        for relative in changed:
            print(f"Would update: {root / relative}")
        return
    backup_directory = Path(tempfile.mkdtemp(prefix="blastdesign-elasticity-docs-"))
    for relative in changed:
        backup = backup_directory / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(documents[relative][0])
    for relative, updated in changed.items():
        path = root / relative
        path.write_bytes(updated)
        print(f"Updated: {path}")
    print(f"Original-file backup: {backup_directory}")
    print("Documented test result: 215 passed, 228 subtests passed")
    print("Changelog entries recorded under Unreleased.")


if __name__ == "__main__":
    main()
