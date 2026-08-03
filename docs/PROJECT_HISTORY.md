# Reconstructed project history

## Purpose

BlastDesign-AI combines three objectives:

1. learn Python, scientific programming, data science and applied AI;
2. reconstruct the MSc-era Visual Basic BlastDesign software;
3. produce auditable and potentially publishable mining-engineering research.

## Scientific foundation

The legacy software was not merely a collection of averaged burden formulas.
Its central contribution was deterministic inverse blast design:

- begin with desired fragmentation;
- derive a compatible blast geometry;
- evaluate ground vibration, airblast and flyrock;
- revise the design to respect technical, safety and environmental limits.

The modern research direction is uncertainty-aware, constrained,
multi-objective inverse design. Legacy and modern modes must remain distinct.

## Reconstructed learning progression

- Created the Windows/Conda/Jupyter project and `mining-ai` environment.
- Learned notebook execution, variables, units, functions and DataFrames.
- Implemented blast geometry, explosive mass, rock volume and powder factor.
- Created a 14-row model registry covering conventional burden,
  fragmentation, vibration, airblast and flyrock.
- Added a provisional seven-category evidence-readiness scorecard.
- Audited seven conventional burden methods:
  Ash; Bhandari and Vutukuri; López Jimeno; Konya 1972; Konya 1983;
  Rustan; Tatiya–Al-Ajmi.
- Reproduced the Gole-Gohar thesis benchmarks.

## Current checkpoint

**Step 24.11 is complete.**

The next task is Step 24.12: compare all seven burden predictions and interpret
their spread as model-form disagreement rather than a 68%/95% confidence
interval.
