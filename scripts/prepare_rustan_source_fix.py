"""Prepare the visually verified Rustan source-range correction.

Save in scripts/. Run --dry-run before the default preparation command.
After the real complete suite passes, --test-count N updates current counts.
The helper preserves existing files with backups outside the checkout and
validates every planned source edit before writing any project file.
"""

from __future__ import annotations

import argparse
import ast
import copy
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile


OLD_FUNCTIONS = {
    "rustan_burden": "def rustan_burden(hole_diameter_mm) -> float:\n    \"\"\"Rustan (1990/1992): B = 18.1 d^0.689, with d and B in metres.\"\"\"\n    diameter_m = positive_float(hole_diameter_mm, \"hole_diameter_mm\") / 1000.0\n    return 18.1 * diameter_m**0.689\n",
    "rustan_applicability": "def rustan_applicability(hole_diameter_mm) -> str:\n    \"\"\"Classify the diameter against the documented 89–311 mm thesis range.\"\"\"\n    diameter_mm = positive_float(hole_diameter_mm, \"hole_diameter_mm\")\n    if diameter_mm < 89:\n        return \"Outside documented domain: below 89 mm\"\n    if diameter_mm <= 311:\n        return \"Within documented 89–311 mm domain\"\n    return \"Extrapolation: above documented 311 mm limit\"\n",
    "build_gole_gohar_diameter_sensitivity_table": "def build_gole_gohar_diameter_sensitivity_table(\n    hole_diameters_mm: Iterable[float] | None = None,\n) -> pd.DataFrame:\n    \"\"\"Build a seven-model diameter-sensitivity comparison.\n\n    The comparison window is greater than 180 mm through 311 mm.\n    This selects the Lopez Jimeno large-hole branch and avoids\n    extrapolating Rustan beyond its documented upper limit.\n\n    The window is not a universal validation domain for all models.\n    \"\"\"\n\n    if hole_diameters_mm is None:\n        raw_diameters = list(\n            DEFAULT_DIAMETER_GRID_MM\n        )\n    else:\n        if isinstance(\n            hole_diameters_mm,\n            (str, bytes),\n        ):\n            raise TypeError(\n                \"hole_diameters_mm must be an iterable \"\n                \"of numerical values.\"\n            )\n\n        try:\n            raw_diameters = list(\n                hole_diameters_mm\n            )\n        except TypeError as error:\n            raise TypeError(\n                \"hole_diameters_mm must be an iterable \"\n                \"of numerical values.\"\n            ) from error\n\n    if not raw_diameters:\n        raise ValueError(\n            \"At least one hole diameter is required.\"\n        )\n\n    diameters = [\n        positive_float(\n            value,\n            \"hole_diameter_mm\",\n        )\n        for value in raw_diameters\n    ]\n\n    if len(set(diameters)) != len(diameters):\n        raise ValueError(\n            \"Hole-diameter values must be unique.\"\n        )\n\n    for diameter in diameters:\n        if not 180.0 < diameter <= 311.0:\n            raise ValueError(\n                \"Diameter sensitivity requires values \"\n                \"greater than 180 mm and no greater \"\n                \"than 311 mm.\"\n            )\n\n    diameters.sort()\n\n    reference_inputs = (\n        gole_gohar_reference_inputs()\n    )\n\n    tables = []\n\n    for diameter in diameters:\n        scenario_inputs = (\n            reference_inputs.copy()\n        )\n        scenario_inputs[\n            \"hole_diameter_mm\"\n        ] = diameter\n\n        model_table = (\n            evaluate_conventional_burden_models(\n                **scenario_inputs\n            )\n        )\n\n        model_table.insert(\n            0,\n            \"hole_diameter_mm\",\n            diameter,\n        )\n\n        tables.append(model_table)\n\n    result = pd.concat(\n        tables,\n        ignore_index=True,\n    )\n\n    fixed_inputs = reference_inputs.copy()\n    reference_diameter = fixed_inputs.pop(\n        \"hole_diameter_mm\"\n    )\n\n    result.attrs[\"analysis_type\"] = (\n        \"one_factor_at_a_time\"\n    )\n    result.attrs[\"varied_parameter\"] = (\n        \"hole_diameter_mm\"\n    )\n    result.attrs[\"reference_hole_diameter_mm\"] = (\n        reference_diameter\n    )\n    result.attrs[\"fixed_inputs\"] = fixed_inputs\n    result.attrs[\"comparison_window_mm\"] = {\n        \"lower_bound_exclusive\": 180.0,\n        \"upper_bound_inclusive\": 311.0,\n    }\n    result.attrs[\"decision_gate\"] = (\n        \"RESEARCH_COMPARATOR_ONLY\"\n    )\n    result.attrs[\"window_warning\"] = (\n        \"The comparison window aligns the Lopez Jimeno \"\n        \"large-hole branch with the documented Rustan \"\n        \"upper limit; it is not a universal validation \"\n        \"domain for all models.\"\n    )\n\n    return result\n"
}
NEW_FUNCTIONS = {
    "rustan_burden": "def rustan_burden(hole_diameter_mm) -> float:\n    \"\"\"Return the normalized practical burden from Rustan (1992), Eq. 22.\n    \n    The existing metre-based expression is B_p1 = 18.1 * d**0.689.\n    B_p1 corresponds to S/B = 1, not an arbitrary-spacing prescription.\n    The conflicting Figure 5 coefficient is recorded in the source audit.\n    \"\"\"\n    diameter_m = positive_float(hole_diameter_mm, \"hole_diameter_mm\") / 1000.0\n    return 18.1 * diameter_m**0.689\n",
    "rustan_applicability": "def rustan_applicability(hole_diameter_mm) -> str:\n    \"\"\"Screen the 89–381 mm interval reported by Rustan (1992), Eq. 22.\n\n    This diameter screen does not verify other source conditions or\n    establish site-specific predictive accuracy.\n    \"\"\"\n    diameter_mm = positive_float(hole_diameter_mm, \"hole_diameter_mm\")\n    if diameter_mm < 89:\n        return \"Outside documented domain: below 89 mm\"\n    if diameter_mm <= 381:\n        return \"Within documented 89–381 mm domain\"\n    return \"Extrapolation: above documented 381 mm limit\"\n",
    "build_gole_gohar_diameter_sensitivity_table": "def build_gole_gohar_diameter_sensitivity_table(\n    hole_diameters_mm: Iterable[float] | None = None,\n) -> pd.DataFrame:\n    \"\"\"Build the historical seven-model diameter-sensitivity comparison.\n    \n    The retained comparison window is greater than 180 mm through 311 mm.\n    It selects the Lopez Jimeno large-hole branch. Rustan (1992), Eq. 22,\n    reports 89–381 mm; 311 mm remains this study's historical upper limit.\n    \n    The comparison window is not a universal model-validation domain.\n    \"\"\"\n\n    if hole_diameters_mm is None:\n        raw_diameters = list(\n            DEFAULT_DIAMETER_GRID_MM\n        )\n    else:\n        if isinstance(\n            hole_diameters_mm,\n            (str, bytes),\n        ):\n            raise TypeError(\n                \"hole_diameters_mm must be an iterable \"\n                \"of numerical values.\"\n            )\n\n        try:\n            raw_diameters = list(\n                hole_diameters_mm\n            )\n        except TypeError as error:\n            raise TypeError(\n                \"hole_diameters_mm must be an iterable \"\n                \"of numerical values.\"\n            ) from error\n\n    if not raw_diameters:\n        raise ValueError(\n            \"At least one hole diameter is required.\"\n        )\n\n    diameters = [\n        positive_float(\n            value,\n            \"hole_diameter_mm\",\n        )\n        for value in raw_diameters\n    ]\n\n    if len(set(diameters)) != len(diameters):\n        raise ValueError(\n            \"Hole-diameter values must be unique.\"\n        )\n\n    for diameter in diameters:\n        if not 180.0 < diameter <= 311.0:\n            raise ValueError(\n                \"Diameter sensitivity requires values \"\n                \"greater than 180 mm and no greater \"\n                \"than 311 mm.\"\n            )\n\n    diameters.sort()\n\n    reference_inputs = (\n        gole_gohar_reference_inputs()\n    )\n\n    tables = []\n\n    for diameter in diameters:\n        scenario_inputs = (\n            reference_inputs.copy()\n        )\n        scenario_inputs[\n            \"hole_diameter_mm\"\n        ] = diameter\n\n        model_table = (\n            evaluate_conventional_burden_models(\n                **scenario_inputs\n            )\n        )\n\n        model_table.insert(\n            0,\n            \"hole_diameter_mm\",\n            diameter,\n        )\n\n        tables.append(model_table)\n\n    result = pd.concat(\n        tables,\n        ignore_index=True,\n    )\n\n    fixed_inputs = reference_inputs.copy()\n    reference_diameter = fixed_inputs.pop(\n        \"hole_diameter_mm\"\n    )\n\n    result.attrs[\"analysis_type\"] = (\n        \"one_factor_at_a_time\"\n    )\n    result.attrs[\"varied_parameter\"] = (\n        \"hole_diameter_mm\"\n    )\n    result.attrs[\"reference_hole_diameter_mm\"] = (\n        reference_diameter\n    )\n    result.attrs[\"fixed_inputs\"] = fixed_inputs\n    result.attrs[\"comparison_window_mm\"] = {\n        \"lower_bound_exclusive\": 180.0,\n        \"upper_bound_inclusive\": 311.0,\n    }\n    result.attrs[\"decision_gate\"] = (\n        \"RESEARCH_COMPARATOR_ONLY\"\n    )\n    result.attrs[\"window_warning\"] = (\n        \"The historical comparison window is greater than 180 mm through 311 \"\n        \"mm and selects the Lopez Jimeno large-hole branch. Rustan (1992), \"\n        \"Eq. 22, reports 89–381 mm; 311 mm is the retained study limit. The \"\n        \"window is not a universal validation domain for all models.\"\n    )\n\n    return result\n"
}
SOURCE_DOCUMENT = "# Rustan source-page audit\n\nReview date: 25 October 2026.\n\n## Source and scope\n\nRustan, R. Agne (1992), *Burden, spacing and borehole diameter at rock blasting*,\nInternational Journal of Surface Mining, Reclamation and Environment 6(3),\n141–149. DOI: [10.1080/09208119208944329](https://doi.org/10.1080/09208119208944329).\n\nPrinted pages 146 and 147 were visually inspected in images supplied by the\nproject author from the institutional reprint. They are marked E6 and E7 in\nPaper E of Rustan's 1995 doctoral thesis, *Controlled fragmentation and contours\nin rock blasting: theoretical and technical approaches*.\n[Institutional thesis record](https://ltu.diva-portal.org/smash/record.jsf?pid=diva2:991783).\n\nThis review establishes what those two pages print. It does not claim visual\ninspection of every page, an author-issued correction, or new field validation.\n\n## Verified readings\n\n| Location | Reading |\n|---|---|\n| Printed p. 146/E6, Section 4.2, Eq. 18 | `B_p1 = sqrt(B_p * S_p)`. `B_p1` is practical burden for `S/B = 1`; the three lengths are expressed in metres. |\n| Printed p. 147/E7, Section 4.3 heading | Open-pit statistical relationship for diameters 89–381 mm. |\n| Printed p. 147/E7, Eq. 22 | `B_p1 = 18.1 * d^0.689`. The line below the equation repeats the 89–381 mm interval. |\n| Printed p. 147/E7, Figure 5 | The surface-mine label prints `18.8 * d^0.689`, conflicting with Eq. 22's coefficient 18.1. |\n| Printed p. 147/E7, Eq. 22 annotations | The labels describe +52% and -37% expected extrema; this page does not assign them a confidence level. |\n\nThe normalization equation preserves the product of practical burden and spacing.\nAlgebraically, if `r = S_p / B_p > 0`, then `B_p = B_p1 / sqrt(r)` and\n`S_p = B_p1 * sqrt(r)`. These are consequences of Eq. 18 and the definition of\n`r`, not additional calibrated design equations implemented by this change.\n\n## Reconstruction decisions\n\nThe implementation follows the explicit numbered Eq. 22 and retains **18.1**.\nThe conflicting **18.8** figure label is recorded as an unresolved internal\nsource discrepancy. This review does not establish which value the author\nintended for the figure, nor assume a published erratum exists.\n\n`rustan_burden` continues to convert its millimetre argument to metres before\nevaluating the existing expression. Its equation, returned numerical values,\nand reconstructed 251 mm benchmark remain unchanged. The returned quantity is\nthe normalized practical burden `B_p1`, not a spacing-independent prescription\nfor arbitrary blast geometry.\n\n`rustan_applicability` is corrected from the thesis-derived 89–311 mm screen to\nthe **89–381 mm interval printed in Section 4.3 and below Eq. 22**. Both endpoints\nare included. Being inside this diameter interval does not establish all other\nsource conditions or predictive accuracy at a particular mine.\n\n## Compatibility and research outputs\n\nThis is an explicitly documented applicability-screen correction. Calls between\n311 and 381 mm change from an extrapolation label to an inside-range label.\nThe human-readable inside-range and upper-extrapolation messages also change\ntheir reported upper bound. Public function names, signatures, physical input\nunits, and DataFrame schemas are retained. This behavioral change must be\nincluded in the next release notes; it is not hidden by recapturing the API baseline.\n\nThe historical all-model diameter comparison retains its existing grid from\n181 through 311 mm and its existing custom-input condition `180 < d_mm <= 311`.\nThe 311 mm study limit remains separate from Rustan's published 381 mm limit.\nIts docstring and runtime warning explain that distinction.\n\nNo existing CSV, JSON, notebook, figure, reference input, or numerical artifact\nis regenerated by this correction. In particular, the ten checksum-verified\nlegacy CSVs remain historical records, including their earlier applicability\nwording. The released v1.0.0 tag and compatibility baseline are preserved.\n\nThe seven-model ensemble remains a comparison of reconstructed legacy equation\noutputs. Rustan's normalized practical quantity must be stated when interpreting\nthe comparison. The source definitions and charging/geometry assumptions for all\nseven relationships have not yet been fully harmonized. The calculated spread\ntherefore does not establish agreement or disagreement between seven independently\nvalidated estimates of an identical operational design target.\n\n## Verification\n\nSix source-based boundary cases cover the lower limit, the former upper limit,\nthe newly included interval, and the published upper limit. A seventh regression\ncheck preserves the historical grid, its custom-input limit, and its research\ndecision gate. Existing benchmark and artifact-consistency tests remain the\nchecks on unchanged numerical outputs. The full real repository suite must pass\nbefore committing the correction.\n\nThe preparation helper changes only the reviewed source/documentation sections\nand the new tests. It checks that research data, notebooks, version metadata,\nand the compatibility baseline retain their existing bytes.\n\n## Review-input identifiers\n\nThe following hashes identify the supplied images inspected in this review;\nthe preparation helper installs the audit text rather than copies of the images.\n\n| Image | Printed page | SHA-256 |\n|---|---:|---|\n| `Extracted pages from FULLTEXT01_Page1.jpg` | 146/E6 | `55c697562d3da41d3506f256b36f72c6fc484ead6c15253ec907192c37f99de8` |\n| `Extracted pages from FULLTEXT01_Page2.jpg` | 147/E7 | `6530896a64a43c2fc6fd6d38380a8c1c999dac04dbe4e0294fb064243a6dfd95` |\n\nThe `RESEARCH_COMPARATOR_ONLY` decision gate remains in force.\n"
TEST_SOURCE = "\"\"\"Regression checks for Rustan's visually verified source interval.\"\"\"\n\nimport unittest\n\nfrom blastdesign import rustan_applicability\nfrom blastdesign.sensitivity import (\n    DEFAULT_DIAMETER_GRID_MM,\n    build_gole_gohar_diameter_sensitivity_table,\n)\n\n\nclass TestRustanSourceRange(unittest.TestCase):\n    \"\"\"Use the printed p. 147/E7 Section 4.3 and Eq. 22 limits.\"\"\"\n\n    def test_diameter_below_published_lower_limit(self):\n        self.assertEqual(\n            rustan_applicability(88.999),\n            \"Outside documented domain: below 89 mm\",\n        )\n\n    def test_published_lower_endpoint_is_included(self):\n        self.assertEqual(\n            rustan_applicability(89.0),\n            \"Within documented 89–381 mm domain\",\n        )\n\n    def test_former_upper_endpoint_reports_corrected_interval(self):\n        self.assertEqual(\n            rustan_applicability(311.0),\n            \"Within documented 89–381 mm domain\",\n        )\n\n    def test_diameter_above_former_limit_is_inside_source_interval(self):\n        self.assertEqual(\n            rustan_applicability(311.001),\n            \"Within documented 89–381 mm domain\",\n        )\n\n    def test_published_upper_endpoint_is_included(self):\n        self.assertEqual(\n            rustan_applicability(381.0),\n            \"Within documented 89–381 mm domain\",\n        )\n\n    def test_diameter_above_published_upper_limit_is_extrapolation(self):\n        self.assertEqual(\n            rustan_applicability(381.001),\n            \"Extrapolation: above documented 381 mm limit\",\n        )\n\n    def test_historical_comparison_window_is_preserved(self):\n        self.assertEqual(DEFAULT_DIAMETER_GRID_MM, (\n            181.0, 191.0, 201.0, 211.0, 221.0, 231.0, 241.0,\n            251.0, 261.0, 271.0, 281.0, 291.0, 301.0, 311.0,\n        ))\n        # The all-model comparison window remains a separate study choice.\n        with self.assertRaisesRegex(ValueError, \"311 mm\"):\n            build_gole_gohar_diameter_sensitivity_table([311.001])\n        table = build_gole_gohar_diameter_sensitivity_table([251.0])\n        self.assertEqual(table.attrs[\"comparison_window_mm\"], {\n            \"lower_bound_exclusive\": 180.0,\n            \"upper_bound_inclusive\": 311.0,\n        })\n        self.assertEqual(table.attrs[\"decision_gate\"], \"RESEARCH_COMPARATOR_ONLY\")\n        self.assertIn(\"89–381 mm\", table.attrs[\"window_warning\"])\n"
OLD_PROVENANCE = {
    "intro": "This is an initial provenance audit. It does not change the equations, public API, compatibility baseline, reference scenario, evidence tiers, or saved numerical results. Findings below are review items, not changes already made to the software.",
    "rustan_section": "## Rustan\n\nFunctions: `rustan_burden(hole_diameter_mm)` and `rustan_applicability(hole_diameter_mm)`.\n\nThe thesis prints millimetres beside Eq. 2-11, but the code uses metres. Its benchmark supports that reconstruction. The applicability helper records 89–311 mm; the numerical function itself accepts any positive diameter.\n\nRustan's 1992 paper [R] was checked through an extracted full-text reproduction, with publication identity corroborated by LTU. Section 4.3, Eq. 22 reports the implemented expression over **89–381 mm**, conflicting with the thesis. Its burden is normalized to spacing/burden equal to one; Section 4.2 defines that quantity using the square root of practical burden times practical spacing. The paper also assumes coupled charges.\n\nThis distinction affects interpretation of the seven-model comparison. The source scan should be visually checked before changing the applicability helper, diameter grid, or associated documentation. The v1.0.0 values remain unchanged by this review.\n\n",
    "p01": "| P01 | Rustan's published upper diameter differs from the thesis-derived helper | Inspect the original page image for Section 4.3/Eq. 22; review the helper, tests, grid rationale, and research text together |",
    "p07": "",
    "reference": "**[R] Original research publication.** Rustan, R. Agne, 1992. *Burden, spacing and borehole diameter at rock blasting*. International Journal of Surface Mining, Reclamation and Environment 6(3), 141–149. [DOI](https://doi.org/10.1080/09208119208944329); [LTU publication record](https://ltu.diva-portal.org/smash/record.jsf?pid=diva2:982260). Relevant extracted text: Sections 4.2–4.3, Eqs. 18 and 22; [reproduction inspected](https://www.scribd.com/document/383336301/Rustan-1992). Original page-image verification remains open."
}
NEW_PROVENANCE = {
    "intro": "The initial 17 October audit recorded review items without changing the software. The Rustan follow-up on 25 October 2026 visually checked printed pages 146–147, corrected the applicability screen to the reported 89–381 mm interval, and clarified the output definition. Implemented follow-ups are marked explicitly; the other findings remain review items. Burden equations, public signatures, sampling grids, the compatibility baseline, reference inputs, historical tiers, and saved numerical artifacts remain unchanged.",
    "rustan_section": "## Rustan\n\nFunctions: `rustan_burden(hole_diameter_mm)` and `rustan_applicability(hole_diameter_mm)`.\n\nThe thesis prints millimetres beside Eq. 2-11, but the implementation uses metres.\nIts benchmark supports that reconstruction. The numerical function continues\nusing coefficient 18.1 and exponent 0.689 and accepts positive diameters; its\nseparate applicability helper supplies the diameter-range screen.\n\nOn 25 October 2026, printed pages 146–147 (E6–E7 in the institutional thesis\nreprint) were visually checked [R]. Page 146, Eq. 18 defines\n`B_p1 = sqrt(B_p * S_p)` as practical burden normalized to `S/B = 1`.\nPage 147, Section 4.3 and the line below Eq. 22 both report **89–381 mm**.\nThe helper is corrected from its thesis-derived 311 mm upper limit to 381 mm.\nThe historical 181–311 mm all-model comparison grid remains unchanged.\n\nPage 147 prints **18.1** in Eq. 22 but **18.8** in Figure 5's surface-mine label.\nThe implementation retains the explicit numbered Eq. 22 coefficient. The\nconflicting label is a recorded source discrepancy, not a resolved author erratum.\n\nThe output definition affects interpretation of the seven-model comparison:\nnormalized practical burden must not silently be treated as an arbitrary-spacing\nburden prescription. The engineering target definitions and geometry/charging\nassumptions of all seven sources have not yet been fully harmonized. The earlier\ncoupled-charge assumption was checked in extracted text outside these two page\nimages; this visual check does not extend to every source page or condition.\n\nSee [the Rustan source-page audit](RUSTAN_SOURCE_AUDIT.md) for the exact readings,\ncompatibility implications, regression checks, and review-input identifiers.\nReleased v1.0.0 artifacts and the ten historical legacy CSVs retain their original\nvalues and wording.\n\n",
    "p01": "| P01 | Rustan source interval verified as 89–381 mm and helper corrected; historical grid retained | Resolved range check on printed pp. 146–147/E6–E7; source-definition harmonization remains under P02 |",
    "p07": "| P07 | Rustan Figure 5 prints 18.8 while Eq. 22 prints 18.1 | Retain explicit Eq. 22 in the reconstruction; record the discrepancy without asserting an author-issued correction |",
    "reference": "**[R] Original research publication.** Rustan, R. Agne, 1992. *Burden, spacing and borehole diameter at rock blasting*. International Journal of Surface Mining, Reclamation and Environment 6(3), 141–149. [DOI](https://doi.org/10.1080/09208119208944329); [LTU publication record](https://ltu.diva-portal.org/smash/record.jsf?pid=diva2:982260). Visually checked on 25 October 2026: printed pp. 146–147/E6–E7, Sections 4.2–4.3, Eqs. 18 and 22, and the Figure 5 label; [reproduction inspected](https://www.scribd.com/document/383336301/Rustan-1992). These supplied page images verify the stated range and normalization and expose the coefficient-label discrepancy; other source conditions are not certified by this two-page check."
}

README_BLOCK = """<!-- BEGIN RUSTAN SOURCE REVIEW -->
### Rustan source clarification

The visually checked Rustan (1992) Eq. 22 reports **89–381 mm**. The historical
181–311 mm all-model comparison grid is retained as a study choice. The
applicability helper now uses the published 381 mm upper bound.

Rustan's output is normalized practical burden for `S/B = 1`. Eq. 22's coefficient
**18.1** is retained; Figure 5's conflicting **18.8** label is documented. The
comparison remains a research comparison of legacy equation outputs, with source
definitions still requiring harmonization across models.

See [the Rustan source-page audit](docs/RUSTAN_SOURCE_AUDIT.md) for the verified
page readings, compatibility implications, and interpretation limits.
<!-- END RUSTAN SOURCE REVIEW -->
"""

RESEARCH_BLOCK = """<!-- BEGIN RUSTAN SOURCE REVIEW -->
## Rustan source-page audit

Visual inspection of Rustan (1992), printed pages 146–147 (E6–E7 in the doctoral
thesis reprint), confirms Eq. 18's normalization
`B_p1 = sqrt(B_p * S_p)` and Eq. 22's **89–381 mm** open-pit diameter interval.
The applicability helper is corrected to that interval. The existing 181–311 mm
diameter-comparison grid is retained independently for reproducibility.

Eq. 22 prints **18.1**, while Figure 5's surface-mine label prints **18.8**. The
implementation continues following the explicit numbered equation with 18.1;
the conflicting figure label is recorded as an unresolved source discrepancy.
No numerical burden expression or saved numerical artifact changes.

Rustan's normalized practical burden is not an arbitrary-spacing burden
prescription. The seven-model study compares reconstructed legacy outputs;
complete harmonization of their engineering target definitions remains open.
This limits interpretation of the ensemble spread as disagreement about an
identical operational design target. Historical evidence-tier CSVs remain
unchanged archival records.

See [the Rustan source-page audit](RUSTAN_SOURCE_AUDIT.md). The
`RESEARCH_COMPARATOR_ONLY` decision gate remains in force.
<!-- END RUSTAN SOURCE REVIEW -->
"""

API_BLOCK = """<!-- BEGIN RUSTAN SOURCE REVIEW -->
## Rustan applicability-source correction (Unreleased)

`blastdesign.rustan_applicability(hole_diameter_mm)` now screens the reported
89–381 mm interval of Rustan (1992), Eq. 22, including both endpoints. Calls above
311 through 381 mm therefore change classification; the returned inside-range
and upper-extrapolation strings report 381 mm. This is a documented source-range
correction, not a recapture of the v1.0.0 compatibility baseline.

`blastdesign.rustan_burden(hole_diameter_mm)` retains its argument, millimetre
input conversion, and numerical expression with coefficient 18.1. Its output
represents normalized practical burden for `S/B = 1`. The historical all-model
diameter-comparison grid and input window stay unchanged.

See [the Rustan source-page audit](RUSTAN_SOURCE_AUDIT.md) for the printed evidence
and the conflicting Figure 5 label. No new predictive-validation claim is made.
<!-- END RUSTAN SOURCE REVIEW -->
"""

FIXED_ENTRY = (
    "- Corrected Rustan's applicability screen to the visually verified "
    "89–381 mm interval in the 1992 paper; retained the historical "
    "181–311 mm comparison grid and updated its explanatory metadata."
)
ADDED_ENTRY = (
    "- Rustan source-page audit documenting normalized practical burden, "
    "the Eq. 22/Figure 5 coefficient discrepancy, and seven regression "
    "checks for the source interval and retained comparison window."
)


def decode(data: bytes) -> str:
    text = data.decode("utf-8-sig")
    if "\r" in text.replace("\r\n", ""):
        raise ValueError("Unexpected bare-CR text line endings; inspect the file before editing.")
    return text.replace("\r\n", "\n")


def encode(text: str, original: bytes | None) -> bytes:
    raw = original or b""
    newline = "\r\n" if b"\r\n" in raw else "\n"
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.replace("\n", newline).encode("utf-8")


def signature(node: ast.AST) -> str:
    return ast.dump(node, include_attributes=False)


def function_node(source: str, name: str) -> ast.FunctionDef:
    nodes = [node for node in ast.parse(source).body
             if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(nodes) != 1 or nodes[0].decorator_list:
        raise ValueError("Expected one undecorated top-level function: " + name)
    return nodes[0]


def replace_node(source: str, node: ast.AST, replacement: str) -> str:
    # AST column offsets count UTF-8 bytes, including in the en-dash docstrings.
    lines = source.encode("utf-8").splitlines(keepends=True)
    start = sum(map(len, lines[:node.lineno - 1])) + node.col_offset
    end = sum(map(len, lines[:node.end_lineno - 1])) + node.end_col_offset
    raw = source.encode("utf-8")
    return (raw[:start] + replacement.encode("utf-8") + raw[end:]).decode("utf-8")


def patch_function(source: str, name: str) -> str:
    current = function_node(source, name)
    old = function_node(OLD_FUNCTIONS[name], name)
    new = function_node(NEW_FUNCTIONS[name], name)
    if signature(current) == signature(new):
        return source
    if signature(current) != signature(old):
        raise ValueError("The function differs from the reviewed source; inspect before changing: " + name)
    updated = replace_node(source, current, NEW_FUNCTIONS[name].rstrip("\n"))
    if signature(function_node(updated, name)) != signature(new):
        raise ValueError("Prepared function did not match the reviewed result: " + name)
    return updated


def calculation_signature(source: str, name: str, ignore_warning: bool = False) -> str:
    node = copy.deepcopy(function_node(source, name))
    if ast.get_docstring(node) is not None:
        node.body.pop(0)
    if ignore_warning:
        for item in ast.walk(node):
            if not isinstance(item, ast.Assign) or len(item.targets) != 1:
                continue
            target = item.targets[0]
            if isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Constant) and target.slice.value == "window_warning":
                item.value = ast.Constant(value="<explanatory warning>")
    return signature(node)


def patch_provenance(text: str) -> str:
    for key in ("intro", "rustan_section", "p01", "p07", "reference"):
        old, new = OLD_PROVENANCE[key], NEW_PROVENANCE[key]
        if new in text:
            continue
        if key == "p07":
            # This new review item follows the existing P06 row.
            rows = re.findall(r"(?m)^\| P06 \|.*$", text)
            if len(rows) != 1:
                raise ValueError("Expected the P06 review row before adding P07.")
            text = text.replace(rows[0], rows[0] + "\n" + new, 1)
            continue
        if text.count(old) != 1:
            raise ValueError("The provenance document differs in the reviewed section: " + key)
        text = text.replace(old, new, 1)
    return text


def clarify_old_prose(text: str) -> str:
    """Correct clear Rustan range claims in active prose, preserving code blocks."""
    sections = re.split(r"(```.*?```|~~~.*?~~~)", text, flags=re.S)
    for index in range(0, len(sections), 2):
        paragraphs = re.split(r"(\n[ \t]*\n)", sections[index])
        for i in range(0, len(paragraphs), 2):
            paragraph = paragraphs[i]
            if "rustan" not in paragraph.casefold() or "311" not in paragraph:
                continue
            # Explicitly historical statements keep their historical meaning.
            if any(word in paragraph.casefold() for word in (
                "thesis-derived", "historical range", "legacy ledger",
                "published v1.0.0", "released v1.0.0",
            )):
                continue
            paragraph = re.sub(r"89\s*[–—-]\s*311(?=\s*mm\b)", "89–381", paragraph)
            paragraph = re.sub(
                r"Rustan(?:['’]s)?\s+documented\s+311\s*mm\s+upper\s+limit",
                "the retained 311 mm comparison limit", paragraph, flags=re.I,
            )
            paragraph = re.sub(
                r"(?:the\s+)?documented\s+Rustan\s+upper\s+limit",
                "the retained diameter-comparison limit", paragraph, flags=re.I,
            )
            paragraph = re.sub(
                r"Rustan(?:['’]s)?\s+(?:documented\s+)?upper\s+limit",
                "the retained diameter-comparison limit", paragraph, flags=re.I,
            )
            paragraphs[i] = paragraph
        sections[index] = "".join(paragraphs)
    return "".join(sections)


def add_review_block(text: str, block: str, readme: bool = False) -> str:
    begin, end = "<!-- BEGIN RUSTAN SOURCE REVIEW -->", "<!-- END RUSTAN SOURCE REVIEW -->"
    if begin in text or end in text:
        if text.count(begin) != 1 or text.count(end) != 1:
            raise ValueError("Ambiguous Rustan review markers in documentation.")
        if text[text.index(begin):text.index(end) + len(end)] != block.rstrip("\n"):
            raise ValueError("The existing Rustan documentation block differs; inspect before changing.")
        return text
    if not readme:
        return text.rstrip("\n") + "\n\n" + block
    header = "## Diameter sensitivity analysis"
    if text.count(header) != 1:
        raise ValueError("Expected the current README diameter-sensitivity heading.")
    start = text.index(header) + len(header)
    following = re.search(r"(?m)^## ", text[start:])
    end_section = start + following.start() if following else len(text)
    return text[:end_section].rstrip("\n") + "\n\n" + block + "\n" + text[end_section:]


def changelog_entry(text: str, heading: str, entry: str) -> str:
    marker = "## [Unreleased]"
    if text.count(marker) != 1:
        raise ValueError("Expected one Unreleased changelog section.")
    start = text.index(marker) + len(marker)
    following = re.search(r"(?m)^## ", text[start:])
    stop = start + following.start() if following else len(text)
    section = text[start:stop]
    if entry in section:
        return text
    title = "### " + heading
    if title in section:
        if section.count(title) != 1:
            raise ValueError("Duplicate changelog heading under Unreleased: " + heading)
        position = section.index(title) + len(title)
        section = section[:position] + "\n\n" + entry + section[position:]
    else:
        section = section.rstrip("\n") + "\n\n" + title + "\n\n" + entry + "\n\n"
    return text[:start] + section + text[stop:]


def update_test_counts(text: str, count: int) -> str:
    for pattern, replacement in (
        (r"\b234 passing automated tests\b", f"{count} passing automated tests"),
        (r"\b234 passing tests\b", f"{count} passing tests"),
        (r"\b234 tests and\s+228 subtests\b", f"{count} tests and 228 subtests"),
        (r"\b234 passed\b", f"{count} passed"),
    ):
        text = re.sub(pattern, replacement, text)
    return text


def protected_snapshot(root: Path) -> dict[str, str]:
    paths = {
        root / name for name in (
            "pyproject.toml", "CITATION.cff", "src/blastdesign_ai/__init__.py",
            "tests/test_public_api.py", "data/processed/public_api_contract.json",
        )
    }
    for directory, patterns in (
        ("data/processed", ("*.csv", "*.json")),
        ("notebooks", ("*.ipynb",)),
        ("outputs/figures", ("*.png", "*.svg")),
    ):
        for pattern in patterns:
            paths.update((root / directory).rglob(pattern))
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(paths) if path.is_file()
    }


def atomic_write(path: Path, data: bytes) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".rustan-source-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--diff", action="store_true", help="Print the planned text diff.")
    parser.add_argument("--test-count", type=int, help="Use only after the real complete suite passes.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.project_root.resolve()
    try:
        if args.test_count is not None and args.test_count != 241:
            raise ValueError("This reviewed update expects 241 tests after adding seven to 234; report a different real count for review.")
        if not (root / ".git").exists():
            raise ValueError("Save this helper in scripts/ inside the actual project Git checkout.")
        if not (root / "docs/LEGACY_OUTPUT_ARCHIVE.md").is_file():
            raise ValueError("This computer lacks the archive checkpoint. Fetch/Pull origin in GitHub Desktop first.")
        required = (
            "src/blastdesign/burden.py", "src/blastdesign/sensitivity.py",
            "docs/BURDEN_MODEL_PROVENANCE.md", "docs/API_COMPATIBILITY.md", "docs/PUBLIC_API_REFERENCE.md",
            "data/processed/public_api_contract.json", "README.md",
            "docs/burden_model_research_note.md", "CHANGELOG.md",
            "pyproject.toml", "CITATION.cff", "src/blastdesign_ai/__init__.py",
            "tests/test_public_api.py",
        )
        for name in required:
            path = root / name
            if not path.is_file() or path.is_symlink():
                raise ValueError("Expected a regular current project file: " + name)
        if "# Public API and compatibility policy" not in decode((root / "docs/API_COMPATIBILITY.md").read_bytes()):
            raise ValueError("Review the actual compatibility policy before applying this update.")
        protected = protected_snapshot(root)
        originals, planned = {}, {}

        def plan(name: str, transform=None, template: str | None = None):
            path = root / name
            if path.is_symlink():
                raise ValueError("Inspect the symlink before editing: " + name)
            raw = path.read_bytes() if path.exists() else None
            originals[name] = raw
            text = decode(raw or b"")
            if template is not None:
                if raw is not None and text != template:
                    raise ValueError("A new destination already contains different contents: " + name)
                value = template
            else:
                value = transform(text)
            data = encode(value, raw)
            if name.endswith(".py"):
                ast.parse(value, filename=name)
            if data != raw:
                planned[name] = data

        burden_name = "src/blastdesign/burden.py"
        burden_before = decode((root / burden_name).read_bytes())
        plan(burden_name, lambda text: patch_function(patch_function(text, "rustan_burden"), "rustan_applicability"))
        burden_after = decode(planned.get(burden_name, originals[burden_name]))
        if calculation_signature(burden_before, "rustan_burden") != calculation_signature(burden_after, "rustan_burden"):
            raise ValueError("The numerical Rustan calculation changed unexpectedly.")
        sensitivity_name = "src/blastdesign/sensitivity.py"
        sensitivity_before = decode((root / sensitivity_name).read_bytes())
        plan(sensitivity_name, lambda text: patch_function(text, "build_gole_gohar_diameter_sensitivity_table"))
        sensitivity_after = decode(planned.get(sensitivity_name, originals[sensitivity_name]))
        if calculation_signature(sensitivity_before, "build_gole_gohar_diameter_sensitivity_table", True) != calculation_signature(sensitivity_after, "build_gole_gohar_diameter_sensitivity_table", True):
            raise ValueError("Diameter calculations or comparison bounds changed unexpectedly.")
        plan("tests/test_rustan_source_range.py", template=TEST_SOURCE)
        plan("docs/RUSTAN_SOURCE_AUDIT.md", template=SOURCE_DOCUMENT)
        plan("docs/BURDEN_MODEL_PROVENANCE.md", patch_provenance)
        plan("docs/PUBLIC_API_REFERENCE.md", lambda text: add_review_block(text, API_BLOCK))
        plan("README.md", lambda text: add_review_block(clarify_old_prose(text), README_BLOCK, readme=True))
        plan("docs/burden_model_research_note.md", lambda text: add_review_block(clarify_old_prose(text), RESEARCH_BLOCK))
        plan("CHANGELOG.md", lambda text: changelog_entry(changelog_entry(text, "Fixed", FIXED_ENTRY), "Added", ADDED_ENTRY))
        if args.test_count is not None:
            for name in ("README.md", "docs/burden_model_research_note.md"):
                current = decode(planned.get(name, originals[name]))
                data = encode(update_test_counts(current, args.test_count), originals[name])
                if data != originals[name]:
                    planned[name] = data
                else:
                    planned.pop(name, None)
            name = "CHANGELOG.md"
            current = decode(planned.get(name, originals[name]))
            value = changelog_entry(current, "Changed", "- Updated the current documented test count to 241 after the complete suite passed.")
            data = encode(value, originals[name])
            if data != originals[name]:
                planned[name] = data
        if protected_snapshot(root) != protected:
            raise ValueError("A protected input changed during preparation; rerun after reviewing that edit.")
        for name in planned:
            print(("Would update: " if args.dry_run else "Planned: ") + name)
            if args.diff:
                print("".join(difflib.unified_diff(
                    decode(originals[name] or b"").splitlines(keepends=True),
                    decode(planned[name]).splitlines(keepends=True),
                    fromfile=name + " (before)", tofile=name + " (after)",
                )), end="")
        if args.dry_run:
            print("Dry run complete; no project files changed.")
            return 0
        if not planned:
            print("The reviewed Rustan source update is already installed; no files changed.")
            return 0
        backup = Path(tempfile.mkdtemp(prefix="blastdesign_rustan_backup_"))
        for name in planned:
            if originals[name] is not None:
                path = backup / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(originals[name])
        (backup / "new-files.json").write_text(json.dumps(
            [name for name in planned if originals[name] is None], indent=2,
        ), encoding="utf-8")
        print("Original-file backups: " + str(backup))
        written = []
        try:
            for name, data in planned.items():
                path = root / name
                current = path.read_bytes() if path.exists() else None
                if current != originals[name]:
                    raise ValueError("An input changed during preparation: " + name)
                if originals[name] is None:
                    with path.open("xb") as stream:
                        try:
                            stream.write(data)
                        except BaseException:
                            stream.close()
                            path.unlink(missing_ok=True)
                            raise
                else:
                    atomic_write(path, data)
                written.append(name)
            if protected_snapshot(root) != protected:
                raise ValueError("Research data, notebook, version, or API-baseline bytes changed during preparation.")
        except BaseException:
            for name in reversed(written):
                if originals[name] is None:
                    (root / name).unlink(missing_ok=True)
                else:
                    atomic_write(root / name, originals[name])
            raise
        for name in planned:
            print("Updated: " + name)
        print("Prepared seven Rustan regression tests. Run the focused tests, then the complete real suite.")
        print("Applicability range: 89–381 mm. Historical comparison grid: 181–311 mm.")
        print("Burden equations, saved research artifacts, versions, release dates, and API baseline are unchanged.")
        print("Update documented counts only after the full suite passes; stage inputs before regenerating checksums.")
        return 0
    except (OSError, UnicodeError, ValueError, SyntaxError) as error:
        print("Rustan source update stopped: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
