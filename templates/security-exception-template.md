# Security exception record

Copy this record for one bounded exception. An unfinished record does not authorize a waiver. Link the same ID from scanner suppressions, release evidence and the finding tracker.

| Field | Required value |
| --- | --- |
| Exception ID / state | EXC-[ID]; requested / approved / expired / closed |
| Control and finding | Canonical control ID, finding ID and evidence link |
| Scope | Specific service, package/path, artifact digest or namespace; excluded scope |
| Requester / accountable owner | Named people and contact route |
| Business justification | Why the requirement cannot currently be met |
| Risk assessment | Impact, exposure, likelihood basis, affected data and residual risk |
| Compensating controls | Control, verification evidence, monitoring and alert owner |
| Remediation plan | Milestone, delivery owner, tracking issue and target date |
| Approval | Authorized risk owner, decision, timestamp and immutable decision reference |
| Validity | Start, review and expiry timestamps in UTC; maximum duration |
| Enforcement | Suppression/policy reference and automatic expiry check |
| Renewal | New risk review and explicit approval; never automatic |
| Closure | Fix verification evidence, suppression removal, closed_at and reviewer |

Expiry restores normal enforcement; if a service cannot tolerate that outcome, its owner must resolve the operational plan before approval. Do not silently extend deadlines. Record both original SLA and exception-adjusted dates. See [Trivy expiry example](../recipes/trivy-ignore-policy.md), [SLA policy](vuln-sla-matrix.md) and [evidence index](../evidence-packs/evidence-index.md).
