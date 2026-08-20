"""Build software-facing BlastDesign-AI burden reports."""
def build_burden_decision_report(
    model_table,
    scenario_table,
):
    required_model_columns = {
        "model_id",
        "model_name",
        "burden_m",
        "evidence_tier",
        "audit_domain_status",
        "independent_validation_established",
    }

    missing_model_columns = required_model_columns.difference(
        model_table.columns
    )

    if missing_model_columns:
        raise ValueError(
            "Missing model-table columns: "
            f"{sorted(missing_model_columns)}"
        )

    required_scenario_ids = {
        "ALL_LEGACY_COMPARATOR",
        "AUDITED_PLUS_PARTIAL",
        "AUDITED_ONLY",
    }

    observed_scenario_ids = set(
        scenario_table["scenario_id"]
    )

    missing_scenarios = required_scenario_ids.difference(
        observed_scenario_ids
    )

    if missing_scenarios:
        raise ValueError(
            f"Missing scenarios: {sorted(missing_scenarios)}"
        )

    scenario_lookup = (
        scenario_table
        .set_index("scenario_id")
    )

    validated_model_count = int(
        model_table[
            "independent_validation_established"
        ].sum()
    )

    if validated_model_count != 0:
        raise ValueError(
            "Step 24.21 expects zero independently validated "
            "models under the current evidence audit."
        )

    def scenario_record(scenario_id):
        row = scenario_lookup.loc[scenario_id]

        return {
            "model_count": int(row["model_count"]),
            "mean_burden_m": round(
                float(row["mean_burden_m"]),
                6,
            ),
            "median_burden_m": round(
                float(row["median_burden_m"]),
                6,
            ),
            "minimum_burden_m": round(
                float(row["minimum_burden_m"]),
                6,
            ),
            "maximum_burden_m": round(
                float(row["maximum_burden_m"]),
                6,
            ),
            "range_m": round(
                float(row["range_m"]),
                6,
            ),
        }

    model_outputs = []

    for _, row in (
        model_table
        .sort_values("burden_m")
        .iterrows()
    ):
        model_outputs.append(
            {
                "model_id": str(row["model_id"]),
                "model_name": str(row["model_name"]),
                "burden_m": round(
                    float(row["burden_m"]),
                    6,
                ),
                "evidence_tier": str(
                    row["evidence_tier"]
                ),
                "audit_domain_status": str(
                    row["audit_domain_status"]
                ),
                "independently_validated": bool(
                    row[
                        "independent_validation_established"
                    ]
                ),
            }
        )

    return {
        "schema_version": "1.0",
        "module": "conventional_burden_comparison",
        "decision": {
            "decision_gate": "RESEARCH_COMPARATOR_ONLY",
            "software_output_mode": (
                "COMPARATIVE_RANGE_WITH_EVIDENCE_WARNING"
            ),
            "recommended_burden_m": None,
            "site_calibration_required": True,
            "independently_validated_model_count": (
                validated_model_count
            ),
        },
        "scenario_summaries": {
            "all_legacy_models": scenario_record(
                "ALL_LEGACY_COMPARATOR"
            ),
            "audited_plus_partial": scenario_record(
                "AUDITED_PLUS_PARTIAL"
            ),
            "audited_only": scenario_record(
                "AUDITED_ONLY"
            ),
        },
        "model_outputs": model_outputs,
        "warnings": [
            (
                "No independently validated burden model was "
                "established in the present audit."
            ),
            (
                "Reported ranges represent deterministic "
                "model-form variation, not confidence intervals."
            ),
            (
                "Site-specific calibration and validation are "
                "required before operational use."
            ),
            (
                "No model output or ensemble statistic should be "
                "presented as a validated design burden."
            ),
        ],
    }

