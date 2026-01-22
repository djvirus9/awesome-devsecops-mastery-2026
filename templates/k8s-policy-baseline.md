# K8s Policy Baseline

Minimum policies to reduce risk in Kubernetes deployments.

- Enforce non-root containers ([Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/))
- Require resource limits
- Restrict privileged and host networking
- Validate image sources and tags
- Require signed images where possible ([Cosign](https://github.com/sigstore/cosign))
