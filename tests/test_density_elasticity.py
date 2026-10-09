"""Analytical and numerical checks for local Konya density elasticities."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import numpy as np

from blastdesign.audit import gole_gohar_reference_inputs
from blastdesign.burden import konya_1972_burden, konya_1983_burden
from blastdesign.density_elasticity import build_konya_density_elasticity_summary
from blastdesign.sensitivity import (
    DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3,
    DEFAULT_ROCK_DENSITY_GRID_G_CM3,
)


BUILD = build_konya_density_elasticity_summary
E = "explosive_density_g_cm3"
R = "rock_density_g_cm3"
EE = "explosive_density_elasticity"
ER = "rock_density_elasticity"
MODELS = {
    "CONV_KONYA_1972": konya_1972_burden,
    "CONV_KONYA_1983": konya_1983_burden,
}


class TestDensityElasticity(unittest.TestCase):
    def test_default_schema_and_canonical_model_ids(self):
        result = BUILD()
        self.assertEqual(result.shape, (2, 9))
        self.assertEqual(result["model_id"].tolist(), list(MODELS))
        self.assertEqual(
            result.columns.tolist(),
            ["model_id", "model_name", "hole_diameter_mm", E, R,
             "explosive_to_rock_density_ratio", "burden_m", EE, ER],
        )

    def test_defaults_follow_centralized_reference_inputs(self):
        reference = gole_gohar_reference_inputs()
        result = BUILD()
        for name in ("hole_diameter_mm", E, R):
            self.assertTrue(result[name].eq(reference[name]).all())
        self.assertTrue(
            result["explosive_to_rock_density_ratio"].eq(reference[E] / reference[R]).all()
        )

    def test_reference_elasticities_match_established_values(self):
        result = BUILD(251.0, 0.85, 4.37).set_index("model_id")
        expected = {
            "CONV_KONYA_1972": 0.33,
            "CONV_KONYA_1983": 0.2059357964869776,
        }
        for model_id, elasticity in expected.items():
            self.assertAlmostEqual(result.loc[model_id, EE], elasticity, places=14)
            self.assertAlmostEqual(result.loc[model_id, ER], -elasticity, places=14)

    def test_burdens_reuse_existing_equations_for_supplied_inputs(self):
        result = BUILD(200.0, 0.9, 2.75).set_index("model_id")
        for model_id, burden_function in MODELS.items():
            self.assertAlmostEqual(
                result.loc[model_id, "burden_m"],
                burden_function(200.0, 0.9, 2.75),
                places=13,
            )

    def test_analytic_elasticities_match_central_differences_across_density_grids(self):
        # Differentiate the existing burden functions, independently of the
        # analytic formulas in the module, at every sampled density pair.
        analytic = []
        numerical = []
        step = 1e-5
        diameter = gole_gohar_reference_inputs()["hole_diameter_mm"]
        for rho_e in DEFAULT_EXPLOSIVE_DENSITY_GRID_G_CM3:
            for rho_r in DEFAULT_ROCK_DENSITY_GRID_G_CM3:
                result = BUILD(diameter, rho_e, rho_r).set_index("model_id")
                for model_id, burden_function in MODELS.items():
                    burden = burden_function(diameter, rho_e, rho_r)
                    numerical_e = (
                        burden_function(diameter, rho_e * (1 + step), rho_r)
                        - burden_function(diameter, rho_e * (1 - step), rho_r)
                    ) / (2 * step * burden)
                    numerical_r = (
                        burden_function(diameter, rho_e, rho_r * (1 + step))
                        - burden_function(diameter, rho_e, rho_r * (1 - step))
                    ) / (2 * step * burden)
                    analytic.append(result.loc[model_id, [EE, ER]].to_numpy(dtype=float))
                    numerical.append([numerical_e, numerical_r])
        np.testing.assert_allclose(analytic, numerical, rtol=1e-7, atol=1e-9)

    def test_proportional_density_pairs_preserve_burden_and_elasticities(self):
        first = BUILD(251.0, 0.8, 2.0)
        second = BUILD(251.0, 1.6, 4.0)
        np.testing.assert_allclose(
            first[["burden_m", EE, ER]], second[["burden_m", EE, ER]],
            rtol=1e-13, atol=1e-13,
        )

    def test_diameter_scaling_changes_burden_but_not_density_elasticities(self):
        first = BUILD(200.0, 0.85, 4.37)
        second = BUILD(400.0, 0.85, 4.37)
        np.testing.assert_allclose(second["burden_m"], 2 * first["burden_m"], rtol=1e-13)
        np.testing.assert_allclose(first[[EE, ER]], second[[EE, ER]], rtol=1e-13)

    def test_konya_1972_is_constant_and_konya_1983_increases_with_ratio(self):
        elasticities = []
        for rho_e in (0.1, 0.5, 1.0, 2.0):
            result = BUILD(251.0, rho_e, 2.75).set_index("model_id")
            self.assertEqual(result.loc["CONV_KONYA_1972", EE], 0.33)
            self.assertEqual(result.loc["CONV_KONYA_1972", ER], -0.33)
            value = result.loc["CONV_KONYA_1983", EE]
            self.assertGreater(value, 0.0)
            self.assertLess(value, 1.0)
            self.assertEqual(result.loc["CONV_KONYA_1983", ER], -value)
            elasticities.append(value)
        self.assertTrue(np.all(np.diff(elasticities) > 0.0))

    def test_invalid_numeric_inputs_are_rejected(self):
        invalid = (0, -1, float("nan"), float("inf"), float("-inf"), 10**10000)
        for name in ("hole_diameter_mm", E, R):
            for value in invalid:
                with self.assertRaises(ValueError, msg=f"Invalid numerical input: {name}"):
                    BUILD(**{name: value})

    def test_nonreal_and_boolean_inputs_are_rejected(self):
        invalid = (True, np.bool_(False), "0.85", b"0.85", 1 + 2j, np.complex128(1j), [])
        for name in ("hole_diameter_mm", E, R):
            for value in invalid:
                with self.assertRaises(TypeError, msg=f"Invalid input type: {name}"):
                    BUILD(**{name: value})

    def test_unrepresentable_ratios_and_burdens_are_rejected(self):
        scenarios = (
            {E: 1e308, R: 1e-308},
            {E: 1e-308, R: 1e308},
            {E: 1e308, R: 1.0},
            {"hole_diameter_mm": 5e-324},
        )
        for inputs in scenarios:
            with self.assertRaises(ValueError, msg=f"Unrepresentable scenario: {inputs}"):
                BUILD(**inputs)

    def test_metadata_is_fresh_and_reference_inputs_are_not_mutated(self):
        reference = {
            "hole_diameter_mm": 220.0, E: 0.9, R: 3.3,
            "ucs_mpa": 85.0, "explosive_type": "ANFO", "ash_burden_ratio": 25.0,
        }
        original = deepcopy(reference)
        with patch(
            "blastdesign.density_elasticity.gole_gohar_reference_inputs",
            return_value=reference,
        ):
            first = BUILD()
            self.assertTrue(first["hole_diameter_mm"].eq(220.0).all())
            self.assertTrue(first[E].eq(0.9).all())
            self.assertTrue(first[R].eq(3.3).all())
            first.attrs["scenario_inputs"][E] = 999.0
            second = BUILD()
        self.assertEqual(reference, original)
        self.assertEqual(second.attrs["scenario_inputs"][E], 0.9)
        self.assertEqual(second.attrs["decision_gate"], "RESEARCH_COMPARATOR_ONLY")
        self.assertEqual(second.attrs["analysis_type"], "analytical_local_density_elasticity")
        self.assertEqual(second.attrs["elasticity_units"], "dimensionless")
        self.assertIn("finite percentage change", second.attrs["interpretation_warning"])
        self.assertIn("density_warning", second.attrs)
        self.assertNotIn("varied_parameter", second.attrs)


if __name__ == "__main__":
    unittest.main()
