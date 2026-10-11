"""Regression checks for saved Konya density-elasticity research outputs."""

import json
from pathlib import Path
import unittest

import pandas as pd

from blastdesign.density_elasticity import (
    build_gole_gohar_konya_density_elasticity_table,
    build_konya_density_elasticity_summary,
)


DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data" / "processed"


class TestDensityElasticityArtifacts(unittest.TestCase):
    def assert_saved_csv_matches(self, filename, expected):
        actual = pd.read_csv(DATA_DIRECTORY / filename)
        pd.testing.assert_frame_equal(
            actual, expected, check_dtype=False, check_exact=False,
            rtol=1e-12, atol=1e-12,
        )

    def test_saved_reference_matches_generated_summary(self):
        self.assert_saved_csv_matches(
            "konya_density_elasticity_reference.csv",
            build_konya_density_elasticity_summary(),
        )

    def test_saved_grid_matches_generated_results(self):
        self.assert_saved_csv_matches(
            "konya_density_elasticity_grid.csv",
            build_gole_gohar_konya_density_elasticity_table(),
        )

    def test_saved_metadata_preserves_units_and_current_research_attributes(self):
        with (DATA_DIRECTORY / "konya_density_elasticity_metadata.json").open(
            encoding="utf-8"
        ) as stream:
            actual = json.load(stream)
        self.assertEqual(actual["schema_version"], 1)
        self.assertEqual(actual["decision_gate"], "RESEARCH_COMPARATOR_ONLY")
        self.assertEqual(actual["calculation_source"], "blastdesign.density_elasticity")
        self.assertEqual(actual["column_units"], {
            "model_id": "identifier", "model_name": "text",
            "hole_diameter_mm": "mm", "explosive_density_g_cm3": "g/cm3",
            "rock_density_g_cm3": "g/cm3", "burden_m": "m",
            "explosive_to_rock_density_ratio": "dimensionless",
            "explosive_density_elasticity": "dimensionless",
            "rock_density_elasticity": "dimensionless",
        })
        expected_tables = {
            "konya_density_elasticity_reference.csv":
                build_konya_density_elasticity_summary(),
            "konya_density_elasticity_grid.csv":
                build_gole_gohar_konya_density_elasticity_table(),
        }
        self.assertEqual(set(actual["artifacts"]), set(expected_tables))
        for filename, table in expected_tables.items():
            expected = {
                "row_count": len(table), "columns": table.columns.tolist(),
                "attributes": json.loads(json.dumps(table.attrs, allow_nan=False)),
            }
            self.assertEqual(actual["artifacts"][filename], expected)


if __name__ == "__main__":
    unittest.main()
