"""Behavior tests for threshold, identity grouping, noise, and telemetry failures."""

import copy
from datetime import timedelta
import json
from pathlib import Path
import unittest

from detect import evaluate, instant


ROOT = Path(__file__).parent
RULES = json.loads((ROOT / "rules.json").read_text())
START = instant("2026-09-15T12:00:00Z")


def event(second, kind="access_denied", subject="alice", request_id=None):
    return {
        "timestamp": (START + timedelta(seconds=second)).isoformat(),
        "service": "sample-api",
        "kind": kind,
        "subject": subject,
        "request_id": request_id or f"demo-{second}-{subject}",
    }


class DetectorTests(unittest.TestCase):
    def run_events(self, events, as_of=120):
        return evaluate(events, RULES, START + timedelta(seconds=as_of))

    def test_supplied_fixture_has_threshold_and_gap(self):
        events = [json.loads(line) for line in (ROOT / "events.jsonl").read_text().splitlines()]
        alerts = self.run_events(events, 240)
        self.assertEqual([a["rule_id"] for a in alerts], ["DEMO-DENIED-REQUESTS", "DEMO-TELEMETRY-GAP"])
        self.assertEqual(alerts[0]["count"], 3)
        self.assertEqual(alerts[1]["heartbeat_age_seconds"], 120)
        self.assertTrue(all(a["owner"] == "sample-api-oncall" for a in alerts))

    def test_exact_window_boundary_counts(self):
        alerts = self.run_events([event(0), event(60), event(120), event(120, "heartbeat")])
        self.assertEqual(len(alerts), 1)

    def test_events_outside_window_do_not_accumulate(self):
        self.assertEqual(self.run_events([event(0), event(60), event(121), event(121, "heartbeat")], 121), [])

    def test_different_subjects_are_not_combined(self):
        self.assertEqual(self.run_events([event(0), event(10, subject="bob"), event(20), event(120, "heartbeat")]), [])

    def test_duplicate_request_does_not_raise_count(self):
        duplicate = event(0)
        self.assertEqual(self.run_events([duplicate, duplicate, event(10), event(120, "heartbeat")]), [])

    def test_normal_access_remains_quiet(self):
        self.assertEqual(self.run_events([event(s, "access_allowed") for s in (0, 10, 20)] + [event(120, "heartbeat")]), [])

    def test_alert_deduplicated_for_subject_in_batch(self):
        alerts = self.run_events([event(s) for s in (0, 10, 20, 30)] + [event(120, "heartbeat")])
        self.assertEqual(len(alerts), 1)

    def test_absent_heartbeat_is_visible_even_without_events(self):
        self.assertEqual(self.run_events([])[0]["rule_id"], "DEMO-TELEMETRY-GAP")

    def test_heartbeat_boundary_is_healthy(self):
        self.assertEqual(self.run_events([event(30, "heartbeat")]), [])
        self.assertEqual(self.run_events([event(29, "heartbeat")])[0]["heartbeat_age_seconds"], 91)

    def test_out_of_order_input_has_same_decisions(self):
        events = [event(0), event(10), event(20), event(120, "heartbeat")]
        self.assertEqual(self.run_events(events), self.run_events(list(reversed(events))))

    def test_invalid_threshold_rejected(self):
        bad = copy.deepcopy(RULES)
        bad["denied_requests"]["threshold"] = 0
        with self.assertRaises(ValueError):
            evaluate([], bad, START)

    def test_missing_subject_and_unknown_service_rejected(self):
        bad = event(0)
        del bad["subject"]
        with self.assertRaises(ValueError):
            self.run_events([bad])
        bad = event(0)
        bad["service"] = "not-in-inventory"
        with self.assertRaises(ValueError):
            self.run_events([bad])

    def test_future_and_naive_timestamps_rejected(self):
        with self.assertRaises(ValueError):
            self.run_events([event(121)])
        with self.assertRaises(ValueError):
            instant("2026-09-15T12:00:00")


if __name__ == "__main__":
    unittest.main()
