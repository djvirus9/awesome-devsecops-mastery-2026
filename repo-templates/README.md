# Repository templates

Generate a complete, consistent copy of the local reference using [scripts/bootstrap_template.py](../scripts/bootstrap_template.py). All three profiles share the canonical application, configuration, tests, and GitHub workflow definitions. Profiles select a follow-on guide; they do not maintain divergent copies of CI or create provider resources.

## Create a fresh practice repository directory

Run from the source repository root. Use Python 3.12 or newer and a destination that does not exist, outside this checkout:

```bash
python3 scripts/bootstrap_template.py --profile microservice --destination ../my-devsecops-reference --dry-run
python3 scripts/bootstrap_template.py --profile microservice --destination ../my-devsecops-reference
cd ../my-devsecops-reference
make setup
make test
make validate
```

The dry run validates required source files and reports the copy plan without creating anything. The real command refuses an existing destination and never initializes Git, adds a remote, installs packages, or contacts GitHub. If the source reference is incomplete, it fails before creating the destination. An interrupted copy may leave a new partial directory; inspect it and choose a fresh destination for the next run.

## Generated structure

```text
my-devsecops-reference/
├── .github/workflows/
│   ├── devsecops-golden-pipeline.yml
│   ├── platform-validation.yml
│   └── release.yml
├── .pre-commit-config.yaml
├── .python-version
├── Makefile
├── requirements-dev.in / requirements-dev.txt
├── tool-versions.json
├── scripts/                 # same helpers used by the copied workflows
├── configs/                 # selected source, scanner, and signing configuration
├── samples/sample-api/      # application, contract, locks, and Dockerfile
├── tests/                   # application and supporting regressions
├── policies/                # complete templates and allowed/denied fixtures
├── labs/                    # source-rule and offline runtime/IR exercises
├── docs/, projects/, ...    # supporting control/evidence/learning library
├── TEMPLATE-SETUP.md        # profile-specific next steps and review checklist
└── template-manifest.json   # copied-file hashes and source revision/dirty state
```

The workflow files are copied locally with their dependencies; no mutable remote reusable workflow is introduced. The manifest describes copied working-tree bytes. It is not a signed build attestation. Git history, local environments/tool downloads, generated reports, `.env` files, private-key files, and caches are excluded. Symbolic-link source files are rejected rather than followed.

## Select a profile

| Profile | Guide | Implemented versus optional |
| --- | --- | --- |
| `microservice` | [Microservice](microservice/README.md) | Runnable local API, tests, image/control reference; registry release and deployment need their own environment. |
| `k8s-app` | [Kubernetes app](k8s-app/README.md) | Same API plus supplied deployment/policy fixtures; live cluster admission and rollout are separate exercises. |
| `serverless` | [Serverless](serverless/README.md) | Same tested baseline and a provider-adaptation design guide; no cloud function or provider IaC is promised. |

## Review before publishing

Read `TEMPLATE-SETUP.md`. Review inherited CODEOWNERS, security/contact routes, upstream documentation links, repository/ref identities in trust policies, manual publishing permissions, and intended project scope. After publishing the copy to GitHub with Actions enabled, the baseline and platform workflows run on their configured PR/main events, including disposable container/cluster workloads. Generation itself starts none. The release workflow remains an optional, manually activated operation requiring identity, registry, and permission review. Configure required checks in your own repository after observing the actual check names/results. The upstream [dated validation record](../evidence-packs/releases/2026-09-15-reference-path.md) describes upstream execution, not validation of a generated copy.

Legacy `ci.yml` paths in profile directories remain compatibility notices. They are not runnable workflows and must not be copied into `.github/workflows/`. The generator installs the canonical workflows at their correct paths.

The legacy `microservice/.pre-commit-config.yaml` is also a compatibility notice. Install hooks from the generated repository's root `.pre-commit-config.yaml`, which is copied from the canonical root configuration.

Verify the generator itself with `python3 -m unittest discover -s repo-templates -p 'test_*.py' -v`. Then validate the generated copy at its declared scope using [the execution matrix](../docs/validation.md).
