# Lab 07: IR and Detections

## Overview

Build a detection and response loop with documented playbooks and alert QA.

## Objectives

- Write a detection rule for a known technique
- Create an incident runbook
- Validate alert routing and response time

## Time

60-90 minutes

## Prerequisites

- Access to logs or a SIEM
- Ticketing or alerting system
- Detection format such as [Sigma](https://sigmahq.io/)

## Steps

1. Create a detection rule mapped to [MITRE ATT&CK](https://attack.mitre.org/).

2. Define a runbook with triage, evidence, containment, and escalation steps.

3. Simulate the detection (tabletop or test event).

4. Track MTTA/MTTR for the test run.

5. Add detection tuning notes to reduce noise.

## Validation

- Detection fires on the test event.
- Alert is routed to the correct channel.
- Runbook is followed and updated.

## Extensions

- Add case management with [TheHive](https://thehive-project.org/).
- Automate ticket creation from alerts.
- Add post-incident retrospectives and metrics.
