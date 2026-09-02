# Changelog

All notable changes to BlastDesign-AI will be documented in this file.

## [Unreleased]

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

[Unreleased]: https://github.com/mehregan1001/BlastDesign-AI/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mehregan1001/BlastDesign-AI/releases/tag/v0.1.0