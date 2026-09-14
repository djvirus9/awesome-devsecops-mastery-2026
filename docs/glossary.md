# Glossary

| Term | Meaning in this reference |
| --- | --- |
| Authentication | Establishing the caller's identity from an accepted credential. |
| Authorization | Deciding whether that identity may perform this operation on this record. |
| Trust boundary | A point where data or actions cross between different control/permission domains. |
| SAST | Static application security testing: inspect source without exercising an external service. |
| SCA | Software composition analysis: identify component risks such as known vulnerable dependencies. |
| DAST | Dynamic application security testing: inspect a running application; passive observation and active tests have different scope. |
| SBOM | Software bill of materials: an inventory tied to the artifact and generator scope. |
| Artifact digest | Content identity of an artifact; distinguish an OCI manifest digest from a local image configuration ID. |
| Signature | Cryptographic evidence that a key signed particular bytes; trust still requires an expected signer. |
| Verification bundle | Retained signature/certificate and associated verification material. |
| OIDC | OpenID Connect, an identity protocol used by supported keyless signing and workload-identity flows. |
| Provenance | Evidence describing an artifact's claimed source and build process; evaluate its trusted builder and subject. |
| IaC | Infrastructure as code: versioned descriptions of infrastructure and configuration. |
| Admission policy | A deployment-time decision on a proposed Kubernetes resource. |
| OPA | Open Policy Agent, a policy evaluation engine; Gatekeeper integrates policy with Kubernetes admission. |
| Detection | An observation matching a rule; it does not automatically prove cause or prevent activity. |
| Telemetry heartbeat | A periodic signal used to distinguish a functioning source from missing data. |
| MTTA | Mean time to acknowledge; specify the population and clock, normally detected to acknowledged. |
| Incident recovery time | Detected to verified recovery/resolution under the selected incident definition. |
| Vulnerability remediation time | Validated finding to verified fix; different from incident recovery. |
| Exception | Approved, scoped, expiring risk treatment with owner and compensating controls. |
| Operating evidence | Result showing a control actually executed for an identified scope/time; configuration alone is insufficient. |

See [metric definitions](metrics.md), [architecture](reference-architecture.md), and [tool comparison](tool-comparison.md) for worked context.
