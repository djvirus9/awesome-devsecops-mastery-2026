# Microservice reference capstone

Take the [sample API](../../samples/sample-api/README.md) through the [seven phases](../../docs/roadmap.md). The application, tests, repository controls, policy fixtures, offline detection, and tabletop are supplied. Registry publication, cluster promotion, and live sensor/delivery evidence require their explicitly configured environments.

## Local reference sequence

Run from the repository root after [foundation setup](../../docs/foundation.md):

```bash
make setup
make test
make validate
make sast
make container
make container-test
make sbom
make policy-test
make runtime-test
```

Docker, scanner/policy CLIs, and versions must match [tool-versions.json](../../tool-versions.json) and each selected lab's prerequisites. Do not silently skip a missing binary and claim success. Complete [Lab 07](../../labs/lab-07-ir-detections/README.md) after generating the runtime report in Lab 05.

## Evidence chain

| Stage | Deliverable | Owner/review question |
| --- | --- | --- |
| Design | [Threat model](../../docs/reference-architecture.md) with deployment-specific decisions | Application/AppSec: which access and trust requirements are covered? |
| Source/CI | Passing controls and controlled failing-fixture evidence | Developer/platform: does a failed check actually block? |
| Build | Image identity, inventory, scanner report, source commit | Release owner: are these the same built artifact? |
| Signing | Retained bundle, expected issuer/identity, verification result | Platform: was the intended identity trusted? |
| Policy | Allowed/denied fixtures and optional admission result | Platform: is this rule evaluation or deployed enforcement? |
| Runtime | Synthetic alerts, heartbeat test, documented live-adapter gap | SRE: can missing telemetry be distinguished from silence? |
| Recovery | Completed tabletop with timings and follow-up | Commander: what established recovery and what remains simulated? |

Retain your results using the [evidence-pack format](../../evidence-packs/README.md). The [example release](../../evidence-packs/example-release.md) is illustrative; replace identifiers with actual evidence rather than copying a pass claim.

## Optional environment completion

A practice release needs a selected registry and exact manifest digest, build identity, provenance, bundle/verification evidence, and a promotion policy. A practice deployment additionally needs TLS/identity decisions, secret delivery, namespace/RBAC/network controls, admission, a rollback target, and operational ownership. A live telemetry path needs a reviewed adapter/sensor, fresh heartbeat, destination-delivery evidence, and retention controls. Record supported versions and costs before provisioned work.

The capstone is complete at its declared scope when a peer reproduces local results, can follow the evidence chain, and sees external steps explicitly passed or pending. No production readiness or SLSA level is inferred. Stop foreground services, remove only your named practice containers/images, and preserve sanitized completion evidence.
