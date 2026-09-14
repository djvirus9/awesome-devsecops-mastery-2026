# Maturity model

This repository's five levels are a teaching rubric, not a certification or an implementation of a named standard. Assess each domain independently with the [complete domain scorecard](../scorecards/maturity-scorecard.md). [OWASP SAMM](https://owaspsamm.org/model/) is a useful external reference for a broader assurance program.

| Level | Focus | Evidence required |
| --- | --- | --- |
| 1 | Hygiene | In-scope services/repos inventoried; owners and response duties assigned; baseline checks active. |
| 2 | CI gates | Checks execute and block appropriately; workflow changes controlled; approved exceptions expire. |
| 3 | Supply chain | Releases traceable to source/build identity; digest-linked inventory and verification evidence retained. |
| 4 | Runtime | Critical-service telemetry coverage measured; detections and delivery tested; alert ownership established. |
| 5 | Resilience | Recovery/rollback exercised; corrective actions closed; recurring causes and controls reassessed. |

Record scope, assessment date, evidence, assessor, accountable owner, current score, target score, and due date for every domain. A tool installation is configuration evidence; a tested control decision is operating evidence. A high runtime score does not compensate for an unprotected release process.

Use N/A only with an explicit applicability rationale and reviewer. Treat missing evidence as an assessed gap, not an assumed pass. Do not turn an arithmetic average into a security guarantee.

Review baseline controls quarterly and after architecture or ownership changes. Track coverage and recovery outcomes using [metric definitions](metrics.md), connect actions to the [control catalog](../templates/control-catalog.md), and retain the assessment with an [evidence pack](../evidence-packs/README.md).
