# Canonical pre-release checklist

Release / source commit / artifact digest / owner / reviewer / assessed_at: [fill]. This is the shared release gate used by the [SDLC release view](../sdlc-checklists/release.md).

- [ ] C01/C02: current requirements/threat model and security tests match the proposed change.
- [ ] C03/C04: required checks succeeded for this commit; reports include tool versions and execution errors.
- [ ] C05: released artifact digest is linked to a schema-valid SBOM retained with release evidence.
- [ ] C06: applicable signature/provenance verification checks expected identity, issuer and digest.
- [ ] C07: applicable workload policies passed declared static/live acceptance checks.
- [ ] C08: local API tests/observations document authenticated coverage and limitations.
- [ ] C09/C10: operational owner, recovery plan and relevant incident decisions are ready.
- [ ] C11: blocking findings resolved or explicitly approved in bounded, unexpired exceptions; original SLA dates retained.
- [ ] C12: [evidence index](../evidence-packs/evidence-index.md) identifies owner, provenance, access/retention and review; missing evidence remains visible.
- [ ] [Release notes and maintenance record](../templates/release-maintenance.md) describe compatibility, rollback and unimplemented capabilities.

Any N/A item requires scope-based justification and reviewer. A checkbox without linked evidence is incomplete. These [control IDs](../templates/control-catalog.md) are adoption criteria, not certification.
