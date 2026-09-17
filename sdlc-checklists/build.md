# Build checklist

Scope / owner / review date: [fill]. Use [canonical controls](../templates/control-catalog.md).

- [ ] C03: required CI checks cover each proposed change and fail when expected.
- [ ] C04: local/CI SAST, dependency and secret checks retain reports and tool versions.
- [ ] C05: SBOM identifies the built artifact precisely.
- [ ] C11: suppressions reference reviewed, unexpired exceptions.

Attach check run, artifact references and failure-case evidence. Follow [secure CI criteria](../templates/secure-ci-guidelines.md).

Record manual code-review scope, observations, and missing regression coverage in the [application security assessment record](../templates/application-security-assessment.md); automated checks do not replace that review.
