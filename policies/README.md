# Policy Packs

Executable, namespace-scoped teaching controls for the [reference application](../samples/sample-api/README.md). The starting mode reports violations; the lab explicitly promotes it to blocking. These packs cover different controls and are not interchangeable security baselines.

- [Kyverno policies](kyverno/README.md)
- [OPA Gatekeeper policies](opa/README.md)

## Verify without a cluster

From the repository root, install the pinned official CLIs and run the fixtures:

```bash
python3 scripts/install_tool.py kyverno
python3 scripts/install_tool.py gator
PATH="$PWD/.tools/bin:$PATH" bash policies/verify.sh
```

Supported policy tool versions: **Kyverno 1.19.1** and **Gatekeeper/Gator 3.23.1**. `verify.sh` rejects other versions. `KYVERNO_BIN` and `GATOR_BIN` can select an existing installation. No network or cluster is used during fixture evaluation.

The suite checks 118 Kyverno expectations, seven Gatekeeper cases, and all four Kyverno controls against the actual reference Deployment and both network-check Jobs (12 direct evaluations). It covers non-root inheritance and overrides, regular/init/ephemeral containers, omitted and zero limits, host namespaces, hostPath, capabilities, filesystem protections, token mounting, namespace boundaries, workload templates, and narrow active/expired exceptions. A negative fixture **passing its test** means the policy correctly rejected it.

`fixtures/` and the exceptions under `kyverno/tests/` are offline test inputs, including deliberately noncompliant objects. Do not recursively apply this directory to Kubernetes. Apply only the named policy files in [Lab 04](../labs/lab-04-k8s-admission-policies/README.md).

## Scope and limits

All workload checks target namespace `devsecops-reference`. Change scope deliberately when adapting them; these are not controls for every namespace. Kyverno covers Pods (including ephemeral-container updates), Deployments, ReplicaSets, StatefulSets, DaemonSets, Jobs, and CronJobs. Gatekeeper checks Pods only, including those created by controllers; its constraints cover non-empty labels and hostPath, not the complete Kyverno set.

Offline results do not establish webhook availability, RBAC configuration, CNI enforcement, image trust, or running container behavior. The local integration checks and cleanup are in [the Kubernetes project](../projects/k8s-gitops/README.md). The [Sigstore policy](../configs/cosign-policy.yaml) is a separate, opt-in registry integration; the local image is unsigned.
