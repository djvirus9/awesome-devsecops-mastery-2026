# Labs

Follow the seven phases using one [sample API](../samples/sample-api/README.md). Begin with [foundation setup](../docs/foundation.md). Run commands from the repository root; Python commands use its `.venv` unless a lab explicitly says otherwise.

| Phase | Lab | Environment | Result |
| --- | --- | --- | --- |
| 1 | [01: Pre-commit/SAST](lab-01-precommit-sast/README.md) | Local + optional hook | Shared source rule and harmless fixture. |
| 2 | [02: CI/PR gates](lab-02-ci-pr-gates/README.md) | Local + practice GitHub repo | Executing checks and observed merge enforcement. |
| 3 | [03: SBOM/signing](lab-03-sbom-signing/README.md) | Docker/Syft + optional OIDC | Artifact inventory and retained verification bundle. |
| 4 | [06: API validation](lab-06-dast-api-testing/README.md) | Local synthetic app/tests | Identity/ownership coverage and retained results. |
| 5 | [04: Admission policy](lab-04-k8s-admission-policies/README.md) | Policy CLI + optional cluster | Allowed/denied fixtures and separately recorded admission. |
| 6 | [05: Runtime detection](lab-05-runtime-detection/README.md) | Offline synthetic telemetry | Detection, local routing, and telemetry health. |
| 7 | [07: Incident response](lab-07-ir-detections/README.md) | Offline tabletop | Decisions, recovery criteria, and response timings. |

Folder numbers are historical and stable: Phase 4 → Lab 06, Phase 5 → Lab 04, Phase 6 → Lab 05. Each lab has prerequisites, expected results, troubleshooting, cleanup, and a challenge/solution. Optional environment steps are not established by local test success. Record version/commit, command, observed result, and limitations using the [validation matrix](../docs/validation.md).
