"""Model registry and provisional evidence-readiness scoring."""

from __future__ import annotations

import pandas as pd


SCORE_COLUMNS = [
    "theoretical_basis_score",
    "independent_validation_score",
    "input_observability_score",
    "transferability_score",
    "uncertainty_capability_score",
    "reproducibility_score",
    "decision_integration_score",
]


def build_model_registry() -> pd.DataFrame:
    """Create the 14-model registry used at the Step 24 checkpoint."""
    rows = [
        ("CONV_ASH", "Ash", "Conventional burden"),
        ("CONV_BHANDARI", "Bhandari", "Conventional burden"),
        ("CONV_JIMENO", "Lopez Jimeno", "Conventional burden"),
        ("CONV_KONYA_1972", "Konya 1972", "Conventional burden"),
        ("CONV_KONYA_1983", "Konya 1983", "Conventional burden"),
        ("CONV_RUSTAN", "Rustan", "Conventional burden"),
        ("CONV_TATIYA", "Tatiya", "Conventional burden"),
        ("FRAG_KUZRAM", "Kuz-Ram", "Fragmentation"),
        ("FRAG_SVEDEFO", "SVEDEFO", "Fragmentation"),
        ("VIB_SCALED_DISTANCE", "Scaled-distance model", "Ground vibration"),
        ("AIR_HUSTRULID", "Hustrulid", "Airblast"),
        ("AIR_BHANDARI", "Bhandari", "Airblast"),
        ("FLY_BENCH", "Ideal bench-blasting model", "Flyrock"),
        ("FLY_CRATER", "Crater-blasting model", "Flyrock"),
    ]
    registry = pd.DataFrame(rows, columns=["model_id", "model_name", "model_family"])
    for column in SCORE_COLUMNS:
        registry[column] = pd.NA
    registry["scoring_status"] = "Not scored"
    registry["evidence_notes"] = ""
    return registry


def score_model(
    registry: pd.DataFrame,
    model_id: str,
    theoretical_basis: int,
    independent_validation: int,
    input_observability: int,
    transferability: int,
    uncertainty_capability: int,
    reproducibility: int,
    decision_integration: int,
    evidence_notes: str,
    scoring_status: str = "Provisional",
) -> None:
    """Mutate one registry row with seven 0–3 evidence-readiness scores."""
    values = [
        theoretical_basis,
        independent_validation,
        input_observability,
        transferability,
        uncertainty_capability,
        reproducibility,
        decision_integration,
    ]
    if any((not isinstance(value, int)) or not 0 <= value <= 3 for value in values):
        raise ValueError("Every evidence-readiness score must be an integer from 0 to 3.")
    mask = registry["model_id"].eq(model_id)
    if mask.sum() != 1:
        raise ValueError(f"Exactly one registry row was expected for {model_id!r}.")
    registry.loc[mask, SCORE_COLUMNS] = values
    registry.loc[mask, "scoring_status"] = scoring_status
    registry.loc[mask, "evidence_notes"] = evidence_notes
