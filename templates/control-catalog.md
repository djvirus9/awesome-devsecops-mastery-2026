# Canonical control catalog

These repository-specific IDs connect phase checklists, evidence and exceptions. They are learning/adoption criteria, not a statement that this repository operates a production security program. Assign named owners and declare scope before assessment.

| ID | Requirement and completion evidence | Accountable role |
| --- | --- | --- |
| C01 | Record assets, data classes, trust boundaries, threat/control/test links and residual risk in a reviewed threat model | Service owner |
| C02 | Document applicable security requirements and prove authorization and input-validation behavior using automated tests | Engineering owner |
| C03 | Required CI checks run for every proposed change; a failing check prevents merge; record settings and a failed-check example | Repository owner |
| C04 | SAST, dependency and secret checks cover declared paths; tool errors and blocking findings fail; retain reports and tool versions | Security owner |
| C05 | Produce a schema-valid SBOM linked to the exact released artifact digest; retain it with release metadata | Release owner |
| C06 | Verify artifact digest, signature identity/issuer and provenance against a written trust policy before promotion | Platform owner |
| C07 | Enforce tested workload policies with valid/invalid fixtures; record engine versions, scope and expiry-backed exclusions | Platform owner |
| C08 | Review passive local API observations together with automated security requirements tests; record authenticated coverage and limits | QA owner |
| C09 | Route documented runtime events to responders; a controlled test proves routing, redaction and acknowledgment | Operations owner |
| C10 | Tabletop incident decisions, evidence preservation, containment and recovery; track follow-up actions to closure | Incident lead |
| C11 | Track risk-ranked findings against an approved clock/SLA; exceptions have accountable approval, expiry and verification | Risk owner |
| C12 | Maintain evidence lineage, metric definitions and maturity assessments with explicit scope, owner and review date | Governance owner |

A checklist check means linked evidence meets the criterion. Mark N/A only with a scope-based reason and reviewer; it is not a pass. Exceptions use [the shared template](security-exception-template.md). Framework mapping requires the exact external framework version/control and an explicit rationale; these IDs are not formal certification controls.
