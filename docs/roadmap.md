# Roadmap

A practical plan to adopt DevSecOps in stages, with measurable milestones.

## Milestones

- Phase 1 (Weeks 1-2): Local guardrails + secrets scanning
- Phase 2 (Weeks 3-4): CI gates + required checks
- Phase 3 (Weeks 5-6): SBOM + artifact signing
- Phase 4 (Weeks 7-8): DAST + API testing in staging
- Phase 5 (Weeks 9-10): Policy-as-code in CD and K8s
- Phase 6 (Weeks 11-12): Runtime detection + alert routing
- Phase 7 (Weeks 13+): IR playbooks + detection tuning

## Deliverables

- Policy baselines: [templates/k8s-policy-baseline.md](../templates/k8s-policy-baseline.md)
- Vulnerability SLAs: [templates/vuln-sla-matrix.md](../templates/vuln-sla-matrix.md)
- Security exceptions: [templates/security-exception-template.md](../templates/security-exception-template.md)
- Pipeline samples: [pipelines](../pipelines/)
- Labs per phase: [labs](../labs/README.md)
