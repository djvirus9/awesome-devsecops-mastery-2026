# Serverless adaptation template profile

This profile generates the complete tested local API/control reference and points to the [serverless design exercise](../../projects/serverless-pipeline/README.md). It is a starting point for provider-specific adaptation, not a provisioned serverless application.

From the source repository root:

```bash
python3 scripts/bootstrap_template.py --profile serverless --destination ../my-serverless-reference
cd ../my-serverless-reference
make setup
make test
make validate
```

Read [template setup and review](../README.md). The generated canonical workflow runs the reference's actual checks with their supporting files. No provider function, IAM role, deployment credentials, Terraform/CloudFormation scan, or cloud infrastructure is invented.

Choose the provider/runtime and complete the design guide's acceptance criteria: identity boundary, versioned IaC, scoped execution role, verified artifact promotion, telemetry, cost/concurrency limits, rollback, and cleanup. Record implementation and environment evidence before describing those controls as working. The old [ci.yml](ci.yml) is a compatibility notice only.
