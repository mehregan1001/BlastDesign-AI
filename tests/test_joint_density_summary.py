"""Numerical and input-contract checks for joint-density summaries."""

from copy import deepcopy
from io import StringIO
import unittest

import numpy as np
import pandas as pd

from blastdesign import (
    build_gole_gohar_joint_density_sensitivity_table,
    build_joint_density_ensemble_summary,
    build_model_joint_density_response_summary,
    evaluate_conventional_burden_models,
    gole_gohar_reference_inputs,
)


E = "explosive_density_g_cm3"
R = "rock_density_g_cm3"
RATIO = "explosive_to_rock_density_ratio"
BUILDERS = (
    build_joint_density_ensemble_summary,
    build_model_joint_density_response_summary,
)


def ordered_models(frame):
    return frame.sort_values("model_id").reset_index(drop=True)


class TestJointDensitySummary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = build_gole_gohar_joint_density_sensitivity_table()
        cls.reference = gole_gohar_reference_inputs()

    def assert_both_reject(self, table, error=ValueError):
        for builder in BUILDERS:
            with self.subTest(builder=builder.__name__):
                with self.assertRaises(error):
                    builder(table)

    def test_ensemble_has_one_complete_summary_per_pair(self):
        summary = build_joint_density_ensemble_summary(self.table)
        self.assertEqual(summary.shape, (84, 9))
        self.assertFalse(summary.duplicated([E, R]).any())
        self.assertTrue(summary["model_count"].eq(7).all())
        expected_pairs = set(zip(self.table[E], self.table[R]))
        self.assertEqual(set(zip(summary[E], summary[R])), expected_pairs)
        self.assertEqual(list(zip(summary[E], summary[R])), sorted(expected_pairs))

    def test_ensemble_statistics_match_independent_numpy_calculations(self):
        summary = build_joint_density_ensemble_summary(self.table).set_index([E, R])
        for pair, group in self.table.groupby([E, R]):
            with self.subTest(pair=pair):
                burdens = group["burden_m"].to_numpy()
                actual = summary.loc[pair]
                expected = [
                    np.mean(burdens), np.median(burdens),
                    np.min(burdens), np.max(burdens), np.ptp(burdens),
                ]
                np.testing.assert_allclose(
                    actual[["mean_burden_m", "median_burden_m",
                            "minimum_burden_m", "maximum_burden_m", "range_m"]],
                    expected, rtol=1e-12, atol=1e-12,
                )
                self.assertAlmostEqual(actual[RATIO], pair[0] / pair[1], places=14)

    def test_reference_ensemble_reproduces_established_benchmark(self):
        summary = build_joint_density_ensemble_summary(self.table).set_index([E, R])
        row = summary.loc[(self.reference[E], self.reference[R])]
        self.assertAlmostEqual(row["mean_burden_m"], 6.137371203249507, places=11)
        self.assertAlmostEqual(row["range_m"], 1.4558649429218485, places=11)

    def test_model_reference_burdens_match_shared_evaluator(self):
        summary = ordered_models(build_model_joint_density_response_summary(self.table))
        expected = ordered_models(evaluate_conventional_burden_models(**self.reference))
        self.assertEqual(summary.shape, (7, 17))
        self.assertEqual(summary["model_id"].tolist(), expected["model_id"].tolist())
        np.testing.assert_allclose(
            summary["reference_burden_m"], expected["burden_m"], rtol=1e-12, atol=1e-12,
        )
        self.assertTrue(summary["reference_explosive_density_g_cm3"].eq(self.reference[E]).all())
        self.assertTrue(summary["reference_rock_density_g_cm3"].eq(self.reference[R]).all())

    def test_only_konya_models_respond_and_fixed_models_have_zero_change(self):
        summary = build_model_joint_density_response_summary(self.table)
        responsive = summary["responds_to_joint_density_grid"]
        self.assertEqual(set(summary.loc[responsive, "model_id"]), {
            "CONV_KONYA_1972", "CONV_KONYA_1983",
        })
        self.assertTrue(summary.loc[~responsive, "distinct_burden_count"].eq(1).all())
        for column in ("ratio_endpoint_change_m", "ratio_endpoint_change_percent", "burden_range_m"):
            self.assertTrue(summary.loc[~responsive, column].eq(0).all())

    def test_ratio_endpoints_use_opposite_density_corners_and_correct_baseline(self):
        summary = build_model_joint_density_response_summary(self.table).set_index("model_id")
        low = self.table.loc[
            self.table[E].eq(self.table[E].min()) & self.table[R].eq(self.table[R].max())
        ].set_index("model_id")
        high = self.table.loc[
            self.table[E].eq(self.table[E].max()) & self.table[R].eq(self.table[R].min())
        ].set_index("model_id")
        for model_id, row in summary.iterrows():
            with self.subTest(model=model_id):
                lower, upper = low.loc[model_id, "burden_m"], high.loc[model_id, "burden_m"]
                self.assertAlmostEqual(row["minimum_sampled_density_ratio"], 0.7 / 5.3, places=14)
                self.assertAlmostEqual(row["maximum_sampled_density_ratio"], 1.0 / 1.8, places=14)
                self.assertAlmostEqual(row["burden_at_minimum_density_ratio_m"], lower, places=12)
                self.assertAlmostEqual(row["burden_at_maximum_density_ratio_m"], upper, places=12)
                self.assertAlmostEqual(row["ratio_endpoint_change_m"], upper - lower, places=12)
                self.assertAlmostEqual(row["ratio_endpoint_change_percent"], (upper - lower) / lower * 100, places=12)
        self.assertGreater(summary.loc["CONV_KONYA_1972", "ratio_endpoint_change_m"], 0)
        self.assertGreater(summary.loc["CONV_KONYA_1983", "ratio_endpoint_change_m"], 0)

    def test_model_extrema_match_all_sampled_burdens(self):
        summary = build_model_joint_density_response_summary(self.table).set_index("model_id")
        for model_id, group in self.table.groupby("model_id"):
            with self.subTest(model=model_id):
                values = group["burden_m"].to_numpy()
                row = summary.loc[model_id]
                self.assertAlmostEqual(row["minimum_burden_m"], np.min(values), places=12)
                self.assertAlmostEqual(row["maximum_burden_m"], np.max(values), places=12)
                self.assertAlmostEqual(row["burden_range_m"], np.ptp(values), places=12)
                self.assertEqual(row["distinct_burden_count"], len(np.unique(values)))

    def test_summaries_do_not_mutate_input_and_replace_stale_metadata(self):
        table = self.table.copy(deep=True)
        table.attrs["varied_parameter"] = "stale_single_parameter"
        table.attrs["inputs"] = {E: 999.0}
        original = table.copy(deep=True)
        original_attrs = deepcopy(table.attrs)
        for builder in BUILDERS:
            with self.subTest(builder=builder.__name__):
                summary = builder(table)
                pd.testing.assert_frame_equal(table, original)
                self.assertEqual(table.attrs, original_attrs)
                self.assertEqual(summary.attrs["decision_gate"], "RESEARCH_COMPARATOR_ONLY")
                self.assertEqual(tuple(summary.attrs["varied_parameters"]), (E, R))
                self.assertNotIn("varied_parameter", summary.attrs)
                self.assertNotIn("inputs", summary.attrs)
                self.assertTrue(summary.attrs["density_warning"])
                self.assertTrue(summary.attrs["interpretation_warning"])

    def test_row_order_does_not_change_summary_values(self):
        shuffled = self.table.sample(frac=1, random_state=17).reset_index(drop=True)
        for builder in BUILDERS:
            with self.subTest(builder=builder.__name__):
                expected, actual = builder(self.table), builder(shuffled)
                if "model_id" in expected:
                    expected, actual = ordered_models(expected), ordered_models(actual)
                pd.testing.assert_frame_equal(actual, expected, check_exact=False, rtol=1e-12, atol=1e-12)

    def test_csv_roundtrip_without_attrs_preserves_summaries(self):
        loaded = pd.read_csv(StringIO(self.table.to_csv(index=False)))
        self.assertEqual(loaded.attrs, {})
        for builder in BUILDERS:
            with self.subTest(builder=builder.__name__):
                pd.testing.assert_frame_equal(
                    builder(loaded), builder(self.table),
                    check_exact=False, rtol=1e-12, atol=1e-12,
                )

    def test_model_summary_requires_reference_pair(self):
        table = build_gole_gohar_joint_density_sensitivity_table([0.75, 0.9], [3.0, 3.6])
        self.assertEqual(len(build_joint_density_ensemble_summary(table)), 4)
        with self.assertRaises(ValueError):
            build_model_joint_density_response_summary(table)

    def test_explicit_reference_and_single_pair_have_zero_sampled_change(self):
        table = build_gole_gohar_joint_density_sensitivity_table([0.75], [3.0])
        summary = ordered_models(build_model_joint_density_response_summary(table, 0.75, 3.0))
        expected = ordered_models(table)
        np.testing.assert_allclose(summary["reference_burden_m"], expected["burden_m"])
        self.assertTrue(summary["reference_density_ratio"].eq(0.25).all())
        self.assertFalse(summary["responds_to_joint_density_grid"].any())
        self.assertTrue(summary["ratio_endpoint_change_m"].eq(0).all())
        self.assertTrue(summary["burden_range_m"].eq(0).all())

    def test_rejects_invalid_table_type_and_schema(self):
        self.assert_both_reject([], TypeError)
        for table in (
            self.table.iloc[:0],
            self.table.drop(columns="burden_m"),
            pd.concat([self.table, self.table[["burden_m"]]], axis=1),
        ):
            self.assert_both_reject(table)

    def test_rejects_duplicates_missing_models_and_missing_density_pairs(self):
        for label, table in (
            ("duplicate", pd.concat([self.table, self.table.iloc[[0]]], ignore_index=True)),
            ("missing model", self.table.iloc[1:]),
            ("missing pair", self.table.iloc[7:]),
        ):
            with self.subTest(problem=label):
                self.assert_both_reject(table)

    def test_rejects_unknown_ids_and_inconsistent_or_empty_names(self):
        for column, value in (("model_id", "UNKNOWN"), ("model_name", "changed"), ("model_name", "")):
            with self.subTest(column=column, value=value):
                bad = self.table.copy()
                bad.loc[bad.index[0], column] = value
                self.assert_both_reject(bad)

    def test_rejects_invalid_numeric_values_and_types(self):
        for column in (E, R, RATIO, "burden_m"):
            for value in (0.0, -1.0, np.nan, np.inf):
                with self.subTest(column=column, value=value):
                    bad = self.table.copy()
                    bad.loc[bad.index[0], column] = value
                    self.assert_both_reject(bad)
            for dtype in (str, bool, complex):
                with self.subTest(column=column, dtype=dtype):
                    bad = self.table.copy()
                    bad[column] = bad[column].astype(dtype)
                    self.assert_both_reject(bad)

    def test_rejects_inconsistent_or_incorrect_density_ratios(self):
        inconsistent = self.table.copy()
        inconsistent.loc[inconsistent.index[0], RATIO] *= 1.1
        self.assert_both_reject(inconsistent)
        incorrect = self.table.copy()
        incorrect[RATIO] *= 1.1
        self.assert_both_reject(incorrect)

    def test_rejects_invalid_explicit_reference_densities(self):
        for parameter in ("reference_explosive_density_g_cm3", "reference_rock_density_g_cm3"):
            for value, error in ((0.0, ValueError), (-1.0, ValueError), (np.nan, ValueError), (np.inf, ValueError), (True, TypeError)):
                with self.subTest(parameter=parameter, value=value):
                    with self.assertRaises(error):
                        build_model_joint_density_response_summary(self.table, **{parameter: value})


if __name__ == "__main__":
    unittest.main()
