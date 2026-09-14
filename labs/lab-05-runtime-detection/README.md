# Lab 05: detection and telemetry health

Phase 6 · 30–45 minutes · Python standard library, Linux/macOS/WSL. Complete [foundation setup](../../docs/foundation.md). This offline lab evaluates synthetic normalized application telemetry. It does not install Falco, monitor your host, or send notifications.

## Supplied rule and events

[rules.json](rules.json) declares three distinct denied requests from one subject/service within an inclusive 120-second window, plus a missing-heartbeat threshold of 90 seconds. The expected service inventory maps `sample-api` to `sample-api-oncall`; that is a local role label, not a real messaging destination.

[events.jsonl](events.jsonl) contains routine access, three synthetic denials, a duplicated request record, and heartbeats. These are fabricated observations for the sample API model, not logs emitted by a real attack or automatically exported by the application. A deployment would need a reviewed log adapter and a stable subject identifier without recording bearer tokens.

| Field | Normalized event contract |
| --- | --- |
| `timestamp` | ISO 8601 with timezone, no later than the explicit evaluation time. |
| `service` | A service present in the configured expected inventory. |
| `kind` | `access_allowed`, `access_denied`, or `heartbeat`. |
| `subject` | Required for access events; stable synthetic identity, never a bearer token. |
| `request_id` | Required for access events; one final access decision per unique service/request pair. Repeated delivery is deduplicated. |

Conflicting outcomes for the same request ID violate this input contract. A production adapter must resolve them explicitly; this batch exercise uses the first observed record and is not a general log-normalization pipeline.

## Run and inspect

From the repository root:

```bash
make runtime-test
.venv/bin/python labs/lab-05-runtime-detection/detect.py \
  --events labs/lab-05-runtime-detection/events.jsonl \
  --as-of 2026-09-15T12:04:00Z \
  --output reports/runtime-alerts.json
```

Expect 13 passing behavior tests and two alerts: `DEMO-DENIED-REQUESTS` at 12:01 with count 3, and `DEMO-TELEMETRY-GAP` at 12:04 with heartbeat age 120 seconds. Both carry service, owner, severity, and a runbook path. The duplicated request does not increase the count. The output survives the process in `reports/runtime-alerts.json`.

Repeat with `--as-of 2026-09-15T12:02:30Z`. Expect only the denied-request alert: heartbeat age is 30 seconds. The detector replays all supplied events up to the explicit evaluation time; future input is rejected instead of silently ignored. It emits one threshold alert per subject/service per input batch, not a persistent streaming incident deduplicator.

Exit 0 means evaluation completed, even when alerts exist. Exit 2 means invalid input/configuration or an I/O error. Detection is an observation, not a deployment gate or an automatic containment decision.

## Verify and hand off

Record the rule version/commit, evaluation time, output, expected positive and negative cases, and accountable owner. Verify that malformed events fail visibly and that absent telemetry generates a health alert even when no security events exist. Hand the two-alert report to [Lab 07](../lab-07-ir-detections/README.md).

If the count differs, check request IDs and timestamps; repeated delivery must not inflate counts. If all input appears in the future, use the supplied historical evaluation time. If a service is unknown, update a reviewed inventory rather than silently dropping its events.

No background service runs, so cleanup is limited to retaining or deleting your generated report. Keep synthetic source fixtures for repeatable tests.

Challenge: should two denials from Alice and one from Bob trigger the threshold? Solution: no; the tests verify subject isolation. A separate aggregate-service rule would require a separate purpose, threshold, and noise assessment.

## Optional host-sensor extension

Falco consumes events and detects matching behavior; detection alone does not block activity. Its kernel-event path requires a compatible Linux host/driver and privileges; a macOS host is not equivalent to the Linux VM used by Docker Desktop. Review [Falco platform requirements](https://falco.org/docs/setup/tarball/) and [driver requirements](https://falco.org/docs/setup/download/) before planning a separate environment exercise.

A deployment validation record must identify kernel/architecture, Falco and chart versions, driver mode, sensor health, benign test event, output configuration, destination owner, delivery result, retention, and tuning. This repository's offline test success does not establish any of those host-sensor results.
