# Tool selection and maintenance

Compare tools against the control you need, supported workload, operating effort, and evidence format. This is a September 2026 documentation review, not a benchmark or a claim that every listed integration was executed. Exact reference versions live in [tool-versions.json](../tool-versions.json); [validation scope](validation.md) records which paths exist.

## Comparable choices

| Need | Candidate and execution model | Good fit | Limitation / selection question |
| --- | --- | --- | --- |
| Source rules | [Semgrep CE](https://semgrep.dev/products/community-edition/), local/CI CLI | Small explicit rules and rapid feedback; used in this reference | CE analysis depth and language support differ from commercial features. Engine and rule licenses are separate. |
| Source dataflow | [CodeQL](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning), extracted code database | Supported languages where deeper query/dataflow analysis is required | Build/database setup and language support matter; verify entitlement for your repository. Not configured in the local reference. |
| Package/config findings | [Trivy](https://trivy.dev/docs/latest/), local/CI CLI and advisory data | Combined image/filesystem checks | Advisory freshness, package detection, explicit exit behavior, and database network access affect results. |
| Package findings from inventory | [Grype](https://github.com/anchore/grype), CLI and advisory data | Separate generator/scanner workflow, including SBOM input | Quality depends on input inventory; adds another database/tool to operate. Optional, not a second required scanner. |
| SBOM generation | [Syft](https://oss.anchore.com/docs/), local/CI CLI | Image/filesystem inventory in multiple formats | Inventories packages; does not establish vulnerability status or provenance by itself. |
| Artifact signing | [Cosign](https://docs.sigstore.dev/), CLI plus selected trust services | Sign and verify an artifact using explicit trust policy | Identity, issuer, subject digest, bundle retention, and service availability require planning. |
| Kubernetes policy | [Kyverno](https://kyverno.io/docs/), CLI/controller | Kubernetes-oriented policy authoring and admission | Offline rule results do not demonstrate cluster installation or enforcement; APIs vary by supported version. |
| Kubernetes policy | [Gatekeeper](https://open-policy-agent.github.io/gatekeeper/website/docs/), OPA/controller | Rego expertise and reusable constraints/templates | Requires matching ConstraintTemplates and constraints plus deployment tests. |
| Response inspection | [ZAP baseline](https://www.zaproxy.org/docs/docker/baseline-scan/), isolated container | Passive checks on observed synthetic responses | Cannot prove authorization coverage; report persistence and observation scope are required. |
| Runtime events | [Falco](https://falco.org/docs/setup/), host/cluster sensor | Rule-driven Linux event detection | Kernel/driver/privilege prerequisites, dropped events, and output delivery must be tested. Detection is distinct from prevention. |

These tools can have overlapping functions, but stacking them does not automatically improve coverage. Choose a representative fixture set, measure actionable results and maintenance effort, and record the reason for adding another tool.

## Standards and frameworks are different building blocks

| Reference | Type | How to use it |
| --- | --- | --- |
| [CycloneDX](https://cyclonedx.org/) | SBOM and related information standard | Choose an exchange format emitted by a generator such as Syft. |
| [SPDX](https://spdx.dev/) | Software information standard | Select a supported version/format accepted by downstream consumers. |
| [OpenAPI](https://spec.openapis.org/oas/latest.html) | API description specification | Describe routes/security expectations; pair with executable regression tests. |
| [SLSA](https://slsa.dev/spec/v1.2/build-track-basics) | Supply-chain assurance framework | Assess builder/provenance guarantees; do not label a signed artifact as a level by itself. |
| [OWASP SAMM](https://owaspsamm.org/model/) | Software assurance maturity model | Assess multiple security practices with evidence. |

## License, cost, and maintenance record

The local reference uses downloadable CLI tools and your own compute. Hosted features, private-repository entitlements, identity/registry services, and operating effort can add cost. Semgrep's engine is LGPL 2.1 while its maintained rules have separate terms; see its [license explanation](https://semgrep.dev/blog/2024/important-updates-to-semgrep-oss/). Consult each project's license and provider terms for the exact version/use case before redistribution or commercial integration; this table does not compare current subscription prices.

For each adopted tool record purpose, accountable owner, upstream source, exact version/digest, operating platform, language/input support, license/cost model, required network/data access, tested command, known limitations, last successful run, and next review. Treat the [catalog](awesome-catalog.md) as discovery material. Pin updates deliberately and attach compatibility evidence; a link's availability is not a tool-maintenance assessment.
