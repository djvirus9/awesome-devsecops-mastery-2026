# Lab 02: executing checks and merge enforcement

Phase 2 · 45–60 minutes · local baseline plus a practice GitHub repository where you can manage rules. Start with [Lab 01](../lab-01-precommit-sast/README.md). Required-check behavior must be observed in GitHub; local command success cannot establish repository settings.

## Exercise

Run `make test`, `make validate`, and `make sast` locally. Read the actual [reference workflow](../../.github/workflows/devsecops-golden-pipeline.yml); reuse it with its scripts, configs, locks, and sample files. Copying only workflow YAML loses those dependencies.

The workflow's controls cover application/detection tests, repository validation, configured source checks, dependencies/secrets, policy fixtures, and a built-image inventory. Scanner execution errors must fail the job. A severity filter alone does not define failure behavior; inspect the explicit exit policy and the stored report. See [Trivy exit behavior](https://trivy.dev/docs/latest/configuration/others/).

In your practice repository, create a normal PR and observe the actual job names and retained artifacts. Configure a rule targeting its default branch to require `Required checks`, a pull request, appropriate review, and deliberate review of workflow changes. Review bypass permissions and whether the repository's plan supports the desired rule. See [GitHub required status checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging).

Create a disposable branch where a harmless assertion in an application test deliberately expects the wrong health result. Open a PR and confirm that the test job and `Required checks` fail and merging is blocked. Correct the expected value in a follow-up commit, rerun checks, and confirm the gate becomes eligible. Keep the exercise in the practice repository; no real vulnerability needs to be introduced.

## Thresholds and exceptions

Record which findings block, whether existing findings are included, report retention, and who responds to a failed scan. Use the [exception template](../../templates/security-exception-template.md) and [control catalog](../../templates/control-catalog.md). An exception document does not suppress a scanner automatically; its exact scope/expiry must match the enforcement mechanism. A broken scanner is not a successful empty scan.

## Verification, troubleshooting, cleanup

Record run URLs, failing and corrected commits, required-check settings, observed merge behavior, and report names. Baseline job names are `Quality (Python 3.12)`, `Quality (Python 3.14)`, `SAST`, `Dependency and secret scan`, `Policy fixtures`, `Container and SBOM`, and the aggregate `Required checks`; check the workflow/run after any rename.

If a required check stays pending, inspect trigger filters and exact status names. If a scanner fails to initialize, keep its error instead of granting an automatic exception. Fork PRs should not need publishing credentials. CI checks do not authorize releases.

Close the disposable PR after recording evidence. Keep intended branch rules active in the practice repository, and remove only settings you deliberately created for a temporary exercise.

Challenge: a job prints “scan complete” but does not invoke a scanner. Solution: the log proves only a message was printed; require command execution, exit behavior, report evidence, and the controlled failure test above.
