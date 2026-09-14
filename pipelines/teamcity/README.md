# TeamCity adaptation

This is a platform adaptation guide; the maintained execution reference is [GitHub Actions](../../.github/workflows/devsecops-golden-pipeline.yml). No TeamCity server or agent was used to validate it. Keep the repository's scripts, configs, policies and samples together.

## Agent and build configuration

Use an isolated Linux x86_64 agent with Python 3.12+, Git, Make and Docker. Check out the exact source revision, install the [pinned tools](../../tool-versions.json) with `python3 scripts/install_tool.py syft trivy gitleaks kyverno gator cosign`, and put `.tools/bin` on the build's PATH. Install the declared Semgrep version from its reviewed distribution. Run from the checkout root:

```bash
make setup
make test validate
make sast
make policy-test
.tools/bin/gitleaks dir . --redact --no-banner --report-format json --report-path reports/gitleaks.json
.tools/bin/trivy fs --config configs/trivy.yaml --format json --output reports/trivy.json .
make container container-test sbom
.tools/bin/trivy image --config configs/trivy.yaml --scanners vuln --format json --output reports/image-scan.json devsecops-reference:local
```

Configure build failure on every nonzero command and publish `reports/**` on failure as well as success, with a retention period. Use a snapshot dependency to promote the same validated build revision; a green build label alone is not proof of those dependencies. Compare a controlled failing rule fixture and its correction before adopting the gate.

## Signing and release

The [signing lab](../../labs/lab-03-sbom-signing/README.md) preserves a bundle and constrains verification identity/issuer. TeamCity needs its own supported identity provider or managed signing key; GitHub/GitLab identity tokens do not appear automatically on a TeamCity agent. Configure that integration explicitly and require verified signatures before promotion. Do not run interactive signing in an unattended job or mark a missing signer successful.

The [manual GitHub release implementation](../../.github/workflows/release.yml) is an example of digest-linked image inventory, signing, provenance and verification. Adapting it requires registry credentials with scoped permissions, an expected TeamCity signer, equivalent provenance checks, and a tested rollback path. Record platform validation in the [evidence pack](../../evidence-packs/README.md).
