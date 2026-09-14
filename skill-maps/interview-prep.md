# Interview preparation

Use your own [capstone evidence](../projects/microservice-api/README.md) to explain decisions. A tool definition alone is not a complete answer.

| Question | Evidence to discuss |
| --- | --- |
| Why can a green pipeline still miss a control? | Lab 02 command execution, failure semantics, and required-check configuration. |
| How do authentication and authorization differ? | Sample owner/route tests, including legitimate access and denied cross-owner reads. |
| What does a signed SBOM prove? | Inventory scope, expected signer verification, artifact identity, and remaining build/provenance assumptions. |
| Why might an admission fixture pass while deployment enforcement fails? | Rule result versus webhook availability, namespace scope, controller version, and actual request path. |
| How do you know quiet alerts mean healthy operations? | Lab 05 normal-event tests plus absent/stale heartbeat detection. |
| How do you respond without causing unnecessary outage? | Lab 07 evidence, competing hypotheses, reversible containment, and recovery criteria. |
| How do you measure improvement? | Dated domain rubric, inventory denominators, unresolved age, operating evidence, consistent clocks. |

Practice a five-minute walkthrough: state the requirement, show one failing and corrected result, explain a limitation, and identify the accountable owner. Then ask a peer to change one assumption, such as adding a second service, a new identity provider, or an unavailable telemetry collector. Explain which design and tests must change before claiming the same assurance.
