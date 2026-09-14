# Kubernetes Delivery and GitOps Foundation

Deploy the same [sample API](../../samples/sample-api/README.md) into a dedicated local Kind cluster, evaluate admission controls, exercise a network boundary, and recover a failed rollout. Allow 60–90 minutes and roughly 6 GiB of available Docker memory.

Implemented: Kustomize manifests, hardened runtime settings, namespace-scoped admission policies, local secret delivery, network controls, an executable network check, and manual drift/rollback exercises. Argo CD/Flux reconciliation, production approval routing, and an automatically verified GitOps promotion controller remain extensions. A directory of manifests alone is not a running GitOps system.

## Supported setup and verification status

The documented combination is Kind **0.33.0**, Kubernetes **1.35.8**, Cilium **1.20.1**, Kyverno **1.19.1** (Helm chart **3.9.1**), and kubectl **1.35.x**. The Kind node image is pinned by digest in `kind.yaml`. Use Docker Desktop on macOS or Docker Engine on Linux, Helm, and repository Python tooling. Install tools using their official release instructions.

The manifests and policy fixtures have been checked offline. The cluster/CNI/signature integration commands have **not** been executed during repository maintenance because the Docker daemon was unavailable. Completing the commands below supplies that integration evidence; do not infer it from an offline policy pass.

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

This replaces only the two named local test Jobs. A same-namespace client labelled `access: sample-api` must reach `/health`; the unlabelled client must resolve DNS successfully but time out connecting. Both Jobs must complete and print `PASS`. The API has no egress allowance because it needs no external service. NetworkPolicy uses pod labels as a policy boundary, so permission to create labelled Pods must be controlled separately. Port forwarding goes through the Kubernetes API and is not proof of CNI enforcement.

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

[The Sigstore policy](../../configs/cosign-policy.yaml) targets only that image repository and accepts only issuer `https://token.actions.githubusercontent.com` and the exact `release.yml@refs/heads/main` workflow identity. It does not accept every workflow from GitHub. It uses the v1beta1 API, with schema reference [policy-controller v0.15.1](https://github.com/sigstore/policy-controller/blob/v0.15.1/config/300-clusterimagepolicy.yaml).

To implement admission verification as a further integration exercise, install policy-controller **0.15.1** using its [official installation guide](https://docs.sigstore.dev/policy-controller/installation/), apply the policy, and opt the dedicated namespace in with `policy.sigstore.dev/include=true`. Switch the manifest to the verified `@sha256:` image and `imagePullPolicy: IfNotPresent`. Check acceptance of the expected signer and rejection of unsigned or unexpected-signer images using server dry runs. Keep policy-controller's unmatched-image rejection behavior; adding a permissive catch-all policy weakens the boundary. The namespace opt-in, registry access, signature-format compatibility, and admission results require live verification and are not part of the completed offline tests.

## Troubleshooting and cleanup

- `ErrImageNeverPull`: build and load the exact image tag into this Kind cluster; `imagePullPolicy: Never` prevents an accidental remote pull.
- `CreateContainerConfigError`: inspect whether `sample-api-tokens` exists and contains `API_TOKENS_JSON`.
- Denied workload: identify the named policy, inspect the container or Pod context, and fix the manifest before retrying. Reapplying policy YAML resets it to Audit/Warn.
- Network test failure: check both Job logs, Cilium readiness, service endpoints, and actual NetworkPolicy selection. A DNS failure is not an expected denial result.
- Unexpected cluster: stop and use the exact `kind-devsecops-reference` context; the helper scripts fix that context explicitly.

Delete only the named disposable cluster when the lesson is complete. This also removes its local Secret, Pods, and in-memory data:

```bash
kind delete cluster --name devsecops-reference
```

References: [Kind v0.33.0 images](https://github.com/kubernetes-sigs/kind/releases/tag/v0.33.0), [Cilium on Kind](https://docs.cilium.io/en/stable/installation/kind/), [NetworkPolicy semantics](https://kubernetes.io/docs/concepts/services-networking/network-policies/).
