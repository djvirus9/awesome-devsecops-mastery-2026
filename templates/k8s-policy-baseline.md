# Kubernetes policy baseline

[C07](control-catalog.md) requires an explicit policy engine/version, workload scope, exceptions and positive/negative verification. Start with [the supplied policies](../policies/README.md); read their coverage limits before adoption.

| Requirement | Evidence required before enforcement |
| --- | --- |
| No privileged workload, host networking or host namespaces | Rejected fixture plus an admitted compliant workload |
| Non-root execution, constrained capabilities, no privilege escalation | Tests covering regular, init and ephemeral containers where applicable |
| Resources bounded | Workload-specific requests/limits and availability review |
| No unrestricted host paths | Approved storage design and tested admission behavior |
| Trusted images | Exact registry/digest policy plus identity-aware signature verification when deployed |
| Restricted identity/network access | Service-account token needs, minimal RBAC and network-policy connectivity tests |

Use the [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) Restricted profile as a reference and record the Kubernetes version; these example policies do not claim full profile equivalence. Test in a disposable local cluster, audit first, review exclusions, then enforce in intended namespaces. Document break-glass approval, expiry and rollback. A static policy test does not prove live admission, CNI enforcement or image-signature verification.
