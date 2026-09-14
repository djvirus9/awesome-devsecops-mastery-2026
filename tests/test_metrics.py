import copy
import importlib.util
import json
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("metrics", Path(__file__).resolve().parents[1] / "scripts/metrics.py")
metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metrics)


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.rows = metrics.load()

    def test_committed_fixture_parity_and_known_durations(self):
        metrics.validate_fixture_parity(self.rows)
        self.assertEqual([r["mttr_hours"] for r in self.rows], [26.0, 10.0])
        text = metrics.exposition(self.rows)
        self.assertIn("devsecops_demo_resolution_seconds_sum 129600\n", text)
        self.assertIn("devsecops_demo_acknowledgment_seconds_sum 2400\n", text)
        self.assertIn("devsecops_demo_incidents 2\n", text)

    def test_original_inconsistent_clock_is_rejected(self):
        self.rows[0]["mttr_hours"] = 25.5
        with self.assertRaisesRegex(ValueError, "detection-to-resolution"):
            metrics.validate(self.rows)

    def test_missing_timezone_and_reversed_events(self):
        for field, value in [("detected_at", "2026-01-01T10:00:00"), ("acknowledged_at", "2025-01-01T10:00:00Z")]:
            with self.subTest(field=field):
                rows = copy.deepcopy(self.rows)
                rows[0][field] = value
                with self.assertRaises(ValueError):
                    metrics.validate(rows)

    def test_duplicate_missing_nonfinite_and_invalid_records(self):
        invalid = [None, {}, [self.rows[0], self.rows[0]], [{**self.rows[0], "mttr_hours": float("nan")}], [{**self.rows[0], "mttr_hours": True}], [{**self.rows[0], "resolved_at": None}]]
        for rows in invalid:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                metrics.validate(rows)

    def test_empty_cohort_emits_zero_not_fabricated_mean(self):
        self.assertIn("devsecops_demo_incidents 0\n", metrics.exposition([]))

    def test_dashboard_queries_reference_exported_metrics(self):
        dashboard = json.loads((metrics.ROOT / "dashboards/grafana-devsecops.json").read_text())
        self.assertEqual(len(dashboard["panels"]), 3)
        for panel in dashboard["panels"]:
            self.assertTrue(panel["targets"][0]["expr"])
            self.assertIn("devsecops_demo_", panel["targets"][0]["expr"])


if __name__ == "__main__":
    unittest.main()
