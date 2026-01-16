# Lab 01: Pre-commit SAST

## Overview

Add local guardrails so secrets and basic security issues are blocked before they reach the repo.

## Objectives

- Install a pre-commit framework
- Add secret scanning and SAST checks
- Fail commits on high-severity findings

## Time

30-45 minutes

## Prerequisites

- Git installed
- Python 3
- Basic familiarity with git hooks

## Steps

1. Install pre-commit.
   ```bash
   python3 -m pip install pre-commit
   ```

2. Add a `.pre-commit-config.yaml` with secret and SAST scanning.
   ```yaml
   repos:
     - repo: https://github.com/gitleaks/gitleaks
       rev: v8.18.1
       hooks:
         - id: gitleaks
     - repo: https://github.com/returntocorp/semgrep
       rev: v1.64.0
       hooks:
         - id: semgrep
           args: ["--config", "p/ci", "--error", "--severity", "ERROR"]
   ```

3. Install git hooks.
   ```bash
   pre-commit install
   ```

4. Create a deliberate secret or vulnerable snippet in a test file.

5. Attempt a commit and confirm it fails.

6. Fix the issue and re-commit.

## Validation

- Commits with secrets or high-severity findings are blocked.
- `pre-commit run --all-files` passes after fixes.

## Extensions

- Add language-specific SAST rules.
- Add a custom Semgrep rule pack.
- Run pre-commit in CI for parity with developer machines.
