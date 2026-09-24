# BlastDesign-AI: Evidence-Aware Comparison of Legacy Mine-Blasting Burden Models

**Author:** Alireza Mehregan  
**Project:** BlastDesign-AI  
**Research stage:** Reproducible methodological reconstruction and comparative assessment  
**Software status:** Python package with 69 passing automated tests

## 1. Research background

BlastDesign-AI reconstructs and modernizes a legacy mine-blasting design program originally developed as part of an MSc thesis in mining engineering.

The original software integrated empirical and semi-empirical relationships describing blast geometry, fragmentation, ground vibration, airblast, and flyrock.

The current Python implementation begins by reassessing seven legacy burden-design relationships through transparent model registration, applicability screening, structural comparison, and explicit decision safeguards.

The original research did not provide an independently collected operational blast dataset. Therefore, the present results are interpreted as comparative research outputs rather than field-validated engineering recommendations.

## 2. Research question

When several historical burden-design equations are applied to the same reference blasting scenario, how much disagreement remains after accounting for documented implementation branches and model-applicability evidence?

A related question is whether a software system can prevent apparently precise numerical outputs from being misrepresented as validated blast-design recommendations.

## 3. Legacy burden models

The reconstructed model collection includes:

1. Ash.
2. Bhandari.
3. López Jimeno.
4. Konya, 1972.
5. Konya, 1983.
6. Rustan.
7. Tatiya–Al-Ajmi.

The reference scenario includes a 251 mm blasthole diameter, ANFO explosive conditions where applicable, and an 85 MPa rock-strength input for the relevant strength-dependent relationship.

This reference scenario is a reconstructed analytical example. It is not an independent field-validation dataset.

## 4. Evidence classification

Each model receives an applicability classification according to the evidence available for its implemented calculation branch.

| Evidence tier | Interpretation | Number of models |
|---|---|---:|
| A | Documented implementation branch matches the reference scenario. | 2 |
| B | Some applicable conditions are documented, but important domain information remains unresolved. | 2 |
| C | Broader applicability or calibration conditions remain unresolved. | 3 |

These evidence tiers describe implementation and applicability transparency. They do not establish independent predictive accuracy.

No model in the current comparison has been independently validated against a suitable site-specific blast dataset.

## 5. Individual burden estimates

| Model | Evidence tier | Estimated burden, m |
|---|---|---:|
| Ash | B | 6.275000 |
| Bhandari | C | 6.874000 |
| López Jimeno | A | 5.773000 |
| Konya, 1972 | C | 5.527324 |
| Konya, 1983 | C | 5.689716 |
| Rustan | A | 6.983189 |
| Tatiya–Al-Ajmi | B | 5.839370 |

## 6. Evidence-conditioned comparison

Three screening scenarios were evaluated:

| Scenario | Models | Mean burden, m | Median burden, m | Population standard deviation, m | Burden range, m |
|---|---:|---:|---:|---:|---:|
| All legacy models | 7 | 6.137371 | 5.839370 | 0.543940 | 1.455865 |
| Audited and partially documented models | 4 | 6.217640 | 6.057185 | 0.482221 | 1.210189 |
| Audited implementation branches only | 2 | 6.378094 | 6.378094 | 0.605094 | 1.210189 |

Restricting the comparison to the two audited implementation branches increases the mean burden by approximately 0.240723 m, or 3.922%, relative to the full seven-model comparison.

However, the audited-only scenario still produces a burden range of approximately 1.210 m.

## 7. Main scientific finding

Applicability screening changes the composition and central tendency of the model ensemble, but substantial disagreement remains even between the two models with documented implementation-branch matches.

This remaining spread represents structural disagreement between empirical equations.

It must not be interpreted as:

- A statistical confidence interval.
- A probabilistic uncertainty bound.
- Evidence of predictive accuracy.
- A validated site-specific design recommendation.

Distinguishing structural model disagreement from validated predictive uncertainty is essential when historical engineering formulas are incorporated into modern decision-support software.

## 8. Decision-safety mechanism

Because independent site-specific validation is unavailable, the software enforces the following decision state:

```text
Decision gate: RESEARCH_COMPARATOR_ONLY
Output mode: COMPARATIVE_RANGE_WITH_EVIDENCE_WARNING
Recommended burden: None
```

The system therefore permits transparent comparison while preventing an unsupported final engineering recommendation.

## 9. Reproducibility and software quality

The project currently includes:

- - Reusable burden-model and sensitivity-analysis code under `src/blastdesign`.
- Evidence-aware decision-report and validation code under `src/blastdesign_ai`.
- Reconstructed burden-model implementations.
- An evidence-aware burden decision-report builder.
- A reusable decision-contract validator.
- An explicitly defined package interface.
- Automated tests covering model behavior, report construction, decision safeguards, and public API consistency.
- A complete automated test suite containing 69 passing tests.
- Version-controlled source code and research outputs.

The automated checks include safeguards against unsupported recommendations, duplicated model identifiers, inconsistent numerical ranges, missing model information, and unsupported validation claims.

## 10. Limitations

The present research stage does not include:

- Independently collected mine-blast measurements.
- Site-specific empirical calibration.
- External predictive validation.
- A trained machine-learning model.
- A probabilistically calibrated uncertainty model.
- A field-ready burden recommendation.

These limitations are explicitly documented and enforced within the software decision logic.

## 11. Future research directions

Potential extensions include:

1. Reconstructing additional fragmentation, vibration, airblast, and flyrock relationships from the legacy BlastDesign framework.
2. Incorporating peer-reviewed post-2010 developments in blast design and predictive modeling.
3. Performing systematic parameter-sensitivity and scenario analyses.
4. Integrating traceable operational datasets when suitable observations become available.
5. Comparing interpretable statistical or machine-learning models against empirical baselines.
6. Introducing calibrated predictive uncertainty only when supported by adequate validation data.
7. Developing constrained, multi-objective mining-engineering decision-support workflows.

The underlying methodological principles—model provenance, applicability checks, uncertainty-aware comparison, explicit decision safeguards, and reproducible testing—may also transfer to other mining-engineering problems, including adaptive underground stope dimensioning.

Such transfer would require its own domain-specific models, geotechnical inputs, and validation evidence.

## 12. Current conclusion

BlastDesign-AI demonstrates that historical mine-blasting relationships can be reconstructed within a transparent and testable Python research framework.

The present comparison identifies persistent structural disagreement among burden equations and demonstrates an explicit software mechanism for preventing unsupported design recommendations when independent validation evidence is unavailable.

## 13. Controlled UCS sensitivity analysis

A deterministic one-factor sensitivity analysis was performed for uniaxial compressive strength (UCS). Hole diameter, explosive density, rock density, explosive type, and other reference inputs were held constant at the reconstructed Gole Gohar scenario values.

The sampled grid deliberately includes values immediately below, at, and immediately above the documented empirical classification boundaries.

| UCS interval, MPa | López Jimeno burden, m | Tatiya–Al-Ajmi burden, m | Seven-model range, m |
|---|---:|---:|---:|
| UCS < 55 | 7.028 | 6.940860 | 1.500676 |
| 55 ≤ UCS < 70 | 7.028 | 5.839370 | 1.500676 |
| 70 ≤ UCS ≤ 110 | 5.773 | 5.839370 | 1.455865 |
| 110 < UCS ≤ 180 | 5.773 | 5.089080 | 1.894109 |
| UCS > 180 | 5.271 | 5.089080 | 1.894109 |

Only two of the seven reconstructed equations respond to UCS:

- López Jimeno changes at 70 MPa and immediately above 180 MPa.
- Tatiya–Al-Ajmi changes at 55 MPa and immediately above 110 MPa.
- Ash, Bhandari, Konya 1972, Konya 1983, and Rustan remain constant because UCS is not an explicit input to their reconstructed equations.

The abrupt numerical changes reflect discrete empirical strength-class rules. They must not be interpreted as abrupt physical changes in rock behavior.

The largest sampled seven-model range is approximately **1.894 m**, occurring immediately above the Tatiya–Al-Ajmi 110 MPa boundary. At the reference UCS of **85 MPa**, the analysis reproduces the established seven-model range of approximately **1.456 m**.

This is a deterministic model-structure sensitivity analysis. It does not provide:

- A calibrated prediction interval.
- A statistical confidence interval.
- Evidence that one model is more accurate.
- A site-specific operational burden recommendation.

The reproducible analysis is available in:

```text
notebooks/ucs_sensitivity_comparison.ipynb
```

Its version-controlled numerical artifacts are:

```text
data/processed/ucs_sensitivity_model_outputs.csv
data/processed/ucs_sensitivity_ensemble_summary.csv
data/processed/ucs_sensitivity_model_response_summary.csv
```

Automated artifact-consistency tests verify that these saved CSV files match results regenerated directly from the current implementation.

The decision state remains:

```text
Decision gate: RESEARCH_COMPARATOR_ONLY
Recommended burden: None
```

## Controlled explosive-density sensitivity analysis

A deterministic one-factor sensitivity analysis was performed for explosive density. Hole diameter, rock density, UCS, explosive type, and all other inputs were held constant at the reconstructed Gole Gohar reference values.

Explosive density was sampled from **0.70 to 1.00 g/cm³** in increments of **0.05 g/cm³**. The reference value is **0.85 g/cm³**. This grid is an exploratory analytical range and must not be interpreted as a recommended operational explosive-density range.

Only two reconstructed equations respond explicitly to explosive density:

- Konya 1972.
- Konya 1983.

Ash, Bhandari, López Jimeno, Rustan, and Tatiya–Al-Ajmi remain constant because explosive density is not an explicit input to their reconstructed equations.

Selected results are:

| Explosive density, g/cm³ | Konya 1972 burden, m | Konya 1983 burden, m | Seven-model range, m |
|---:|---:|---:|---:|
| 0.70 | 5.184287 | 5.482943 | 1.798902 |
| 0.85 | 5.527324 | 5.689716 | 1.455865 |
| 1.00 | 5.831854 | 5.896490 | 1.210189 |

Across the sampled endpoints:

- The Konya 1972 burden increases by approximately **0.648 m**.
- The Konya 1983 burden increases by approximately **0.414 m**.
- The seven-model burden range decreases from approximately **1.799 m** to **1.210 m**.
- The reference density reproduces the established seven-model range of approximately **1.456 m**.

The reduction in ensemble range does not demonstrate improved predictive accuracy. It occurs because two equations respond to explosive density while the remaining five are unchanged, and because the identities of the limiting models can change across the sampled grid.

These results represent deterministic model-structure sensitivity. They do not provide:

- A calibrated prediction interval.
- A statistical confidence interval.
- Evidence that either Konya equation is more accurate.
- A recommended explosive product or density.
- A site-specific operational burden recommendation.

The reproducible analysis is available in:

```text
notebooks/explosive_density_sensitivity_comparison.ipynb