# Case Studies

Practical examples of implementing DevSecOps in different environments. Use these as reference blueprints.

## Startup (1-10 engineers)

- Stack: GitHub Actions, Semgrep, Trivy, Syft, Cosign
- Focus: fast feedback, minimal overhead
- Metrics: PR gate pass rate, SLA compliance

## Mid-size SaaS (10-100 engineers)

- Stack: GitHub or GitLab, Semgrep/CodeQL, Trivy/Snyk, OPA/Kyverno, Falco
- Focus: standardized pipelines, staged gates, exception workflows
- Metrics: SBOM coverage, MTTR, policy exceptions per quarter

## Enterprise (100+ engineers)

- Stack: centralized SOC, SIEM, policy-as-code, federated CI
- Focus: governance, provenance, and consistent runtime detection
- Metrics: signed artifact coverage, detection fidelity, audit readiness

## Regulated Environment (PCI/HIPAA/SOC2)

- Stack: signed artifacts, strict approval gates, auditable exceptions
- Focus: evidence collection, compliance mapping, continuous monitoring
- Metrics: audit findings, SLA adherence, coverage by asset criticality
