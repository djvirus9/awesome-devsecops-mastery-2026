# Lab 01: local source checks

Phase 1 · 30–45 minutes · local Python and Semgrep. Complete [foundation setup](../../docs/foundation.md). Install the Semgrep version declared in [tool-versions.json](../../tool-versions.json) using its [official installation guide](https://semgrep.dev/docs/getting-started/quickstart). Run from the repository root.

## Exercise

```bash
make setup
make test
make sast
```

`make sast` loads [configs/semgrep.yml](../../configs/semgrep.yml), fails on findings, and retains `reports/semgrep.json`. Read the actual rules before interpreting a clean result: this small local rule set is a baseline, not comprehensive code review.

The [harmless fixture](fixtures/no_eval.py) contains a constant arithmetic expression evaluated dynamically. It is only a scanner input; no user-controlled content or external system is involved.

```bash
semgrep scan --config configs/semgrep.yml --error --metrics off labs/lab-01-precommit-sast/fixtures/no_eval.py
```

Expect a `no-eval` finding and exit status 1. The next command validates the annotated positive and negative cases:

```bash
semgrep --test --config configs/semgrep.yml labs/lab-01-precommit-sast/fixtures/no_eval.py
semgrep --test --config configs/semgrep.yml labs/lab-01-precommit-sast/fixtures/no_eval.js
```

The solution is direct arithmetic or a purpose-built parser when parsing is a requirement. The fixtures show direct arithmetic as the allowed case. Python and JavaScript use separate language-specific rules; both annotated tests must pass. Keep deliberate fixtures out of the application scan scope.

## Hook and CI parity

The repository CI runs the same rule file. A local hook is a convenience; it does not enforce merge policy. The supplied local hooks use the pinned Semgrep package and a locally installed Gitleaks binary. Install pre-commit from its [official instructions](https://pre-commit.com/#installation), install Gitleaks through the reviewed tool helper, then run:

```bash
python3 scripts/install_tool.py gitleaks
pre-commit install
pre-commit run --all-files
```

Secret scanning is distinct from the arithmetic fixture. Never use a real credential as test input. If a real secret is exposed, notify its owner and revoke/rotate it before treating code removal as completion. The [secret-leak playbook](../../playbooks/README.md) covers the response.

## Verification and troubleshooting

Completion evidence: normal sample checks pass, the fixture produces the named finding, the annotated rule tests pass, and you can explain the fix. An empty result from the wrong path is not a pass.

If Semgrep is missing, verify its install and version. If no finding appears, confirm the selected configuration and fixture path. If a hook is bypassed, CI should still run; [Lab 02](../lab-02-ci-pr-gates/README.md) verifies that boundary. Keep reports local, retain sanitized result notes, and remove an optional practice hook with `pre-commit uninstall` if you no longer want it.

Challenge: explain why suppressing the entire sample directory would make this control ineffective. Solution: it removes the protected code from coverage; suppress only a reviewed, scoped case with a tracked rationale and expiry where the tool supports it.
