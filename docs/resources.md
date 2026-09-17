# Resource index

Use [tool comparisons](tool-comparison.md) to make a selection and the [catalog](awesome-catalog.md) to discover alternatives. Exact reference versions and execution scope are in [tool-versions.json](../tool-versions.json) and [validation criteria](validation.md).

| Learning need | Official starting point | Apply it here |
| --- | --- | --- |
| Secure-development practices | [NIST SSDF](https://csrc.nist.gov/projects/ssdf), [OWASP SAMM](https://owaspsamm.org/model/) | Control catalog and domain maturity assessment. |
| Threat modeling | [OWASP threat modeling](https://owasp.org/www-community/Threat_Modeling) | Worked sample architecture and assumptions. |
| Source-rule feedback | [Semgrep docs](https://semgrep.dev/docs/), [pre-commit](https://pre-commit.com/) | Lab 01 shared configuration and fixtures. |
| CI trust | [GitHub Actions security](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) | Lab 02 permissions, required checks, and failure evidence. |
| Package inventory | [Syft docs](https://oss.anchore.com/docs/), [CycloneDX format](https://cyclonedx.org/) | Lab 03 image inventory; generator and standard are separate. |
| Artifact verification | [Sigstore](https://docs.sigstore.dev/), [SLSA](https://slsa.dev/spec/v1.2/build-track-basics) | Identity verification and build-trust reasoning. |
| API controls | [OWASP authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html), [OpenAPI](https://spec.openapis.org/oas/latest.html) | Lab 06 expected owner/route behavior. |
| Deployment security | [Kubernetes security](https://kubernetes.io/docs/concepts/security/), [Kyverno](https://kyverno.io/docs/) | Lab 04 policy behavior and optional admission. |
| Runtime signals | [Falco setup](https://falco.org/docs/setup/), [OpenTelemetry](https://opentelemetry.io/docs/) | Separate sensor prerequisites from offline detection tests. |
| Response/evidence | [OWASP logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) | Lab 07 sanitized evidence and recovery decisions. |

A successful link is not proof of current maintenance or suitability. Record your adopted version, operating model, license/cost, supported inputs, owner, and last validation. [Illustrative scenarios](case-studies.md) show planning tradeoffs without claiming measured customer results.
