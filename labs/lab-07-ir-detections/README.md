# Lab 07: incident response tabletop

Phase 7 · 45–60 minutes · offline synthetic exercise. Complete [Lab 05](../lab-05-runtime-detection/README.md); Python and a text editor are sufficient. No SIEM, customer logs, external messaging, or production changes are needed.

## Scenario and roles

The sample API's Alice client sees repeated denied requests after a configuration rollout. Bob's synthetic requests remain successful. The local alert report shows `DEMO-DENIED-REQUESTS` at 12:01 and a heartbeat gap at 12:04. An alert establishes a condition to investigate, not its cause.

Assign incident commander (decisions), application owner (access/configuration), SRE (health/recovery), and scribe (timeline/evidence). One learner can play all roles but must record each decision. Open the supplied [exercise record](exercise-record.md) and [solution](solution.md) only after working through the injects.

## Timed injects

| Exercise time, UTC | New evidence | Required decision |
| --- | --- | --- |
| 12:01 | Three distinct denied synthetic requests from Alice in 120 seconds | Acknowledge and assign an owner. Are more facts needed before containment? |
| 12:04 | Last heartbeat was 12:02 | Determine whether this is service failure, collector failure, or missing evidence. Do not interpret silence as recovery. |
| 12:05 | Deployment note: Alice's demo client still uses a previous configuration; Bob's local checks pass | Reassess the access alert. Identify which credential/configuration change would explain it without assuming misuse. |
| 12:08 | Collector configuration was paused during an exercise change | Restore the practice collector configuration in the written plan; decide how telemetry recovery is demonstrated. |
| 12:12 | Corrected client configuration passes own-record access; cross-owner regression still denies; current heartbeat observed | Verify recovery against both application and telemetry criteria. |
| 12:15 | No unintended data returned in supplied evidence; event counts stabilized | Close only after evidence, owner approval, and follow-up criteria are complete. |

These timestamps and claims are fictional injects, not commands or observed deployment results. Preserve original fixtures, use UTC, keep request identifiers, and exclude raw tokens from notes. If the limited evidence cannot establish exposure, record the uncertainty explicitly.

## Completion evidence

Fill a local copy of the [record](exercise-record.md): severity rationale, scope, owner, acknowledgment time, hypotheses, containment choice, evidence pointers, recovery checks, resolved time, and one corrective action with owner/due date/verification. Reference the [control catalog](../../templates/control-catalog.md) and [playbooks](../../playbooks/README.md).

Compute acknowledgment from detection to acknowledgment and recovery from detection to resolution. If acknowledgment is 12:03 and verified recovery is 12:12, the values are 2 minutes and 11 minutes. Do not subtract acknowledgment from recovery and call it the same metric. Use [metric definitions](../../docs/metrics.md) for consistent reporting; retrospective completion at 12:15 is separate.

Run `make test` to confirm the local application/detection regressions remain healthy. This verifies the supplied local control behavior; the scenario's collector recovery remains a tabletop statement until a practice environment is exercised.

## Challenge, troubleshooting, cleanup

Challenge: what if the heartbeat remains missing but Alice's requests succeed? Solution: service availability may have recovered while telemetry remains impaired. Keep the telemetry action open and require fresh heartbeat/delivery evidence before declaring the whole incident recovered.

If the alert report is absent, rerun Lab 05 with its exact historical evaluation time. If no cause is supported, list competing hypotheses and evidence needed instead of inventing attribution. No services are started or third parties contacted in this exercise. Retain the sanitized record with a synthetic/tabletop label and remove disposable copies when no longer needed.
