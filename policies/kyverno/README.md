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

After `make setup`, `.venv/bin/python policies/render-exception.py --ticket LAB-04 --approver local-lab-owner --reason 'Observe the limit exception'` prints an exception JSON document without applying it. It is restricted to one Pod, in one namespace, for the resource-limit policy only, with a deadline in 15 minutes (maximum 120). **Do not apply it alone:** render its companion with `--guard-for <exception.json>` and follow the guard-first sequence in [Lab 04](../../labs/lab-04-k8s-admission-policies/README.md#4-exercise-a-narrowly-scoped-expiring-exception).

Native `spec.expiresAt` records the deadline but is **not the enforcement mechanism** here. Kyverno 1.19.1 filters expired exceptions when compiling policies, without a deadline-triggered cache eviction. Its separate PolicyException admission compiler also does **not** expose `time.now()` in match conditions; adding that expression makes the exception invalid even though the offline evaluator accepts it. The CLI does not enforce `expiresAt` from supplied exception files. Neither is evidence of timely native expiry.

The generated `reference-limits-deadline` ValidatingPolicy uses the full policy compiler's supported `time.now()` and evaluates each admission. It derives variables, original Pod/subresource rules, and limits expressions from `require-resource-limits.yaml`, narrows them to the exact Pod, and requires the original limits after the deadline. It uses `Deny`, `failurePolicy: Fail`, and no background evaluation. The native exception never references this guard. No cleanup controller or additional delete privileges are needed.

Install and wait for the guard **before** granting the exception. After the deadline, the live harness requires a guard-specific denial while the unchanged exception still exists, and acceptance of a corrected same-name Pod. Revoke the exception, confirm the original limits policy denies, and only then remove the guard. Until a successful platform run, the live transition remains an acceptance requirement, not a claimed result. Clock synchronization and webhook availability matter; this controls later admissions, not already-running objects. Applications receive no permission to edit exceptions or policies. Creation is reserved for the cluster operator in the dedicated lab. Metadata records an approval; it does not authenticate the approver or implement organizational approval routing.

References: [v1.19.1 API schema](https://github.com/kyverno/kyverno/blob/v1.19.1/config/crds/policies.kyverno.io/policies.kyverno.io_validatingpolicies.yaml), [v1.19.1 exception schema](https://github.com/kyverno/kyverno/blob/v1.19.1/config/crds/policies.kyverno.io/policies.kyverno.io_policyexceptions.yaml), [exception admission compiler](https://github.com/kyverno/kyverno/blob/v1.19.1/pkg/cel/compiler/policy_exception.go), [full policy time library](https://github.com/kyverno/kyverno/blob/v1.19.1/pkg/cel/policies/vpol/compiler/compiler.go), and [cached exception evaluation](https://github.com/kyverno/kyverno/blob/v1.19.1/pkg/cel/policies/vpol/compiler/policy.go).
