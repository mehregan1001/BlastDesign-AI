"""Regression checks for Rustan's visually verified source interval."""

import unittest

from blastdesign import rustan_applicability
from blastdesign.sensitivity import (
    DEFAULT_DIAMETER_GRID_MM,
    build_gole_gohar_diameter_sensitivity_table,
)


class TestRustanSourceRange(unittest.TestCase):
    """Use the printed p. 147/E7 Section 4.3 and Eq. 22 limits."""

    def test_diameter_below_published_lower_limit(self):
        self.assertEqual(
            rustan_applicability(88.999),
            "Outside documented domain: below 89 mm",
        )

    def test_published_lower_endpoint_is_included(self):
        self.assertEqual(
            rustan_applicability(89.0),
            "Within documented 89–381 mm domain",
        )

    def test_former_upper_endpoint_reports_corrected_interval(self):
        self.assertEqual(
            rustan_applicability(311.0),
            "Within documented 89–381 mm domain",
        )

    def test_diameter_above_former_limit_is_inside_source_interval(self):
        self.assertEqual(
            rustan_applicability(311.001),
            "Within documented 89–381 mm domain",
        )

    def test_published_upper_endpoint_is_included(self):
        self.assertEqual(
            rustan_applicability(381.0),
            "Within documented 89–381 mm domain",
        )

    def test_diameter_above_published_upper_limit_is_extrapolation(self):
        self.assertEqual(
            rustan_applicability(381.001),
            "Extrapolation: above documented 381 mm limit",
        )

    def test_historical_comparison_window_is_preserved(self):
        self.assertEqual(DEFAULT_DIAMETER_GRID_MM, (
            181.0, 191.0, 201.0, 211.0, 221.0, 231.0, 241.0,
            251.0, 261.0, 271.0, 281.0, 291.0, 301.0, 311.0,
        ))
        # The all-model comparison window remains a separate study choice.
        with self.assertRaisesRegex(ValueError, "311 mm"):
            build_gole_gohar_diameter_sensitivity_table([311.001])
        table = build_gole_gohar_diameter_sensitivity_table([251.0])
        self.assertEqual(table.attrs["comparison_window_mm"], {
            "lower_bound_exclusive": 180.0,
            "upper_bound_inclusive": 311.0,
        })
        self.assertEqual(table.attrs["decision_gate"], "RESEARCH_COMPARATOR_ONLY")
        self.assertIn("89–381 mm", table.attrs["window_warning"])
