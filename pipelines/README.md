# Pipelines

The maintained reference is [the active GitHub workflow](../.github/workflows/devsecops-golden-pipeline.yml): application/metrics/detector tests, repository validation, real SAST, secret/dependency scanning, policy fixtures, container smoke checks, and image SBOM evidence. Its `Required checks` job fails when any required job fails, is cancelled, or is skipped. PR jobs have read-only repository permissions and no publishing identity.

[Release publishing](../.github/workflows/release.yml) is a separate manual action on `main`: it repeats required checks, builds/scans the image to publish, records its registry digest, signs/verifies it, generates build provenance, and retains verification evidence. It publishes to GHCR only when deliberately dispatched. Creating this workflow does not establish a SLSA level or prove cluster admission.

The [GitHub adapter](github-actions/devsecops.yml) calls the canonical workflow from the same checkout. Keep the shared files and workflow when copying it; do not replace the canonical workflow with the adapter. Use the [template generator](../repo-templates/README.md) for a complete copy.

The [GitLab adaptation](gitlab/.gitlab-ci.yml) uses shell-capable images, checksum-pinned tools, enforced gates, ordered artifacts, and GitLab.com OIDC verification. It produces a **source** SBOM, not a container SBOM. Configure the file as project-local CI, run GitLab CI Lint, and enable both protected branches and **Pipelines must succeed** before treating it as a merge gate. GitLab execution/signing and self-managed identity integration require platform validation; this repository's CI runs on GitHub.

[TeamCity](teamcity/README.md), [Jenkins](../integrations/jenkins.md), and [Azure DevOps](../integrations/azure-devops.md) are adaptation guides with explicit platform prerequisites, not execution evidence.
