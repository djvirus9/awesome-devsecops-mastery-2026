# Foundation: run and understand the sample

Budget 30–60 minutes for first-time setup and 15 minutes for orientation. Run commands from the repository root. Linux and macOS shells are supported; Windows users should use WSL. CI targets Python 3.12 and 3.14. Docker is optional until the image/SBOM lab; the local path needs no cluster or cloud account.

## Prerequisite checklist

| Skill | Demonstration before proceeding |
| --- | --- |
| Git/PRs | Explain a branch, commit, diff, review, and required check. |
| Shell | Navigate to the repository root, set a command-scoped variable, stop a process with Ctrl+C. |
| Python/YAML | Explain a virtual environment, dependency lock, and indentation. |
| HTTP/TLS | Identify method, route, status, header, and the purpose of transport encryption. |
| Identity/authorization | Explain who a token represents and why identity still needs object-level permission. |
| Containers/CI | Distinguish source, image, container, and ephemeral build job. |

Use the [glossary](glossary.md) and [resource index](resources.md) for unfamiliar terms.

## Local setup

```bash
git --version
make --version
python3 --version
make setup
make test
make validate
```

`make setup` creates an isolated `.venv` from pinned dependencies. Downloads need network access. `make test` exercises behavior; `make validate` checks repository structure and configuration. Additional tools and optional environments are listed in the [validation matrix](validation.md).

```bash
API_TOKENS_JSON='{"demo-alice-token":"alice","demo-bob-token":"bob"}' make run
```

In a second terminal:

```bash
DEMO_ALICE_TOKEN='demo-alice-token'
curl --fail http://127.0.0.1:8080/health
curl --fail -H "Authorization: Bearer $DEMO_ALICE_TOKEN" http://127.0.0.1:8080/v1/items
```

Expect service health and Alice's records only. These are public synthetic credentials supplied explicitly for a local exercise. Read [app.py](../samples/sample-api/app.py) and the [sample README](../samples/sample-api/README.md). The application has no default authenticated user.

## Understand the control boundaries

The API has public health information and private synthetic records. A caller crosses an HTTP boundary into the application. The server resolves identity from its configured token map and applies ownership rules before returning data. Changes cross a separate boundary when they become a CI build. Later phases verify release identity and help operators recognize failures.

Read the [worked threat model](reference-architecture.md). Write three statements: what must remain private, who may change a release build, and which evidence identifies the intended deployment. These are requirements for the next labs.

## Verification and troubleshooting

Completion requires passing checks, the expected HTTP responses, and the three trust decisions. This is orientation evidence, not a production readiness assessment.

| Symptom | Resolution |
| --- | --- |
| Python older than 3.12 | Install a supported interpreter; select its binary through the Makefile's Python setting. |
| Dependency installation fails | Confirm interpreter/network settings; retain the error and use the pinned dependency files. |
| Port 8080 in use | Stop the prior sample process before testing. |
| Protected routes return 401 | Supply the documented token map at startup and matching bearer header. |
| Scanner binary missing | Setup does not install every optional tool; follow that lab's prerequisites. |

Stop the server with Ctrl+C. Synthetic records are in memory. Keep `.venv` for the next lab and keep local credentials/generated reports out of commits. Continue to [Lab 01](../labs/lab-01-precommit-sast/README.md).
