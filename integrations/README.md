# CI platform integration guides

[GitHub Actions](github-actions.md) is the reference integration. [GitLab](gitlab-ci.md) includes a pipeline example; [Jenkins](jenkins.md) and [Azure DevOps](azure-devops.md) describe adaptation and acceptance criteria rather than claiming platform-tested implementations.

Every adoption must record runner/tool versions, trust/permission boundaries, expected checks, artifact locations, failed-check behavior and actual platform-run evidence. Local YAML or script validation is not proof of hosted-platform execution.

Use [secure CI criteria](../templates/secure-ci-guidelines.md), [canonical controls](../templates/control-catalog.md) and the [evidence index](../evidence-packs/evidence-index.md).
