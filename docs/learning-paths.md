# Learning paths

All paths share the [foundation](foundation.md), [architecture](reference-architecture.md), and [seven phases](roadmap.md). Time ranges assume part-time practice after setup; assess deliverables rather than hours spent.

## Experience levels

| Level | Sequence | Assessed deliverable |
| --- | --- | --- |
| Foundation, 1–2 sessions | Setup, API requests, threat-model discussion | Working app, passing tests, three named trust decisions. |
| [Beginner](../skill-maps/beginner.md), 2–4 weeks | Labs 01 → 02 → 03 | Local/CI evidence, corrected failing fixture, image SBOM, distinction between signature and provenance. |
| [Intermediate](../skill-maps/intermediate.md), 4–8 weeks | Labs 06 → 04 → 05 | Role/route coverage, policy decisions, alerts, promotion/rollback design. |
| [Advanced](../skill-maps/advanced.md), 8+ weeks | Lab 07 and capstone | Artifact trust policy, scoped exceptions, identified evidence gaps, recovery record, architectural tradeoffs. |

Signing a file is introduced at beginner level. Advanced work examines builder trust, artifact identity, provenance, workload identity, and recovery across components.

## Role paths and handoffs

| Role | Primary work | Deliverable and recipient |
| --- | --- | --- |
| Application developer | Foundation, Labs 01/06, dependencies | Authorization regressions and reasoned code change; hand to reviewer/AppSec. |
| Platform/DevOps | Labs 02/03/04, CI identity and deployment | Workflow contract with permissions, checks, verification, and rollback; hand to service owners. |
| AppSec | Threat model, Labs 01/06/04, triage | Requirements mapped to tests, policy criteria, expiring exceptions; hand to developers/platform. |
| SRE/detection | Labs 05/07, telemetry health, recovery | Tested alert-owner contract and completed tabletop; hand to incident/on-call owners. |
| Program/security owner | Maturity rubric, controls, metrics | Dated assessment with scope, evidence gaps, owners, deadlines; hand to engineering leads. |

Review a neighboring role's deliverable once. A platform engineer should explain API authorization tests; a developer should explain release verification; a responder should know who can revoke build trust.

For each deliverable record commit, versions, command/procedure, observed result, evidence location, owner, and limitation. A peer should reproduce the local portion without hidden setup. Mark cluster, registry, and identity steps pending until their environments supply evidence. Use the [worked release record](../evidence-packs/example-release.md) and [capstone](../projects/microservice-api/README.md).
