# 🛡️ The Ultimate End-to-End DevSecOps Roadmap (2026)

[![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38/badge.svg)](https://github.com/sindresorhus/awesome)
![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

> **"Security is not a gated process; it is a continuous thread."**
> This is a comprehensive, stage-by-stage guide to building a modern DevSecOps pipeline—from the first line of code to production runtime.

---

## Who This Is For

- Beginners: guided labs, curated tools, and clear adoption order
- Practitioners: production-ready controls, metrics, and templates
- DevOps/SRE/Security: a shared source of truth across disciplines

## Quick Start (10 minutes)

- Read the overview: [docs/README.md](docs/README.md)
- Run the first lab: [labs/README.md](labs/README.md)
- Align on SLAs: [templates/vuln-sla-matrix.md](templates/vuln-sla-matrix.md)
- See the pipeline example: [pipelines/github-actions/devsecops.yml](pipelines/github-actions/devsecops.yml)

## Golden Path

Recommended stack and order of adoption:

1. Shift-left hygiene: pre-commit + SAST ([Gitleaks](https://github.com/gitleaks/gitleaks), [Semgrep](https://semgrep.dev/))
2. CI PR gates: required checks + SCA ([GitHub Actions](https://docs.github.com/actions) + [Trivy](https://github.com/aquasecurity/trivy))
3. Supply chain: SBOM + signing ([Syft](https://github.com/anchore/syft) + [Cosign](https://github.com/sigstore/cosign))
4. DAST/API: staging scans ([OWASP ZAP](https://www.zaproxy.org/))
5. CD & K8s: policy-as-code ([Kyverno](https://kyverno.io/))
6. Runtime detection: eBPF alerts ([Falco](https://falco.org/))
7. IR + detections: runbooks and tuning

## Lab Navigation

- [Lab 01: Pre-commit SAST](labs/lab-01-precommit-sast/README.md)
- [Lab 02: CI PR Gates](labs/lab-02-ci-pr-gates/README.md)
- [Lab 03: SBOM and Signing](labs/lab-03-sbom-signing/README.md)
- [Lab 04: K8s Admission Policies](labs/lab-04-k8s-admission-policies/README.md)
- [Lab 05: Runtime Detection](labs/lab-05-runtime-detection/README.md)
- [Lab 06: DAST and API Testing](labs/lab-06-dast-api-testing/README.md)
- [Lab 07: IR and Detections](labs/lab-07-ir-detections/README.md)

## Key Docs

- Program overview: [docs/README.md](docs/README.md)
- Reference architecture: [docs/reference-architecture.md](docs/reference-architecture.md)
- Maturity model: [docs/maturity-model.md](docs/maturity-model.md)
- Metrics and KPIs: [docs/metrics.md](docs/metrics.md)
- Learning paths: [docs/learning-paths.md](docs/learning-paths.md)
- Resource index: [docs/resources.md](docs/resources.md)
- Tool comparison: [docs/tool-comparison.md](docs/tool-comparison.md)
- Case studies: [docs/case-studies.md](docs/case-studies.md)
- Cheatsheets: [docs/cheatsheets.md](docs/cheatsheets.md)
- Awesome catalog: [docs/awesome-catalog.md](docs/awesome-catalog.md)
- Glossary: [docs/glossary.md](docs/glossary.md)

## Practical Assets

- Project blueprints: [projects/README.md](projects/README.md)
- Ready configs: [configs/README.md](configs/README.md)
- Operational checklists: [checklists/README.md](checklists/README.md)
- Incident playbooks: [playbooks/README.md](playbooks/README.md)
- Policy packs: [policies/README.md](policies/README.md)
- Metrics dashboards: [dashboards/README.md](dashboards/README.md)
- Repo templates: [repo-templates/README.md](repo-templates/README.md)
- Skill maps: [skill-maps/README.md](skill-maps/README.md)
- Secure SDLC checklists: [sdlc-checklists/README.md](sdlc-checklists/README.md)
- Sample repos: [samples/README.md](samples/README.md)
- Integration guides: [integrations/README.md](integrations/README.md)
- Security testing recipes: [recipes/README.md](recipes/README.md)
- Incident metrics templates: [metrics-templates/README.md](metrics-templates/README.md)
- Maturity scorecards: [scorecards/README.md](scorecards/README.md)
- Evidence packs: [evidence-packs/README.md](evidence-packs/README.md)

## Real-world Examples

- [GitHub Actions starter workflows](https://github.com/actions/starter-workflows)
- [Semgrep rules](https://github.com/semgrep/semgrep-rules)
- [Trivy examples](https://github.com/aquasecurity/trivy)
- [Syft + Grype examples](https://github.com/anchore/syft)
- [Cosign examples](https://github.com/sigstore/cosign)
- [Kyverno policy library](https://github.com/kyverno/policies)
- [OPA Gatekeeper library](https://github.com/open-policy-agent/gatekeeper-library)
- [Falco rules](https://github.com/falcosecurity/rules)
- [OpenTelemetry demos](https://github.com/open-telemetry/opentelemetry-demo)

---

## 🧭 Roadmap Navigation

- [🔄 Phase 1: Shift Left (IDE & Pre-Commit)](#-phase-1-shift-left-ide--pre-commit)
- [🏗️ Phase 2: CI Security (Build & Static Analysis)](#-phase-2-ci-security-build--static-analysis)
- [📦 Phase 3: Supply Chain (SBOM & Artifacts)](#-phase-3-supply-chain-sbom--artifacts)
- [🌐 Phase 4: DAST & Application Testing](#-phase-4-dast--application-testing)
- [☸️ Phase 5: CD & Infrastructure (Cloud/K8s)](#-phase-5-cd--infrastructure-cloudk8s)
- [🕵️ Phase 6: Runtime & Threat Detection](#-phase-6-runtime--threat-detection)
- [🤖 Phase 7: AI-Driven Remediation (2026 Trend)](#-phase-7-ai-driven-remediation-2026-trend)

---

## 🔄 Phase 1: Shift Left (IDE & Pre-Commit)

*Goal: Catch vulnerabilities and secrets before they are even pushed to Git.*

- **[Gitleaks](https://github.com/gitleaks/gitleaks)**: Prevent hardcoded secrets (API keys, passwords) from being committed.
- **[Talisman](https://github.com/thoughtworks/talisman)**: A hook to scan outgoing changes for sensitive information.
- **[Pre-commit](https://pre-commit.com/)**: A framework for managing multi-language git hooks.
- **[Snyk IDE Plugin](https://snyk.io/)**: Real-time vulnerability feedback inside VS Code/JetBrains.

## 🏗️ Phase 2: CI Security (Build & Static Analysis)

*Goal: Automate code quality and vulnerability checks on every PR.*

- **SAST (Static Analysis)**:
  - **[Semgrep](https://semgrep.dev/)**: Ultra-fast, customizable static analysis.
  - **[SonarQube](https://www.sonarqube.org/)**: Comprehensive code health and security monitoring.
- **IaC Scanning (Infrastructure as Code)**:
  - **[Checkov](https://www.checkov.io/)**: Policy-as-code for Terraform, CloudFormation, and K8s.
  - **[KICS](https://kics.io/)**: Find security vulnerabilities and compliance issues in IaC.

## 📦 Phase 3: Supply Chain (SBOM & Artifacts)

*Goal: Secure your "Ingredients list" and ensure dependency integrity.*

- **SCA (Dependency Scanning)**:
  - **[Trivy](https://github.com/aquasecurity/trivy)**: Scans packages, OS libraries, and configurations.
- **SBOM Management**:
  - **[Syft](https://github.com/anchore/syft)** / **[Grype](https://github.com/anchore/grype)**: Generate and scan Software Bill of Materials.
- **Signature & Trust**:
  - **[Sigstore/Cosign](https://github.com/sigstore/cosign)**: Keyless signing to verify image provenance.

## 🌐 Phase 4: DAST & Application Testing

*Goal: Identify vulnerabilities in the running application (Dynamic Analysis).*

- **[OWASP ZAP](https://www.zaproxy.org/)**: World's most popular free DAST tool.
- **[Nuclei](https://github.com/projectdiscovery/nuclei)**: Template-based scanning for fast vulnerability detection.
- **[42Crunch](https://42crunch.com/)**: Dedicated security for APIs (REST/GraphQL).

## ☸️ Phase 5: CD & Infrastructure (Cloud/K8s)

*Goal: Secure deployment and cloud configuration.*

- **[Kyverno](https://kyverno.io/)**: Kubernetes admission controller to block non-compliant pods.
- **[Prowler](https://github.com/prowler-cloud/prowler)**: AWS, Azure, and GCP security assessment and hardening.
- **[ArgoCD](https://argoproj.github.io/cd/)**: Secure GitOps deployments with drift detection.

## 🕵️ Phase 6: Runtime & Threat Detection

*Goal: Observe behavior in production and block attacks.*

- **[Falco](https://falco.org/)**: The surveillance camera for Kubernetes (eBPF-powered).
- **[Trivy Operator](https://github.com/aquasecurity/trivy-operator)**: Continuous security scanning inside your cluster.
- **[Istio](https://istio.io/)**: Service mesh to enforce mTLS and zero-trust networking.

## 🤖 Phase 7: AI-Driven Remediation (2026 Trend)

*Goal: Move from "Finding" to "Fixing" automatically.*

- **[Plexicus](https://www.plexicus.ai/)**: AI agents that generate fix PRs for your security findings.
- **[Jit](https://www.jit.io/)**: Orchestrate your entire security stack in one developer-friendly portal.
- **[Mend.io](https://www.mend.io/)**: Automated patching of vulnerable open-source libraries.

---

## Repository Structure

- [docs](docs/README.md)
- [labs](labs/README.md)
- [templates](templates/)
- [pipelines](pipelines/)

## 🤝 Contributing

Contributions are welcome! If you have a tool or resource that fits the 2026 DevSecOps landscape, please open a PR.

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
