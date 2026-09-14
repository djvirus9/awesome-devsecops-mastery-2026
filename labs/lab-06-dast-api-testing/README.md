# Lab 06: defensive API validation

Phase 4 · 30–45 minutes · local Python only. This is Lab 06 for historical URL compatibility. Use the supplied synthetic API and [foundation setup](../../docs/foundation.md); no external target, cloud account, or privileged scanner is required.

## Exercise and expected coverage

Read the [API setup](../../samples/sample-api/README.md), [OpenAPI contract](../../samples/sample-api/openapi.yaml), and [regression tests](../../tests/test_sample_api.py). Run from the repository root:

```bash
make setup
.venv/bin/python -m unittest discover -s tests -p 'test_sample_api.py' -v
```

These tests use the application test client with synthetic owners and tokens. They check expected behavior without starting a remote service.

| Route/state | Expected result | Risk addressed |
| --- | --- | --- |
| `GET /health`, no token | 200 health response | Health endpoint contract. |
| Protected route, missing/invalid token | 401 | Authentication required. |
| List with Alice/Bob identity | Only that owner's records | Server-side ownership filtering. |
| Item owned by caller | 200 and expected record | Authorized behavior remains usable. |
| Other owner's or absent item | Unavailable with consistent response | No cross-owner disclosure. |

Compare the table with the OpenAPI document and tests. If a new route is introduced, add positive and negative requirements before considering it covered.

For a real HTTP sanity check, start the sample with the explicit demonstration token map from the [quick start](../../README.md), then make the two documented successful local requests. Unit tests and local HTTP checks establish different evidence; neither validates a TLS proxy, gateway, or production identity provider.

## Baseline DAST versus API authorization

A passive baseline can identify issues in observed responses, such as missing headers. It cannot establish that every owner/route authorization rule is correct. This lab's required path is the deterministic regression suite. Optional passive-only local observation is described in [recipes](../../recipes/README.md); retain reports and keep the synthetic service in an isolated environment. There is no active scan or arbitrary-target workflow in this lab.

## Verification, troubleshooting, cleanup

Record the test count/result, commit, route/owner coverage, and remaining deployment boundaries. Do not infer authenticated coverage from a healthy public endpoint.

If tests cannot import Flask, rerun `make setup` and use `.venv/bin/python`. If the local HTTP request returns 401, check the server's token map and bearer header. If the port is occupied, stop the existing sample process before retrying.

Stop the optional server with Ctrl+C. Test data stays in memory, and the suite creates no customer accounts. Challenge: add a harmless new owner with no records in a private exercise and define the list response. Solution: authenticated empty collection, without returning another owner's data; add a regression to preserve that expectation.
