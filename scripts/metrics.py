#!/usr/bin/env python3
"""Validate fictional closed-incident fixtures and expose aggregate metrics."""
import argparse
import csv
import json
import math
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "metrics-templates/incident-metrics.json"
FIELDS = {"incident_id", "severity", "detected_at", "acknowledged_at", "resolved_at", "root_cause", "mttr_hours"}


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamps must be ISO 8601 strings")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return result


def validate(rows):
    if not isinstance(rows, list):
        raise ValueError("dataset must be a JSON array")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ValueError("each record must have exactly the documented fields")
        incident_id = row["incident_id"]
        if not isinstance(incident_id, str) or not incident_id or incident_id in seen:
            raise ValueError("incident IDs must be nonempty and unique")
        seen.add(incident_id)
        if row["severity"] not in {"Critical", "High", "Medium", "Low"}:
            raise ValueError("unsupported severity")
        if not isinstance(row["root_cause"], str):
            raise ValueError("root_cause must be a string")
        detected, acknowledged, resolved = (timestamp(row[name]) for name in ("detected_at", "acknowledged_at", "resolved_at"))
        if not detected <= acknowledged <= resolved:
            raise ValueError("expected detected_at <= acknowledged_at <= resolved_at")
        expected = (resolved - detected).total_seconds() / 3600
        duration = row["mttr_hours"]
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or not math.isclose(duration, expected, abs_tol=1e-6):
            raise ValueError("mttr_hours must equal detection-to-resolution hours")
    return rows


def load(path=DEFAULT_INPUT):
    with Path(path).open(encoding="utf-8") as source:
        return validate(json.load(source))


def validate_fixture_parity(rows):
    with (ROOT / "metrics-templates/incident-metrics.csv").open(newline="", encoding="utf-8") as source:
        csv_rows = list(csv.DictReader(source))
    for row in csv_rows:
        row["mttr_hours"] = float(row["mttr_hours"])
    if validate(csv_rows) != rows:
        raise ValueError("committed CSV and JSON fixtures differ")


def exposition(rows):
    validate(rows)
    resolution = sum((timestamp(row["resolved_at"]) - timestamp(row["detected_at"])).total_seconds() for row in rows)
    acknowledgment = sum((timestamp(row["acknowledged_at"]) - timestamp(row["detected_at"])).total_seconds() for row in rows)
    values = [
        ("devsecops_demo_incidents", "Closed incidents in the illustrative cohort.", len(rows)),
        ("devsecops_demo_resolution_seconds_sum", "Detection-to-resolution seconds in the illustrative cohort.", resolution),
        ("devsecops_demo_acknowledgment_seconds_sum", "Detection-to-acknowledgment seconds in the illustrative cohort.", acknowledgment),
    ]
    return "".join(f"# HELP {name} {help_text}\n# TYPE {name} gauge\n{name} {value:g}\n" for name, help_text, value in values)


def handler_for(payload):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/metrics":
                self.send_error(404)
                return
            body = payload.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=9108)
    args = parser.parse_args()
    try:
        rows = load(args.input)
        if args.input.resolve() == DEFAULT_INPUT.resolve():
            validate_fixture_parity(rows)
        payload = exposition(rows)
    except (ValueError, OSError, TypeError) as error:
        parser.error(str(error))
    if not args.serve:
        print(payload, end="")
        return
    with HTTPServer(("127.0.0.1", args.port), handler_for(payload)) as server:
        print(f"Illustrative metrics: http://127.0.0.1:{args.port}/metrics (Ctrl-C to stop)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
