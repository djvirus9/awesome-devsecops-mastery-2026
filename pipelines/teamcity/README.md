# TeamCity Pipeline

Reference steps to implement DevSecOps checks in TeamCity.

## Build Steps (Example)

1. Checkout code
2. SAST (Semgrep)
3. SCA (Trivy)
4. SBOM (Syft)
5. Signing (Cosign)
6. Publish artifacts

## Example Commands

- SAST:
  ```bash
  semgrep ci --config p/ci
  ```
- SCA:
  ```bash
  trivy fs --severity CRITICAL,HIGH --ignore-unfixed .
  ```
- SBOM:
  ```bash
  syft dir:. -o cyclonedx-json > sbom.json
  ```
- Signing:
  ```bash
  COSIGN_EXPERIMENTAL=1 cosign sign-blob --yes --output-signature sbom.sig sbom.json
  ```

## Notes

- Store SBOMs and signatures as artifacts
- Gate promotions on verified signatures
- Track policy exceptions using [templates/security-exception-template.md](../../templates/security-exception-template.md)
