# Lab 04: Kubernetes Admission Policies

**Canonical phase: 5 — CD, cloud, and Kubernetes.** Allow 60–90 minutes after the [sample API](../../samples/sample-api/README.md) and local container checks work. This lab uses Kubernetes 1.35.8, Kyverno 1.19.1, Helm chart 3.9.1, and the dedicated `kind-devsecops-reference` context from [the Kubernetes project](../../projects/k8s-gitops/README.md).

Finish with evidence that compliant workloads pass, risky settings identify the correct control, enforcement blocks, and a narrow exception stops applying after its deadline. Non-root and privileged-mode checks are separate policies: one cannot substitute for the other.

## 1. Check the policy logic offline

Run from the repository root:

```bash
python3 scripts/install_tool.py kyverno
python3 scripts/install_tool.py gator
PATH="$PWD/.tools/bin:$PATH" bash policies/verify.sh
```

Expected: 118 Kyverno assertions, seven Gator cases, and 12 direct policy evaluations of the actual reference Deployment and network-check Jobs pass. The suite includes positive and negative regular/init/ephemeral-container fixtures, nested workload templates, and active/expired exception cases. A negative fixture is expected to fail policy evaluation and therefore pass its regression test.

This offline step is verified in repository checks. The live steps below require Docker and have not been executed during this repository update. Dry-run admission checks do not start Pods.

## 2. Install and observe in audit mode

Complete only the **Create the local cluster** section of [the Kubernetes project](../../projects/k8s-gitops/README.md), then:

```bash
kubectl --context kind-devsecops-reference apply -f projects/k8s-gitops/base/namespace.yaml
kubectl --context kind-devsecops-reference create namespace policy-exceptions
helm repo add kyverno https://kyverno.github.io/kyverno/
helm repo update kyverno
helm upgrade --install kyverno kyverno/kyverno --version 3.9.1 \
  --namespace kyverno --create-namespace --kube-context kind-devsecops-reference \
  --set features.policyExceptions.enabled=true \
  --set features.policyExceptions.namespace=policy-exceptions \
  --wait --timeout 5m
kubectl --context kind-devsecops-reference apply \
  -f policies/kyverno/require-non-root.yaml \
  -f policies/kyverno/disallow-privileged.yaml \
  -f policies/kyverno/require-resource-limits.yaml \
  -f policies/kyverno/restrict-workload.yaml
kubectl --context kind-devsecops-reference get validatingpolicies
```

Wait for the policies' `READY` column to show true. The policy files use `Audit` and `Warn`; evaluation errors use `failurePolicy: Fail`. Check audit warnings with server dry runs:

```bash
kubectl --context kind-devsecops-reference apply --dry-run=server -f policies/fixtures/good.yaml
kubectl --context kind-devsecops-reference apply --dry-run=server -f policies/fixtures/privileged.yaml
```

Both dry runs should be allowed in audit mode. The second must include the privileged-mode warning. Record the policy name, object, and message. No noncompliant Pod is created. Now complete the project's **Deploy the reference app** section, confirm `/health`, and inspect persisted policy results:

```bash
kubectl --context kind-devsecops-reference -n devsecops-reference get policyreports -o yaml
```

Reports may appear after the background scan. Dry-run objects are not persisted and should not be expected in those reports.

## 3. Promote the same controls to enforcement

```bash
bash policies/set-mode.sh enforce
kubectl --context kind-devsecops-reference apply --dry-run=server -f policies/fixtures/good.yaml
kubectl --context kind-devsecops-reference apply --dry-run=server -f policies/fixtures/privileged.yaml
kubectl --context kind-devsecops-reference apply --dry-run=server -f policies/fixtures/override-root.yaml
kubectl --context kind-devsecops-reference apply --dry-run=server -f policies/fixtures/missing-limits.yaml
```

The compliant object should pass. Each remaining command should exit nonzero and identify `disallow-privileged`, `require-non-root`, or `require-resource-limits`, respectively. Check the actual policy message: an unavailable webhook or malformed manifest is not evidence that the intended control blocked it. Existing Pods are not evicted by switching to Deny; correct them and roll out the change explicitly.

To return to the starting mode:

```bash
bash policies/set-mode.sh audit
```

Switch back to enforcement before continuing. The helper mutates only the four named policies in the dedicated Kind context. Keep those mode changes in the lab evidence; a production implementation should promote policy through reviewed configuration.

## 4. Exercise a narrowly scoped, expiring exception

The only exception is for the `missing-limits` Pod in `devsecops-reference`, and only for the limits policy. Other objects and all other controls remain evaluated. The test Pod is never started.

```bash
python3 policies/render-exception.py --minutes 1 --ticket LAB-04 \
  --approver local-lab-owner --reason 'Demonstrate expiration using server dry runs' \
  > /tmp/devsecops-reference-exception.json
```

Inspect the JSON and its exact deadline, scope, and recorded approver. In an organization, obtain the actual approval before applying; metadata alone does not verify it. Only the local cluster operator has access to the dedicated exception namespace; the sample app receives no API privileges.

```bash
kubectl --context kind-devsecops-reference apply -f /tmp/devsecops-reference-exception.json
kubectl --context kind-devsecops-reference apply --dry-run=server -f policies/fixtures/missing-limits.yaml
kubectl --context kind-devsecops-reference apply --dry-run=server -f policies/fixtures/init-missing-limits.yaml
```

The exact Pod should now pass after the exception is reconciled. The init-container case must still fail because it has a different name. After the recorded deadline passes, repeat the `missing-limits.yaml` dry run: it must fail again. Both the `expiresAt` field and a CEL server-clock condition carry that deadline, so enforcement does not depend on deleting the exception on time. Clock synchronization matters. Expiration affects later admissions; it does not stop a running object.

```bash
kubectl --context kind-devsecops-reference -n policy-exceptions delete policyexception.policies.kyverno.io reference-limits-exercise
```

Keep the reviewed record and before/after command outcomes as evidence. The checked-in test exception with a 2099 timestamp is **only an offline fixture**; use the renderer's bounded lifetime for this exercise.

## 5. Complete the deployment checks and handoff

Run the project's **network boundary**, **drift**, and **rollback** exercises. Record the policy version, Git revision, actual denial messages, successful reference health check, network check logs, exception expiry result, and recovery result. Include failure investigation when a result differs from the expectation.

For troubleshooting, first inspect the named policy status and webhook Pods, then the exact container fields. In `Audit` mode, admission is deliberately allowed. In `Deny` mode, evaluate missing limits separately from non-root inheritance and privileged mode. Do not recursively apply `policies/` because it contains noncompliant fixtures.

Cleanup is `kind delete cluster --name devsecops-reference`, which deletes only this disposable cluster and its in-memory application data. Remove the reviewed temporary exception file when it is no longer needed.

The [Gatekeeper alternative](../../policies/opa/README.md) has complete templates and offline cases but covers a smaller control set. [Signed-image admission](../../projects/k8s-gitops/README.md#signed-release-extension) requires a released image, a separate policy-controller installation, namespace opt-in, and additional live verification.
