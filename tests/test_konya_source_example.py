"""Check the reconstructed expression against a published worked example."""

import pytest

from blastdesign import konya_1983_burden


def test_konya_1983_matches_fhwa_example_6_2_using_charge_diameter():
    """FHWA-HI-92-001, printed p. 92: 6.25 ft equals 1.905 m."""
    # The source uses a 2.5-inch cartridge in a 3-inch borehole.
    # For this equation check, pass its charge diameter (63.5 mm) into
    # the legacy scalar argument, despite that argument's hole-based name.
    # This is not an operational validation or a decoupling correction.
    result = konya_1983_burden(
        hole_diameter_mm=63.5,
        explosive_density_g_cm3=1.3,
        rock_density_g_cm3=2.6,
    )

    assert result == pytest.approx(1.905, rel=1e-12, abs=0.0)
