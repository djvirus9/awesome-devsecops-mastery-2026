# Kubernetes Delivery and GitOps Foundation

Deploy the same [sample API](../../samples/sample-api/README.md) into a dedicated local Kind cluster, evaluate admission controls, exercise a network boundary, and recover a failed rollout. Allow 60–90 minutes and roughly 6 GiB of available Docker memory.

Implemented: Kustomize manifests, hardened runtime settings, namespace-scoped admission policies, local secret delivery, network controls, an executable network check, and manual drift/rollback exercises. Argo CD/Flux reconciliation, production approval routing, and an automatically verified GitOps promotion controller remain extensions. A directory of manifests alone is not a running GitOps system.

## Supported setup and verification status

The documented combination is Kind **0.33.0**, Kubernetes/kubectl **1.35.8**, Helm **3.22.0**, Cilium **1.20.1**, and Kyverno **1.19.1** (Helm chart **3.9.1**). The Kind node image is pinned by digest in `kind.yaml`. Use Docker Desktop on macOS or Docker Engine on Linux and repository Python tooling. `python3 scripts/install_tool.py kind helm kubectl` installs checksum-pinned clients into `.tools/bin`; prepend that directory to PATH. Helm 3 migration is due before its [February 10, 2027 security-support end](https://helm.sh/blog/helm-v3-end-of-life).

The manifests and policy fixtures have been checked offline. Cluster/CNI/signature integration results require the separate platform-validation workflow; do not infer them from an offline policy pass. The local Docker daemon was unavailable during implementation.

## Automated disposable-cluster validation

On a dedicated **Linux amd64** Docker runner, from the repository root:

```bash
make setup
python3 scripts/install_tool.py kind helm kubectl cosign
bash projects/k8s-gitops/validate-live.sh
```

The harness refuses an existing `devsecops-reference` cluster or labelled orphaned nodes. It uses fresh temporary Kubernetes/Helm configuration, permits only a local Unix-socket Docker endpoint, creates the named cluster, and records JSON results and command evidence in a new `reports/k8s/` run directory. It tests API-valid Audit warnings, Deny controls, one-minute exception deadline enforcement, health/authentication/ownership, runtime hardening/RBAC, both ingress NetworkPolicy Jobs, drift, and rollback. The exception requires a separate exact-object admission guard: native `expiresAt` alone does not reliably revoke cached exceptions in this Kyverno version. The harness proves guard-specific denial while the exception still exists, corrected same-name acceptance, and restoration of the original policy before guard cleanup. See [Lab 04](../../labs/lab-04-k8s-admission-policies/README.md#4-exercise-a-narrowly-scoped-expiring-exception). Noncompliant Pods are **only server dry runs**. It deletes the successfully created cluster on normal completion, failure, or handled termination. A hard-killed process cannot clean up; an interrupted partial creation is explicitly reported for disposal with the dedicated runner, not silently claimed as cleaned up.

An optional `IMAGE_REFERENCE` must be an exact `ghcr.io/djvirus9/awesome-devsecops-mastery-2026/sample-api@sha256:...` digest from a successful release. This adds provenance admission, a deliberately wrong expected-identity denial, unmatched-image denial, and a real released-image rollout. Private GHCR access uses optional `REGISTRY_TOKEN`/`REGISTRY_USER` provided by the workflow: the pull Secret and registry credential file exist only in the disposable namespace/temp directory and are excluded from reports. The harness never publishes or signs an image. Its ingress checks do not dynamically prove egress denial; it does not publish an unsigned same-repository fixture or claim that negative test. See the [platform validation workflow](../../.github/workflows/platform-validation.yml) for current run evidence.

## Create the local cluster

Run from the repository root. All Kubernetes mutations below name the dedicated context explicitly.

```bash
make container
kind create cluster --config projects/k8s-gitops/kind.yaml
helm repo add cilium https://helm.cilium.io/
helm repo update cilium
helm upgrade --install cilium cilium/cilium --version 1.20.1 \
  --namespace kube-system --kube-context kind-devsecops-reference \
  --set ipam.mode=kubernetes --set kubeProxyReplacement=false \
  --set operator.replicas=1 --wait --timeout 5m
kubectl --context kind-devsecops-reference wait --for=condition=Ready nodes --all --timeout=120s
kind load docker-image devsecops-reference:local --name devsecops-reference
```

The cluster disables Kind's default CNI because it does not enforce Kubernetes NetworkPolicy. Install Cilium before waiting for nodes to become ready. This is a disposable, single-node learning setup, without ingress, public services, or high availability.

## Deploy the reference app

Complete the Kyverno installation and audit step in [Lab 04](../../labs/lab-04-k8s-admission-policies/README.md), then create an ephemeral local credential and deploy:

```bash
kubectl --context kind-devsecops-reference apply -f projects/k8s-gitops/base/namespace.yaml
kubectl --context kind-devsecops-reference -n devsecops-reference create secret generic sample-api-tokens \
  --from-literal='API_TOKENS_JSON={"demo-alice-token":"alice"}'
kubectl --context kind-devsecops-reference apply -k projects/k8s-gitops/base
kubectl --context kind-devsecops-reference -n devsecops-reference rollout status deployment/sample-api --timeout=120s
kubectl --context kind-devsecops-reference -n devsecops-reference port-forward service/sample-api 8080:8080
```

The published token is synthetic and only for this disposable localhost lesson. Production credentials require a secrets manager, rotation, and restricted API/storage access; Kubernetes Secrets are not encryption by themselves. In another terminal:

```bash
DEMO_ALICE_TOKEN='demo-alice-token'
curl --fail http://127.0.0.1:8080/health
curl --fail -H "Authorization: Bearer $DEMO_ALICE_TOKEN" http://127.0.0.1:8080/v1/items
```

The health request returns success; the items request returns the authenticated actor's items. Missing credentials should return 401. Data is held in memory and disappears on restart. Stop port forwarding with Ctrl-C.

The Service is ClusterIP only. The workload runs as UID/GID 10001, drops all capabilities, uses RuntimeDefault seccomp, disables privilege escalation, and has a read-only root filesystem plus bounded `/tmp`. Its ServiceAccount has no RoleBindings and no mounted API token because the app needs no Kubernetes API access.

## Check the network boundary

```bash
bash projects/k8s-gitops/check-network.sh
```

This replaces only the two named local test Jobs. A same-namespace client labelled `access: sample-api` must reach `/health`; the unlabelled client must resolve DNS successfully but time out connecting. Both Jobs must complete and print `PASS`. The API has no egress allowance because it needs no external service. The manifest uses explicit `policyTypes: [Ingress, Egress]` with no `egress` field: this is the [documented deny-egress form](https://kubernetes.io/docs/concepts/services-networking/network-policies/#default-deny-all-egress-traffic). Omitting an empty list avoids generation-only drift caused by API serialization in the pinned version; it does not grant outbound traffic. NetworkPolicy uses pod labels as a policy boundary, so permission to create labelled Pods must be controlled separately. Port forwarding goes through the Kubernetes API and is not proof of CNI enforcement.

## Drift and rollback exercise

Save rollout history, then simulate a benign deployment error using a missing local image:

```bash
kubectl --context kind-devsecops-reference -n devsecops-reference rollout history deployment/sample-api
kubectl --context kind-devsecops-reference -n devsecops-reference set image deployment/sample-api sample-api=devsecops-reference:missing-local-tag
kubectl --context kind-devsecops-reference -n devsecops-reference rollout status deployment/sample-api --timeout=45s
kubectl --context kind-devsecops-reference diff -k projects/k8s-gitops/base
```

The rollout should time out, and `diff` should exit 1 with the changed image. `maxUnavailable: 0` preserves the old healthy Pod while the new image fails. Recover using the retained revision:

```bash
kubectl --context kind-devsecops-reference -n devsecops-reference rollout undo deployment/sample-api
kubectl --context kind-devsecops-reference -n devsecops-reference rollout status deployment/sample-api --timeout=120s
kubectl --context kind-devsecops-reference diff -k projects/k8s-gitops/base
```

The last diff should be empty (exit 0), and `/health` should succeed again. Record the revision, observed failure, recovery duration, and health result. An Argo CD/Flux extension should reconcile these same manifests from a reviewed Git revision and demonstrate that a manual edit is detected and restored.

## Signed release extension

The checked-in `devsecops-reference:local` image is intentionally unsigned and never pulled. The repository's manually dispatched [release workflow](../../.github/workflows/release.yml) publishes `ghcr.io/djvirus9/awesome-devsecops-mastery-2026/sample-api` and signs its digest. After a successful release, verify that exact digest using the documented release verification command before changing a deployment.

[The Sigstore policy](../../configs/cosign-policy.yaml), `require-reference-release-provenance`, requires a signed **SLSA v1 provenance bundle** for that image repository and accepts only issuer `https://token.actions.githubusercontent.com` and the exact `release.yml@refs/heads/main` workflow identity. It does not accept every workflow from GitHub. Cosign 3 plain-signature bundles are not implemented in the pinned controller's signature verification API; this policy intentionally uses its supported attestation path. It uses the v1beta1 API, with schema reference [policy-controller v0.15.1](https://github.com/sigstore/policy-controller/blob/v0.15.1/config/300-clusterimagepolicy.yaml).

The automated signed path installs Helm chart **0.10.8**, whose default image is older, with an explicit **0.15.1** controller digest override, OCI1.1 discovery enabled, and unmatched-image behavior explicitly set to `deny`. The pin and exact arguments are in [the harness](validate_live.py). It applies the policy, opts only the dedicated namespace in with `policy.sigstore.dev/include=true`, and uses `imagePullPolicy: IfNotPresent` with the verified digest. Keep unmatched-image rejection; a permissive catch-all weakens this boundary. Namespace opt-in, registry access, signature-format compatibility, and admission results require a successful live workflow run. The current release builds Linux amd64; macOS arm64 learners should use the local image path rather than assuming release-image emulation.

## Troubleshooting and cleanup

- `ErrImageNeverPull`: build and load the exact image tag into this Kind cluster; `imagePullPolicy: Never` prevents an accidental remote pull.
- `CreateContainerConfigError`: inspect whether `sample-api-tokens` exists and contains `API_TOKENS_JSON`.
- Denied workload: identify the named policy, inspect the container or Pod context, and fix the manifest before retrying. Reapplying policy YAML resets it to Audit/Warn.
- Policies not ready: inspect `status.conditionStatus`; `RBACPermissionsGranted: False` for `pods/ephemeralcontainers` means the [read-only reporting RBAC](kyverno-report-rbac.yaml) from Lab 04 is missing. Do not remove the subresource match to silence the error.
- Network test failure: check both Job logs, Cilium readiness, service endpoints, and actual NetworkPolicy selection. A DNS failure is not an expected denial result.
- Unexpected cluster: stop and use the exact `kind-devsecops-reference` context; the helper scripts fix that context explicitly.

Delete only the named disposable cluster when the lesson is complete. This also removes its local Secret, Pods, and in-memory data:

```bash
kind delete cluster --name devsecops-reference
```

References: [Kind v0.33.0 images](https://github.com/kubernetes-sigs/kind/releases/tag/v0.33.0), [Cilium on Kind](https://docs.cilium.io/en/stable/installation/kind/), [NetworkPolicy semantics](https://kubernetes.io/docs/concepts/services-networking/network-policies/).
