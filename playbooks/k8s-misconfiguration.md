# Playbook: Kubernetes Misconfiguration

## Trigger

- Policy violation or insecure configuration detected

## Triage

- Identify impacted namespaces and workloads
- Assess exposure (public endpoints, privileges)

## Containment

- Apply emergency policies
- Scale down or isolate risky workloads

## Eradication

- Fix IaC templates or Helm charts
- Add policy-as-code checks

## Recovery

- Redeploy with compliant configuration
- Validate with admission controls

## Communication

- Notify owners and update ticket

## Post-Incident

- Add baseline policies
- Add automated drift detection
