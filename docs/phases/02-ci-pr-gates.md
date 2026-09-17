# Phase 2: CI and PR gates

A merge gate needs an executing control, defined failure semantics, and a repository rule that requires the resulting check. [Lab 02](../../labs/lab-02-ci-pr-gates/README.md) connects those pieces in a practice repository.

## Implementation contract

The [workflow](../../.github/workflows/devsecops-golden-pipeline.yml) uses local configuration, tests, lock files, scripts, and sample artifacts. Preserve that dependency set when copying it. Use restricted job permissions and reviewed immutable action references. PR-controlled code must not gain release publishing identity.

Platform owners define exact required status names, report retention, failure ownership, and which severity/risk thresholds block. AppSec documents existing findings, exclusions, and approved expiring exceptions; maintainers review changes to workflow trust. Errors initializing a scanner must fail visibly.

Definition of done: a harmless incorrect assertion causes the real check and aggregate gate to fail; merge is blocked in the practice repo; the corrected commit passes. Retain settings and run evidence. A local green test does not establish branch enforcement.

See [exceptions](../../templates/security-exception-template.md), [integration guides](../../integrations/README.md), and [GitHub required status checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging).
