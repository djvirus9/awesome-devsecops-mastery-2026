# OPA Gatekeeper Policies

Gatekeeper/Gator **3.23.1** alternative exercises. Every constraint includes its required structural `templates.gatekeeper.sh/v1` ConstraintTemplate. Templates use the supported Rego v0 syntax in `targets[].rego`.

- [Require labels](require-labels.yaml)
- [Disallow hostPath](disallow-hostpath.yaml)

## Offline verification

```bash
.tools/bin/gator verify policies/opa/tests/suite.yaml
```

Seven cases check valid, missing, and empty labels, allowed volumes, disallowed hostPath volumes, and namespace scope. The same actual ConstraintTemplate code runs in Gator and the admission controller.

## Optional local installation

Use the dedicated Kind cluster from [the Kubernetes project](../../projects/k8s-gitops/README.md). This is an alternative lesson; install Kyverno for the main lab. Gatekeeper does not implement the other Kyverno controls in this pack.

```bash
helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts
helm repo update gatekeeper
helm upgrade --install gatekeeper gatekeeper/gatekeeper \
  --version 3.23.1 --namespace gatekeeper-system --create-namespace \
  --kube-context kind-devsecops-reference --wait --timeout 5m
kubectl --context kind-devsecops-reference apply -f policies/opa/templates/
kubectl --context kind-devsecops-reference wait \
  --for=condition=Established crd/k8srequiredlabels.constraints.gatekeeper.sh \
  crd/k8sdisallowhostpaths.constraints.gatekeeper.sh --timeout=60s
kubectl --context kind-devsecops-reference apply \
  -f policies/opa/require-labels.yaml -f policies/opa/disallow-hostpath.yaml
kubectl --context kind-devsecops-reference get k8srequiredlabels,k8sdisallowhostpath -o yaml
```

Templates must be installed before constraints because they create the corresponding CRDs. Check `status` for compilation errors and audit violations. Constraints initially use `enforcementAction: dryrun`. After inspecting those results, promote the exact constraints:

```bash
kubectl --context kind-devsecops-reference patch k8srequiredlabels require-app-label \
  --type=merge -p '{"spec":{"enforcementAction":"deny"}}'
kubectl --context kind-devsecops-reference patch k8sdisallowhostpath disallow-hostpath \
  --type=merge -p '{"spec":{"enforcementAction":"deny"}}'
kubectl --context kind-devsecops-reference apply --dry-run=server \
  -f policies/fixtures/hostpath.yaml
```

The last command must be rejected with the `disallow-hostpath` violation. Restore `dryrun` or reapply the two checked-in constraint files to return to audit. No Gatekeeper exception workflow is implemented here; the expiring exception exercise uses Kyverno.

References: [ConstraintTemplates](https://open-policy-agent.github.io/gatekeeper/website/docs/constrainttemplates/), [Gator](https://open-policy-agent.github.io/gatekeeper/website/docs/gator/), and [v3.23.1 release](https://github.com/open-policy-agent/gatekeeper/releases/tag/v3.23.1).
