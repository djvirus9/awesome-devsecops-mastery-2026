# Worked tabletop solution

Illustrative completed reasoning, not an actual incident or deployed recovery test. Exercise ID: DEMO-IR-001. Scope: sample-api synthetic Alice client and its telemetry path. Roles: learner as commander, application owner, SRE, and scribe.

At 12:01, the commander treats the repeated-denial alert as a warning requiring prompt triage. No supplied evidence establishes data access or an intruder. At 12:03 the application owner acknowledges it. Original synthetic events and detector output are retained with the repository commit and explicit replay time; raw tokens are excluded.

At 12:04, SRE creates a separate telemetry-health work item. Bob's successful requests support partial service health but do not establish full application correctness or collector health. The commander records three hypotheses: stale client configuration, application authorization regression, and activity needing further investigation.

At 12:05 the configuration inject supports the stale-client explanation. No isolation or automatic account disabling is justified by the supplied evidence. The planned reversible action is restoring the intended demo client configuration. If evidence instead suggested credential disclosure, the credential owner would coordinate revocation and replacement; that event is not established here.

At 12:08 the SRE identifies the exercise collector pause and plans restoration. Recovery requires fresh heartbeat and delivery evidence in addition to successful own-record access and continued denial for another owner's record. At 12:12 all three criteria are supplied as tabletop injects. Local regression tests can be executed independently; the record labels collector recovery as simulated.

The commander approves simulated recovery at 12:12. Acknowledgment is 12:03 − 12:01 = 2 minutes. Recovery is 12:12 − 12:01 = 11 minutes. The 12:15 retrospective is not the recovery timestamp.

Corrective action DEMO-ACTION-001: application/platform owner adds a client-configuration compatibility check and collector heartbeat check to the deployment review; due at the next practice release. Closure requires evidence of a corrected rollout and a failing test when configuration is stale. Status: proposed, not completed by this written solution.

The exercise is complete when the learner's record distinguishes observation from assumption, preserves evidence, assigns ownership, explains containment tradeoffs, checks application and telemetry recovery, computes consistent durations, and leaves a verifiable follow-up action. There is no automatic real-world notification or infrastructure change.
