# Public API reference for v1.0.0

This reference records the v1.0 public interface. It is paired with
[the compatibility policy](API_COMPATIBILITY.md) and the saved machine-readable
baseline at `data/processed/public_api_contract.json`.

Type annotations are omitted here so interpreter-specific annotation formatting
does not define compatibility. Argument names, kinds, and defaults are recorded.

## blastdesign

- `blastdesign.DEFAULT_ASH_BURDEN_RATIO_GRID`: `[20.0, 22.5, 25.0, 27.5, 30.0, 32.5, 35.0, 37.5, 40.0]` (tuple).

- `blastdesign.DEFAULT_DIAMETER_GRID_MM`: `[181.0, 191.0, 201.0, 211.0, 221.0, 231.0, 241.0, 251.0, 261.0, 271.0, 281.0, 291.0, 301.0, 311.0]` (tuple).

- `blastdesign.DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3`: `[0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]` (tuple).

- `blastdesign.DEFAULT_ROCK_DENSITY_GRID_G_CM3`: `[1.8, 2.1, 2.4, 2.6, 2.75, 3.0, 3.3, 3.75, 4.0, 4.37, 4.8, 5.3]` (tuple).

- `blastdesign.DEFAULT_UCS_GRID_MPA`: `[40.0, 54.999, 55.0, 69.999, 70.0, 85.0, 110.0, 110.001, 180.0, 180.001, 220.0]` (tuple).

- `blastdesign.SCORE_COLUMNS`: `['theoretical_basis_score', 'independent_validation_score', 'input_observability_score', 'transferability_score', 'uncertainty_capability_score', 'reproducibility_score', 'decision_integration_score']` (list).

- `blastdesign.ash_burden(hole_diameter_mm, burden_ratio=25.0)`
  Existing direct import: `blastdesign.burden.ash_burden`.

- `blastdesign.assert_close(actual, expected, tolerance=1e-12)`
  Existing direct import: `blastdesign.validation.assert_close`.

- `blastdesign.bhandari_burden(hole_diameter_mm)`
  Existing direct import: `blastdesign.burden.bhandari_burden`.

- `blastdesign.build_ash_burden_ratio_ensemble_summary(sensitivity_table)`
  Existing direct import: `blastdesign.sensitivity.build_ash_burden_ratio_ensemble_summary`.

- `blastdesign.build_diameter_ensemble_summary(sensitivity_table)`
  Existing direct import: `blastdesign.sensitivity.build_diameter_ensemble_summary`.

- `blastdesign.build_explosive_density_ensemble_summary(sensitivity_table)`
  Existing direct import: `blastdesign.sensitivity.build_explosive_density_ensemble_summary`.

- `blastdesign.build_gole_gohar_ash_burden_ratio_sensitivity_table(ash_burden_ratios=None)`
  Existing direct import: `blastdesign.sensitivity.build_gole_gohar_ash_burden_ratio_sensitivity_table`.

- `blastdesign.build_gole_gohar_diameter_sensitivity_table(hole_diameters_mm=None)`
  Existing direct import: `blastdesign.sensitivity.build_gole_gohar_diameter_sensitivity_table`.

- `blastdesign.build_gole_gohar_explosive_density_sensitivity_table(explosive_densities_g_cm3=None)`
  Existing direct import: `blastdesign.sensitivity.build_gole_gohar_explosive_density_sensitivity_table`.

- `blastdesign.build_gole_gohar_joint_density_sensitivity_table(explosive_densities_g_cm3=None, rock_densities_g_cm3=None)`
  Existing direct import: `blastdesign.joint_density.build_gole_gohar_joint_density_sensitivity_table`.

- `blastdesign.build_gole_gohar_konya_density_elasticity_table(explosive_densities_g_cm3=None, rock_densities_g_cm3=None)`
  Existing direct import: `blastdesign.density_elasticity.build_gole_gohar_konya_density_elasticity_table`.

- `blastdesign.build_gole_gohar_rock_density_sensitivity_table(rock_densities_g_cm3=None)`
  Existing direct import: `blastdesign.sensitivity.build_gole_gohar_rock_density_sensitivity_table`.

- `blastdesign.build_gole_gohar_ucs_sensitivity_table(ucs_values_mpa=None)`
  Existing direct import: `blastdesign.sensitivity.build_gole_gohar_ucs_sensitivity_table`.

- `blastdesign.build_integrated_sensitivity_summary()`
  Existing direct import: `blastdesign.synthesis.build_integrated_sensitivity_summary`.

- `blastdesign.build_joint_density_ensemble_summary(sensitivity_table)`
  Existing direct import: `blastdesign.joint_density.build_joint_density_ensemble_summary`.

- `blastdesign.build_konya_density_elasticity_summary(hole_diameter_mm=None, explosive_density_g_cm3=None, rock_density_g_cm3=None)`
  Existing direct import: `blastdesign.density_elasticity.build_konya_density_elasticity_summary`.

- `blastdesign.build_model_ash_burden_ratio_response_summary(sensitivity_table, reference_ash_burden_ratio=25.0)`
  Existing direct import: `blastdesign.sensitivity.build_model_ash_burden_ratio_response_summary`.

- `blastdesign.build_model_diameter_response_summary(sensitivity_table, reference_diameter_mm=251.0)`
  Existing direct import: `blastdesign.sensitivity.build_model_diameter_response_summary`.

- `blastdesign.build_model_explosive_density_response_summary(sensitivity_table, reference_explosive_density_g_cm3=0.85)`
  Existing direct import: `blastdesign.sensitivity.build_model_explosive_density_response_summary`.

- `blastdesign.build_model_joint_density_response_summary(sensitivity_table, reference_explosive_density_g_cm3=None, reference_rock_density_g_cm3=None)`
  Existing direct import: `blastdesign.joint_density.build_model_joint_density_response_summary`.

- `blastdesign.build_model_parameter_dependency_matrix()`
  Existing direct import: `blastdesign.synthesis.build_model_parameter_dependency_matrix`.

- `blastdesign.build_model_registry()`
  Existing direct import: `blastdesign.registry.build_model_registry`.

- `blastdesign.build_model_rock_density_response_summary(sensitivity_table, reference_rock_density_g_cm3=4.37)`
  Existing direct import: `blastdesign.sensitivity.build_model_rock_density_response_summary`.

- `blastdesign.build_model_ucs_response_summary(sensitivity_table, reference_ucs_mpa=85.0)`
  Existing direct import: `blastdesign.sensitivity.build_model_ucs_response_summary`.

- `blastdesign.build_rock_density_ensemble_summary(sensitivity_table)`
  Existing direct import: `blastdesign.sensitivity.build_rock_density_ensemble_summary`.

- `blastdesign.build_ucs_ensemble_summary(sensitivity_table)`
  Existing direct import: `blastdesign.sensitivity.build_ucs_ensemble_summary`.

- `blastdesign.calculate_blast_metrics(bench_height_m, hole_diameter_mm, burden_m, spacing_m, subdrilling_m, stemming_m, explosive_density_kg_m3, number_of_holes)`
  Existing direct import: `blastdesign.core.calculate_blast_metrics`.

- `blastdesign.evaluate_conventional_burden_models(hole_diameter_mm, ucs_mpa, explosive_density_g_cm3, rock_density_g_cm3, explosive_type='ANFO', ash_burden_ratio=25.0)`
  Existing direct import: `blastdesign.comparison.evaluate_conventional_burden_models`.

- `blastdesign.gole_gohar_burden_results()`
  Existing direct import: `blastdesign.audit.gole_gohar_burden_results`.

- `blastdesign.gole_gohar_reference_inputs()`
  Existing direct import: `blastdesign.audit.gole_gohar_reference_inputs`.

- `blastdesign.konya_1972_burden(hole_diameter_mm, explosive_density_g_cm3, rock_density_g_cm3)`
  Existing direct import: `blastdesign.burden.konya_1972_burden`.

- `blastdesign.konya_1983_burden(hole_diameter_mm, explosive_density_g_cm3, rock_density_g_cm3)`
  Existing direct import: `blastdesign.burden.konya_1983_burden`.

- `blastdesign.lopez_jimeno_burden(hole_diameter_mm, ucs_mpa, explosive_type='ANFO')`
  Existing direct import: `blastdesign.burden.lopez_jimeno_burden`.

- `blastdesign.rustan_applicability(hole_diameter_mm)`
  Existing direct import: `blastdesign.burden.rustan_applicability`.

- `blastdesign.rustan_burden(hole_diameter_mm)`
  Existing direct import: `blastdesign.burden.rustan_burden`.

- `blastdesign.score_model(registry, model_id, theoretical_basis, independent_validation, input_observability, transferability, uncertainty_capability, reproducibility, decision_integration, evidence_notes, scoring_status='Provisional')`
  Existing direct import: `blastdesign.registry.score_model`.

- `blastdesign.tatiya_al_ajmi_burden(hole_diameter_mm, ucs_mpa, explosive_type='ANFO')`
  Existing direct import: `blastdesign.burden.tatiya_al_ajmi_burden`.

- `blastdesign.tatiya_al_ajmi_coefficients(ucs_mpa)`
  Existing direct import: `blastdesign.burden.tatiya_al_ajmi_coefficients`.

## blastdesign_ai

- `blastdesign_ai.build_burden_decision_report(model_table, scenario_table)`
  Existing direct import: `blastdesign_ai.decision_report.build_burden_decision_report`.

- `blastdesign_ai.validate_burden_decision_contract(report)`
  Existing direct import: `blastdesign_ai.decision_contract.validate_burden_decision_contract`.

## Default research DataFrame schemas

Column order and the recorded decision-gate metadata are part of this baseline.

### blastdesign.build_gole_gohar_diameter_sensitivity_table

```text
hole_diameter_mm
model_id
model_name
burden_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_diameter_ensemble_summary

```text
hole_diameter_mm
model_count
mean_burden_m
median_burden_m
minimum_burden_m
maximum_burden_m
range_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_model_diameter_response_summary

```text
model_id
model_name
lower_diameter_mm
upper_diameter_mm
burden_at_lower_endpoint_m
reference_diameter_mm
reference_burden_m
burden_at_upper_endpoint_m
endpoint_change_m
endpoint_change_percent
burden_range_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_gole_gohar_ucs_sensitivity_table

```text
ucs_mpa
model_id
model_name
burden_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_ucs_ensemble_summary

```text
ucs_mpa
model_count
mean_burden_m
median_burden_m
minimum_burden_m
maximum_burden_m
range_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_model_ucs_response_summary

```text
model_id
model_name
distinct_burden_count
responds_to_ucs
reference_ucs_mpa
reference_burden_m
minimum_burden_m
maximum_burden_m
burden_range_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_gole_gohar_explosive_density_sensitivity_table

```text
explosive_density_g_cm3
explosive_to_rock_density_ratio
model_id
model_name
burden_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_explosive_density_ensemble_summary

```text
explosive_density_g_cm3
explosive_to_rock_density_ratio
model_count
mean_burden_m
median_burden_m
minimum_burden_m
maximum_burden_m
range_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_model_explosive_density_response_summary

```text
model_id
model_name
distinct_burden_count
responds_to_explosive_density
lower_explosive_density_g_cm3
upper_explosive_density_g_cm3
burden_at_lower_endpoint_m
reference_explosive_density_g_cm3
reference_density_ratio
reference_burden_m
burden_at_upper_endpoint_m
endpoint_change_m
endpoint_change_percent
burden_range_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_gole_gohar_rock_density_sensitivity_table

```text
rock_density_g_cm3
explosive_to_rock_density_ratio
model_id
model_name
burden_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_rock_density_ensemble_summary

```text
rock_density_g_cm3
explosive_to_rock_density_ratio
model_count
mean_burden_m
median_burden_m
minimum_burden_m
maximum_burden_m
range_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_model_rock_density_response_summary

```text
model_id
model_name
distinct_burden_count
responds_to_rock_density
lower_rock_density_g_cm3
upper_rock_density_g_cm3
burden_at_lower_endpoint_m
reference_rock_density_g_cm3
reference_density_ratio
reference_burden_m
burden_at_upper_endpoint_m
endpoint_change_m
endpoint_change_percent
burden_range_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_gole_gohar_ash_burden_ratio_sensitivity_table

```text
ash_burden_ratio
model_id
model_name
burden_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_ash_burden_ratio_ensemble_summary

```text
ash_burden_ratio
model_count
mean_burden_m
median_burden_m
minimum_burden_m
maximum_burden_m
range_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_model_ash_burden_ratio_response_summary

```text
model_id
model_name
distinct_burden_count
responds_to_ash_burden_ratio
lower_ash_burden_ratio
upper_ash_burden_ratio
burden_at_lower_endpoint_m
reference_ash_burden_ratio
reference_burden_m
burden_at_upper_endpoint_m
endpoint_change_m
endpoint_change_percent
burden_range_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_gole_gohar_joint_density_sensitivity_table

```text
explosive_density_g_cm3
rock_density_g_cm3
explosive_to_rock_density_ratio
model_id
model_name
burden_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_joint_density_ensemble_summary

```text
explosive_density_g_cm3
rock_density_g_cm3
explosive_to_rock_density_ratio
model_count
mean_burden_m
median_burden_m
minimum_burden_m
maximum_burden_m
range_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_model_joint_density_response_summary

```text
model_id
model_name
distinct_burden_count
responds_to_joint_density_grid
reference_explosive_density_g_cm3
reference_rock_density_g_cm3
reference_density_ratio
reference_burden_m
minimum_sampled_density_ratio
maximum_sampled_density_ratio
burden_at_minimum_density_ratio_m
burden_at_maximum_density_ratio_m
ratio_endpoint_change_m
ratio_endpoint_change_percent
minimum_burden_m
maximum_burden_m
burden_range_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_integrated_sensitivity_summary

```text
analysis_id
parameter_name
parameter_label
unit
reference_value
sampled_minimum
sampled_maximum
sample_count
responding_model_count
responding_model_ids_json
reference_mean_burden_m
reference_range_m
minimum_ensemble_range_m
minimum_range_parameter_values_json
maximum_ensemble_range_m
maximum_range_parameter_values_json
ensemble_range_span_m
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_model_parameter_dependency_matrix

```text
model_id
model_name
hole_diameter_mm
ucs_mpa
explosive_density_g_cm3
rock_density_g_cm3
ash_burden_ratio
responsive_parameter_count
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_konya_density_elasticity_summary

```text
model_id
model_name
hole_diameter_mm
explosive_density_g_cm3
rock_density_g_cm3
explosive_to_rock_density_ratio
burden_m
explosive_density_elasticity
rock_density_elasticity
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.build_gole_gohar_konya_density_elasticity_table

```text
model_id
model_name
hole_diameter_mm
explosive_density_g_cm3
rock_density_g_cm3
explosive_to_rock_density_ratio
burden_m
explosive_density_elasticity
rock_density_elasticity
```

Decision gate: `RESEARCH_COMPARATOR_ONLY`.

### blastdesign.evaluate_conventional_burden_models

```text
model_id
model_name
burden_m
```

## Units and interpretation

- Fields ending in `_mm` use millimetres; `_mpa` uses MPa; `_g_cm3` uses g/cm3.
- Geometric burden and range fields ending in `_m` use metres.
- Fields ending in `_percent` use percent.
- Density ratios, the Ash burden ratio, and elasticities are dimensionless.
- The integrated-summary `unit` field identifies each varied parameter's unit.
- Counts, response flags, identifiers, and JSON list fields are not physical measurements.
- Low-level numerical outputs and model disagreement remain research comparisons.
