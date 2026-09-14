# Kyverno Policies

Kyverno **1.19.1**, using the current `policies.kyverno.io/v1` `ValidatingPolicy` API. The old `ClusterPolicy` API is deprecated in this version. Local installation uses Helm chart **3.9.1**, whose application version is 1.19.1.

- [Require non-root](require-non-root.yaml)
- [Require resource limits](require-resource-limits.yaml)
- [Disallow privileged](disallow-privileged.yaml)
- [Restrict workload privileges and filesystem access](restrict-workload.yaml)

The policies start with `validationActions: [Audit, Warn]`. `failurePolicy: Fail` controls evaluation errors; it does not turn audit into enforcement. Promotion to `validationActions: [Deny]` is explicit in [Lab 04](../../labs/lab-04-k8s-admission-policies/README.md). Reapplying the checked-in files restores their initial audit mode.

The `podSpec` variable selects the actual Pod specification for each supported workload type. This also lets the offline CLI validate controller templates directly. Native autogeneration is disabled to avoid a second policy expansion of those explicit resource rules.

Non-root settings may be inherited from the Pod or set on each container; a container cannot override them with `false` or UID 0. Omitted `privileged` is valid because Kubernetes defaults it to false. Resource limits must be positive for regular and init containers. Ephemeral containers are deliberately excluded from the limits requirement because Kubernetes forbids their resource fields; they still receive the other checks.

## Expiring exception exercise

`python3 policies/render-exception.py --ticket LAB-04 --approver local-lab-owner --reason 'Observe the limit exception'` prints an exception JSON document without applying it. It is restricted to one Pod, in one namespace, for the resource-limit policy only, and expires in 15 minutes (maximum 120). Review the approval metadata before applying it in the local lab.

Both `expiresAt` and an explicit `time.now()` condition carry the same deadline. The time condition is exercised by the offline before/after tests; `expiresAt` alone was insufficient in the tested CLI. Expiration closes admission for future requests; it does not terminate an already-running workload. Applications receive no permission to create or edit exceptions. Exception creation is reserved for the cluster operator in the dedicated `policy-exceptions` namespace. Metadata records an approval; it does not authenticate the approver or implement organizational approval routing.

References: [v1.19.1 API schema](https://github.com/kyverno/kyverno/blob/v1.19.1/config/crds/policies.kyverno.io/policies.kyverno.io_validatingpolicies.yaml), [v1.19.1 exception schema](https://github.com/kyverno/kyverno/blob/v1.19.1/config/crds/policies.kyverno.io/policies.kyverno.io_policyexceptions.yaml), [policy exceptions](https://kyverno.io/docs/guides/exceptions/), and [CEL time functions](https://kyverno.io/docs/policy-types/cel-libraries/#time-functions).
