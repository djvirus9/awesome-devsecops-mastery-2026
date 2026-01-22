# Microservice API Security Project

## Goal

Build a secure microservice pipeline with CI gates, SBOM signing, and DAST.

## Scope

- REST API service with OpenAPI spec
- Containerized deployment
- Staging and production environments

## Deliverables

- CI pipeline with SAST, SCA, and SBOM
- Signed artifacts and verification gate
- DAST baseline scan in staging
- Alerts routed to incident workflow

## Suggested Stack

- CI: [GitHub Actions](https://docs.github.com/actions)
- SAST: [Semgrep](https://semgrep.dev/)
- SCA: [Trivy](https://github.com/aquasecurity/trivy)
- SBOM: [Syft](https://github.com/anchore/syft)
- Signing: [Cosign](https://github.com/sigstore/cosign)
- DAST: [OWASP ZAP](https://www.zaproxy.org/)

## Steps (High-Level)

1. Add CI gates for SAST and SCA.
2. Generate and sign SBOMs for every build.
3. Require signature verification before deploy.
4. Run ZAP baseline in staging.
5. Track findings and enforce SLAs.
