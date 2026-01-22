# Playbook: Secrets Leak

## Trigger

- Secret detected in repo, CI logs, or artifacts

## Triage

- Identify exposed secret type and scope
- Confirm exposure window and access level
- Search for usage across repos and logs

## Containment

- Revoke/rotate the secret immediately
- Remove the secret from history if needed
- Invalidate sessions or tokens

## Eradication

- Fix root cause (pre-commit, vault, secret scanning)
- Add prevention controls to CI

## Recovery

- Re-issue credentials and update dependents
- Validate services with new secrets

## Communication

- Notify affected teams
- Document incident timeline

## Post-Incident

- Add detection rules and training
- Update SLAs and checklist items
