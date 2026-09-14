# GitLab CI adaptation

Use [the GitLab example](../pipelines/gitlab/.gitlab-ci.yml). It is an adaptation scaffold; actual GitLab runner execution and project settings require separate validation.

1. Review runner isolation, Python/tool requirements, image pins and available artifacts. Copy the example to the root `.gitlab-ci.yml` in your GitLab project.
2. Ensure merge-request pipelines are created for every change and that finding/error exits fail jobs. Do not set security gates to allowed failure.
3. Configure protected-branch permissions **and** the separate merge check **Pipelines must succeed**. Review skipped/missing pipeline behavior and approval/bypass rules.
4. Exercise a controlled failed check and verify that the merge remains blocked; retain the exact pipeline and commit references.
5. Verify SBOM/report upload even where appropriate checks fail; set artifact access/retention and document missing signing/promotion capabilities.
6. Record actual GitLab version, runner type, check results and settings in the [evidence index](../evidence-packs/evidence-index.md).

References: [successful-pipeline merge requirement](https://docs.gitlab.com/user/project/merge_requests/auto_merge/#require-a-successful-pipeline-for-merge), [GitLab application security](https://docs.gitlab.com/user/application_security/). Protected branches alone are not proof of successful security checks.
