# Playbook: supply-chain compromise

Apply [shared roles/evidence rules](README.md). Trigger: credible evidence of a malicious dependency, altered artifact or compromised build/signing identity. Preserve advisory/source references and exact package versions, commits, artifact digests, builder identities and deployment inventory.

| Decision | Action / owner | Evidence and exit condition |
| --- | --- | --- |
| Which released digests include the suspect input? | Release owner correlates inventory, SBOM and provenance | Explicit affected and unaffected scope; unknowns remain visible |
| Ongoing distribution/execution? | Incident lead blocks affected promotion/download paths and coordinates containment | Scope-specific block verified; availability effects recorded |
| Builder, cache or signing identity compromised? | Platform owner isolates implicated build environment, revokes affected credentials/trust and preserves evidence | Trusted rebuild path established; keys alone are not the full trust boundary |
| Clean replacement available? | Engineering/release owners review source/dependencies and rebuild in a trusted environment | New artifact digest, SBOM, provenance and trusted identity verification |
| Ready to restore? | Incident lead verifies removal of affected artifacts, clean deployment and monitoring | Release/incident evidence reviewed before resuming promotion |

A valid signature from a compromised builder does not prove a clean artifact. Avoid rebuilding through the same suspect caches or credentials. Tabletop with fictional artifact IDs: success means the team can identify downstream exposure, prevent promotion, select a trusted rebuild route and document recovery criteria and follow-up owners.
