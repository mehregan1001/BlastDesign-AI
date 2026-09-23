"""BlastDesign-AI reconstructed learning and research package."""

from .audit import (
    gole_gohar_burden_results,
    gole_gohar_reference_inputs,
)
from .burden import (
    ash_burden,
    bhandari_burden,
    konya_1972_burden,
    konya_1983_burden,
    lopez_jimeno_burden,
    rustan_applicability,
    rustan_burden,
    tatiya_al_ajmi_burden,
    tatiya_al_ajmi_coefficients,
)
from .comparison import (
    evaluate_conventional_burden_models,
)
from .core import calculate_blast_metrics
from .registry import (
    SCORE_COLUMNS,
    build_model_registry,
    score_model,
)
from .sensitivity import (
    DEFAULT_DIAMETER_GRID_MM,
    DEFAULT_UCS_GRID_MPA,
    build_diameter_ensemble_summary,
    build_gole_gohar_diameter_sensitivity_table,
    build_gole_gohar_ucs_sensitivity_table,
    build_model_diameter_response_summary,   
    build_model_ucs_response_summary,
    build_ucs_ensemble_summary,
    DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3,
    build_gole_gohar_explosive_density_sensitivity_table,
    build_explosive_density_ensemble_summary,
    build_model_explosive_density_response_summary,
)
from .validation import assert_close


__all__ = [
    "DEFAULT_DIAMETER_GRID_MM",
    "DEFAULT_UCS_GRID_MPA",
    "SCORE_COLUMNS",
    "ash_burden",
    "assert_close",
    "bhandari_burden",
    "build_diameter_ensemble_summary",
    "build_gole_gohar_diameter_sensitivity_table",
    "build_gole_gohar_ucs_sensitivity_table",
    "build_model_diameter_response_summary",
    "build_model_registry",
    "calculate_blast_metrics",
    "evaluate_conventional_burden_models",
    "gole_gohar_burden_results",
    "gole_gohar_reference_inputs",
    "konya_1972_burden",
    "konya_1983_burden",
    "lopez_jimeno_burden",
    "rustan_applicability",
    "rustan_burden",
    "score_model",
    "tatiya_al_ajmi_burden",
    "tatiya_al_ajmi_coefficients",
    "build_model_ucs_response_summary",
    "build_ucs_ensemble_summary",
    "DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3",
    "build_gole_gohar_explosive_density_sensitivity_table",
    "build_explosive_density_ensemble_summary",
    "build_model_explosive_density_response_summary",
]