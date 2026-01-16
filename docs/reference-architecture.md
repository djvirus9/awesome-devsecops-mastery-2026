# Reference Architecture

A reference DevSecOps architecture that integrates security across the SDLC.

## Core Flow

1. Developer workstation: pre-commit hooks, local SAST
2. Source control: branch protection, required reviews
3. CI: SAST, SCA, secret scanning, IaC scanning, SBOM
4. Artifact: signing, attestations, provenance
5. CD: policy-as-code, approvals, environment promotion
6. Runtime: detection, logging, alert routing
7. IR: playbooks, metrics, continuous improvement

## Reference Stack (Example)

- SCM: [GitHub](https://github.com/), [GitLab](https://about.gitlab.com/)
- Pre-commit: [pre-commit](https://pre-commit.com/), [gitleaks](https://github.com/gitleaks/gitleaks)
- SAST: [Semgrep](https://semgrep.dev/), [CodeQL](https://codeql.github.com/)
- SCA: [Trivy](https://github.com/aquasecurity/trivy), [Snyk](https://snyk.io/)
- IaC: [Checkov](https://www.checkov.io/), [KICS](https://kics.io/)
- SBOM: [Syft](https://github.com/anchore/syft), [CycloneDX](https://cyclonedx.org/)
- Signing: [Cosign](https://github.com/sigstore/cosign), [SLSA](https://slsa.dev/)
- DAST: [OWASP ZAP](https://www.zaproxy.org/), [Nuclei](https://github.com/projectdiscovery/nuclei)
- K8s policy: [Kyverno](https://kyverno.io/), [OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/)
- Runtime detection: [Falco](https://falco.org/)
- Observability: [OpenTelemetry](https://opentelemetry.io/), [Prometheus](https://prometheus.io/)
- Incident response: [PagerDuty](https://www.pagerduty.com/), [TheHive](https://thehive-project.org/)

## Controls by Stage

- Shift-left: secrets scanning, secure coding standards, linting
- CI: policy gates, SBOM generation, signing
- CD: admission control, configuration drift checks
- Runtime: detection rules, response workflows

## Key Outputs

- SBOM and provenance for every release
- Signed artifacts with verification
- Audit trails for exceptions and approvals
- Measurable security KPIs
