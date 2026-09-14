# Metric definitions

Define the population before interpreting a number. The included dashboard only implements the first two rows and closed-incident count using fictional data.

| Metric | Calculation and population | Source / accountable owner |
| --- | --- | --- |
| Incident acknowledgment mean | Sum(acknowledged − detected) / acknowledged incidents in chosen detection cohort | Incident tracker / incident lead |
| Incident resolution mean | Sum(resolved − detected) / closed incidents in chosen detection cohort | Incident tracker / incident lead |
| Vulnerability remediation time | verified_fixed_at − first_detected_at, per finding; report median and p90 by risk tier | Finding tracker / service owner |
| SLA compliance | Findings verified fixed by original due date / all findings whose original due date falls in reporting period, including overdue open findings | Finding tracker / security owner |
| SBOM coverage | Released artifact digests with schema-valid SBOM linked to that digest / all released artifact digests | Release inventory / release owner |
| Verified signature coverage | Released artifact digests verified against expected identity, issuer and digest policy / all released artifact digests | Verification logs / release owner |
| Exception count | Number created in period; show active, expired and renewed counts separately | Exception register / risk owner |
| Exception rate | Active exceptions / assessed applicable controls in declared scope | Exception register and control inventory / risk owner |

For a real program, use a monthly UTC reporting period, publish the cohort cutoff, ingestion lag, deduplication key, and severity-at-detection. Preserve original due dates after exception approval; report exception-adjusted performance separately. Reopened findings retain the original detection clock unless a reviewer records a distinct cause. Document treatment of rejected/duplicate findings, holidays and migration data.

Zero denominators mean **N/A**, not 100% compliance. Report sample counts, open backlog age, p90 and maximum durations alongside means. Never mix incidents with findings or infer efficacy from tool installation. A signed artifact is not necessarily trustworthy if its builder or signing identity was compromised.

Targets are organization decisions approved with [SLAs](../templates/vuln-sla-matrix.md). Incident response targets belong to the incident plan, not vulnerability fix SLAs. The demo makes no target-compliance claim.
