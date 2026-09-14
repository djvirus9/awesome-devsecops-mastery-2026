# Azure DevOps adaptation plan

Status: **design guidance; no Azure Pipelines YAML or hosted execution is supplied**. The [GitHub reference pipeline](../pipelines/github-actions/devsecops.yml) defines behavior to translate.

Prerequisites: an Azure DevOps project, an isolated agent with Python 3.12+ and documented tools, and explicit permissions for any service connection.

| Stage | Required behavior / acceptance |
| --- | --- |
| Build validation | Run setup, tests, validation and declared security checks for each proposed change |
| Gate | Require build validation in branch policies; prove a controlled failure blocks completion |
| Artifacts | Publish reports/SBOM with source commit, artifact digest, access and retention |
| Promotion, if adopted | Configure environment approvals/checks outside untrusted source control; restrict service connections |
| Verification | Validate artifact identity/provenance and perform recovery review before deployment |

Create and validate platform-specific YAML in your own project. Record actual agent/tool versions, run URLs, branch policy and environment-check behavior. Distinguish a check that merely publishes findings from one that fails the build; review bypass permissions.

References: [Azure Pipelines](https://learn.microsoft.com/azure/devops/pipelines/), [approvals and checks](https://learn.microsoft.com/azure/devops/pipelines/process/approvals). Record results in the [evidence index](../evidence-packs/evidence-index.md).
