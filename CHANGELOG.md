# Changelog

All notable changes to BlastDesign-AI will be documented in this file.

## [Unreleased]
### Fixed

- Removed an unreachable duplicate UCS sensitivity-column declaration and normalized sensitivity-module spacing without changing numerical behavior.
## [0.3.0] - 2026-09-21

### Added

- Controlled one-factor UCS sensitivity analysis across documented empirical strength-class boundaries.
- UCS ensemble-disagreement and per-model response summary functions.
- Reproducible UCS sensitivity notebook with a research-safety interpretation.
- Version-controlled UCS model-output, ensemble-summary, and model-response CSV artifacts.
- Automated tests verifying UCS boundary behavior, summary calculations, and saved-artifact consistency.
- - Deterministic SHA-256 checksum generation for reproducibility-critical source code, tests, notebooks, documentation, and research artifacts.

### Changed

- Expanded the research note and README with UCS sensitivity findings and limitations.
- Increased the complete automated test suite to 54 passing tests.
### Added

- Controlled one-factor UCS sensitivity analysis across documented empirical strength-class boundaries.
- UCS ensemble-disagreement and per-model response summary functions.
- Reproducible UCS sensitivity notebook with a research-safety interpretation.
- Version-controlled UCS model-output, ensemble-summary, and model-response CSV artifacts.
- Automated tests verifying UCS boundary behavior, summary calculations, and saved-artifact consistency.

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
- Automated tests for model behavior, report construction, decision safeguards,
  command-line behavior, package metadata, and public API consistency.
- GitHub Actions testing across Python 3.10, 3.11, 3.12, 3.13, and 3.14.
- Research-software citation metadata.
- MIT software licence.

### Decision safeguards

- Enforces the `RESEARCH_COMPARATOR_ONLY` decision gate.
- Prevents unsupported operational burden recommendations.
- Distinguishes structural model disagreement from validated predictive
  uncertainty.

### Known research limitations

- No independent field validation.
- No site-specific empirical calibration.
- No trained machine-learning model.
- No probabilistically calibrated uncertainty model.
- No field-ready blasting recommendation.

[Unreleased]: https://github.com/mehregan1001/BlastDesign-AI/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/mehregan1001/BlastDesign-AI/compare/v0.3.0...v0.3.0