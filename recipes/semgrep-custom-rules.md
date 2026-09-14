# A tested, narrow Semgrep rule

The example catches a Python variable named `password` assigned a literal string. It is a rule-writing exercise, not a complete secret detector: other names and data flows are outside its scope. The fixture contains only fictional strings.

Files are supplied at [rules.yaml](semgrep/rules.yaml) and [rules.py](semgrep/rules.py). Install Semgrep using its [official installation guidance](https://semgrep.dev/docs/getting-started/), record `semgrep --version`, and run from repository root:

```bash
semgrep scan --validate --config recipes/semgrep/rules.yaml
semgrep scan --test recipes/semgrep
semgrep scan --error --config recipes/semgrep/rules.yaml recipes/semgrep/rules.py
```

Expected: schema validation and annotated tests succeed; the final scan reports one illustrative match and exits **1**. `severity: ERROR` is report metadata; `--error` makes findings fail this local-scan command. Tool/configuration errors are also failures and need separate triage. Do not treat an unexecuted scan as passing.

Add paired matching/nonmatching fixtures when changing the rule. Review exclusions and false positives before requiring it on application changes; do not broadly suppress errors to get a green build. This rule is not the repository-wide secret-scanning policy.

Validated locally on 2026-09-15 with Semgrep 1.176.0: configuration valid, annotated rule test passed (1/1), and the final scan returned one finding with exit 1 as expected. Validation used `--metrics off --disable-version-check` with the local rule. Re-run when upgrading or changing the fixtures.

Reference checked 2026-09-15: [Semgrep CLI and exit codes](https://docs.semgrep.dev/cli-reference).
