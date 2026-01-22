# Lab 05: Runtime Detection

## Overview

Deploy runtime detection and validate alerting for suspicious behavior.

## Objectives

- Install a runtime sensor
- Generate a test alert
- Route alerts to a ticketing or chat channel

## Time

60-90 minutes

## Prerequisites

- Kubernetes cluster
- Helm installed
- Access to alerting destination (Slack, email, or ticketing)
- [Falco](https://falco.org/)

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

- Add custom rules from [Falco Rules](https://falco.org/docs/rules/).
- Integrate with [Prometheus](https://prometheus.io/) and [Grafana](https://grafana.com/).
- Add suppression for noisy alerts.
