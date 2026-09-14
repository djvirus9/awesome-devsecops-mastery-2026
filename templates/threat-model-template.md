# Threat model record

System / owner / version / review date: [fill]. Scope and excluded components: [fill]. Data classification, retention and external dependencies: [fill]. Link an architecture/data-flow diagram showing identities, stores, trust boundaries and deployment context.

| Threat ID / requirement | Asset and trust boundary | Control ID and implementation | Verification evidence | Residual risk / owner |
| --- | --- | --- | --- | --- |
| [fill] | [fill] | [fill] | [test/log/review] | [fill] |

Use a declared enumeration method such as [STRIDE](https://learn.microsoft.com/security/engineering/threat-modeling). ATT&CK can supplement operational detection analysis; it is not a replacement for understanding this application's data flows. Review changes to identity, data classification, dependencies and deployment boundaries.

## Worked illustrative model: local sample API

This is a design example, not a production assessment. Owner: learning participant. Scope: loopback Flask API, in-memory item store and explicitly configured demo token-to-actor mapping. External identity providers and durable storage are absent. Data: fictional item metadata. Retention: process lifetime.

Flow: local client → HTTP authorization boundary → API actor checks → in-memory store. Configuration injects tokens at process start; logs cross into local operator visibility.

| Threat / requirement | Boundary | Control | Verification to attach | Residual risk / owner |
| --- | --- | --- | --- | --- |
| TM-01: an actor must only access its own records | Client → record ownership | C02: server-side actor/owner comparison | Automated ownership tests from `make test` | Demo tokens require explicit local configuration; learner |
| TM-02: credentials must not enter logs | Request → application logs | C09: structured events omit Authorization values | Redaction test and sanitized log sample | Host operators can inspect process environment; learner |
| TM-03: unreviewed dependency changes must be visible | Source → build | C04/C05: dependency checks and SBOM | Scanner result, version inventory and SBOM | Tool/database freshness and coverage limits; learner |
| TM-04: accidental network exposure | Process → host network | C07: local binding and container port guidance | Bind configuration and local acceptance check | Not designed as an internet service; learner |

Acceptance: attach actual run identifiers and reviewer before claiming controls are verified. Escalate any deployment beyond this local learning scope for a new threat review.
