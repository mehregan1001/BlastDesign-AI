"""Audited conventional burden relationships from legacy BlastDesign.

These functions reproduce the equations used in the MSc-era software.  They
are engineering models, not field-validated design recommendations.  Modern
mode will later add applicability filtering, uncertainty and calibration.
"""

from __future__ import annotations

from .validation import positive_float


def ash_burden(hole_diameter_mm, burden_ratio=25.0) -> float:
    """Ash: B = K_B d, with d converted from millimetres to metres."""
    diameter_m = positive_float(hole_diameter_mm, "hole_diameter_mm") / 1000.0
    ratio = positive_float(burden_ratio, "burden_ratio")
    if not 20 <= ratio <= 40:
        raise ValueError("Ash burden_ratio must be between 20 and 40.")
    return ratio * diameter_m


def bhandari_burden(hole_diameter_mm) -> float:
    """Bhandari and Vutukuri: B = 24d + 0.85, with d and B in metres."""
    diameter_m = positive_float(hole_diameter_mm, "hole_diameter_mm") / 1000.0
    return 24.0 * diameter_m + 0.85


def lopez_jimeno_burden(
    hole_diameter_mm,
    ucs_mpa,
    explosive_type="ANFO",
) -> float:
    """Piecewise López Jimeno burden tables for small and large holes."""
    diameter_mm = positive_float(hole_diameter_mm, "hole_diameter_mm")
    ucs = positive_float(ucs_mpa, "ucs_mpa")
    diameter_m = diameter_mm / 1000.0

    if diameter_mm <= 165:
        if ucs < 70:
            factor = 39.0
        elif ucs <= 120:
            factor = 37.0
        elif ucs <= 180:
            factor = 35.0
        else:
            factor = 33.0
        return factor * diameter_m

    if diameter_mm <= 180:
        raise ValueError(
            "López Jimeno documents small holes through 165 mm and large "
            "holes above 180 mm; 165–180 mm is an unsupported gap."
        )

    if not isinstance(explosive_type, str):
        raise TypeError("explosive_type must be a string.")
    explosive = explosive_type.strip().upper().replace("-", "")
    if explosive == "ANFO":
        factors = (28.0, 23.0, 21.0)
    elif explosive in {"EMULSION", "WATERGEL", "WATER GEL"}:
        factors = (38.0, 32.0, 30.0)
    else:
        raise ValueError("Large-hole table supports ANFO, emulsion or watergel.")

    if ucs < 70:
        factor = factors[0]
    elif ucs <= 180:
        factor = factors[1]
    else:
        factor = factors[2]
    return factor * diameter_m


def konya_1972_burden(
    hole_diameter_mm,
    explosive_density_g_cm3,
    rock_density_g_cm3,
) -> float:
    """Metric Konya (1972): B = 37.8 d (rho_e/rho_r)^0.33."""
    diameter_m = positive_float(hole_diameter_mm, "hole_diameter_mm") / 1000.0
    rho_e = positive_float(explosive_density_g_cm3, "explosive_density_g_cm3")
    rho_r = positive_float(rock_density_g_cm3, "rock_density_g_cm3")
    return 37.8 * diameter_m * (rho_e / rho_r) ** 0.33


def konya_1983_burden(
    hole_diameter_mm,
    explosive_density_g_cm3,
    rock_density_g_cm3,
) -> float:
    """Verified metric Konya (1983): B = 12 d (2 rho_e/rho_r + 1.5)."""
    diameter_m = positive_float(hole_diameter_mm, "hole_diameter_mm") / 1000.0
    rho_e = positive_float(explosive_density_g_cm3, "explosive_density_g_cm3")
    rho_r = positive_float(rock_density_g_cm3, "rock_density_g_cm3")
    return 12.0 * diameter_m * (2.0 * rho_e / rho_r + 1.5)


def rustan_burden(hole_diameter_mm) -> float:
    """Rustan (1990/1992): B = 18.1 d^0.689, with d and B in metres."""
    diameter_m = positive_float(hole_diameter_mm, "hole_diameter_mm") / 1000.0
    return 18.1 * diameter_m**0.689


def rustan_applicability(hole_diameter_mm) -> str:
    """Classify the diameter against the documented 89–311 mm thesis range."""
    diameter_mm = positive_float(hole_diameter_mm, "hole_diameter_mm")
    if diameter_mm < 89:
        return "Outside documented domain: below 89 mm"
    if diameter_mm <= 311:
        return "Within documented 89–311 mm domain"
    return "Extrapolation: above documented 311 mm limit"


def tatiya_al_ajmi_coefficients(ucs_mpa) -> dict:
    """Return ANFO coefficients for the Tatiya–Al-Ajmi quadratic."""
    ucs = positive_float(ucs_mpa, "ucs_mpa")
    if ucs < 55:
        return {"strength_class": "UCS < 55 MPa", "a": -40.0, "b": 35.9, "c": 0.45}
    if ucs <= 110:
        return {
            "strength_class": "55 <= UCS <= 110 MPa",
            "a": -30.0,
            "b": 29.4,
            "c": 0.35,
        }
    return {"strength_class": "UCS > 110 MPa", "a": -20.0, "b": 24.1, "c": 0.30}


def tatiya_al_ajmi_burden(
    hole_diameter_mm,
    ucs_mpa,
    explosive_type="ANFO",
) -> float:
    """Tatiya–Al-Ajmi: B = ad² + bd + c; audited coefficients are ANFO-only."""
    if not isinstance(explosive_type, str):
        raise TypeError("explosive_type must be a string.")
    if explosive_type.strip().upper() != "ANFO":
        raise ValueError("Audited Tatiya–Al-Ajmi coefficients apply only to ANFO.")
    diameter_m = positive_float(hole_diameter_mm, "hole_diameter_mm") / 1000.0
    coefficients = tatiya_al_ajmi_coefficients(ucs_mpa)
    return (
        coefficients["a"] * diameter_m**2
        + coefficients["b"] * diameter_m
        + coefficients["c"]
    )
