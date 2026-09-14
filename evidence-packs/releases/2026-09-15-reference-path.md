# Reference-path validation — 15 September 2026

Actual execution evidence for the upstream GitHub reference, not an illustrative assessment or a production-readiness certification. The record date uses Asia/Kolkata; the executions below occurred on 14 September UTC. Collection and technical review were performed by Codex for repository owner `djvirus9`; no independent human approval is implied.

## Source and scope

The tested and released source is **`962bf398398a7318607a80b58401b025d7068734`**, the normal merge of [PR #285](https://github.com/djvirus9/awesome-devsecops-mastery-2026/pull/285). The main-branch runs below checked out that exact commit. Earlier PR runs tested their PR checkout, not an interchangeable main/release snapshot. This documentation record was added after the implementation commit and does not change its image identity.

Earlier implementation was merged through [PR #282](https://github.com/djvirus9/awesome-devsecops-mastery-2026/pull/282) and the release-verification correction through [PR #284](https://github.com/djvirus9/awesome-devsecops-mastery-2026/pull/284).

| Execution | Source / environment | Result and evidence |
| --- | --- | --- |
| Main baseline | `962bf398`; hosted Ubuntu 24.04 amd64; Python 3.12 and 3.14 | [Run 34904165956](https://github.com/djvirus9/awesome-devsecops-mastery-2026/actions/runs/34904165956) passed: 111 Python tests per selected Python version, repository checks, source rules, dependency/secret scans, policy fixtures, container smoke checks, image scan and SBOM. |
| Disposable platform | Same commit; hosted Ubuntu 24.04 amd64 | [Run 34904165985](https://github.com/djvirus9/awesome-devsecops-mastery-2026/actions/runs/34904165985) passed both Kubernetes and Grafana integration plus the required aggregate. Kubernetes evidence was retained at 22:31:12 UTC. |
| Image publication and verification | Same commit; hosted Ubuntu 24.04 amd64 | [Run 34904193368](https://github.com/djvirus9/awesome-devsecops-mastery-2026/actions/runs/34904193368), 22:27:24–22:29:03 UTC, passed the full reusable baseline and publication/verification job. |
| Released-image admission and deployment | Same commit and exact digest below | [Run 34904544605](https://github.com/djvirus9/awesome-devsecops-mastery-2026/actions/runs/34904544605), 22:31:37–22:36:48 UTC, passed the full default platform path plus trusted-provenance admission, wrong-identity/unmatched-image denials and the actual released-image rollout/API checks. |
| Fresh generated microservice | Same clean source; macOS arm64, Python 3.12.14; no Git metadata | 224 files copied. Hash-locked setup, 90 core + 8 generator + 13 runtime tests, 468 local-link checks and policy checks passed. No local container/cluster execution is implied. |

Policy CLI checks included 117 Kyverno expectations, nine generated deadline-guard cases, seven Gator cases and 12 direct evaluations of the supplied deployment/network Job manifests. Versions and checksums are in [tool-versions.json](../../tool-versions.json). Cluster versions: Kind 0.33.0, Kubernetes 1.35.8, Helm 3.22.0, Cilium 1.20.1, Kyverno 1.19.1/chart 3.9.1. The checked-in node/container digests define the remaining runtime pins.

## Released artifact and trust evidence

```text
ghcr.io/djvirus9/awesome-devsecops-mastery-2026/sample-api@sha256:f0bdd94a14a12295a451c9ef632e8d82871bfaf0c5c57e544626d2788f16d118
```

The published image is Linux amd64. The release's pre-push image configuration and layer identities match its scan evidence. At 22:28:39 UTC, Trivy 0.74.0 reported **zero HIGH/CRITICAL findings** across 38 OS and nine Python packages. This is a dated result of the configured severity gate, not an all-severity or exhaustive vulnerability-absence claim. No scan exception or reduced threshold was used.

Syft 1.51.1 produced a CycloneDX 1.7 SBOM with 964 components: 909 files, 47 libraries, seven applications and one operating system. Component counts are not package counts.

Cosign 3.1.3 verified the registry image signature and retained image bundle, and separately verified the unchanged SBOM bytes against their retained bundle. GitHub CLI verified SLSA v1 provenance both from the registry and from the saved bundle. The checks require:

- Signer: `https://github.com/djvirus9/awesome-devsecops-mastery-2026/.github/workflows/release.yml@refs/heads/main`.
- Issuer: `https://token.actions.githubusercontent.com`.
- Provenance source: exact commit `962bf398398a7318607a80b58401b025d7068734`, source ref `refs/heads/main`, repository `djvirus9/awesome-devsecops-mastery-2026`, and a GitHub-hosted runner.
- Verified invocation, matched during evidence review: release run `34904193368`, attempt 1; subject: the complete image digest above. The automated verifier enforces the source/ref/identity/issuer/runner contract, not a separate run-ID argument.

Use [verify_release.py](../../scripts/verify_release.py) for the repository's exact provenance verification contract. A signature by itself does not establish source review, safe application behavior or a SLSA assurance level. Registry access may require credentials; package visibility was not changed as part of this work.

### Public release evidence hashes

These are SHA-256 values of the individual, unchanged report files selected for release attachment. They differ from GitHub's compressed workflow-artifact digest.

| File | SHA-256 |
| --- | --- |
| `image.sigstore.json` | `261b09fe50fb6513b1d15e80e2df26121ceaf27cbb8275178cb3fe9ecf126ea3` |
| `sbom.cdx.json` | `7ac334bfed99b886449b73412bbc090534d25c9b30a3830a5838414ae9d05398` |
| `sbom.sigstore.json` | `a38f542c60467f3aeab3407aa633e63a03b84a30647c01b00f2b7bdec4e917ff` |
| `provenance-verification.json` | `871fb296e634b3e51682f6300ac1cee54a68367ddb9889047d1714eba3d7700b` |
| `release-scan.json` | `39304b9375664b61b102ea2355aaa577e6ecb2a74bdfb4ce6874887f5b4d49e7` |

The original `release-evidence` artifact is ID `10372301313`, archive digest `sha256:c8d9e9f438f19db0bf5d5dbbbe8d3c414db66cc810a41c58c91ccf739a38a8a2`, expiring 14 October 2026 UTC. Raw Docker inspection and the redundant registry-verification summary are kept in the maintainer archive rather than the minimal public asset set. Secret-scanner matches in release metadata were individually checked: they were public source tags and a public Python GPG fingerprint, not credentials. Signed SBOM bytes were not edited to suppress those matches.

## Observed Kubernetes behavior

The default main run created and removed its own single-node Kind cluster, using a private kubeconfig and synthetic application credentials. It confirmed:

- Audit acceptance and a named warning, followed by enforced acceptance/rejection decisions for the supplied fixtures.
- API health, required authentication, per-owner access, non-root execution, read-only root filesystem, writable temporary storage, dropped capabilities, no mounted service-account token and no Secret-reading permission.
- A narrowly scoped temporary exception with a separately enforced deadline guard. The exact object was accepted before the deadline; another object was denied. After the deadline, the guard denied the noncompliant object while the same exception persisted unchanged; a corrected object passed; revocation restored the original policy. This does not prove organizational approval routing.
- Allowed ingress from the labelled client and denied ingress from the unlabelled client, with DNS checked separately. Egress is configured but was not dynamically tested.
- An intentionally unavailable local image failed rollout; drift was detected; the old revision remained healthy; rollback restored health and a strict `kubectl diff` returned zero.
- Owned-cluster cleanup completed successfully. Negative admission fixtures were server-side dry runs, not deployed insecure workloads.

The main default Kubernetes artifact is ID `10372581031`, archive digest `sha256:cd47d097751a4d09449641c6cc13c012ab310024dab056e4ccc345516040cc31`, expiring 28 September 2026 UTC. It explicitly records that released-image admission was not requested in that default run.

### Signed-image admission and deployment

The separately dispatched run `34904544605` used the complete released digest above and the same source commit. Sigstore policy-controller v0.15.1, deployed with chart 0.10.8 and its explicit image digest, verified the signed SLSA v1 provenance bundle against the expected release workflow identity. The CLI separately verified the image signature. The evidence confirms:

- Trusted released-image Deployment accepted in a server-side dry run.
- Additional deliberately wrong workflow-identity policy rejected that same digest with a named certificate-identity error; removing the extra policy restored acceptance.
- An unrelated digest-pinned image was rejected because no policy matched. This is not an unsigned same-repository test.
- The released image actually rolled out, then passed health, authentication and ownership checks.
- The owned cluster was removed successfully. Temporary registry access was confined to the dedicated runner/namespace and cleanup scope; no registry credential is a public release asset.

Artifact ID `10372272439` has archive digest `sha256:64b0f3355933bf7185f8acd16e06f615d3c43479a501f53ae9ea5131590af201`, expiring 28 September 2026 UTC. Its public `result.json` has SHA-256 `5a55bf4a17984419c8d9db75bd7c56a28161ab6206187775184eff3b2d35a9d4`, records the exact image reference and 28 successful checks, and contains no command logs or credentials.

## Dashboard evidence and visual review

The main Grafana run executed from 22:27:12 to 22:28:10 UTC. Prometheus and Grafana queries returned the expected synthetic values: **18 hours** mean detection-to-resolution, **20 minutes** mean acknowledgment, and **two** closed incidents. These are fixture values, not operational KPIs or SLA results.

The official renderer produced three 1000 × 500 PNGs. Codex visually inspected the earlier rendered images for clear titles/values and rendering errors; the main-run PNGs are byte-identical to those accepted images. The harness itself checks values and PNG integrity, not subjective visual acceptance. Its cleanup error list was empty; no Docker ports were published to the host.

| Public image | SHA-256 |
| --- | --- |
| `panel-1.png` | `8a3c46b164b88fa49c34711781a783e7102c9f9a2338db52b0ebb36d49b1e884` |
| `panel-2.png` | `f386656560252357b3dfc8b4453a63ce9543d5801fca22a34694c7bc031f1269` |
| `panel-3.png` | `fa0ebbb3ce2d1cf780a7d23aa2ff262e524d008584f84e3e1b501384542f7f28` |

The dashboard artifact is ID `10371946220`, archive digest `sha256:8b9f689dfc026d5326f0d5fa4f13227b6ff98897a02126f191e14eaee46d3ea6`, expiring 28 September 2026 UTC.

## Merge enforcement and residual scope

`main` requires a PR, resolved conversations, an up-to-date branch, and both `Required checks` and `Platform checks` from GitHub Actions. A failed platform run left PR #285 blocked; after both checks passed, the exact head `aed80f4273d28e33224e943734066560c3adc71f` merged normally at 22:27:03 UTC without an administrator bypass. Private vulnerability reporting is enabled. Force pushes/deletion are disabled for the normal protected path. Mandatory approvals remain zero for this single-maintainer repository; administrators retain an explicit maintenance override. These settings are not installed by the template generator.

Not established by this record: GitLab execution without an authorized project/runner/identity destination; Argo CD/Flux reconciliation; cloud/serverless deployment; host-sensor operation; external alert delivery; Gatekeeper admission in a live cluster; dynamic egress denial; an unsigned same-repository admission fixture; independent human approval; or production readiness. The local Docker engine was unavailable, so container/cluster evidence comes from the scoped hosted runners, not the user's other Kubernetes contexts.

Release decision: the bounded GitHub learning reference passes its recorded baseline, supply-chain and disposable-platform criteria. Publication destination: the [dated GitHub Release](https://github.com/djvirus9/awesome-devsecops-mastery-2026/releases/tag/v2026.9.15), with selected sanitized reports, the signed-deployment summary, dashboard images and this record. Full command logs remain in the maintainer evidence archive; workflow-artifact retention is not permanent preservation. This record distinguishes successful execution from optional extensions; do not carry its passes over to another source revision, environment or generated repository without rerunning the relevant checks.
