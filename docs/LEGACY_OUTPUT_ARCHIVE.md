# Legacy research-output archive

## Scope and status

This archive retains ten CSV checkpoints from the original seven-model burden
comparison. Their raw bytes are checked against `CHECKSUMS.sha256` in the published
`v1.0.0` release, whose commit is
`8e4991f4e24afd82666119d6f2f5616e5f1c9d86`.

The October 2026 cross-computer audit found six CSVs present locally but ignored
and untracked, and four absent. No history for these paths was found in the fetched
Git refs. The six surviving files matched the original hashes exactly. The four
absent files were reconstructed from reviewed notebook code on 2026-10-18; all four
reconstructed byte sequences also match the original release hashes exactly.

The recovery script preserves each matching existing file, restores only missing
files for which it carries a verified reconstruction, and prepares explicit Git
rules for all ten. The archive is published and backed up by Git only after these
files are staged, committed, and pushed. A checksum entry alone does not store data.

## Inventory

| File in `data/processed/` | Rows | Columns | Recovery action |
|---|---:|---:|---|
| `burden_aggregation_comparison_step_24_15.csv` | 4 | 6 | Retained original |
| `burden_applicability_ledger_step_24_16.csv` | 7 | 7 | Retained original |
| `burden_decision_readiness_step_24_20.csv` | 1 | 15 | Reconstructed |
| `burden_evidence_tiers_step_24_17.csv` | 7 | 10 | Reconstructed |
| `burden_leave_one_out_step_24_14.csv` | 7 | 10 | Retained original |
| `burden_results_step_24_11.csv` | 7 | 5 | Retained original |
| `burden_robust_spread_step_24_15.csv` | 1 | 7 | Retained original |
| `burden_screening_scenarios_step_24_17.csv` | 3 | 12 | Reconstructed |
| `burden_structural_uncertainty_step_24_18.csv` | 3 | 20 | Reconstructed |
| `model_registry_step_24_11.csv` | 14 | 12 | Retained original |

Row counts exclude the header. Original column order, row order, UTF-8 text,
full-precision numerical representations, quoted CSV fields, and CRLF endings
are retained. No original six-file payload is overwritten by the recovery script.

## Reconstruction method

The source is `notebooks/02_blastdesign_model_audit.ipynb`. Cell indices below are
zero-based, as reported by `scripts/audit_legacy_outputs.py`.

1. Cells 44 and 45 create the applicability ledger and join it to the seven-model
   Gole Gohar benchmark. The recreated ledger itself matches its original checksum.
2. Cell 50 loads that CSV through `pandas.read_csv`. This serialization/read step
   matters for faithfully reproducing the subsequent floating-point values.
3. Cell 52 assigns the historical evidence tiers and builds the three screening
   scenarios. It creates the evidence-tier and screening-scenario CSVs.
4. Cell 54 adds the structural-disagreement quantities and creates their CSV.
5. Cell 58 applies the research decision gate and creates the readiness CSV.

Only the reviewed calculations were used in the reconstruction. The notebook's
file-writing, plotting, and display statements were excluded from that local
reconstruction. Python 3.12.14, pandas 2.2.3, and NumPy 2.3.5 were used, with UTF-8
CSV serialization and explicit CRLF line terminators. The result was compared
against each independently recorded original hash, rather than accepting rounded
notebook displays as replacement data.

The installer embeds the four resulting byte-equivalent CSV payloads. Installation
uses the Python standard library and Git and does not execute notebook cells or
import the scientific package. This is a targeted recovery of historical artifacts,
not a live regeneration command for future scientific changes.

These hashes identify the exact UTF-8 code-cell source strings reviewed during
reconstruction; they identify code text, not a complete notebook-file checksum:

| Cell | SHA-256 of source string |
|---:|---|
| 44 | `61ce12f346c2eb8f07f53f7422f8c0346aaa2125491bb763e865c388aef2bfcb` |
| 45 | `11ffbb1939d51134341cb1bb7cce0afae1fb688f3e25f1e2d0aed3909d003869` |
| 50 | `722e9d82099d41618672706c3b28623271180b1339cab6512f2c2ff3c7ba1c7e` |
| 52 | `91867c33ef9dc574b4d3cdca0e7eb06cad1bca8a37c9662921522e94b659f965` |
| 54 | `fb057b546af26f32173ef1ce201d82c3a1cf355df41d67f3da231c1a57329f17` |
| 58 | `6542e4c481f85eb8b5a47b388a760ead4c60eb2d4c1c4db5aad1f58f3cc447f9` |

## Git storage and verification

`.gitignore` receives ten explicit file exceptions. `.gitattributes` receives
rules scoped to these same ten paths that disable text conversion, filters,
working-tree encoding conversion, and ident expansion. This preserves the original
CRLF byte sequences as stored Git blobs on both Windows and Linux. CSV text diffs
remain available. The scoped whitespace rule recognizes CR at the end of a line
while retaining the usual trailing-blank, final-blank-line, and space-before-tab
checks. No global Git settings are changed.

After reviewing and staging the intended archive/configuration files, run:

```text
python -B scripts/recover_legacy_csvs.py --check-staged
python scripts/generate_checksums.py
git add CHECKSUMS.sha256
python scripts/generate_checksums.py --check
git diff --cached --check
```

The first command checks both the working copies and the ten staged blob payloads
against the v1.0.0 hashes. The subsequent manifest covers the selected staged project
inputs under the [checksum policy](CHECKSUM_MANIFEST.md). A fresh checkout will
therefore carry the archive itself, not merely references to local files.

## Interpretation

These files are historical research outputs. Restoring the original bytes leaves
historical tier assignments, applicability wording, and legacy screening labels
intact. The later [burden-model provenance review](BURDEN_MODEL_PROVENANCE.md)
records unresolved source and domain questions separately. Historical labels do
not supersede that review.

Agreement with a historical checksum establishes byte identity. It does not supply
independent field validation, a calibrated uncertainty interval, an optimal burden,
or permission for an operational blasting recommendation. The decision-readiness
artifact retains `RESEARCH_COMPARATOR_ONLY`, no site calibration, zero independently
validated models, and `operational_recommendation_allowed=False`.

The published v1.0.0 tag, its manifest, package versions, release dates, model
equations, and public API baseline are unchanged by the archive preparation.

## Original reference digests

| File | Original SHA-256 |
|---|---|
| `burden_aggregation_comparison_step_24_15.csv` | `3209fef1192f84ebe05ad91202895353876d39ea103092e53c7ca735f54d657c` |
| `burden_applicability_ledger_step_24_16.csv` | `92840ff0ed30c9ee552b201b88ca60a2e03f6c5bf2ef9389d45e84b62916b805` |
| `burden_decision_readiness_step_24_20.csv` | `be16f5f2afc39e456e29055f8a914be18bfafdab8b77168ebf581bdc8df41016` |
| `burden_evidence_tiers_step_24_17.csv` | `c5a6323188904e40b7b400dbea8fb10d6588e9cc6ff78ebad491b321694249bf` |
| `burden_leave_one_out_step_24_14.csv` | `50add02b10708567b87d0b6a4bc2030dc6bec75517d5ad8d5027287a82642b85` |
| `burden_results_step_24_11.csv` | `eb61343a8ae654952e831e8a27b41e1eae96fddff4b5d97b608b5e5ea0db6550` |
| `burden_robust_spread_step_24_15.csv` | `7408a957711ad11f5b4ae5ddcbb26c0c1e1e73a416f99669fe596a15c244d476` |
| `burden_screening_scenarios_step_24_17.csv` | `696df43aee6a7d05b3a41a885e61d185d29e91307f33d98577b1f9b614ddfc76` |
| `burden_structural_uncertainty_step_24_18.csv` | `a7d96840eebb6128a142b3eb2f3b2e7c12b9590920cdc8bc3e2ad88d03b0ec2f` |
| `model_registry_step_24_11.csv` | `0adf8b2cda0b94c25e8a1893294e2d11a42321dbe594553a6c140324feb20f67` |
