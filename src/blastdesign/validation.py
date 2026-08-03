"""Small validation helpers used throughout BlastDesign-AI."""

from __future__ import annotations

import math


def positive_float(value, name: str) -> float:
    """Return *value* as a finite positive float."""
    if isinstance(value, bool):
        raise TypeError(f"{name} must be numeric, not Boolean.")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise TypeError(f"{name} must be numeric.") from None
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{name} must be finite and greater than zero.")
    return number


def assert_close(actual: float, expected: float, tolerance: float = 1e-12) -> None:
    """Raise AssertionError when two floating-point values differ materially."""
    if not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError(f"Expected {expected}, but obtained {actual}")
