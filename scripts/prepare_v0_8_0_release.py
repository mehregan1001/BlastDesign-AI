"""Prepare v0.8.0 metadata and documentation without changing equations.

Save in scripts/ and run from the project environment:
    python scripts/prepare_v0_8_0_release.py --release-date 2026-10-06

All required files and edits are checked before any file is written.
Use --dry-run to inspect the planned diff without writing files.
"""

from __future__ import annotations

import argparse
from datetime import date
import difflib
from pathlib import Path
import re


VERSION = "0.8.0"
REPOSITORY = "https://github.com/mehregan1001/BlastDesign-AI"

README_SECTION = """## Controlled joint-density sensitivity analysis

A Cartesian analysis varies explosive density and rock density together while
hole diameter, UCS, explosive-type label, and Ash burden ratio remain fixed.
The default grids combine seven explosive densities (0.70-1.00 g/cm³) with
twelve rock densities (1.80-5.30 g/cm³), producing 84 density pairs and 588
outputs from the seven reconstructed models.

Only Konya 1972 and Konya 1983 respond to these density inputs. Both equations
depend on the explosive-to-rock density ratio: proportional changes in the
two densities preserve their calculated burdens at fixed hole diameter.

| Sampled result | Seven-model range, m |
|---|---:|
| Reference pair: explosive 0.85, rock 4.37 g/cm³ | 1.455865 |
| Minimum, attained by 44 sampled pairs | 1.210189 |
| Maximum: explosive 0.70, rock 5.30 g/cm³ | 2.118704 |

These are grid-dependent structural comparisons. The minimum-range plateau
does not identify an optimal explosive, rock condition, or blast design.
The broad rock-density grid includes uncommon geological endmembers; density
measurement bases must remain consistent with the intended source equation.
The fixed ANFO label does not establish that every sampled explosive density
corresponds to a realizable product with unchanged energy or performance.

The reproducible notebook is
`notebooks/joint_density_sensitivity_comparison.ipynb`. Its three-panel figure
shows both Konya burden surfaces and the seven-model range on the actual
density coordinates. Three saved CSV tables under `data/processed/` contain
model outputs, ensemble summaries, and model response summaries.
Regenerate the CSV files with:

```bash
python scripts/generate_joint_density_artifacts.py
```

The analysis retains the `RESEARCH_COMPARATOR_ONLY` decision gate.
"""

RESEARCH_SECTION = """## Controlled joint explosive-density and rock-density analysis

### Computational design

Both density inputs were varied over a Cartesian grid while hole diameter
(251 mm), UCS (85 MPa), explosive-type label (ANFO), and Ash burden ratio (25)
were held fixed. Seven explosive densities from 0.70 to 1.00 g/cm³ were
combined with twelve rock densities from 1.80 to 5.30 g/cm³. The resulting
84 density pairs were each evaluated with all seven reconstructed equations,
giving 588 model-output rows.

The rock-density grid includes 2.75 g/cm³ and the reference value of
4.37 g/cm³. It is an exploratory computational grid rather than a frequency
distribution of mine lithologies, a universal geological range, or an
operational recommendation. Mineral, grain, dry-bulk, saturated-bulk, and
in-situ density definitions must not be treated as interchangeable.
Holding the ANFO label fixed does not establish the physical realizability
or unchanged explosive performance of every sampled density setting.

### Density-ratio dependence

For the current implemented equations, let q = rho_e / rho_r and let d
denote hole diameter in metres:

```text
Konya 1972: B = 37.8 d q^0.33
Konya 1983: B = 12 d (2q + 1.5)
```

The exponent 0.33 preserves the reconstruction and is not replaced by 1/3.
The minimum sampled ratio is 0.70 / 5.30 = 0.132075, the maximum is
1.00 / 1.80 = 0.555556, and the reference ratio is
0.85 / 4.37 = 0.194508 (values rounded to six decimal places).

Only the two Konya equations respond to the joint density grid. Increasing
explosive density at fixed rock density increases their calculated burdens;
increasing rock density at fixed explosive density decreases them.
Proportional density changes preserve q and therefore preserve both burdens
at fixed diameter. A reproducible check using pairs (0.75, 3.00) and
(0.90, 3.60) g/cm³ confirms equal outputs at q = 0.25.
This ratio dependence describes the implemented equations and does not
establish two independent physical mechanisms in blasting.

### Per-model responses

| Model | Burden at minimum ratio, m | Reference burden, m | Burden at maximum ratio, m | Ratio-endpoint change, m | Ratio-endpoint change, % |
|---|---:|---:|---:|---:|---:|
| Konya 1972 | 4.864485 | 5.527324 | 7.814939 | 2.950454 | 60.652969 |
| Konya 1983 | 5.313623 | 5.689716 | 7.864667 | 2.551044 | 48.009507 |

Ratio-endpoint change means the burden at the maximum sampled ratio minus
the burden at the minimum sampled ratio. Percentage change uses the burden
at the minimum ratio as its baseline. It is a joint-grid comparison and
differs from the negative endpoint change in the rock-density-only sweep.
The other five reconstructed models remain constant across this grid.

### Seven-model disagreement

At the reference pair, the mean burden is 6.137371 m and the range is
1.455865 m. The smallest sampled range is 1.210189 m and is attained by
44 sampled density pairs. The largest sampled range is 2.118704 m,
at explosive density 0.70 g/cm³ and rock density 5.30 g/cm³.

The minimum-range plateau occurs where both Konya estimates fall between
the fixed López Jimeno and Rustan estimates, which then define the ensemble
extremes. It does not identify an optimal explosive or rock condition.
These extrema depend on the selected grid; they do not establish physical
parameter importance or a universal ranking of model accuracy.

The range remains structural disagreement among reconstructed equations.
It is not a confidence interval or a calibrated prediction interval.
The `RESEARCH_COMPARATOR_ONLY` decision gate remains in force, and the
analysis does not produce a field-ready burden recommendation.

### Reproducibility

The analysis is implemented in `src/blastdesign/joint_density.py` and exported
through the public `blastdesign` interface. Reproducible outputs include:

- `notebooks/joint_density_sensitivity_comparison.ipynb`
- `outputs/figures/joint_density_sensitivity_comparison.png`
- `data/processed/joint_density_sensitivity_model_outputs.csv`
- `data/processed/joint_density_sensitivity_ensemble_summary.csv`
- `data/processed/joint_density_sensitivity_model_response_summary.csv`

The figure retains the uneven rock-density spacing. Nearest-sample colour
cells show the two Konya burden surfaces on a shared scale and the ensemble
range on a separate scale. The reference pair and a constant reference-ratio
line are marked explicitly. The colour cells are a display of sampled
calculations rather than continuous field measurements.

The CSV export script is `scripts/generate_joint_density_artifacts.py`.
DataFrame metadata are not serialized into CSV; interpretation and density
measurement warnings are recorded in the source and notebook.
Automated tests verify Cartesian coverage, density ratios, agreement with
both existing one-factor sweeps, reference reproduction, proportional-pair
invariance, response direction, summary statistics, invalid-input rejection,
metadata handling, and consistency of saved CSV artifacts.
"""

CHANGELOG_SECTION = """## [0.8.0] - {release_date}

### Added

- Controlled Cartesian explosive-density and rock-density analysis with 84 density pairs and seven models per pair.
- Joint-density input validation, ensemble-disagreement summaries, and per-model ratio-response summaries.
- Reproducible joint-density notebook and three-panel figure with actual density coordinates and reference-ratio annotations.
- CSV regeneration script and version-controlled joint-density model-output, ensemble-summary, and model-response tables.
- Automated tests for grid coverage, one-factor slice agreement, equal-ratio invariance, response direction, reference reproduction, summary contracts, and saved-artifact consistency.

### Changed

- Expanded the README and research note with joint-density findings and interpretation limits.
- Increased the automated test suite from 135 to 192 passing tests; the new summary tests also execute 228 subtests.

### Research safeguards

- Distinguishes joint-grid ratio-endpoint changes from changes along either density axis alone.
- Treats the minimum-range plateau as structural equation disagreement rather than a blast-design optimization result.
- Documents exploratory grid limits, density measurement bases, and the physical limitations of holding the ANFO label fixed.
- Retains the `RESEARCH_COMPARATOR_ONLY` decision gate.
"""


def version_line(text: str, pattern: str, label: str) -> str:
    matches = list(re.finditer(pattern, text, flags=re.MULTILINE))
    if len(matches) != 1:
        raise ValueError(f"Expected one version declaration in {label}.")
    match = matches[0]
    if match.group(2) not in {"0.7.0", VERSION}:
        raise ValueError(
            f"Unexpected version {match.group(2)!r} in {label}; "
            "no files have been written."
        )
    return text[:match.start(2)] + VERSION + text[match.end(2):]


def current_test_counts(text: str, label: str, phrases: tuple[str, ...]) -> str:
    for phrase in phrases:
        pattern = rf"\b(?:135|192)(?= {re.escape(phrase)}\b)"
        if not re.search(pattern, text):
            raise ValueError(f"Cannot locate the current test count for {phrase!r} in {label}.")
        text = re.sub(pattern, "192", text)
    return text


def update_changelog(text: str, release_date: str) -> str:
    unreleased = re.search(r"^## \[Unreleased\][ \t]*$", text, re.MULTILINE)
    if unreleased is None:
        raise ValueError("CHANGELOG.md must contain an [Unreleased] heading.")
    if not re.search(r"^## \[0\.8\.0\]", text, re.MULTILINE):
        previous = re.search(
            r"^## \[(?!Unreleased)[^\]]+\]", text[unreleased.end():], re.MULTILINE
        )
        if previous is None:
            raise ValueError("Cannot locate previous release history in CHANGELOG.md.")
        insertion = unreleased.end() + previous.start()
        section = CHANGELOG_SECTION.format(release_date=release_date).strip()
        text = text[:insertion].rstrip() + "\n\n" + section + "\n\n" + text[insertion:]
    else:
        text = re.sub(
            r"^## \[0\.8\.0\] - \d{4}-\d{2}-\d{2}[ \t]*$",
            f"## [{VERSION}] - {release_date}", text, flags=re.MULTILINE,
        )

    unreleased_link = f"[Unreleased]: {REPOSITORY}/compare/v{VERSION}...HEAD"
    if not re.search(r"^\[Unreleased\]:.*$", text, re.MULTILINE):
        raise ValueError("Cannot locate the Unreleased comparison link in CHANGELOG.md.")
    text = re.sub(r"^\[Unreleased\]:.*$", unreleased_link, text, flags=re.MULTILINE)
    release_link = f"[{VERSION}]: {REPOSITORY}/compare/v0.7.0...v{VERSION}"
    if re.search(r"^\[0\.8\.0\]:.*$", text, re.MULTILINE):
        text = re.sub(r"^\[0\.8\.0\]:.*$", release_link, text, flags=re.MULTILINE)
    else:
        text = text.replace(unreleased_link, unreleased_link + "\n" + release_link, 1)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--release-date", default="2026-10-06")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    date.fromisoformat(args.release_date)
    project_root = args.project_root.resolve()

    filenames = (
        "pyproject.toml",
        "src/blastdesign_ai/__init__.py",
        "tests/test_public_api.py",
        "CITATION.cff",
        "README.md",
        "docs/burden_model_research_note.md",
        "CHANGELOG.md",
    )
    originals = {}
    originals_bytes = {}
    for filename in filenames:
        raw = (project_root / filename).read_bytes()
        originals_bytes[filename] = raw
        originals[filename] = raw.decode("utf-8-sig").replace("\r\n", "\n")
    revised = originals.copy()

    version_patterns = {
        "pyproject.toml": r'''(^version\s*=\s*["'])([^"']+)(["'])''',
        "src/blastdesign_ai/__init__.py": r'''(^__version__\s*=\s*["'])([^"']+)(["'])''',
        "tests/test_public_api.py": r'''(^\s*assert\s+blastdesign_ai\.__version__\s*==\s*["'])([^"']+)(["'])''',
        "CITATION.cff": r'''(^version:\s*["']?)([0-9]+\.[0-9]+\.[0-9]+)(["']?\s*$)''',
    }
    for filename, pattern in version_patterns.items():
        revised[filename] = version_line(revised[filename], pattern, filename)

    citation, replacements = re.subn(
        r"^date-released:.*$", f"date-released: {args.release_date}",
        revised["CITATION.cff"], flags=re.MULTILINE,
    )
    if replacements != 1:
        raise ValueError("Expected one date-released field in CITATION.cff.")
    revised["CITATION.cff"] = citation

    readme = current_test_counts(
        revised["README.md"], "README.md", ("passing tests", "passed")
    )
    if "## Controlled joint-density sensitivity analysis" not in readme:
        marker = "## Decision safeguards"
        if marker not in readme:
            raise ValueError("Cannot locate the README Decision safeguards section.")
        readme = readme.replace(marker, README_SECTION.strip() + "\n\n" + marker, 1)
    revised["README.md"] = readme

    note = current_test_counts(
        revised["docs/burden_model_research_note.md"],
        "docs/burden_model_research_note.md",
        ("passing automated tests", "passing tests"),
    )
    if "## Controlled joint explosive-density and rock-density analysis" not in note:
        note = note.rstrip() + "\n\n" + RESEARCH_SECTION.strip() + "\n"
    revised["docs/burden_model_research_note.md"] = note
    revised["CHANGELOG.md"] = update_changelog(revised["CHANGELOG.md"], args.release_date)

    changes = []
    for filename in filenames:
        if revised[filename] != originals[filename]:
            changes.append(filename)
    if args.dry_run:
        for filename in changes:
            print("".join(difflib.unified_diff(
                originals[filename].splitlines(keepends=True),
                revised[filename].splitlines(keepends=True),
                fromfile=filename, tofile=filename,
            )), end="")
        print(f"Dry run: {len(changes)} files would change.")
        return

    for filename in changes:
        raw = originals_bytes[filename]
        text = revised[filename]
        if b"\r\n" in raw:
            text = text.replace("\n", "\r\n")
        encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
        (project_root / filename).write_bytes(text.encode(encoding))
        print(f"Updated: {filename}")
    print(f"Version {VERSION} preparation complete: {len(changes)} files changed.")
    print("Reinstall the editable package, regenerate checksums, and run pytest next.")


if __name__ == "__main__":
    main()
