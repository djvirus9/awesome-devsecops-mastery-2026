# Roadmap

Take the same application through seven phases. Progress when evidence exists; week estimates are examples for part-time learners.

| Order | Phase | Lab | Milestone |
| --- | --- | --- | --- |
| Before week 1 | [Foundation](foundation.md) | Local setup | Running application and understood trust boundaries. |
| Weeks 1–2 | [1. Shift left](phases/01-shift-left.md) | [01](../labs/lab-01-precommit-sast/README.md) | Harmless rule fixture fails; corrected source passes. |
| Weeks 3–4 | [2. CI/PR gates](phases/02-ci-pr-gates.md) | [02](../labs/lab-02-ci-pr-gates/README.md) | Named controls execute; required checks block failed changes. |
| Weeks 5–6 | [3. Supply chain](phases/03-supply-chain.md) | [03](../labs/lab-03-sbom-signing/README.md) | Image SBOM and retained bundle have verification evidence. |
| Weeks 7–8 | [4. API validation](phases/04-dast-api-testing.md) | [06](../labs/lab-06-dast-api-testing/README.md) | Identity, ownership, and contract regressions are tested. |
| Weeks 9–10 | [5. CD/cloud/Kubernetes](phases/05-cd-cloud-k8s.md) | [04](../labs/lab-04-k8s-admission-policies/README.md) | Policy fixtures pass; optional cluster behavior recorded separately. |
| Weeks 11–12 | [6. Runtime detection](phases/06-runtime-detection.md) | [05](../labs/lab-05-runtime-detection/README.md) | Synthetic alerts and telemetry-health decisions verified. |
| Weeks 13+ | [7. Incident response](phases/07-ir-detections.md) | [07](../labs/lab-07-ir-detections/README.md) | Response decisions, recovery evidence, and follow-up owners recorded. |

Lab numbers are historical and preserved: Phase 4 → Lab 06, Phase 5 → Lab 04, Phase 6 → Lab 05. AI-assisted remediation is an optional advanced specialization after these phases.

Use [learning paths](learning-paths.md) for role-specific depth, the [capstone](../projects/microservice-api/README.md) for integration, and [validation criteria](validation.md) to record execution. For organizational adoption, add the [maturity model](maturity-model.md), [control catalog](../templates/control-catalog.md), and [exception process](../templates/security-exception-template.md).
