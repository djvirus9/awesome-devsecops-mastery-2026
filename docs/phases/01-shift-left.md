# Phase 1: shift left

Connect requirements to fast developer feedback. Start with the [worked threat model](../reference-architecture.md): identities and ownership, credential handling, and trusted build changes are distinct concerns.

## Implement and verify

Use [Lab 01](../../labs/lab-01-precommit-sast/README.md) to run shared source rules and a harmless positive/negative fixture. Keep one reviewed rule file for local and CI execution. Hooks improve feedback speed but can be skipped, so [Phase 2](02-ci-pr-gates.md) repeats enforcement in CI.

The developer owns code corrections and tests; AppSec owns rule intent and scoped triage. Never put real credentials in fixtures. Secret removal, credential revocation/rotation, evidence handling, and downstream consumer recovery are separate steps.

Definition of done: sample tests pass; a supplied harmless fixture triggers the named rule; its corrected case passes; the learner explains coverage and suppression scope. Store command/version/commit and results. See the [control catalog](../../templates/control-catalog.md) and [secure SDLC checklists](../../sdlc-checklists/README.md).

Official references: [pre-commit](https://pre-commit.com/), [Semgrep documentation](https://semgrep.dev/docs/), [OWASP secrets management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html).
