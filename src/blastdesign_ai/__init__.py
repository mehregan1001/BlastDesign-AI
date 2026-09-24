"""BlastDesign-AI: uncertainty-aware mining blast-model research tools."""

from .decision_contract import validate_burden_decision_contract
from .decision_report import build_burden_decision_report

__all__ = [
    "build_burden_decision_report",
    "validate_burden_decision_contract",
]

__version__ = "0.4.0"
