# Illustrative adoption scenarios

These are fictional planning scenarios, not customer case studies or measured outcomes. They demonstrate tradeoffs; substitute actual workload, budget, ownership, and evidence before making a decision.

| Scenario | Constraints | Initial choice | Tradeoff and validation |
| --- | --- | --- | --- |
| Small service team | One API, limited operating capacity | Shared local/CI tests, narrow source rules, dependency inventory, named owner | Keep rules understandable; prove a failing fixture blocks and exceptions expire. |
| Growing SaaS | Multiple teams and release pipelines | Reusable CI contract, service inventory, artifact verification, policy rollout | Standardization needs clear ownership; compare adoption coverage and bypasses across teams. |
| Large platform | Federated builders and many deployments | Builder identities, promotion trust policy, workload identity, telemetry contracts | Central policy can interrupt delivery; stage rollout and test recovery before enforcement. |
| Regulated service | Sensitive data and retention obligations | Control-to-evidence mapping, access review, retained verification, recovery exercises | Evidence retention can itself expose data; classify and redact records and involve the relevant assurance owner. |

For the small-team scenario, complete the [microservice capstone](../projects/microservice-api/README.md) first. For a larger program, use the [domain scorecard](../scorecards/maturity-scorecard.md) to find missing foundations before adding runtime tools. No scenario here establishes compliance or predicts a percentage improvement.
