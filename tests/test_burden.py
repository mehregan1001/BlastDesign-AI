import math

import pytest

from blastdesign import (
    ash_burden,
    bhandari_burden,
    konya_1972_burden,
    konya_1983_burden,
    lopez_jimeno_burden,
    rustan_burden,
    tatiya_al_ajmi_burden,
    tatiya_al_ajmi_coefficients,
)


def close(actual, expected):
    assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12)


def test_gole_gohar_benchmarks():
    close(ash_burden(251, 25), 6.275)
    close(bhandari_burden(251), 6.874)
    close(lopez_jimeno_burden(251, 85, "ANFO"), 5.773)
    close(konya_1972_burden(251, 0.85, 4.37), 5.5273236163425565)
    close(konya_1983_burden(251, 0.85, 4.37), 5.689716247139588)
    close(rustan_burden(251), 6.983188559264405)
    close(tatiya_al_ajmi_burden(251, 85), 5.839369999999999)


def test_lopez_jimeno_small_hole_branches():
    close(lopez_jimeno_burden(100, 50), 3.9)
    close(lopez_jimeno_burden(100, 100), 3.7)
    close(lopez_jimeno_burden(100, 150), 3.5)
    close(lopez_jimeno_burden(100, 200), 3.3)


def test_lopez_jimeno_gap_is_rejected():
    with pytest.raises(ValueError):
        lopez_jimeno_burden(170, 85)


def test_tatiya_boundaries_and_anfo_constraint():
    assert tatiya_al_ajmi_coefficients(54.999)["a"] == -40.0
    assert tatiya_al_ajmi_coefficients(55)["a"] == -30.0
    assert tatiya_al_ajmi_coefficients(110)["a"] == -30.0
    assert tatiya_al_ajmi_coefficients(110.001)["a"] == -20.0
    with pytest.raises(ValueError):
        tatiya_al_ajmi_burden(100, 85, "Emulsion")
