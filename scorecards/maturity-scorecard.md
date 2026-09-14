# Evidence-based maturity scorecard

This is a repository-specific learning/adoption rubric, not an OWASP SAMM score or certification. Assess a declared service population and period. Levels are cumulative per domain: award the highest level whose criteria and every preceding level have evidence. Use 0 for no demonstrated practice; N/A requires a reviewer-approved scope reason. Never substitute an average for unresolved critical gaps.

| Domain | 1: establish | 2: repeat | 3: enforce | 4: measure | 5: improve |
| --- | --- | --- | --- | --- | --- |
| Design / shift left | Owner and asset/data inventory recorded | Threat/control/test model reviewed for one service | C01/C02 required for all scoped design changes | Quarterly sample measures model freshness and test linkage | Two review cycles show design gaps closed and recurrence tracked |
| CI PR gates | Local checks documented | CI runs checks on each scoped PR | C03/C04 failing fixture blocks merge; fork behavior verified | Coverage, runtime and failure causes reviewed monthly | Two cycles reduce measured gaps without weakening enforcement |
| Supply chain | Dependencies inventoried | C05 SBOM generated for one exact artifact | C06 verification required for every scoped release | Digest/identity coverage and missing evidence measured monthly | Recovery exercise validates compromised-builder response and closes gaps |
| API verification | Auth/input requirements recorded | Local authorized/unauthorized cases automated | C02/C08 required tests and explicit passive coverage retained per change | Route/requirement coverage and regressions reviewed monthly | Two cycles improve uncovered requirements with regression evidence |
| CD / Kubernetes | Workload baseline and owner recorded | Policy fixtures evaluated locally | C07 admitted/rejected behavior verified in intended environment | Drift, exclusions and enforcement coverage reviewed monthly | Exercise validates safe rollback and expiry behavior; gaps closed |
| Runtime detection | Events and response owner specified | Controlled test produces redacted events | C09 test proves routing and acknowledgment | Coverage, noise and response latency measured monthly | Two tuning cycles improve measured signals; missed-event cases tested |
| Incident response | Roles and contacts assigned | One C10 tabletop completed with timeline | Recovery criteria and follow-up ownership verified for each scoped exercise | Recurrence, recovery time and action aging reviewed quarterly | Repeat exercise proves prior gaps fixed across all scoped incident classes |
| Governance / metrics | C11 owner and policy adopted | Finding/exception register and C12 evidence index maintained | Expiry and evidence checks required for scoped releases | Metrics include backlog, denominators and sample counts; review quarterly | Two cycles show tracked improvements; independent sample verifies evidence |

For “all scoped” claims, attach the inventory denominator and every exclusion. Reviewers may choose stricter thresholds before assessment; do not change them after seeing results.

| Domain | Current level | Target / due date | Scope and evidence links | Gap / accountable owner | Reviewer / assessed_at |
| --- | --- | --- | --- | --- | --- |
| Design / shift left | [0–5 or N/A] | [fill] | [fill] | [fill] | [fill] |
| CI PR gates | [fill] | [fill] | [fill] | [fill] | [fill] |
| Supply chain | [fill] | [fill] | [fill] | [fill] | [fill] |
| API verification | [fill] | [fill] | [fill] | [fill] | [fill] |
| CD / Kubernetes | [fill] | [fill] | [fill] | [fill] | [fill] |
| Runtime detection | [fill] | [fill] | [fill] | [fill] | [fill] |
| Incident response | [fill] | [fill] | [fill] | [fill] | [fill] |
| Governance / metrics | [fill] | [fill] | [fill] | [fill] | [fill] |

Use [canonical controls](../templates/control-catalog.md) and [evidence indexing](../evidence-packs/evidence-index.md). For organization-wide assessment consider the separate [OWASP SAMM model](https://owaspsamm.org/model/).
