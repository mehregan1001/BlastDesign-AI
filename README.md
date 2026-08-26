# BlastDesign-AI

## Status note: Preliminary public research prototype (alpha).
BlastDesign-AI is under active development and has not been validated for operational or safety-critical blasting decisions. The current repository is published to document the project concept, initial computational work and planned development.

BlastDesign-AI builds on the author’s MSc research and the original BlastDesign engineering model for drilling-and-blasting design under technical, safety and environmental constraints. The present project aims to extend that work with Python-based data analysis and machine-learning methods.


### Evidence-aware reconstruction and modernization of legacy mine-blasting design software

BlastDesign-AI is a Python research project that reconstructs and modernizes a mine-blasting design program originally developed during an MSc research project in mining engineering at Imam Khomeini International University, Iran.

The original BlastDesign software integrated empirical and semi-empirical models describing blast geometry, rock fragmentation, ground vibration, airblast, and flyrock.

The current project reassesses these legacy relationships using transparent Python implementations, model-applicability screening, structural uncertainty analysis, explicit decision safeguards, and automated software testing.

> **Current research status:** Comparative research framework only. No site-specific operational design recommendation is issued without independent calibration and validation.

## Research motivation

Historical blasting formulas frequently produce different results for the same design inputs. Averaging those outputs without checking their assumptions, applicability, or supporting evidence can create a misleading impression of certainty.

BlastDesign-AI addresses this problem by asking:

1. Which empirical relationships can be reconstructed reproducibly?
2. Which calculation branches are demonstrably applicable to a specified scenario?
3. How much disagreement remains between alternative models?
4. Can decision-support software prevent unsupported engineering recommendations when validation evidence is insufficient?

## Current implementation

The first completed research component examines seven burden-design models:

- Ash.
- Bhandari.
- López Jimeno.
- Konya, 1972.
- Konya, 1983.
- Rustan.
- Tatiya–Al-Ajmi.

Each relationship is assessed using documented implementation conditions and assigned an evidence tier:

| Tier | Meaning | Models |
|---|---|---:|
| A | Documented implementation branch matches the reference scenario. | 2 |
| B | Some applicability conditions are documented, but important evidence remains incomplete. | 2 |
| C | Important applicability or calibration conditions remain unresolved. | 3 |

Evidence tiers indicate the transparency of implementation and applicability checks. They do not establish independent predictive accuracy.

## Initial research finding

For the reconstructed reference scenario, the burden estimates are:

| Model | Tier | Burden, m |
|---|---|---:|
| Ash | B | 6.275 |
| Bhandari | C | 6.874 |
| López Jimeno | A | 5.773 |
| Konya, 1972 | C | 5.527 |
| Konya, 1983 | C | 5.690 |
| Rustan | A | 6.983 |
| Tatiya–Al-Ajmi | B | 5.839 |

Screening the models by available applicability evidence produces:

| Comparison scenario | Models | Mean burden, m | Burden range, m |
|---|---:|---:|---:|
| All legacy models | 7 | 6.137 | 1.456 |
| Audited and partially documented models | 4 | 6.218 | 1.210 |
| Audited implementation branches only | 2 | 6.378 | 1.210 |

The two audited model branches still disagree by approximately **1.210 m**.

This disagreement represents structural differences between empirical equations. It is not a confidence interval, a calibrated uncertainty estimate, or evidence that either result is correct for a particular mine.

## Decision safeguards

Because independent site-specific validation is not available, the software enforces:

```text
Decision gate: RESEARCH_COMPARATOR_ONLY
Output mode: COMPARATIVE_RANGE_WITH_EVIDENCE_WARNING
Recommended burden: None
```

These safeguards prevent a comparative research result from being misrepresented as an operational blasting recommendation.

## Software structure

Important project components include:

```text
docs/burden_model_research_note.md
src/blastdesign_ai/__init__.py
src/blastdesign_ai/__main__.py
src/blastdesign_ai/decision_contract.py
src/blastdesign_ai/decision_report.py
tests/test_burden.py
tests/test_core.py
tests/test_decision_contract.py
tests/test_decision_report.py
tests/test_public_api.py
tests/test_cli.py
```

The software includes:

- Reusable burden decision-report construction.
- Explicit decision-contract validation.
- A documented public Python package interface.
- A command-line report validator.
- Automated checks for unsupported recommendations and inconsistent model outputs.
- A full test suite with **21 passing tests**.

## Run the automated tests

From Anaconda Prompt on Windows:

```bat
conda activate mining-ai
cd /d F:\Projects\BlastDesign-AI
python -m pytest -v
```

Expected result:

```text
21 passed
```

## Validate the research decision report

From the project root:

```bat
blastdesign-validate data\processed\burden_decision_report_step_24_21.json
```

Expected output:

```text
Contract validation: PASSED
Decision policy: research-comparator safeguards enforced
```

## Research limitations

The current project does not claim:

- Independent field validation.
- Site-specific calibration.
- A field-ready blasting recommendation.
- A trained machine-learning model.
- A probabilistically calibrated uncertainty estimate.

The absence of independent operational data is treated as an explicit methodological limitation rather than concealed behind apparently precise numerical outputs.

## Planned development

Future research directions include:

1. Expanding the reconstruction to fragmentation, ground vibration, airblast, and flyrock.
2. Reviewing relevant post-2010 developments in empirical and data-driven blast modeling.
3. Performing systematic sensitivity and scenario analyses.
4. Integrating traceable operational datasets when available.
5. Comparing interpretable machine-learning methods against empirical baselines.
6. Introducing uncertainty calibration only when supported by appropriate validation data.
7. Developing transparent multi-objective mining-engineering decision-support workflows.

The general methodological approach—model provenance, applicability screening, structural disagreement, explicit uncertainty, and decision safeguards—may also be relevant to other mining-engineering problems, including adaptive underground stope dimensioning.

Any extension to stope design would require separate geotechnical models, domain-specific inputs, and independent validation.

## Additional research documentation

See:

```text
docs/burden_model_research_note.md
```

for the detailed research background, evidence classification, numerical results, methodological limitations, and future development directions.

## Author

**Alireza Mehregan**

Mining engineer and research engineer working on computational mining, empirical model reconstruction, uncertainty-aware engineering analysis, and the integration of Python-based data science into mining research.

## Copyright Information
Copyright © 2026 Alireza Mehregan. All rights reserved. Licensing terms will be added in a later project release.