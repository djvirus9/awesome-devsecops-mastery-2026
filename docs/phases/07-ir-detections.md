# Phase 7: incident response and detection engineering

Complete [Lab 07](../../labs/lab-07-ir-detections/README.md) using the synthetic alert report from Phase 6. Phase 7 is incident response; AI-assisted remediation is an [optional advanced specialization](../../skill-maps/advanced.md).

The exercise assigns commander, application owner, SRE, and scribe. Its injects distinguish stale client configuration from authorization regression, and service recovery from telemetry recovery. Preserve evidence, identify unknowns, weigh containment impact, and record reversible decisions.

Definition of done: a completed incident record links evidence and timeline, documents acknowledgment/recovery clocks, shows required recovery checks, and assigns a corrective action with verification. A tabletop recovery is labeled simulated until a real practice environment supplies proof. Detections need positive, negative, boundary, and missing-source tests; tool installation alone is not detection engineering.

Use the [playbooks](../../playbooks/README.md), [metric definitions](../metrics.md), [control catalog](../../templates/control-catalog.md), and [worked tabletop solution](../../labs/lab-07-ir-detections/solution.md). A threat-technique catalog such as [MITRE ATT&CK](https://attack.mitre.org/) can inform coverage discussions; it is not evidence of cause or attribution for an alert.
