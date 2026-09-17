# Shared configurations

The reference workflows explicitly consume these files. [tool-versions.json](../tool-versions.json) records the supported binary versions; action and image references are pinned in the workflows.

| Configuration | Consumer and behavior |
| --- | --- |
| [Semgrep](semgrep.yml) | `make sast` and CI scan sample source using local, language-specific rules; Lab 01 tests expected findings. This is a small teaching baseline, not comprehensive SAST coverage. |
| [Trivy](trivy.yaml) | CI filesystem and image scans fail on HIGH/CRITICAL findings, retain unfixed risks, and include the development lockfile explicitly. Database updates remain enabled. |
| [Syft](syft.yaml) | `make sbom` inventories the built sample image and writes `reports/sbom.cdx.json`. A source inventory must be labeled separately. |
| [Sigstore admission](cosign-policy.yaml) | Optional policy-controller configuration with an exact release workflow identity and image scope. It requires the matching controller, namespace enrollment, published image and live integration validation. |

Run `make validate` for configuration structure, `make sast` for rule execution, and `make policy-test` for policy behavior. Python dependency locks use hashes. To update locks after editing the `.in` files, use the same `uv pip compile --python-version 3.12 --generate-hashes` commands recorded in each generated lockfile header, then run tests and scanners. Review tool-release hashes and upstream changes before updating the binary manifest.

Unfixed vulnerabilities remain visible and blocking at the configured threshold. A suppression needs the documented [exception workflow](../templates/security-exception-template.md), scope and expiry; changing severity or disabling database updates to obtain a green result is not validation.
