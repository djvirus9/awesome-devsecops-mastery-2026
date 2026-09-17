# Release and maintenance record

Release owner / version / source commit / review date: [fill]. Support scope and known limitations: [fill].

1. Review dependency/action updates, upstream deprecations and open security findings. Record actual tool versions and the date primary documentation was checked.
2. Run documented local validation from a clean checkout; retain commands, outputs and platform details. List checks that were skipped and why.
3. Follow the canonical [pre-release checklist](../checklists/pre-release.md). Link exact artifacts/digests and verification results; do not reuse evidence from a different commit.
4. Summarize behavior changes, compatibility, migration/rollback and known limitations in release notes.
5. Confirm documentation links, owner/contact routes and dated recipe validation. Use “draft”, “locally validated” or “platform validated” with evidence; never infer production readiness.
6. After release, review reported regressions and record follow-up ownership.

Maintenance cadence is a plan chosen by maintainers, not an automatic service guarantee. Suggested review: dependency PRs when raised; broken links and recipe/tool drift monthly; learning rubric/evidence examples quarterly. Archive historical material with provenance instead of presenting activity counts as project quality.
