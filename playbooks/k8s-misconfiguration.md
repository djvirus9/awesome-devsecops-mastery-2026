# Playbook: Kubernetes misconfiguration

Apply [shared roles/evidence rules](README.md). Trigger: drift, admission violation or insecure workload configuration. Record cluster/context, namespace, workload/controller, policy version, exposure and business criticality.

| Decision | Action / owner | Evidence and exit condition |
| --- | --- | --- |
| Configuration defect or active compromise? | Incident lead assesses workload/audit evidence | Severity and uncertainty recorded; suspected compromise expands scope |
| Immediate isolation needed? | Service owner selects bounded containment with incident lead | Availability impact, dependent services and rollback recorded before disruptive changes |
| Evidence at risk? | Evidence custodian captures allowed workload/audit/configuration state before restart/scale-down when feasible | Restricted, timestamped records; collection must not unnecessarily delay urgent containment |
| Durable fix available? | Platform owner fixes source IaC/controller configuration and tests policy fixtures | Change survives reconciliation; compliant deployment accepted |
| Ready to restore? | Service owner validates health, policy enforcement, intended identity/network access and drift monitoring | Recovery approval and monitoring period recorded |

Do not respond to every policy violation by indiscriminately scaling down workloads. Emergency exclusions need [C11 approval and expiry](../templates/security-exception-template.md). In a disposable local tabletop, prove the team can choose a safe rollback and distinguish static policy tests from real admission behavior.
