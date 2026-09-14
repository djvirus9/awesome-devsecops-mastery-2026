# Phase 5: CD, cloud, and Kubernetes

Use [Lab 04](../../labs/lab-04-k8s-admission-policies/README.md). Local policy evaluation and live cluster admission provide different evidence; preserve the historical lab URL and record both scopes explicitly.

## Control progression

Start with supplied allowed/denied fixtures and the [policy pack](../../policies/README.md). In a disposable supported cluster, inventory workloads, introduce policies in a reviewed rollout, observe denials, and then enforce. Evaluate applicable normal, init, and ephemeral container settings and inherited security context where the selected rule requires them.

Platform owners also need a deployment design for workload identity/RBAC, namespace/network boundaries, secret delivery, resource limits, and expected image verification. Release owners promote immutable artifacts with retained evidence and a reversible rollback target. Cloud-provider permissions and hosting are environment choices, not provisioned assumptions.

Definition of done for local work: allowed/denied fixtures have expected results. Cluster completion additionally needs controller/version setup, installation order, admission observations, scoped exceptions, drift handling, rollback, and cleanup. The [GitOps project](../../projects/k8s-gitops/README.md) describes the extension.

References: [Kubernetes security contexts](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/), [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/), [Kyverno](https://kyverno.io/docs/), [Gatekeeper](https://open-policy-agent.github.io/gatekeeper/website/docs/howto/).
