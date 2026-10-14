# Public API and compatibility policy

Starting with version 1.0.0, BlastDesign-AI commits to a documented software
interface for its reconstructed research comparator. Software-interface
stability does not establish independent field validation or operational
blast-design suitability.

## Supported interface

- Public exports declared by `blastdesign.__all__` and `blastdesign_ai.__all__`.
- Existing direct-import aliases listed in [the API reference](PUBLIC_API_REFERENCE.md).
- Documented argument names, positional/keyword kinds, and default values.
- Documented physical units, reference-scenario inputs, and default sampling grids.
- Column names and order for the recorded research DataFrame schemas.
- The existing `blastdesign-validate REPORT.json` command: zero exit status for
  successful validation and nonzero status for an invalid report or invocation.

The saved baseline is `data/processed/public_api_contract.json`. Three
compatibility tests compare it with the implementation. They do not regenerate
the baseline during a test run.

## Versioning commitments

- Patch releases contain compatible corrections. A numerical bug fix may alter
  computed values; the correction, affected outputs, and supporting reasoning
  must be documented, and dependent artifacts must be regenerated.
- Minor releases can add compatible functionality. Existing supported calls,
  units, and output schemas must retain their documented interpretation.
- Removing or renaming supported interfaces, changing required arguments, or
  making an incompatible unit/schema change requires a major release.
- Deprecations must be documented before removal.
- Published release tags and their recorded artifacts are not rewritten.

An intentional interface change requires reviewing the compatibility policy,
versioning impact, tests, reference, and saved baseline together. An unexpected
test failure is not resolved by automatically recapturing the baseline.

## What the baseline does not freeze

Private names beginning with `_`, internal code organisation, type-annotation
rendering, exact error-message text, incidental DataFrame attributes, pandas
storage dtypes, notebook execution counters, and figure bytes are outside this
interface contract. Documented direct-import aliases remain supported even if
implementation code is reorganised.

The baseline protects interfaces. Existing equation, decision-contract, and
saved-artifact tests protect numerical behaviour and research safeguards.
Passing software tests does not measure predictive accuracy against mine data.

## Installation and platform checks

`python scripts/check_wheel_installation.py` builds a normal wheel from a
temporary source copy, installs it with its declared dependencies into a fresh
virtual environment, checks package origins and metadata, runs the repository
suite against that wheel, and validates the saved research report with the
installed command-line entry point.

Release CI is configured for Linux on Python 3.10, 3.11, 3.12, 3.13, and 3.14,
plus Windows on Python 3.11. Review successful runs for the release commit;
configuration alone is not evidence that those environments passed. This
matrix does not test every allowed dependency combination or every future
Python release.

The wheel supplies the two Python packages and validator. Research notebooks,
saved CSV/JSON artifacts, figures, and documentation are obtained from the
source repository or release source archive.

## Reproducibility and research scope

Saved-artifact tests compare the recorded tables with regenerated calculations.
Retain units and interpretation metadata when exporting: CSV does not preserve
DataFrame attributes. Record Python and dependency versions when reproducing
research outputs. Re-run and save a modified notebook before committing its
outputs, and regenerate `CHECKSUMS.sha256` after the final file changes.

The existing `RESEARCH_COMPARATOR_ONLY` decision gate remains in force.
Structural model disagreement and local elasticities are deterministic
equation comparisons; they are not calibrated predictive uncertainty or
field-ready operational burden recommendations. No new field-validation
claim is introduced by the 1.0 software milestone.
