# Phase 4: API and running-application validation

Use [Lab 06](../../labs/lab-06-dast-api-testing/README.md), whose folder number is retained for compatibility. Required work uses the supplied local API and deterministic defensive tests.

Map each route and identity to expected access. Test authorized behavior as well as denied missing/invalid credentials and cross-owner requests. Keep the OpenAPI contract and response assertions aligned. A health endpoint does not establish authenticated route coverage.

A passive baseline inspects observed responses and can complement these tests. It does not prove application authorization. The reference path does not add active scanners or arbitrary external-target workflows. Any optional observation uses the synthetic isolated service and retains its report.

The application owner maintains contract/authorization tests; AppSec reviews requirements and triage. Definition of done: expected routes/owners covered, test failures visible, results retained, and TLS/gateway/real-identity coverage gaps documented. Continue to [Phase 5](05-cd-cloud-k8s.md).

References: [OpenAPI specification](https://spec.openapis.org/oas/latest.html), [OWASP authorization guidance](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html), [ZAP baseline coverage](https://www.zaproxy.org/docs/docker/baseline-scan/).
