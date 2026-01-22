# Playbook: Supply-Chain Compromise

## Trigger

- Malicious dependency or compromised artifact detected

## Triage

- Identify affected versions, builds, and systems
- Confirm impact on production

## Containment

- Block compromised packages/artifacts
- Freeze deployments if necessary

## Eradication

- Remove malicious dependency
- Rotate signing keys if exposed
- Rebuild from verified sources

## Recovery

- Redeploy clean artifacts
- Verify SBOM and signatures

## Communication

- Notify stakeholders and update advisory

## Post-Incident

- Add provenance checks
- Strengthen dependency pinning and review
