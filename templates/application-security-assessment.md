# Application security assessment record

Use this working record to plan an authorized VAPT (vulnerability assessment and penetration testing), mobile-security assessment, or manual code review. It coordinates scope and evidence; it is not authorization, an executable penetration-testing procedure, a completed assessment, or certification.

Start with [canonical controls](control-catalog.md), the [threat model](threat-model-template.md), and the [evidence index](../evidence-packs/evidence-index.md). The runnable learning path in this repository uses local, synthetic fixtures only. This repository supplies no mobile application or device lab.

## 1. Identify the assessment subject

- Assessment ID, purpose, owner, reviewer, and assessment date: [fill].
- Repository, base/head commit or reviewed source revision, and included paths: [fill].
- Application/build version, artifact digest, environment, and backend version: [fill].
- Mobile scope, if applicable: package/bundle ID, build variant, device/emulator, OS version, and supported versions not assessed: [fill].
- Security requirements, threat-model revision, and selected external framework version/control IDs: [fill]. Record a release or source revision for changing online guidance.
- Evidence classification, access restrictions, retention/deletion date, and evidence-index location: [fill]. Keep real credentials, customer data, and sensitive reports out of public commits.

## 2. Agree on scope before testing

| Planning item | Agreed value / approval reference |
| --- | --- |
| Accountable owner and authorization | [named approver, approved scope, dated reference] |
| Included and excluded systems | [exact assets, environments, components; third-party dependencies are not automatically authorized targets] |
| Permitted methods | [source/configuration review, named local tests, or separately approved assessment procedures; limits and prohibited actions] |
| Test identities and data | [synthetic roles/owners, fixture reset owner; no credentials in this record] |
| Time window and operational limits | [dates/timezone, approved rate/concurrency where applicable, monitoring contact] |
| Stop and recovery conditions | [unexpected sensitive data, service impact, scope ambiguity; stop contact, rollback/cleanup owner, resumption approval] |

An incomplete approval or unclear boundary is a reason to pause, not an implicit extension of scope. Use [NIST SP 800-115 (2008)](https://csrc.nist.gov/pubs/sp/800/115/final) as planning background; the exact rules must be agreed for the assessment at hand. This template adds no active scanner or external-target workflow.

## 3. Record coverage separately from results

Create one row per security requirement and relevant platform/identity. Expand the table as needed; these illustrative rows have **not** been executed by filling in this template.

| ID / requirement | Location and identity | Planned method / expected behavior | Execution state | Observed result / evidence / limits |
| --- | --- | --- | --- | --- |
| COV-01 / C02: owner-scoped item access | Local sample API, `item_detail`, synthetic Alice/Bob | Existing regression: owner succeeds; different owner cannot read the item | Planned | Not run for this record; attach actual run and reviewed commit |
| COV-02 / [selected mobile control] | [app build, platform, relevant storage paths] | [approved source/device checks and expected sensitive-data handling] | Not assessed | No mobile target supplied; no result inferred from API tests |
| COV-[ID] / [requirement] | [file/function, route, build, role] | [method and expected behavior] | [state] | [actual observation, evidence ID, coverage limits] |

Execution states: **Planned**, **Performed**, **Blocked**, **Not assessed**, or **Not applicable**. A blocked item needs a reason and follow-up owner; N/A needs a scope-based rationale and reviewer. For performed work, record the outcome separately: **requirement met in stated scope**, **issue observed**, or **inconclusive**. Tool errors and missing access are not passes. Expected behavior is never an observed result.

## 4. Manual code-review prompts

Record exact file/function references and a reviewed commit for each applicable prompt. A grep match or scanner alert is a lead, not a confirmed vulnerability.

- Trace entry points through validation, transformations, authorization decisions, and sensitive operations; include affected callers and error paths outside the diff.
- Check who may perform each operation on each object. Authentication and client-side checks do not replace the server's authorization decision. Include valid and denied behavior in regression coverage.
- Review sensitive-data storage and logging, configuration defaults, dependency changes, cryptographic API usage, file/network boundaries, and resource limits where relevant to the change.
- Distinguish a demonstrated issue from a hypothesis or hardening suggestion. Record preconditions, the reachable code path, impact, confidence, and the smallest remediation or next verification step.
- Identify the regression that would detect a recurrence. Record whether it was run, on which revision, and what remains outside its scope.

These prompts complement automated checks; they do not establish a whole-codebase review. Background: [OWASP secure code review](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html) and [authorization guidance](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

## 5. Mobile review prompts

Use the selected [OWASP MASVS](https://mas.owasp.org/MASVS/) controls and [MASTG](https://mas.owasp.org/MASTG/) procedures to define concrete coverage rows. These short prompts are not a complete standards mapping. Keep native-client and backend evidence separate.

| Area | Question to resolve with source/configuration references and approved test evidence |
| --- | --- |
| Storage | Where can sensitive data persist, including backups, logs, caches, and screenshots? |
| Cryptography | Where are keys generated, protected, used, rotated, and removed? |
| Authentication | Which decisions are local, which are server-enforced, and how are sessions ended? |
| Network | Which endpoints, trust settings, and network exceptions ship in this build? |
| Platform | Which permissions, exported components, deep links, entitlements, and WebView interfaces are exposed? |
| Code and updates | Which dependencies, supported OS versions, and debug/release settings affect this artifact? |
| Privacy | Which data and SDK flows are necessary, disclosed, retained, and deleted? |
| Resilience | Which threat-specific integrity requirements apply, and what are their limitations? |

Record the adopted MASVS version and specific controls; do not label this short record as an L1/L2/R certification. MASVS 2.0 onward no longer contains the old verification levels. Static configuration review does not establish runtime behavior on every device. Missing mobile fixtures mean **not assessed**, not a successful mobile assessment. Client hardening does not prove backend authorization, and privacy review does not prove legal compliance.

## 6. Findings, retest, and handoff

For each observation, record its ID, affected revision/artifact, exact location, preconditions, actual evidence, impact/confidence, disposition, remediation owner, and next action. Separate confirmed findings, hypotheses, and hardening advice. Use the existing [SLA policy template](vuln-sla-matrix.md) and [exception record](security-exception-template.md); do not invent a second deadline policy here.

Retest links must identify the changed revision/artifact, original requirement, observed result, and reviewer. A merged fix or approved exception is not proof that the deployed issue is resolved. Preserve the original finding and detection time.

- Blocking findings / unresolved requirements and release decision owner: [fill].
- Follow-ups, unassessed or blocked coverage, accountable owners, and due dates: [fill].
- Residual risk and approved, bounded exception references: [fill].
- Evidence completeness, sanitized publication scope, cleanup, and final reviewer/date: [fill].

## Local starting point

For COV-01, inspect the supplied [API source](../samples/sample-api/app.py) and [authorization tests](../tests/test_sample_api.py), then follow [Lab 06](../labs/lab-06-dast-api-testing/README.md). From the repository root:

```sh
make setup
git rev-parse HEAD
.venv/bin/python -m unittest discover -s tests -p 'test_sample_api.py' -v
```

Attach the actual output and revision to your own record before changing its status. The suite uses an in-process Flask client and fictional identities, not a network target. It provides no mobile, production identity-provider, TLS gateway, or full VAPT coverage. Consult the [validation boundaries](../docs/validation.md) before extending any claim.
