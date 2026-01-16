# Phase 01: Shift Left

## Goals

- Catch secrets and common flaws before code leaves a laptop
- Make secure defaults the path of least resistance

## Practices

- Pre-commit hooks for secrets and SAST
- Secure coding guidelines and training
- IDE-integrated feedback

## Tools

- Secrets scanning: [Gitleaks](https://github.com/gitleaks/gitleaks), [Talisman](https://github.com/thoughtworks/talisman)
- Pre-commit framework: [pre-commit](https://pre-commit.com/)
- SAST: [Semgrep](https://semgrep.dev/)
- IDE security: [Snyk IDE](https://snyk.io/)

## Deliverables

- `.pre-commit-config.yaml` baseline
- Secure coding checklist
- Local SAST profile

## Lab

- [Lab 01: Pre-commit SAST](../../labs/lab-01-precommit-sast/README.md)
