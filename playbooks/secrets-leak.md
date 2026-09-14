# Playbook: secrets exposure

Apply [shared roles/evidence rules](README.md). Trigger: a credential appears in source, logs or an artifact. Record credential type and identifier, exposure window, permissions and dependent services; never paste the secret into a ticket.

| Decision | Action / owner | Evidence and exit condition |
| --- | --- | --- |
| Credential active or status unknown? | Credential owner revokes/rotates promptly; service owner coordinates dependent updates | Provider confirms old credential is invalid; test dependencies with replacement |
| Evidence of misuse? | Incident lead expands incident scope; preserve relevant provider/auth/audit records | Time-bounded evidence set and affected identities/services recorded |
| Removal from history needed? | Repository owner coordinates cleanup after revocation and evidence preservation | Affected branches, forks/caches and collaborator effects assessed; no claim that deletion reverses exposure |
| Source of recurrence? | Engineering owner repairs logging, secret injection or scanning gap | Regression/prevention check and reviewed change |
| Ready to recover? | Service owner and incident lead review credential invalidation, dependent health and monitoring | Recovery acceptance and timestamp recorded |

Rotate other credentials or invalidate sessions when exposure evidence warrants it. Do not assume a history rewrite revokes credentials. Revoke the demo credential and update a fictional dependent service during a tabletop; success means old access is rejected, service health recovers, evidence is preserved and an owner accepts every follow-up.
