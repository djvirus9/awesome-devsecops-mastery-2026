# Lab 05: Runtime Detection

## Overview

Deploy runtime detection and validate alerting for suspicious behavior.

## Objectives

- Install a runtime sensor (Falco)
- Generate a test alert
- Route alerts to a ticketing or chat channel

## Time

60-90 minutes

## Prerequisites

- Kubernetes cluster
- Helm installed
- Access to alerting destination (Slack, email, or ticketing)

## Steps

1. Install Falco with Helm.
   ```bash
   helm repo add falcosecurity https://falcosecurity.github.io/charts
   helm install falco falcosecurity/falco
   ```

2. Trigger a known alert (example: shell inside a container).
   ```bash
   kubectl exec -it <pod> -- /bin/sh
   ```

3. Configure Falco outputs to Slack, webhook, or email.

4. Verify alerts are received and routed.

## Validation

- Alert shows in Falco logs.
- Alert is delivered to the chosen channel.

## Extensions

- Add custom rules for sensitive namespaces.
- Integrate with SIEM.
- Add suppression for noisy alerts.
