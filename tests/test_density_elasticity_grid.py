"""Checks for Cartesian sampling and metadata of Konya elasticities."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from blastdesign.audit import gole_gohar_reference_inputs
from blastdesign.burden import konya_1972_burden, konya_1983_burden
from blastdesign.density_elasticity import (
    build_gole_gohar_konya_density_elasticity_table,
    build_konya_density_elasticity_summary,
)
from blastdesign.sensitivity import (
    DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3,
    DEFAULT_ROCK_DENSITY_GRID_G_CM3,
)


BUILD = build_gole_gohar_konya_density_elasticity_table
E = "explosive_density_g_cm3"
R = "rock_density_g_cm3"
EE = "explosive_density_elasticity"
ER = "rock_density_elasticity"
MODELS = {
    "CONV_KONYA_1972": konya_1972_burden,
    "CONV_KONYA_1983": konya_1983_burden,
}


class TestDensityElasticityGrid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = BUILD()

    def test_default_grid_contains_every_pair_and_both_models_once(self):
        expected_pairs = {
            (rho_e, rho_r)
            for rho_e in DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3
            for rho_r in DEFAULT_ROCK_DENSITY_GRID_G_CM3
        }
        table = self.table
        self.assertEqual(table.shape, (2 * len(expected_pairs), 9))
        self.assertEqual(set(zip(table[E], table[R])), expected_pairs)
        self.assertFalse(table.duplicated([E, R, "model_id"]).any())
        self.assertTrue(table.groupby([E, R])["model_id"].nunique().eq(2).all())
        self.assertEqual(set(table["model_id"]), set(MODELS))
        self.assertEqual(list(zip(table[E], table[R])), sorted(zip(table[E], table[R])))

    def test_grid_values_agree_with_density_ratios_and_existing_burden_equations(self):
        table = self.table
        np.testing.assert_allclose(
            table["explosive_to_rock_density_ratio"], table[E] / table[R],
            rtol=1e-13, atol=1e-13,
        )
        np.testing.assert_allclose(table[EE] + table[ER], 0.0, atol=1e-14)
        for row in table.itertuples(index=False):
            expected = MODELS[row.model_id](
                row.hole_diameter_mm,
                row.explosive_density_g_cm3,
                row.rock_density_g_cm3,
            )
            self.assertAlmostEqual(row.burden_m, expected, places=13)
        summary = table.groupby("model_id")[EE].agg(["min", "max"])
        np.testing.assert_allclose(
            summary.loc["CONV_KONYA_1972"], [0.33, 0.33], atol=1e-14,
        )
        np.testing.assert_allclose(
            summary.loc["CONV_KONYA_1983"],
            [0.1497326203208556, 0.425531914893617],
            rtol=1e-13, atol=1e-13,
        )

    def test_reference_pair_reproduces_single_scenario_summary(self):
        reference = gole_gohar_reference_inputs()
        actual = self.table.loc[
            self.table[E].eq(reference[E]) & self.table[R].eq(reference[R])
        ].reset_index(drop=True)
        actual.attrs.clear()
        expected = build_konya_density_elasticity_summary()
        expected.attrs.clear()
        pd.testing.assert_frame_equal(actual, expected, rtol=1e-13, atol=1e-13)

    def test_custom_grids_are_sorted_and_accept_generators_without_mutating_lists(self):
        explosive = [0.9, 0.7]
        rock = [4.37, 2.75]
        original = deepcopy((explosive, rock))
        table = BUILD(explosive, rock)
        self.assertEqual((explosive, rock), original)
        self.assertEqual(table.shape, (8, 9))
        self.assertEqual(table[E].drop_duplicates().tolist(), [0.7, 0.9])
        self.assertEqual(table[R].drop_duplicates().tolist(), [2.75, 4.37])
        generated = BUILD((x for x in explosive), (x for x in rock))
        pd.testing.assert_frame_equal(table, generated)
        self.assertFalse(table.attrs["reference_density_pair_sampled"])
        single = BUILD([0.85], [4.37])
        self.assertEqual(single.shape, (2, 9))
        self.assertTrue(single.attrs["reference_density_pair_sampled"])

    def test_invalid_density_grids_are_rejected_on_each_axis(self):
        cases = (
            ([], ValueError),
            (0.85, TypeError),
            ("0.85", TypeError),
            (b"0.85", TypeError),
            ([0.85, 0.85], ValueError),
            ([0], ValueError),
            ([-1], ValueError),
            ([float("nan")], ValueError),
            ([float("inf")], ValueError),
            ([10**10000], ValueError),
            ([True], TypeError),
            ([np.bool_(False)], TypeError),
            (["0.85"], TypeError),
            ([1 + 2j], TypeError),
        )
        for name in ("explosive_densities_g_cm3", "rock_densities_g_cm3"):
            for values, error in cases:
                with self.assertRaises(error, msg=f"Invalid density grid: {name}"):
                    BUILD(**{name: values})

    def test_unrepresentable_ratios_and_burdens_are_rejected(self):
        for explosive, rock in (
            ([1e308], [1e-308]),
            ([1e-308], [1e308]),
            ([1e308], [1.0]),
        ):
            with self.assertRaises(ValueError):
                BUILD(explosive, rock)

    def test_grid_metadata_is_complete_fresh_and_contains_no_single_scenario(self):
        table = BUILD()
        attrs = table.attrs
        self.assertEqual(attrs["analysis_type"], "analytical_local_density_elasticity_grid")
        self.assertEqual(attrs["decision_gate"], "RESEARCH_COMPARATOR_ONLY")
        self.assertEqual(tuple(attrs["varied_parameters"]), (E, R))
        self.assertEqual(tuple(attrs["grid_shape"]), (7, 12))
        self.assertEqual(attrs["scenario_count"], 84)
        self.assertEqual(attrs["models_per_scenario"], 2)
        self.assertEqual(attrs["elasticity_units"], "dimensionless")
        self.assertTrue(attrs["reference_density_pair_sampled"])
        self.assertEqual(attrs["sampled_intervals_g_cm3"][E], {"minimum": 0.7, "maximum": 1.0})
        self.assertEqual(attrs["sampled_intervals_g_cm3"][R], {"minimum": 1.8, "maximum": 5.3})
        self.assertIn("finite percentage change", attrs["interpretation_warning"])
        self.assertIn("not probability distributions", attrs["density_warning"])
        self.assertNotIn("scenario_inputs", attrs)
        self.assertNotIn("varied_parameter", attrs)
        attrs["fixed_inputs"]["hole_diameter_mm"] = 999.0
        fresh = BUILD()
        self.assertEqual(
            fresh.attrs["fixed_inputs"]["hole_diameter_mm"],
            gole_gohar_reference_inputs()["hole_diameter_mm"],
        )

    def test_fixed_diameter_and_reference_metadata_follow_centralized_inputs(self):
        reference = {
            "hole_diameter_mm": 220.0, E: 0.9, R: 3.3,
            "ucs_mpa": 85.0, "explosive_type": "ANFO", "ash_burden_ratio": 25.0,
        }
        original = deepcopy(reference)
        with patch(
            "blastdesign.density_elasticity.gole_gohar_reference_inputs",
            return_value=reference,
        ):
            table = BUILD([0.8, 0.9], [2.75, 3.3])
        self.assertEqual(reference, original)
        self.assertTrue(table["hole_diameter_mm"].eq(220.0).all())
        self.assertEqual(table.attrs["fixed_inputs"], {"hole_diameter_mm": 220.0})
        self.assertEqual(table.attrs["reference_density_pair"], {E: 0.9, R: 3.3})
        self.assertTrue(table.attrs["reference_density_pair_sampled"])


if __name__ == "__main__":
    unittest.main()
