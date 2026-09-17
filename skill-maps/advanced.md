# Advanced skill map

Complete the intermediate path, [Lab 07](../labs/lab-07-ir-detections/README.md), and the [microservice capstone](../projects/microservice-api/README.md). Depth comes from connecting trust decisions and operational outcomes.

## Assessable outcomes

| Area | Required work |
| --- | --- |
| Build trust | Explain trusted builder/workflow identity, contributor boundaries, provenance fields, and the remaining guarantees. Do not infer a SLSA level from a signed file. |
| Promotion | Link source, exact artifact identity, inventory, verification, and deployment decision. Demonstrate rejection for an unexpected identity in a practice environment. |
| Platform controls | Design reusable controls, workload identity/RBAC, staged policy rollout, drift handling, and reversible recovery. |
| Governance | Assess every maturity domain with scope/evidence; review expiring exceptions and unresolved gaps. |
| Detection/recovery | Test positive/negative/missing-telemetry cases; complete the tabletop and verify the corrective action. |

An assessor should review a design decision, the linked test evidence, and one failure/recovery path. Document limitations and environment steps that remain pending.

## Optional specialization: AI-assisted remediation

After the core capstone, evaluate suggestions on sanitized local examples. Give the assistant the minimum context needed; keep credentials and sensitive reports out of inputs. Treat output as a proposed code change requiring human review, regression tests, provenance of the suggestion, and rollback. Compare accepted changes with rejected suggestions using a predefined evaluation set. Autonomous release or production changes are not an exercise in this repository.

References: [SLSA build track](https://slsa.dev/spec/v1.2/build-track-basics), [Sigstore verification](https://docs.sigstore.dev/cosign/verifying/verify/), and [OWASP SAMM](https://owaspsamm.org/model/).
