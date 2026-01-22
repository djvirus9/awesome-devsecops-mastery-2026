# Serverless Pipeline Security Project

## Goal

Secure a serverless app pipeline with IaC scanning and runtime alerting.

## Scope

- Serverless functions (AWS Lambda or equivalent)
- IaC templates for deployment
- Centralized logging and alerts

## Deliverables

- IaC scanning in CI
- Secret scanning for configs
- Alerts for suspicious invocations

## Suggested Stack

- IaC scanning: [Checkov](https://www.checkov.io/), [KICS](https://kics.io/)
- Secrets: [Gitleaks](https://github.com/gitleaks/gitleaks)
- Observability: [OpenTelemetry](https://opentelemetry.io/)

## Steps (High-Level)

1. Run IaC scans on every PR.
2. Enforce secrets scanning for config files.
3. Add runtime alerts for anomalies.
4. Create a response runbook for serverless incidents.
