# K8s GitOps Security Project

## Goal

Secure GitOps delivery with policy-as-code and verified artifacts.

## Scope

- GitOps CD pipeline (Argo CD or Flux)
- Kubernetes cluster with admission controls
- Signed container images

## Deliverables

- Admission policies enforcing non-root and signed images
- Drift detection and audit logs
- Exception workflow with approvals

## Suggested Stack

- GitOps: [Argo CD](https://argo-cd.readthedocs.io/), [Flux](https://fluxcd.io/)
- Policy: [Kyverno](https://kyverno.io/), [OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/)
- Signing: [Cosign](https://github.com/sigstore/cosign)

## Steps (High-Level)

1. Enable admission policies for baseline security.
2. Require signed images in production namespaces.
3. Enforce policy exceptions with approvals.
4. Monitor drift and audit policy violations.
