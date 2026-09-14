# Secure CI adoption criteria

Use [C03–C06](control-catalog.md) with the [GitHub integration](../integrations/github-actions.md). These are requirements to verify, not claims about a newly copied workflow.

- Pin third-party actions to full commit SHAs and retain readable version comments; pin build dependencies and image digests where reproducibility requires them. Automate reviewed update PRs.
- Default job permissions to read-only; grant write or OIDC permissions only to the job that needs them. Untrusted pull-request code must not receive publishing credentials or execute in a privileged release context.
- Separate tests from release/promotion. Scope short-lived identity to expected repository, workflow, branch/tag and environment.
- Make both scanner execution errors and policy-blocking findings fail. Prove this with a controlled failing fixture; uploading a report alone is not a gate.
- Configure repository merge checks explicitly. Document expected check names and fork behavior; consider sole-maintainer recovery before making approvals mandatory.
- Keep artifacts even on failed checks when safe; redact secrets and define access/retention. Link reports, SBOM and provenance to a specific commit and artifact digest.
- Verify signatures and provenance against a defined issuer/identity/digest policy before promotion. Signing a report is not equivalent to signing a deployable artifact.
- Record exceptions through C11; expired exceptions must not silently keep a gate open.

References: [GitHub Actions security](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions). Record the actual check run and platform configuration in the [evidence index](../evidence-packs/evidence-index.md).
