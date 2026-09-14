# Validation scope and release criteria

The reference path is source-controlled learning material with executable checks. Record what ran, where it ran, and what it proved. A configured workflow, an offline fixture pass, and a deployed control decision are different evidence.

## Execution matrix

Run commands from the repository root. Python baseline: 3.12 or newer, with 3.12 and 3.14 selected for CI. Exact external tool versions are in [tool-versions.json](../tool-versions.json); Python packages are locked in [requirements-dev.txt](../requirements-dev.txt) and the sample's dependency file.

The [pinned binary installer](../scripts/install_tool.py) supports Linux amd64 and macOS arm64. The portable Python exercises have a broader platform scope; do not assume every optional binary/host sensor supports the same platforms. Downloads are matched to committed release-asset checksums; that check is distinct from build-provenance verification.

| Path | Entry point | Prerequisites | What successful execution establishes |
| --- | --- | --- | --- |
| Application and supporting behavior | `make setup` then `make test` | Supported Python, network for dependency setup | Supplied application, metrics, and detector regressions pass. |
| Repository consistency | `make validate` | Python environment | Implemented structural/configuration checks pass; this is not a runtime scanner. |
| Source rules | `make sast` and Lab 01 fixture commands | Pinned Semgrep | Selected local rules execute, expected fixture triggers, normal sample passes. |
| Built application | `make container` then `make container-test` | Docker daemon | Named image builds and supplied container smoke checks pass. |
| Image inventory | `make sbom` | Built image and pinned Syft | `reports/sbom.cdx.json` describes the selected built image. |
| Policy behavior | `make policy-test` | Pinned Kyverno and Gator CLIs | Allowed/denied fixture expectations hold; cluster admission is separate. |
| Detection behavior | `make runtime-test` and Lab 05 replay | Python standard library | Threshold, grouping, deduplication, noise, and telemetry-gap cases pass. |
| Metrics | `make metrics`; optional `make metrics-serve` | Python environment | Synthetic fixture calculations and the loopback exporter work. |
| CI gates | [Reference workflow](../.github/workflows/devsecops-golden-pipeline.yml) | GitHub Actions runner/tool downloads | Named job behavior and retained artifacts for that exact run. |
| Merge enforcement | [Lab 02](../labs/lab-02-ci-pr-gates/README.md) | Practice repo with rule-management access | The configured merge path blocks a controlled failed check. |
| Keyless signing | [Lab 03](../labs/lab-03-sbom-signing/README.md) | Cosign, network, chosen OIDC provider | A retained bundle verifies against the expected signer/issuer. |
| Kubernetes admission | [Lab 04](../labs/lab-04-k8s-admission-policies/README.md) | Disposable supported cluster/controller | Actual admission and rollout behavior in the recorded environment. |
| Passive response inspection | [Local ZAP recipe](../recipes/zap-authenticated.md) | Native ZAP and synthetic loopback API | Only the deliberately observed local responses were inspected. |
| Incident recovery | [Lab 07](../labs/lab-07-ir-detections/README.md) | Synthetic tabletop evidence | Response reasoning and clocks; live restoration requires environment evidence. |

Local defaults do not create a cloud service, publish a registry image, install a host sensor, send external alerts, or establish a SLSA assurance level. Optional workflows and project extensions state their own permissions and activation requirements.

## Recorded validation versus intended support

The runtime exercise was executed with Python 3.14.7 during the September 2026 content update: all 13 detector tests passed, and the supplied fixture at `2026-09-15T12:04:00Z` yielded the expected two alerts. The support matrix above is a reproducible contract, not a blanket claim that every platform was tested in that editing environment.

The separated Python/JavaScript source rules were tested with Semgrep 1.177.0: both annotated fixture suites passed, the deliberate Python fixture produced one finding and exit 1, and the normal sample scan returned no findings. The template generator's eight behavior tests also passed with Python 3.14.7.

A fresh generated microservice reference (213 copied files, without Git metadata) was also exercised with Python 3.14.7: `make setup` installed the hash-locked dependencies; `make test` passed 54 tests across the core, bootstrap, and runtime suites; `make validate` reported zero errors across 445 local links. Those counts describe that validation snapshot and will change as the reference grows. No container, registry, cluster, or signing execution is implied by these Python/template results.

Use the [latest workflow runs](https://github.com/djvirus9/awesome-devsecops-mastery-2026/actions/workflows/devsecops-golden-pipeline.yml) and the relevant PR for the exact commit's CI evidence. Record local results and any unavailable Docker, cluster, registry, OIDC, or notification services in the release record. Never convert a pending external step into a pass because offline tests succeeded.

## Evidence and maintenance

For a supported release record commit/ref, OS/architecture, Python/tool versions, commands, UTC execution time, exit/result, report locations, reviewer, and limitations. Use [release maintenance criteria](../templates/release-maintenance.md) and the [evidence pack](../evidence-packs/README.md). The [worked release record](../evidence-packs/example-release.md) is labeled illustrative and must not be mistaken for execution evidence.

Before publishing a release: complete required checks, review tool pins and upstream changes, validate the intended sample/policy path, check local links and changed external references, verify expected artifact identity, record optional environment gaps, and attach sanitized evidence. Do not publish credentials or fabricate success for unavailable services.

Keep the 2026 edition's URLs stable where practical. Review dependency/action updates through normal PRs with compatibility evidence. A future annual edition should document migration and supported versions rather than duplicate unmaintained examples. A documentation site is an optional presentation layer after the executable path and navigation remain healthy.
