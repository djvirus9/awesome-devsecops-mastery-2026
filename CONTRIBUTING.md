# Contributing

Contributions should improve a reader's ability to understand, run or verify a defensive DevSecOps practice. Activity counts and automated badge commits are not acceptance criteria.

## Workflow and acceptance

1. Branch from the current default branch and keep scope reviewable.
2. Explain the concrete problem, resulting behavior and affected learning level. Include primary documentation for tool/version claims.
3. For a code or policy change, add meaningful positive/negative verification where behavior warrants it. Run `make setup`, `make test` and `make validate` from repository root; record exact results and any unavailable platform/tool checks.
4. Update affected docs, examples and canonical controls together. Label unexecuted integrations as design guidance; do not claim a platform run from static validation.
5. Open a PR with the source commit, commands/results, compatibility concerns, security impact and remaining limitations. Maintainers decide merge readiness; passing automation alone does not establish correctness.

Before committing, follow the [contributor attribution preflight](docs/contributor-attribution.md) to check the author identity and accurately credit shared work.

## Content criteria

- Tool entries explain purpose, maintained official source, license/access constraints, last verification date and when to choose the tool.
- Labs state prerequisites, local-only scope, expected artifacts, acceptance criteria, troubleshooting and cleanup.
- Examples use fictional data; no live credentials, third-party targets, unsolicited active scanning or exploitation workflows.
- Third-party actions/dependencies use reviewed immutable or reproducible references and a documented update path.
- Evidence distinguishes expected output from an actual observed result. Link the exact run/artifact when claiming validation.
- Security exceptions use [the shared record](templates/security-exception-template.md); broad permanent ignores need redesign.
- Preserve historical material under `archive/` with provenance rather than treating it as current guidance.

## Review and maintenance

Use [release/maintenance guidance](templates/release-maintenance.md), [canonical controls](templates/control-catalog.md) and the [pre-release checklist](checklists/pre-release.md). CODEOWNERS identifies review responsibility; required approval is a separate repository setting.

For vulnerabilities use [private reporting](SECURITY.md). For community behavior follow [the Code of Conduct](CODE_OF_CONDUCT.md).
