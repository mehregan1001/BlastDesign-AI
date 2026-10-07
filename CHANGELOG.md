# Changelog

All notable changes to BlastDesign-AI will be documented in this file.

## [Unreleased]

## [0.8.0] - 2026-10-08

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

## [0.7.0] - 2026-10-06

### Added

- Integrated synthesis of five deterministic one-factor sensitivity analyses.
- Cross-analysis summary of sampled ensemble ranges and responding-model counts.
- Seven-model by five-parameter numerical dependency matrix.
- Reproducible integrated-synthesis notebook, comparative figure, and version-controlled CSV artifacts.
- Automated structural and artifact-regression tests for the synthesis outputs.

### Changed

- Expanded the README and research note with integrated sensitivity findings and interpretation limitations.
- Increased the complete automated test suite from 123 to 135 passing tests.

### Research safeguards

- Explicitly prevents cross-grid results from being interpreted as a universal ranking of parameter importance.
- Distinguishes reconstructed equation dependencies from causal influence, predictive sensitivity, and field significance.
- Retains the `RESEARCH_COMPARATOR_ONLY` decision gate.

## [0.6.0] - 2026-09-28

### Added

- Controlled one-factor Ash burden-ratio sensitivity analysis across the currently implemented dimensionless interval from 20 to 40.
- Ash burden-ratio table validation, ensemble-disagreement summaries, and per-model response summaries.
- Reproducible Ash burden-ratio sensitivity notebook and comparative two-panel figure.
- Version-controlled Ash burden-ratio model-output, ensemble-summary, and model-response CSV artifacts.
- Automated tests covering grid validation, reference-scenario reproduction, linear Ash response, fixed-model behavior, summary calculations, research-safety metadata, and saved-artifact consistency.

### Changed

- Expanded the README and research note with Ash burden-ratio sensitivity findings, interpretation, limitations, and reproducible outputs.
- Increased the complete automated test suite from 96 to 123 passing tests.

### Research safeguards

- Treats the Ash burden ratio as an empirical equation coefficient rather than a probabilistically calibrated variable.
- Treats the implemented 20–40 interval as an analytical sampling constraint, not a universal calibration or operational range.
- - Documents why cross-grid results cannot establish a universal ranking of parameter importance.
- Retains the `RESEARCH_COMPARATOR_ONLY` decision gate and does not issue a field-ready burden recommendation.

## [0.5.0] - 2026-09-27

### Added

- Controlled one-factor rock-density sensitivity analysis over a broad exploratory grid from 1.80 to 5.30 g/cm³.
- Explicit explosive-to-rock density-ratio calculations for every sampled scenario.
- Rock-density table validation, ensemble-disagreement summaries, and per-model response summaries.
- Reproducible rock-density sensitivity notebook and comparative two-panel figure.
- Version-controlled rock-density model-output, ensemble-summary, and model-response CSV artifacts.
- Automated tests covering grid validation, reference-scenario reproduction, density-ratio calculations, responsive-model identification, monotonic Konya behavior, research-safety metadata, and saved-artifact consistency.

### Changed

- Expanded the README and research note with rock-density findings, geological context, measurement-basis safeguards, and reproducible outputs.
- Increased the complete automated test suite from 69 to 96 passing tests.

### Research safeguards

- Distinguishes mineral, grain, dry-bulk, saturated-bulk, loose-material, and in-situ rock-mass density.
- Treats the 1.80–5.30 g/cm³ grid as a broad exploratory computational interval rather than a universal geological or operational range.
- Retains the reconstructed 4.37 g/cm³ reference value while explicitly identifying its original measurement basis as requiring further provenance auditing.
- Identifies the minimum ensemble range as a plateau rather than an optimum rock density or blast-design condition.
- Retains the `RESEARCH_COMPARATOR_ONLY` decision gate.

## [0.4.0] - 2026-09-24

### Added

- Controlled one-factor explosive-density sensitivity analysis with explicit explosive-to-rock density ratios.
- Explosive-density ensemble-disagreement and per-model response summary metrics.
- Reproducible explosive-density sensitivity notebook and comparative figure.
- Version-controlled explosive-density model-output, ensemble-summary, and model-response CSV artifacts.
- Automated tests confirming that only the Konya 1972 and Konya 1983 equations respond to explosive density in the current seven-model comparison.
- Artifact-regression tests verifying that saved explosive-density results match regenerated calculations.

### Changed

- Expanded the research note and README with explosive-density sensitivity findings and limitations.
- Increased the complete automated test suite from 54 to 69 passing tests.

### Fixed

- Removed an unreachable duplicate UCS sensitivity-column declaration and normalized sensitivity-module spacing without changing numerical behavior.

## [0.3.0] - 2026-09-21

### Added

- Controlled one-factor UCS sensitivity analysis across documented empirical strength-class boundaries.
- UCS ensemble-disagreement and per-model response summary functions.
- Reproducible UCS sensitivity notebook with a research-safety interpretation.
- Version-controlled UCS model-output, ensemble-summary, and model-response CSV artifacts.
- Automated tests verifying UCS boundary behavior, summary calculations, and saved-artifact consistency.
- Deterministic SHA-256 checksum generation for reproducibility-critical source code, tests, notebooks, documentation, and research artifacts.

### Changed

- Expanded the research note and README with UCS sensitivity findings and limitations.
- Updated the documented automated-test count to 54 passing tests.

## [0.2.0] - 2026-09-16

### Added

- Centralized Gole Gohar reference-scenario inputs.
- Shared evaluator for the seven reconstructed conventional burden models.
- Controlled one-factor-at-a-time hole-diameter sensitivity analysis.
- Ensemble-level and model-level diameter-response summary functions.
- Reproducible Jupyter notebook and publication-quality sensitivity figure.
- Machine-readable model-output, ensemble-summary, and model-response CSV files.
- Automated verification that saved sensitivity artifacts match regenerated calculations.
- Detailed diameter-sensitivity research documentation.

### Changed

- Expanded the automated test suite from 21 to 39 tests.
- Updated the project overview with the diameter-sensitivity findings and limitations.

### Research safeguards

- Retains the `RESEARCH_COMPARATOR_ONLY` decision gate.
- Treats the calculated range as structural model disagreement, not a confidence interval.
- Does not identify an optimal diameter or issue an operational burden recommendation.

## [0.1.0] - 2026-09-02

### Added

- Python reconstruction of seven empirical burden-design models.
- Explicit model-applicability screening and evidence-tier classification.
- Comparative analysis of structural disagreement between burden equations.
- Evidence-aware burden decision-report builder.
- Research-use decision-contract validator.
- Command-line report validation through `blastdesign-validate`.
- Reusable and explicitly declared Python package interface.
- Detailed burden-model research note.
- Professional research-focused repository overview.
- Automated tests for model behavior, report construction, decision safeguards, command-line behavior, package metadata, and public API consistency.
- GitHub Actions testing across Python 3.10, 3.11, 3.12, 3.13, and 3.14.
- Research-software citation metadata.
- MIT software licence.

### Decision safeguards

- Enforces the `RESEARCH_COMPARATOR_ONLY` decision gate.
- Prevents unsupported operational burden recommendations.
- Distinguishes structural model disagreement from validated predictive uncertainty.

### Known research limitations

- No independent field validation.
- No site-specific empirical calibration.
- No trained machine-learning model.
- No probabilistically calibrated uncertainty model.
- No field-ready blasting recommendation.

[Unreleased]: https://github.com/mehregan1001/BlastDesign-AI/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/mehregan1001/BlastDesign-AI/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/mehregan1001/BlastDesign-AI/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/mehregan1001/BlastDesign-AI/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/mehregan1001/BlastDesign-AI/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/mehregan1001/BlastDesign-AI/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/mehregan1001/BlastDesign-AI/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/mehregan1001/BlastDesign-AI/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mehregan1001/BlastDesign-AI/releases/tag/v0.1.0