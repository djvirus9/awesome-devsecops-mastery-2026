# Incident decision playbooks

These templates require a named incident lead, service owner, evidence custodian and communications owner before operational use. Define contact routes, severity criteria, response objectives and update cadence for your organization; no response promise is made by this repository.

1. Record trigger, affected scope, detection timestamp and evidence confidence. Distinguish a policy violation from confirmed active compromise.
2. The incident lead chooses containment with the service owner, preserving evidence and recording availability tradeoffs.
3. The evidence custodian restricts access, timestamps collection, records provenance/hashes and follows retention requirements.
4. The communications owner maintains the timeline, stakeholder updates and approved external notifications without exposing credentials or personal data.
5. Resume only after the scenario's recovery criteria are verified; track follow-up actions, owner and due date.

- [Secrets exposure](secrets-leak.md)
- [Supply-chain compromise](supply-chain-compromise.md)
- [Kubernetes misconfiguration](k8s-misconfiguration.md)

Use [C10](../templates/control-catalog.md), the [incident checklist](../checklists/incident-response.md) and [metric definitions](../dashboards/kpi-definitions.md). Tabletop these scenarios using fictional evidence before adopting disruptive actions.
