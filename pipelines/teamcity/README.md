# TeamCity Pipeline

Reference steps to implement DevSecOps checks in TeamCity.

## Recommended Steps

- SAST: [Semgrep](https://semgrep.dev/), [CodeQL](https://codeql.github.com/)
- SCA: [Trivy](https://github.com/aquasecurity/trivy), [Snyk](https://snyk.io/)
- SBOM: [Syft](https://github.com/anchore/syft)
- Signing: [Cosign](https://github.com/sigstore/cosign)

## Notes

- Store SBOMs and signatures as artifacts
- Gate promotions on verified signatures
- Track policy exceptions
