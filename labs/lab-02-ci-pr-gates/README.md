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

- GitHub repository admin access
- CI runner enabled

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
           run: echo "Run SAST"
         - name: SCA
           run: echo "Run SCA"
   ```

2. In GitHub Settings, enable branch protection for `main`.

3. Require status checks for the security workflow.

4. Define thresholds (example): fail build on Critical/High findings.

5. Add a security exception process:
   - Use an issue template for exceptions
   - Require a security approval label

## Validation

- PRs cannot merge without passing the required checks.
- Exceptions are visible and auditable.

## Extensions

- Add code coverage minimums.
- Add secret scanning and license checks.
- Add time-bound exceptions and auto-expiry.
