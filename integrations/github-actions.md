# GitHub Actions Integration

## Goal

Add SAST, SCA, SBOM, and signing to a GitHub Actions pipeline.

## Steps

1. Add a workflow similar to `pipelines/github-actions/devsecops.yml`.
2. Enable required status checks on `main`.
3. Store SBOM and signatures as artifacts.
4. Add branch protection for security approvals.

## References

- [Security hardening for GitHub Actions](https://docs.github.com/actions/security-guides/security-hardening-for-github-actions)
