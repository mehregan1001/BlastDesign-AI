"""Restore four checksum-verified legacy CSVs and prepare all ten for Git.

Run from scripts/ with --dry-run first. Default mode prepares local files only.
After explicitly staging the archive, --check-staged verifies its stored bytes.
No notebook is executed; no package versions, equations, tags or dates change.
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
import tempfile


# Filled from the independently recorded v1.0.0 manifest and the reviewed notebook.
EXPECTED = {
    "burden_aggregation_comparison_step_24_15.csv": "3209fef1192f84ebe05ad91202895353876d39ea103092e53c7ca735f54d657c",
    "burden_applicability_ledger_step_24_16.csv": "92840ff0ed30c9ee552b201b88ca60a2e03f6c5bf2ef9389d45e84b62916b805",
    "burden_decision_readiness_step_24_20.csv": "be16f5f2afc39e456e29055f8a914be18bfafdab8b77168ebf581bdc8df41016",
    "burden_evidence_tiers_step_24_17.csv": "c5a6323188904e40b7b400dbea8fb10d6588e9cc6ff78ebad491b321694249bf",
    "burden_leave_one_out_step_24_14.csv": "50add02b10708567b87d0b6a4bc2030dc6bec75517d5ad8d5027287a82642b85",
    "burden_results_step_24_11.csv": "eb61343a8ae654952e831e8a27b41e1eae96fddff4b5d97b608b5e5ea0db6550",
    "burden_robust_spread_step_24_15.csv": "7408a957711ad11f5b4ae5ddcbb26c0c1e1e73a416f99669fe596a15c244d476",
    "burden_screening_scenarios_step_24_17.csv": "696df43aee6a7d05b3a41a885e61d185d29e91307f33d98577b1f9b614ddfc76",
    "burden_structural_uncertainty_step_24_18.csv": "a7d96840eebb6128a142b3eb2f3b2e7c12b9590920cdc8bc3e2ad88d03b0ec2f",
    "model_registry_step_24_11.csv": "0adf8b2cda0b94c25e8a1893294e2d11a42321dbe594553a6c140324feb20f67"
}
SHAPES = {
    "burden_aggregation_comparison_step_24_15.csv": [
        4,
        6
    ],
    "burden_applicability_ledger_step_24_16.csv": [
        7,
        7
    ],
    "burden_decision_readiness_step_24_20.csv": [
        1,
        15
    ],
    "burden_evidence_tiers_step_24_17.csv": [
        7,
        10
    ],
    "burden_leave_one_out_step_24_14.csv": [
        7,
        10
    ],
    "burden_results_step_24_11.csv": [
        7,
        5
    ],
    "burden_robust_spread_step_24_15.csv": [
        1,
        7
    ],
    "burden_screening_scenarios_step_24_17.csv": [
        3,
        12
    ],
    "burden_structural_uncertainty_step_24_18.csv": [
        3,
        20
    ],
    "model_registry_step_24_11.csv": [
        14,
        12
    ]
}
RECOVERED_TEXT = {
    "burden_decision_readiness_step_24_20.csv": "benchmark_hole_diameter_mm,benchmark_ucs_mpa,benchmark_explosive,audited_model_count,partial_model_count,unresolved_model_count,independently_validated_model_count,minimum_validated_models_required,site_calibration_available,audited_model_range_m,operational_recommendation_allowed,decision_status,software_output_mode,blocking_reasons,warning_reasons\n251.0,85.0,ANFO,2,2,3,0,1,False,1.210188559264405,False,RESEARCH_COMPARATOR_ONLY,COMPARATIVE_RANGE_WITH_EVIDENCE_WARNING,NO_INDEPENDENTLY_VALIDATED_MODEL; NO_SITE_CALIBRATION_DATA,UNRESOLVED_MODEL_APPLICABILITY_DOMAINS; STRUCTURAL_DISAGREEMENT_REMAINS\n",
    "burden_evidence_tiers_step_24_17.csv": "model_id,model_name,burden_m,audit_domain_status,known_conditions_checked,unresolved_evidence,independent_validation_status,evidence_tier,tier_description,independent_validation_established\nCONV_ASH,Ash,6.275,PARTIAL_BRANCH_MATCH,Burden ratio 25 is inside implemented range 20–40,Primary calibration domain and independent field validation remain unresolved,Not established,B,Partial implementation/domain match,False\nCONV_BHANDARI,Bhandari,6.874,DOMAIN_UNRESOLVED,Positive 251 mm hole diameter,\"Diameter, geology and calibration limits are not yet verified from a primary source\",Not established,C,Applicability domain unresolved,False\nCONV_JIMENO,Lopez Jimeno,5.773,AUDITED_BRANCH_MATCH,251 mm is above 180 mm; ANFO large-hole branch; UCS 85 MPa,Independent predictive validation remains unresolved,Not established,A,Audited implementation-branch match,False\nCONV_KONYA_1972,Konya 1972,5.5273236163425565,DOMAIN_UNRESOLVED,Positive diameter and positive explosive and rock densities,Original calibration and applicability limits remain unresolved,Not established,C,Applicability domain unresolved,False\nCONV_KONYA_1983,Konya 1983,5.689716247139588,DOMAIN_UNRESOLVED,Positive diameter and positive explosive and rock densities,Original calibration and applicability limits remain unresolved,Not established,C,Applicability domain unresolved,False\nCONV_RUSTAN,Rustan,6.983188559264405,AUDITED_BRANCH_MATCH,251 mm is inside documented 89–311 mm range,Independent predictive validation remains unresolved,Not established,A,Audited implementation-branch match,False\nCONV_TATIYA,Tatiya–Al-Ajmi,5.839369999999999,PARTIAL_BRANCH_MATCH,ANFO coefficients; UCS 85 MPa is inside the 55–110 MPa branch,Diameter and broader calibration-domain limits remain unresolved,Not established,B,Partial implementation/domain match,False\n",
    "burden_screening_scenarios_step_24_17.csv": "scenario_id,scenario_description,included_tiers,model_count,model_ids,mean_burden_m,median_burden_m,population_sd_m,minimum_burden_m,maximum_burden_m,range_m,independently_validated_model_count\nALL_LEGACY_COMPARATOR,Unfiltered seven-model legacy comparator,A+B+C,7,\"CONV_ASH, CONV_BHANDARI, CONV_JIMENO, CONV_KONYA_1972, CONV_KONYA_1983, CONV_RUSTAN, CONV_TATIYA\",6.137371203249507,5.839369999999999,0.5439399623579156,5.5273236163425565,6.983188559264405,1.4558649429218482,0\nAUDITED_PLUS_PARTIAL,Models with audited or partial branch matches,A+B,4,\"CONV_ASH, CONV_JIMENO, CONV_RUSTAN, CONV_TATIYA\",6.217639639816101,6.057185,0.48222082303942665,5.773,6.983188559264405,1.210188559264405,0\nAUDITED_ONLY,Models with audited implementation-branch matches,A,2,\"CONV_JIMENO, CONV_RUSTAN\",6.378094279632203,6.378094279632203,0.6050942796322025,5.773,6.983188559264405,1.210188559264405,0\n",
    "burden_structural_uncertainty_step_24_18.csv": "scenario_id,scenario_description,included_tiers,model_count,model_ids,mean_burden_m,median_burden_m,population_sd_m,minimum_burden_m,maximum_burden_m,range_m,independently_validated_model_count,mean_shift_from_legacy_m,mean_shift_from_legacy_percent,median_shift_from_legacy_m,lower_deviation_from_mean_m,upper_deviation_from_mean_m,relative_range_percent,coefficient_of_variation_percent,evidence_state\nALL_LEGACY_COMPARATOR,Unfiltered seven-model legacy comparator,A+B+C,7,\"CONV_ASH, CONV_BHANDARI, CONV_JIMENO, CONV_KONYA_1972, CONV_KONYA_1983, CONV_RUSTAN, CONV_TATIYA\",6.137371203249507,5.839369999999999,0.5439399623579156,5.5273236163425565,6.983188559264405,1.4558649429218482,0,0.0,0.0,0.0,0.6100475869069504,0.8458173560148978,23.721311530758033,8.862751564870639,SITE_CALIBRATION_AND_VALIDATION_REQUIRED\nAUDITED_PLUS_PARTIAL,Models with audited or partial branch matches,A+B,4,\"CONV_ASH, CONV_JIMENO, CONV_RUSTAN, CONV_TATIYA\",6.217639639816101,6.057185,0.48222082303942665,5.773,6.983188559264405,1.210188559264405,0,0.08026843656659377,1.3078634794664963,0.21781500000000076,0.444639639816101,0.765548919448304,19.463793808741848,7.75568947340424,SITE_CALIBRATION_AND_VALIDATION_REQUIRED\nAUDITED_ONLY,Models with audited implementation-branch matches,A,2,\"CONV_JIMENO, CONV_RUSTAN\",6.378094279632203,6.378094279632203,0.6050942796322025,5.773,6.983188559264405,1.210188559264405,0,0.24072307638269574,3.922250559901639,0.5387242796322038,0.605094279632203,0.6050942796322021,18.97414033419072,9.48707016709536,SITE_CALIBRATION_AND_VALIDATION_REQUIRED\n"
}
ARCHIVE_DOCUMENT = "# Legacy research-output archive\n\n## Scope and status\n\nThis archive retains ten CSV checkpoints from the original seven-model burden\ncomparison. Their raw bytes are checked against `CHECKSUMS.sha256` in the published\n`v1.0.0` release, whose commit is\n`8e4991f4e24afd82666119d6f2f5616e5f1c9d86`.\n\nThe October 2026 cross-computer audit found six CSVs present locally but ignored\nand untracked, and four absent. No history for these paths was found in the fetched\nGit refs. The six surviving files matched the original hashes exactly. The four\nabsent files were reconstructed from reviewed notebook code on 2026-10-18; all four\nreconstructed byte sequences also match the original release hashes exactly.\n\nThe recovery script preserves each matching existing file, restores only missing\nfiles for which it carries a verified reconstruction, and prepares explicit Git\nrules for all ten. The archive is published and backed up by Git only after these\nfiles are staged, committed, and pushed. A checksum entry alone does not store data.\n\n## Inventory\n\n| File in `data/processed/` | Rows | Columns | Recovery action |\n|---|---:|---:|---|\n| `burden_aggregation_comparison_step_24_15.csv` | 4 | 6 | Retained original |\n| `burden_applicability_ledger_step_24_16.csv` | 7 | 7 | Retained original |\n| `burden_decision_readiness_step_24_20.csv` | 1 | 15 | Reconstructed |\n| `burden_evidence_tiers_step_24_17.csv` | 7 | 10 | Reconstructed |\n| `burden_leave_one_out_step_24_14.csv` | 7 | 10 | Retained original |\n| `burden_results_step_24_11.csv` | 7 | 5 | Retained original |\n| `burden_robust_spread_step_24_15.csv` | 1 | 7 | Retained original |\n| `burden_screening_scenarios_step_24_17.csv` | 3 | 12 | Reconstructed |\n| `burden_structural_uncertainty_step_24_18.csv` | 3 | 20 | Reconstructed |\n| `model_registry_step_24_11.csv` | 14 | 12 | Retained original |\n\nRow counts exclude the header. Original column order, row order, UTF-8 text,\nfull-precision numerical representations, quoted CSV fields, and CRLF endings\nare retained. No original six-file payload is overwritten by the recovery script.\n\n## Reconstruction method\n\nThe source is `notebooks/02_blastdesign_model_audit.ipynb`. Cell indices below are\nzero-based, as reported by `scripts/audit_legacy_outputs.py`.\n\n1. Cells 44 and 45 create the applicability ledger and join it to the seven-model\n   Gole Gohar benchmark. The recreated ledger itself matches its original checksum.\n2. Cell 50 loads that CSV through `pandas.read_csv`. This serialization/read step\n   matters for faithfully reproducing the subsequent floating-point values.\n3. Cell 52 assigns the historical evidence tiers and builds the three screening\n   scenarios. It creates the evidence-tier and screening-scenario CSVs.\n4. Cell 54 adds the structural-disagreement quantities and creates their CSV.\n5. Cell 58 applies the research decision gate and creates the readiness CSV.\n\nOnly the reviewed calculations were used in the reconstruction. The notebook's\nfile-writing, plotting, and display statements were excluded from that local\nreconstruction. Python 3.12.14, pandas 2.2.3, and NumPy 2.3.5 were used, with UTF-8\nCSV serialization and explicit CRLF line terminators. The result was compared\nagainst each independently recorded original hash, rather than accepting rounded\nnotebook displays as replacement data.\n\nThe installer embeds the four resulting byte-equivalent CSV payloads. Installation\nuses the Python standard library and Git and does not execute notebook cells or\nimport the scientific package. This is a targeted recovery of historical artifacts,\nnot a live regeneration command for future scientific changes.\n\nThese hashes identify the exact UTF-8 code-cell source strings reviewed during\nreconstruction; they identify code text, not a complete notebook-file checksum:\n\n| Cell | SHA-256 of source string |\n|---:|---|\n| 44 | `61ce12f346c2eb8f07f53f7422f8c0346aaa2125491bb763e865c388aef2bfcb` |\n| 45 | `11ffbb1939d51134341cb1bb7cce0afae1fb688f3e25f1e2d0aed3909d003869` |\n| 50 | `722e9d82099d41618672706c3b28623271180b1339cab6512f2c2ff3c7ba1c7e` |\n| 52 | `91867c33ef9dc574b4d3cdca0e7eb06cad1bca8a37c9662921522e94b659f965` |\n| 54 | `fb057b546af26f32173ef1ce201d82c3a1cf355df41d67f3da231c1a57329f17` |\n| 58 | `6542e4c481f85eb8b5a47b388a760ead4c60eb2d4c1c4db5aad1f58f3cc447f9` |\n\n## Git storage and verification\n\n`.gitignore` receives ten explicit file exceptions. `.gitattributes` receives\nrules scoped to these same ten paths that disable text conversion, filters,\nworking-tree encoding conversion, and ident expansion. This preserves the original\nCRLF byte sequences as stored Git blobs on both Windows and Linux. CSV text diffs\nremain available. The scoped whitespace rule recognizes CR at the end of a line\nwhile retaining the usual trailing-blank, final-blank-line, and space-before-tab\nchecks. No global Git settings are changed.\n\nAfter reviewing and staging the intended archive/configuration files, run:\n\n```text\npython -B scripts/recover_legacy_csvs.py --check-staged\npython scripts/generate_checksums.py\ngit add CHECKSUMS.sha256\npython scripts/generate_checksums.py --check\ngit diff --cached --check\n```\n\nThe first command checks both the working copies and the ten staged blob payloads\nagainst the v1.0.0 hashes. The subsequent manifest covers the selected staged project\ninputs under the [checksum policy](CHECKSUM_MANIFEST.md). A fresh checkout will\ntherefore carry the archive itself, not merely references to local files.\n\n## Interpretation\n\nThese files are historical research outputs. Restoring the original bytes leaves\nhistorical tier assignments, applicability wording, and legacy screening labels\nintact. The later [burden-model provenance review](BURDEN_MODEL_PROVENANCE.md)\nrecords unresolved source and domain questions separately. Historical labels do\nnot supersede that review.\n\nAgreement with a historical checksum establishes byte identity. It does not supply\nindependent field validation, a calibrated uncertainty interval, an optimal burden,\nor permission for an operational blasting recommendation. The decision-readiness\nartifact retains `RESEARCH_COMPARATOR_ONLY`, no site calibration, zero independently\nvalidated models, and `operational_recommendation_allowed=False`.\n\nThe published v1.0.0 tag, its manifest, package versions, release dates, model\nequations, and public API baseline are unchanged by the archive preparation.\n\n## Original reference digests\n\n| File | Original SHA-256 |\n|---|---|\n| `burden_aggregation_comparison_step_24_15.csv` | `3209fef1192f84ebe05ad91202895353876d39ea103092e53c7ca735f54d657c` |\n| `burden_applicability_ledger_step_24_16.csv` | `92840ff0ed30c9ee552b201b88ca60a2e03f6c5bf2ef9389d45e84b62916b805` |\n| `burden_decision_readiness_step_24_20.csv` | `be16f5f2afc39e456e29055f8a914be18bfafdab8b77168ebf581bdc8df41016` |\n| `burden_evidence_tiers_step_24_17.csv` | `c5a6323188904e40b7b400dbea8fb10d6588e9cc6ff78ebad491b321694249bf` |\n| `burden_leave_one_out_step_24_14.csv` | `50add02b10708567b87d0b6a4bc2030dc6bec75517d5ad8d5027287a82642b85` |\n| `burden_results_step_24_11.csv` | `eb61343a8ae654952e831e8a27b41e1eae96fddff4b5d97b608b5e5ea0db6550` |\n| `burden_robust_spread_step_24_15.csv` | `7408a957711ad11f5b4ae5ddcbb26c0c1e1e73a416f99669fe596a15c244d476` |\n| `burden_screening_scenarios_step_24_17.csv` | `696df43aee6a7d05b3a41a885e61d185d29e91307f33d98577b1f9b614ddfc76` |\n| `burden_structural_uncertainty_step_24_18.csv` | `a7d96840eebb6128a142b3eb2f3b2e7c12b9590920cdc8bc3e2ad88d03b0ec2f` |\n| `model_registry_step_24_11.csv` | `0adf8b2cda0b94c25e8a1893294e2d11a42321dbe594553a6c140324feb20f67` |\n"

STATUS_SECTION = """<!-- BEGIN LEGACY CSV RECOVERY STATUS -->
## Legacy CSV archive recovery

The four missing CSVs listed above were reconstructed from reviewed code in
`notebooks/02_blastdesign_model_audit.ipynb`. Each reconstructed file matches its
original v1.0.0 SHA-256 exactly. The six surviving local CSVs were retained after
the same original-manifest check. See [Legacy research-output archive](LEGACY_OUTPUT_ARCHIVE.md)
for the ten-file inventory, reconstruction method, and interpretation limits.

These ten historical CSVs have explicit `.gitignore` exceptions and path-specific
`.gitattributes` rules preserving their original stored bytes, including CRLF.
`scripts/recover_legacy_csvs.py --check-staged` verifies the staged copies against
the original hashes. They enter the current manifest after being staged and after
normal checksum generation. The published v1.0.0 tag and manifest stay unchanged.
<!-- END LEGACY CSV RECOVERY STATUS -->
"""
CHANGELOG_ENTRY = (
    "- Recovered four historical burden-analysis CSVs with exact v1.0.0 checksum "
    "matches and prepared all ten legacy outputs for version-controlled archival "
    "with their original bytes preserved."
)
ATTRIBUTES = {
    "text": "unset", "filter": "unset", "working-tree-encoding": "unset", "ident": "unset",
    "whitespace": "blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol",
}


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
                (local / "GitHubDesktop").glob("app-*/resources/app/git/cmd/git.exe"), reverse=True,
            ))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise ValueError("Git was not found. Run in a terminal with Git available.")


def run_git(git: str, root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [git, "--no-pager", "-C", str(root), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"},
    )


def git_bytes(git: str, root: Path, *args: str) -> bytes:
    result = run_git(git, root, *args)
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_text(data: bytes) -> str:
    text = data.decode("utf-8-sig")
    if "\r" in text.replace("\r\n", ""):
        raise ValueError("Unexpected bare-CR line endings in a configuration/documentation file.")
    return text.replace("\r\n", "\n")


def encode_text(text: str, original: bytes | None) -> bytes:
    raw = original or b""
    newline = "\r\n" if b"\r\n" in raw else "\n"
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.replace("\n", newline).encode("utf-8")


def append_block(text: str, title: str, lines: list[str]) -> str:
    begin, end = f"# BEGIN {title}", f"# END {title}"
    block = "\n".join([begin, *lines, end])
    if begin in text or end in text:
        if text.count(begin) != 1 or text.count(end) != 1:
            raise ValueError(f"Ambiguous existing configuration markers: {title}")
        found = text[text.index(begin):text.index(end) + len(end)]
        if found != block:
            raise ValueError(f"Existing archive rules differ; inspect before updating: {title}")
        return text
    return text.rstrip("\n") + ("\n\n" if text else "") + block + "\n"


def add_changelog_entry(text: str) -> str:
    marker = "## [Unreleased]"
    if text.count(marker) != 1:
        raise ValueError("Expected one Unreleased changelog section.")
    start = text.index(marker) + len(marker)
    next_section = re.search(r"(?m)^## ", text[start:])
    end = start + next_section.start() if next_section else len(text)
    section = text[start:end]
    if CHANGELOG_ENTRY in section:
        return text
    header = "### Fixed"
    if header in section:
        if section.count(header) != 1:
            raise ValueError("Expected at most one Fixed heading under Unreleased.")
        position = section.index(header) + len(header)
        section = section[:position] + "\n\n" + CHANGELOG_ENTRY + section[position:]
    else:
        section = section.rstrip("\n") + "\n\n### Fixed\n\n" + CHANGELOG_ENTRY + "\n\n"
    return text[:start] + section + text[end:]


def add_policy_status(text: str) -> str:
    begin = "<!-- BEGIN LEGACY CSV RECOVERY STATUS -->"
    end = "<!-- END LEGACY CSV RECOVERY STATUS -->"
    if begin in text or end in text:
        if text.count(begin) != 1 or text.count(end) != 1:
            raise ValueError("Ambiguous legacy-recovery status markers in checksum policy.")
        existing = text[text.index(begin):text.index(end) + len(end)]
        if existing != STATUS_SECTION.rstrip("\n"):
            raise ValueError("Existing legacy-recovery status differs from the reviewed version.")
        return text
    anchor = "## Implementation references"
    if text.count(anchor) != 1:
        raise ValueError("Expected the reviewed checksum-policy reference section.")
    return text.replace(anchor, STATUS_SECTION + "\n" + anchor, 1)


def verify_csv(name: str, data: bytes) -> None:
    if digest(data) != EXPECTED[name]:
        raise ValueError(f"Original v1.0.0 checksum mismatch: {name}; no replacement is allowed.")
    rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig"), newline=""), strict=True))
    shape = [len(rows) - 1, len(rows[0]) if rows else 0]
    if shape != SHAPES[name] or any(len(row) != shape[1] for row in rows):
        raise ValueError(f"Unexpected archive CSV shape: {name}")


def check_attributes(git: str, root: Path, paths: list[str], cached: bool = False) -> None:
    options = ["check-attr"] + (["--cached"] if cached else [])
    raw = git_bytes(git, root, *options, "-z", *ATTRIBUTES, "--", *paths).split(b"\0")
    records = raw[:-1] if raw and raw[-1] == b"" else raw
    if len(records) != 3 * len(paths) * len(ATTRIBUTES):
        raise ValueError("Unexpected Git attribute inventory.")
    for index in range(0, len(records), 3):
        path, attribute, value = (part.decode("utf-8") for part in records[index:index + 3])
        if value != ATTRIBUTES[attribute]:
            raise ValueError(f"Another Git attributes file overrides the archive rule: {path}: {attribute}={value}")


def atomic_write(path: Path, data: bytes, replace: bool = True) -> None:
    if not replace:
        # Exclusive creation prevents overwriting an archive that appeared meanwhile.
        with path.open("xb") as stream:
            try:
                stream.write(data)
            except BaseException:
                stream.close()
                path.unlink(missing_ok=True)
                raise
        return
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".legacy-archive-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--check-staged", action="store_true")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        root = args.project_root.resolve()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            if os.environ.get(key):
                raise ValueError(f"Unset {key} before preparing the archive.")
        for relative in ("pyproject.toml", ".gitignore", "CHANGELOG.md", "docs/CHECKSUM_MANIFEST.md"):
            if not (root / relative).is_file():
                raise ValueError("Expected the current project checkout. Missing: " + relative)
        git = find_git()
        actual = Path(os.fsdecode(git_bytes(git, root, "rev-parse", "--show-toplevel").rstrip(b"\r\n"))).resolve()
        if actual != root:
            raise ValueError("The requested directory is not the Git checkout root.")
        release = git_bytes(git, root, "show", "v1.0.0:CHECKSUMS.sha256").decode("utf-8-sig")
        reference = {}
        for line in release.splitlines():
            if not line:
                continue
            match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
            if not match or match[2] in reference:
                raise ValueError("Invalid or duplicate entry in the published release manifest.")
            reference[match[2]] = match[1]
        paths = ["data/processed/" + name for name in EXPECTED]
        for name, relative in zip(EXPECTED, paths):
            if reference.get(relative) != EXPECTED[name]:
                raise ValueError("The published baseline differs from the reviewed record: " + relative)

        planned, originals = {}, {}
        for name, relative in zip(EXPECTED, paths):
            path = root / relative
            if path.is_symlink() or not path.parent.is_dir() or path.parent.resolve() != root / "data/processed":
                raise ValueError("Inspect archive path/directory before restoration: " + relative)
            original = path.read_bytes() if path.exists() else None
            if original is not None:
                verify_csv(name, original)
                print("Verified original: " + name)
            elif args.check_staged or name not in RECOVERED_TEXT:
                raise ValueError("A retained original is missing; recover its source copy first: " + name)
            else:
                payload = RECOVERED_TEXT[name].replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
                verify_csv(name, payload)
                originals[relative] = None
                planned[relative] = payload

        if args.check_staged:
            check_attributes(git, root, paths, cached=True)
            for name, relative in zip(EXPECTED, paths):
                staged = git_bytes(git, root, "show", ":" + relative)
                verify_csv(name, staged)
            print("Staged legacy archive PASSED: all 10 stored blobs match v1.0.0 exactly.")
            return 0

        texts = {}
        for relative in (".gitignore", ".gitattributes", "CHANGELOG.md", "docs/CHECKSUM_MANIFEST.md", "docs/LEGACY_OUTPUT_ARCHIVE.md"):
            path = root / relative
            if path.is_symlink():
                raise ValueError("Inspect symlink before editing: " + relative)
            original = path.read_bytes() if path.exists() else None
            originals[relative] = original
            texts[relative] = decode_text(original or b"")
        texts[".gitignore"] = append_block(
            texts[".gitignore"], "LEGACY CSV ARCHIVE v1.0.0", ["!" + name for name in paths],
        )
        attributes = "-text -filter -working-tree-encoding -ident whitespace=" + ATTRIBUTES["whitespace"]
        texts[".gitattributes"] = append_block(
            texts[".gitattributes"], "LEGACY CSV ARCHIVE v1.0.0", [name + " " + attributes for name in paths],
        )
        texts["CHANGELOG.md"] = add_changelog_entry(texts["CHANGELOG.md"])
        texts["docs/CHECKSUM_MANIFEST.md"] = add_policy_status(texts["docs/CHECKSUM_MANIFEST.md"])
        if texts["docs/LEGACY_OUTPUT_ARCHIVE.md"] and texts["docs/LEGACY_OUTPUT_ARCHIVE.md"] != ARCHIVE_DOCUMENT:
            raise ValueError("The existing archive document differs; inspect it before replacement.")
        texts["docs/LEGACY_OUTPUT_ARCHIVE.md"] = ARCHIVE_DOCUMENT
        for relative, text in texts.items():
            data = encode_text(text, originals[relative])
            if data != originals[relative]:
                planned[relative] = data
        for relative in planned:
            print(("Would update: " if args.dry_run else "Planned: ") + relative)
        if args.dry_run:
            print("Dry run complete. No project files or Git state changed.")
            return 0
        if not planned:
            check_attributes(git, root, paths)
            print("All 10 original CSVs and archive rules are already in place.")
            return 0

        backup = Path(tempfile.mkdtemp(prefix="blastdesign_legacy_archive_backup_"))
        for relative in planned:
            if originals[relative] is not None:
                target = backup / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(originals[relative])
        (backup / "new-files.json").write_text(json.dumps(
            [name for name in planned if originals[name] is None], indent=2,
        ), encoding="utf-8")
        print("Original-file backups: " + str(backup))
        written = []
        try:
            for relative, data in planned.items():
                target = root / relative
                current = target.read_bytes() if target.exists() else None
                if current != originals[relative]:
                    raise ValueError("An input changed during preparation; rerun after review: " + relative)
                atomic_write(target, data, replace=originals[relative] is not None)
                written.append(relative)
            check_attributes(git, root, paths)
            for relative in paths:
                ignored = run_git(git, root, "check-ignore", "--no-index", "--quiet", "--", relative)
                if ignored.returncode != 1:
                    raise ValueError("An ignore rule still blocks the archive; inspect: " + relative)
                verify_csv(Path(relative).name, (root / relative).read_bytes())
        except BaseException:
            for relative in reversed(written):
                if originals[relative] is None:
                    (root / relative).unlink(missing_ok=True)
                else:
                    atomic_write(root / relative, originals[relative])
            raise
        for relative in planned:
            print("Updated: " + relative)
        print("Recovery verified: all 10 local CSVs match the v1.0.0 hashes exactly.")
        print("The six retained originals were not overwritten. Review and stage intended files next.")
        print("After staging, use --check-staged; then regenerate, stage, and check CHECKSUMS.sha256.")
        return 0
    except (OSError, ValueError, UnicodeError, csv.Error, subprocess.SubprocessError) as error:
        print("Legacy archive preparation stopped: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
