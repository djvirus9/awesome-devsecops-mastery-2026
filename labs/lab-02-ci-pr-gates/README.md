# Lab 02: CI PR Gates

## Overview

Enforce security checks on pull requests with required status checks and risk-based policies.

## Objectives

- Add required checks for SAST and SCA
- Set clear failure thresholds
- Introduce a security exception workflow

## Time

45-60 minutes

## Prerequisites

- Repository admin access
- CI enabled (e.g., [GitHub Actions](https://docs.github.com/actions))

## Steps

1. Create a security workflow that runs on pull requests.
   ```yaml
   name: Security Checks
   on: [pull_request]
   jobs:
     scan:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: SAST
           run: echo "Run SAST" # https://semgrep.dev/
         - name: SCA
           run: echo "Run SCA" # https://github.com/aquasecurity/trivy
   ```

2. Enable branch protection for `main` and require the security checks.

3. Define thresholds (example: fail on Critical/High findings).

4. Add a security exception process using [templates/security-exception-template.md](../../templates/security-exception-template.md).

## Validation

- PRs cannot merge without passing required checks.
- Exceptions are documented and time-bound.

## Extensions

- Add [CodeQL](https://codeql.github.com/) and [Dependabot](https://docs.github.com/en/code-security/dependabot).
- Add license checks with [FOSSA](https://fossa.com/).
- Add automatic ticket creation on failed checks.
