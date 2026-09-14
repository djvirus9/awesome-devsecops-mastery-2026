# Sample API: the shared reference application

A small, read-only Flask application for learning control integration. It holds two synthetic items in memory and maps explicitly supplied bearer tokens to owners. The same application is used for source checks, API regression tests, container build/inventory, and optional deployment exercises.

## Setup and local run

Use Python 3.12 or newer. Run from the **repository root**, not this sample directory:

```bash
make setup
make test
make validate
API_TOKENS_JSON='{"demo-alice-token":"alice","demo-bob-token":"bob"}' make run
```

`make setup` creates `.venv` and installs the complete hash-locked development dependencies. `make run` uses the Flask development server with debugging disabled, bound to `127.0.0.1:8080`. It is for the local exercise. Stop it with Ctrl+C.

In another terminal:

```bash
DEMO_ALICE_TOKEN='demo-alice-token'
DEMO_BOB_TOKEN='demo-bob-token'
curl --fail http://127.0.0.1:8080/health
curl --fail -H "Authorization: Bearer $DEMO_ALICE_TOKEN" http://127.0.0.1:8080/v1/items
curl --fail -H "Authorization: Bearer $DEMO_BOB_TOKEN" http://127.0.0.1:8080/v1/items/item-2
```

Expected bodies are `{"status":"ok"}`, a collection containing Alice's `item-1`, and Bob's `item-2`, respectively. Names are synthetic training text; no customer data is present.

## Identity and API contract

[app.py](app.py) contains the implementation; [openapi.yaml](openapi.yaml) describes the routes and bearer scheme. The public demonstration token strings above have no use outside the isolated exercise.

| Route | Credentials | Result |
| --- | --- | --- |
| `GET /health` | None required | 200 with process health; no dependency/readiness checks are implied. |
| `GET /v1/items` | Configured bearer token | 200 with only the caller's item IDs/names. |
| `GET /v1/items/{item_id}` | Configured bearer token, owned record | 200 with that item. |
| Either protected route | Missing or invalid token | 401 and a bearer authentication challenge. |
| Item detail | Valid token, absent or other owner's record | 404 with the same response shape. |

`API_TOKENS_JSON` must be a JSON object mapping nonempty ASCII tokens (at most 256 characters, no whitespace) to nonempty owner strings. There are **no default tokens**: an omitted value is an empty map, and all protected requests are unauthorized. Invalid configuration fails startup without echoing credential values. The configured map is loaded at application creation, so changes require restarting the process.

Item ownership is decided on the server; callers cannot select another owner using request parameters. Error responses and denial logs omit bearer values. Responses include `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, and a restrictive content security policy. These defaults do not replace deployment TLS, gateway policy, or identity design.

## Regression tests

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_sample_api.py' -v
```

[The tests](../../tests/test_sample_api.py) use Flask's in-process client with explicit synthetic identities. They cover public health, missing/invalid credentials, owner-filtered lists, per-item ownership, absent/default configuration, credential redaction, and response headers. They make no external requests. [Lab 06](../../labs/lab-06-dast-api-testing/README.md) explains route/identity coverage and the remaining deployment boundaries.

## Container run and smoke check

Docker is optional until this stage. The [Dockerfile](Dockerfile) uses a digest-pinned Python base, hash-locked runtime dependencies, non-root UID/GID 10001, and Gunicorn bound to port 8080 inside the container. Binding inside the container is separate from exposing a host port.

The runtime uses Alpine 3.24 (musl), with an explicit `libuuid=2.42.3-r1` security update because the pinned base predates that package release. Runtime dependencies install only from hash-verified wheels; the lock includes CPython 3.12 musllinux wheels for amd64 and arm64. Review package availability, compatibility, and the image scan whenever changing the base or lock. See the [base-image validation record](../../docs/validation.md#container-base-selection).

```bash
make container
make container-test
```

The default image name is `devsecops-reference:local`; `make container` builds it but does not start a service or publish it. The smoke helper starts a uniquely named, temporary container on a random loopback-only host port, checks health/authentication/ownership, and stops that container. It uses a read-only filesystem, dropped capabilities, no new privileges, and a small `/tmp` mount.

For an interactive local session, stop any existing server on port 8080 and run:

```bash
docker run --rm --name devsecops-reference-demo \
  --publish 127.0.0.1:8080:8080 \
  --read-only --cap-drop ALL --security-opt no-new-privileges \
  --tmpfs /tmp:rw,nosuid,nodev,size=16m \
  --env API_TOKENS_JSON='{"demo-alice-token":"alice","demo-bob-token":"bob"}' \
  devsecops-reference:local
```

Use the same local HTTP requests above. Stop with Ctrl+C; if needed, `docker stop devsecops-reference-demo` stops this named practice container. `--rm` removes it after stopping. Retain the image for the inventory lab or remove it with `docker image rm devsecops-reference:local` when finished.

## Dependencies, image inventory, and release evidence

[requirements.in](requirements.in) lists direct runtime dependencies; [requirements.txt](requirements.txt) contains the complete hash-locked resolution used by the image. The root [development input](../../requirements-dev.in) adds tooling required by local checks, with its own [lock](../../requirements-dev.txt). Review input and generated-lock changes together; changing only one can make local and container installations diverge.

Install the pinned Syft binary, then inventory the already-built image:

```bash
python3 scripts/install_tool.py syft
make sbom
```

The Makefile includes `.tools/bin` on its command path. Syft explicitly loads [its configuration](../../configs/syft.yaml) and writes `reports/sbom.cdx.json` from the image. A source-directory inventory has different coverage. [Lab 03](../../labs/lab-03-sbom-signing/README.md) explains signatures, retained bundles, and expected identity verification.

Normal PR/main CI performs checks and retains reports without signing or publishing. Only the separate, manually dispatched [release workflow](../../.github/workflows/release.yml) publishes and signs a registry image after checks. Its presence is not evidence that a release was run; no release is triggered by the commands on this page.

## Limitations and troubleshooting

This reference has no login/password flow, token issuance/expiry/revocation service, persistent database, rate limiter, production TLS, or cloud deployment. Token mapping is deliberately simple and read-only data is deterministic. Read the [threat model](../../docs/reference-architecture.md) before adapting it.

Denial logs expose sanitized application events, but they are not directly the normalized fixture format used by Lab 05. That offline exercise uses [fabricated telemetry](../../labs/lab-05-runtime-detection/README.md); a live collector/adapter and heartbeat/delivery tests remain separate deployment work.

| Symptom | Check |
| --- | --- |
| `ModuleNotFoundError` | Run `make setup` at repository root and use `.venv/bin/python`. |
| 401 on a protected route | Check the startup token map and exact bearer value; there is no implicit account. |
| Startup configuration error | Correct JSON/map types without logging actual credentials. |
| Port 8080 busy | Stop the previous sample process or named practice container. |
| Docker unavailable | Continue the Python path; record image/container checks as pending. |
| Syft missing or no image found | Install the declared binary and run `make container` before `make sbom`. |

See [foundation setup](../../docs/foundation.md), [the capstone](../../projects/microservice-api/README.md), and [validation scope](../../docs/validation.md) for the connected learning path.
