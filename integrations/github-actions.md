# GitHub Actions reference integration

Start with [the reference pipeline](../pipelines/github-actions/devsecops.yml) and [repository workflows](../.github/workflows/). Read the workflow's current triggers and permissions; copying a YAML file outside `.github/workflows/` does not activate it.

1. Prepare a repository with the documented Python/tool prerequisites. Run `make setup`, `make test` and `make validate` locally.
2. Review workflow permissions, immutable action references and fork behavior. Keep release credentials/OIDC out of untrusted PR execution.
3. Run the workflow in your repository and record actual job/check names. Configure branch/ruleset checks to require those names only after a successful initial run.
4. Prove a controlled failing check prevents the intended merge path; review bypass permissions and sole-maintainer recovery. CODEOWNERS identifies reviewers but is not by itself approval enforcement.
5. Inspect retained tests/scanner reports/SBOM artifacts and bind release evidence to the source commit and artifact digest. If signing or deployment is not configured, mark C06 not implemented.
6. Record platform-run URLs, tool versions, branch settings, artifact retention and any limitations in the [evidence index](../evidence-packs/evidence-index.md).

A workflow's presence is not evidence that checks are required or passing. Do not enable deployment/publishing permissions merely to complete a learning exercise.

Reference: [GitHub Actions security](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions).
