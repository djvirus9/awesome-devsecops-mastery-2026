# Maturity Model

A clear progression from baseline security hygiene to proactive detection and response.

## Levels

| Level | Focus | Signals |
| --- | --- | --- |
| 1 | Hygiene | Pre-commit hooks, basic scanning, documented SLAs |
| 2 | CI Gates | Required checks, risk thresholds, automated SCA |
| 3 | Supply Chain | SBOMs, signed artifacts, provenance |
| 4 | Runtime | Detection rules, alert routing, dashboards |
| 5 | Resilience | Playbooks, continuous tuning, metrics-driven improvement |

## KPIs

- Mean time to triage (MTTT)
- Mean time to remediate (MTTR)
- % critical findings fixed within SLA
- % releases with SBOM + signatures
