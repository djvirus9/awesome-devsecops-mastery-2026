# Serverless deployment design exercise

Status: optional blueprint, not a supplied or provisioned cloud application. Complete the [microservice reference](../microservice-api/README.md) first; it establishes the API and control contract to adapt.

Choose a provider and owner before implementation. Record function runtime/version, gateway/identity boundary, invocation permissions, secret source, network access, data retention, event retries, concurrency/cost limits, deployment approvals, rollback mechanism, and incident contacts. Those decisions change the architecture and cannot be inferred from generic Lambda-style examples.

## Acceptance criteria for an implementation

| Area | Required evidence |
| --- | --- |
| API/identity | Same own-record and denied cross-owner semantics as the sample; gateway and function authorization tested. |
| Infrastructure | Versioned IaC, supported scanner, allowed/denied fixtures, narrowly scoped execution role. |
| Build | Locked dependencies, retained package inventory, exact deployed version/package identity. |
| Promotion | Verified build evidence, review/approval, staged traffic or equivalent rollback procedure. |
| Operations | Request/telemetry schema, delivery/health checks, bounded retries and concurrency, named alert owner. |
| Recovery | Practice rollback/replay decision and cleanup evidence, including data/cost consequences. |

Do not describe a generic IaC placeholder as a working gate. Start with [repository templates](../../repo-templates/README.md), [control catalog](../../templates/control-catalog.md), and [validation criteria](../../docs/validation.md). Mark each external step pending until its chosen provider supplies reproducible results. No cloud resources are created by this document.
