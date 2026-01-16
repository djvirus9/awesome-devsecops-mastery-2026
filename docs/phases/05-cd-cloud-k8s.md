# Phase 05: CD, Cloud, and K8s

## Goals

- Enforce policy at deploy time
- Reduce misconfigurations and drift

## Practices

- Policy-as-code in CD
- Admission controls in K8s
- Environment promotions with approvals

## Tools

- Policy: [Kyverno](https://kyverno.io/), [OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/)
- GitOps CD: [Argo CD](https://argo-cd.readthedocs.io/), [Flux](https://fluxcd.io/)
- Cloud security: [Prowler](https://github.com/prowler-cloud/prowler), [ScoutSuite](https://github.com/nccgroup/ScoutSuite)

## Deliverables

- Baseline policy set
- Admission controller deployed
- Promotion rules and approvals

## Lab

- [Lab 04: K8s Admission Policies](../../labs/lab-04-k8s-admission-policies/README.md)
