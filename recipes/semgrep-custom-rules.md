# Semgrep Custom Rules

## Goal

Add project-specific rules to catch risky patterns.

## Example Rule

```yaml
rules:
  - id: no-hardcoded-password
    pattern: password = "..."
    message: "Do not hardcode passwords."
    severity: ERROR
    languages: [python]
```

## Usage

```bash
semgrep --config ./rules.yml .
```
