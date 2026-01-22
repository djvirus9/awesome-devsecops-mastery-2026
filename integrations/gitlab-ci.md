# GitLab CI Integration

## Goal

Add SAST, SCA, and SBOM generation in GitLab pipelines.

## Steps

1. Add jobs similar to `pipelines/gitlab/.gitlab-ci.yml`.
2. Use GitLab protected branches for gating.
3. Store SBOM artifacts for traceability.

## References

- [GitLab Application Security](https://docs.gitlab.com/ee/user/application_security/)
