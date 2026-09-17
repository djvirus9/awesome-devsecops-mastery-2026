"""Offline detection exercise over synthetic normalized JSONL, with no network I/O."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


def instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def stamp(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def positive_integer(value: object, field: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{field} must be a positive integer")
    return value


def evaluate(events: list[dict], rules: dict, as_of: datetime) -> list[dict]:
    """One threshold alert per service/subject per input batch, plus service health."""
    if as_of.tzinfo is None:
        raise ValueError("evaluation time must include a timezone")
    threshold = positive_integer(rules["denied_requests"]["threshold"], "threshold")
    window = positive_integer(rules["denied_requests"]["window_seconds"], "window_seconds")
    max_age = positive_integer(rules["heartbeat_max_age_seconds"], "heartbeat_max_age_seconds")
    services = rules["services"]
    if not isinstance(services, dict) or not services or any(
        not isinstance(service, str) or not service or not isinstance(owner, str) or not owner
        for service, owner in services.items()
    ):
        raise ValueError("services must map service names to accountable owners")

    normalized = []
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("every event must be a JSON object")
        timestamp = instant(event["timestamp"])
        service = event["service"]
        kind = event["kind"]
        if service not in services:
            raise ValueError(f"service is outside the configured inventory: {service}")
        if kind not in {"heartbeat", "access_allowed", "access_denied"}:
            raise ValueError(f"unsupported event kind: {kind}")
        if kind != "heartbeat":
            for field in ("subject", "request_id"):
                if not isinstance(event.get(field), str) or not event[field]:
                    raise ValueError(f"access events require {field}")
        if timestamp > as_of:
            raise ValueError("event is later than the evaluation time")
        normalized.append((timestamp, event))

    denied = defaultdict(deque)
    seen_requests = set()
    alerted = set()
    heartbeats = {}
    alerts = []
    for timestamp, event in sorted(normalized, key=lambda item: item[0]):
        service = event["service"]
        if event["kind"] == "heartbeat":
            heartbeats[service] = timestamp
            continue
        request_key = (service, event["request_id"])
        if request_key in seen_requests:
            continue
        seen_requests.add(request_key)
        if event["kind"] != "access_denied":
            continue
        key = (service, event["subject"])
        denied[key].append(timestamp)
        while (timestamp - denied[key][0]).total_seconds() > window:
            denied[key].popleft()
        if len(denied[key]) >= threshold and key not in alerted:
            alerted.add(key)
            alerts.append({
                "rule_id": "DEMO-DENIED-REQUESTS",
                "service": service,
                "subject": event["subject"],
                "observed_at": stamp(timestamp),
                "count": len(denied[key]),
                "window_seconds": window,
                "severity": "warning",
                "owner": services[service],
                "runbook": "labs/lab-07-ir-detections/README.md",
            })

    for service, owner in sorted(services.items()):
        latest = heartbeats.get(service)
        age = (as_of - latest).total_seconds() if latest else None
        if latest is None or age > max_age:
            alerts.append({
                "rule_id": "DEMO-TELEMETRY-GAP",
                "service": service,
                "observed_at": stamp(as_of),
                "heartbeat_age_seconds": age,
                "severity": "warning",
                "owner": owner,
                "runbook": "labs/lab-07-ir-detections/README.md",
            })
    return alerts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--rules", type=Path, default=Path(__file__).with_name("rules.json"))
    parser.add_argument("--as-of", required=True, help="Explicit timezone-aware replay time")
    parser.add_argument("--output", type=Path, help="Optional local JSON report path")
    args = parser.parse_args()
    try:
        events = [json.loads(line) for line in args.events.read_text().splitlines() if line.strip()]
        rules = json.loads(args.rules.read_text())
        alerts = evaluate(events, rules, instant(args.as_of))
        report = json.dumps({"synthetic": True, "alerts": alerts}, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report)
        print(report, end="")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"Detection input error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
