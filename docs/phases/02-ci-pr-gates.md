# Phase 02: CI PR Gates

## Goals

- Enforce security checks on every pull request
- Reduce risk with defined thresholds and exceptions

## Practices

- Required status checks and branch protection
- Risk-based fail thresholds
- Exception workflows with approvals

## Tools

- CI: [GitHub Actions](https://docs.github.com/actions), [GitLab CI](https://docs.gitlab.com/ee/ci/)
- SAST: [Semgrep](https://semgrep.dev/), [CodeQL](https://codeql.github.com/)
- SCA: [Trivy](https://github.com/aquasecurity/trivy), [Snyk](https://snyk.io/)
- Dependency updates: [Dependabot](https://docs.github.com/en/code-security/dependabot), [Renovate](https://docs.renovatebot.com/)

## Deliverables

- Required PR checks and branch protections
- Exception workflow and audit log
- Security checklist in PR templates

## Lab

- [Lab 02: CI PR Gates](../../labs/lab-02-ci-pr-gates/README.md)
