# Example vulnerability SLA policy

This is an adoption template, **not a response promise from this repository's maintainer**. Policy owner: [assign]. Scope: [services/assets]. Effective date/version: [fill]. Approval: [record].

| Risk tier | Acknowledge/assign | Verify remediation |
| --- | --- | --- |
| Critical | 24 calendar hours | 7 calendar days |
| High | 48 calendar hours | 14 calendar days |
| Medium | 5 calendar days | 30 calendar days |
| Low | 10 calendar days | 90 calendar days |

These example targets require approval for your environment. Determine risk using technical severity, exposure, asset importance, evidence of exploitation, reachable code and compensating controls. Record the scoring source and version (for example [CVSS](https://www.first.org/cvss/)); the score alone does not establish a deadline. Evidence of ongoing compromise enters the [incident process](../playbooks/README.md) immediately rather than waiting for this schedule.

## Clock and lifecycle

- Start at first recorded detection in UTC; assignment, scanning-tool changes or rediscovery do not reset it.
- Close only when remediation is deployed in affected scope and independently verified; a merged patch alone does not stop the clock.
- Track first_detected_at, original_due_at, owner, affected asset/version, verified_fixed_at, reopened_at and evidence.
- Duplicates link to the original finding. A rejected finding needs an evidence-backed disposition. Reopening retains the original clock unless a reviewer establishes a distinct issue.
- Escalate approaching deadlines to the service owner; overdue critical/high findings to the risk owner. Assign actual people/contact routes before adoption.
- Exceptions follow [C11](control-catalog.md) and the [exception template](security-exception-template.md). Preserve original due dates; publish accepted-risk and overdue totals separately.
- Incident acknowledgment and recovery objectives are separately defined in the incident plan. Do not compare them to vulnerability fix times.

Calculate [SLA compliance](../dashboards/kpi-definitions.md) using all findings due in the period, including overdue open findings.
