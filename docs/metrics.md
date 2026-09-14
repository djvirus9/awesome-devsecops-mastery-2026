# Metrics and KPIs

Use the [metric datasets and calculator](../metrics-templates/README.md) and [working dashboard setup](../dashboards/README.md). Synthetic examples are teaching data, not this repository's operational history.

## Measurement contract

| Metric | Definition and clock | Scope, source, and owner |
| --- | --- | --- |
| Incident acknowledgment time | Acknowledged timestamp minus detected timestamp, elapsed hours. | Incidents detected during the reporting period; incident record; response lead. |
| Incident recovery time | Resolved timestamp minus detected timestamp, elapsed hours. | Resolved incidents, with unresolved age reported separately; incident record; SRE. |
| Vulnerability remediation time | Verified-fix timestamp minus validated-finding timestamp. | Findings fixed in period plus open-aging distribution; finding tracker; AppSec. |
| SLA compliance | Eligible findings completed within their severity-specific deadline / all eligible findings due in period. | Include overdue open findings; exclude only approved, documented applicability cases; AppSec. |
| SBOM coverage | Releases with inventory linked to exact artifact identity / releases in scope. | Release evidence, reporting period and service criticality; platform owner. |
| Verified signature coverage | Releases verified against expected issuer/identity and artifact digest / releases in scope. | Verification evidence, not signature-presence count; release owner. |
| CI enforcement coverage | Repositories with tested required checks / repositories in scope. | Repository inventory and rule evidence; platform owner. |
| Telemetry health | Healthy expected service/collector intervals / expected monitored intervals. | Explicit expected inventory and heartbeat source; SRE. |

Document UTC timestamps, time window, exclusions, service scope, units, source query, and owner alongside each chart. Separate incident recovery from vulnerability remediation even when both are casually called MTTR. Reopened records retain their original clocks and include the reopening decision. Do not reset age by silently recreating a finding.

Means alone hide outliers. Show medians/percentiles where sample size supports them, overdue counts, unresolved age, and denominators. A low CI failure rate can indicate missing checks; compare it with coverage and controlled failing-fixture results.

The [SLA matrix](../templates/vuln-sla-matrix.md) defines policy examples. Acknowledgment, triage, response, remediation, and recovery are separate events; their deadlines need explicit clock and population definitions. Approved exceptions remain visible with owner and expiry.

## Review cadence

- Weekly: overdue items, failed controls, missing telemetry, unowned alerts.
- Monthly: inventory/evidence coverage, aging distribution, exception renewals, noisy detections.
- Quarterly: [maturity assessment](maturity-model.md), recovery exercises, recurring causes, control effectiveness.

Retain the calculation version and source data with each report so results are reproducible. See [Lab 07](../labs/lab-07-ir-detections/README.md) for a worked exercise using distinct detection, acknowledgment, and recovery times.
