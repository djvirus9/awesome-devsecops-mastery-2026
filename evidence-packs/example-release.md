# Completed illustrative release assessment

**Fictional tabletop example. No builds, deployments, approvals or compliance results are represented as actual events.** This example intentionally concludes that promotion is blocked when evidence is incomplete.

| Field | Example value |
| --- | --- |
| Assessment | DEMO-ASSESSMENT-001 |
| System / scope | Local learning API; loopback only; fictional item records |
| Release / source / artifact | demo-release-001 / unbuilt illustrative revision / no digest generated |
| Period / assessed_at | 2026-01-01 to 2026-01-03 UTC / 2026-01-03T19:00:00Z |
| Collector / reviewer | Fictional learner / fictional peer reviewer |
| Classification / access / retention | Public synthetic example / repository readers / retained as teaching material |
| External framework | None claimed |
| Decision | Block promotion: executable artifact identity and verification evidence missing |

| Evidence ID / control | Objective | Evidence location | Result / collection context | Follow-up |
| --- | --- | --- | --- | --- |
| DEMO-EV-01 / C01 | Bound identity and data flows | [Worked model](../templates/threat-model-template.md) | Design illustration only; no reviewer approval implied | Learner attaches review for actual commit |
| DEMO-EV-02 / C12 | Calculate consistent incident durations | [Fixture](../metrics-templates/incident-metrics.json) | Synthetic records: 26h and 10h; expected mean 18h; no operational SLA inference | Learner records actual metrics validation output |
| DEMO-EV-03 / C03 | Prevent merge on failed checks | No settings/run evidence collected | NOT TESTED; workflow source alone insufficient | Repository owner supplies controlled failed-check record |
| DEMO-EV-04 / C05/C06 | Link SBOM and trusted signature to released digest | No artifact created | MISSING; no digest, identity or verification result | Release owner builds and records actual artifacts |
| DEMO-EV-05 / C11 | Track waiver accountability | No waiver requested | No exception authorizes release with missing evidence | Risk owner evaluates only if a bounded request is submitted |

This is a fully filled assessment of a fictional, incomplete release—not a fake successful audit. For a real release replace every fictional field, attach immutable artifacts and hashes, record real collection times/tool versions, and have a reviewer evaluate results.
