# Awesome DevSecOps Mastery 2026

[![Reference checks](https://github.com/djvirus9/awesome-devsecops-mastery-2026/actions/workflows/devsecops-golden-pipeline.yml/badge.svg)](https://github.com/djvirus9/awesome-devsecops-mastery-2026/actions/workflows/devsecops-golden-pipeline.yml)
[![Platform checks](https://github.com/djvirus9/awesome-devsecops-mastery-2026/actions/workflows/platform-validation.yml/badge.svg)](https://github.com/djvirus9/awesome-devsecops-mastery-2026/actions/workflows/platform-validation.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Learn DevSecOps by taking one small API from local checks through build evidence, deployment policy, detection, and incident recovery. This repository combines an executable local reference path with optional environment exercises and a curated resource library.

Start with the [foundation setup](docs/foundation.md). The [validation matrix](docs/validation.md) distinguishes local checks, CI checks, and exercises needing a registry, cluster, or identity provider. Adopting these learning examples for a service requires its own threat model and deployment review.

## Quick start

Prerequisites: Git, Make, Python 3.12 or newer, and a POSIX shell on Linux, macOS, or Windows through WSL. Allow 10–15 minutes after installing prerequisites; full labs take longer.

```bash
git clone https://github.com/djvirus9/awesome-devsecops-mastery-2026.git
cd awesome-devsecops-mastery-2026
make setup
make test
make validate
API_TOKENS_JSON='{"demo-alice-token":"alice","demo-bob-token":"bob"}' make run
```

In another terminal:

```bash
DEMO_ALICE_TOKEN='demo-alice-token'
curl --fail http://127.0.0.1:8080/health
curl --fail -H "Authorization: Bearer $DEMO_ALICE_TOKEN" http://127.0.0.1:8080/v1/items
```

Expect a healthy response and Alice's synthetic items. Tokens above are public demonstration values for this local exercise. Stop the server with Ctrl+C. See the [sample API](samples/sample-api/README.md) for its contract, tests, container setup, and limitations.

## Seven phases, one reference application

Follow phase order. Existing lab folder numbers are retained so published links keep working: Phase 4 → Lab 06, Phase 5 → Lab 04, Phase 6 → Lab 05.

| Phase | Exercise | Evidence of completion |
| --- | --- | --- |
| 1. Shift left | [Lab 01: local checks](labs/lab-01-precommit-sast/README.md) | Tests and source rules pass; a harmless failing fixture is detected. |
| 2. CI and PR gates | [Lab 02: enforced checks](labs/lab-02-ci-pr-gates/README.md) | Real checks execute; required checks are verified in a practice repository. |
| 3. Supply chain | [Lab 03: SBOM and signing](labs/lab-03-sbom-signing/README.md) | Image inventory and retained signature bundle can be verified against an expected identity. |
| 4. API validation | [Lab 06: API regression tests](labs/lab-06-dast-api-testing/README.md) | Missing credentials and cross-owner requests are denied; expected access passes. |
| 5. CD and Kubernetes | [Lab 04: admission policies](labs/lab-04-k8s-admission-policies/README.md) | Fixtures prove allowed and denied cases; cluster validation is recorded separately. |
| 6. Runtime detection | [Lab 05: telemetry and detection](labs/lab-05-runtime-detection/README.md) | Synthetic events produce expected alerts and reveal a telemetry gap. |
| 7. Incident response | [Lab 07: response tabletop](labs/lab-07-ir-detections/README.md) | Decisions, recovery checks, timings, and follow-up ownership are recorded. |

AI-assisted remediation is an [optional advanced specialization](skill-maps/advanced.md), with human review and test evidence. Phase 7 is incident response throughout this repository.

## Choose your path

| Starting point | Outcome |
| --- | --- |
| [Foundation](docs/foundation.md) | Run the application and identify its trust boundaries. |
| [Beginner](skill-maps/beginner.md) | Produce local checks, a meaningful merge gate, and an SBOM. |
| [Intermediate](skill-maps/intermediate.md) | Connect API tests, policy enforcement, and detection evidence. |
| [Advanced](skill-maps/advanced.md) | Review release trust, exceptions, and recovery as an integrated system. |
| [Role paths](docs/learning-paths.md) | Developer, platform, AppSec, SRE, and program-owner deliverables. |

The [microservice capstone](projects/microservice-api/README.md) connects the exercises. Its [architecture and threat model](docs/reference-architecture.md) explains why each control exists.

## Practical assets

- Learning: [docs](docs/README.md), [roadmap](docs/roadmap.md), [labs](labs/README.md), [skill maps](skill-maps/README.md), [project extensions](projects/README.md).
- Implementation: [samples](samples/README.md), [CI examples](pipelines/), [configurations](configs/README.md), [policies](policies/README.md), [repository templates](repo-templates/README.md), [integrations](integrations/README.md), [recipes](recipes/README.md).
- Operations: [control catalog](templates/control-catalog.md), [checklists](checklists/README.md), [SDLC checklists](sdlc-checklists/README.md), [playbooks](playbooks/README.md), [exceptions](templates/security-exception-template.md).
- Evidence: [actual dated validation record](evidence-packs/releases/2026-09-15-reference-path.md), [illustrative release assessment](evidence-packs/example-release.md), [metrics](docs/metrics.md), [datasets](metrics-templates/README.md), [dashboards](dashboards/README.md), [maturity rubric](scorecards/maturity-scorecard.md).
- References: [tool comparison](docs/tool-comparison.md), [catalog](docs/awesome-catalog.md), [cheatsheets](docs/cheatsheets.md), [glossary](docs/glossary.md), [illustrative scenarios](docs/case-studies.md).

## Contributing and maintenance

Read [CONTRIBUTING.md](CONTRIBUTING.md), run local checks, and include commands, supported versions, expected results, and limitations for a new example. Tool names alone do not establish a working control. The badges link to separate baseline and disposable-platform checks. The dated validation record identifies the tested source, environment, results, and remaining gaps; copying this repository does not reproduce its settings or execution evidence. Released-image admission/deployment needs its own signed-path run; GitLab, Argo CD/Flux, cloud, and host-sensor paths are not implied by the GitHub baseline.

The 2026 edition is a rolling learning resource. Record tool upgrades and validation changes in pull requests; see the [validation and release criteria](docs/validation.md). Report security issues through [SECURITY.md](SECURITY.md). Distributed under the [MIT License](LICENSE).
