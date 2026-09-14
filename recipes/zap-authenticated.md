# Observe the local API with authenticated passive ZAP

Status: documented manual exercise; record your installed ZAP/add-on versions and actual result. This is passive inspection of one local GET, not comprehensive DAST or proof that authorization is correct. Automated authorization checks are in `make test`.

Prerequisites: native ZAP desktop with Replacer, passive scanning and report-generation add-ons; curl; the repository's Python environment. Use only the provided loopback API and fictional tokens.

1. At repository root, start the sample: `API_TOKENS_JSON='{"demo-alice-token":"alice","demo-bob-token":"bob"}' make run`.
2. Open ZAP in **Safe mode**. Configure its local proxy to listen on `127.0.0.1:8090` so it does not conflict with the API's port 8080.
3. In Options → Replacer, add an enabled rule: description `local-demo-auth`; URL `^http://127\.0\.0\.1:8080/.*$`; match type **Request Header (will add if not present)**; match string `Authorization`; replacement `Bearer demo-alice-token`. Leave regex matching of the header name disabled. An empty URL applies to all messages, so the URL restriction is essential.
4. Send just the local read request below. The proxy inserts the fictional token. Confirm a 200 response and Alice's `item-1` in the returned items; a login error/401 is failed authenticated coverage, not a clean scan.
5. Review the request in ZAP History, wait for the passive queue to drain, and export a report through the report-generation dialog into a local evidence directory. Record ZAP version, exact localhost URL, identity, observation count and limitations. Keep real credentials and sensitive responses out of published reports.
6. Disable/delete the Replacer rule, close the ZAP session and stop the API with Ctrl-C. Do not reuse fictional demo tokens in deployed systems.

```bash
curl --proxy http://127.0.0.1:8090 --noproxy '' --fail http://127.0.0.1:8080/v1/items
```

No spider or active scan is needed for this exercise. A single observed route leaves other routes, identities and behavior unassessed. Reference [the API contract](../samples/sample-api/openapi.yaml) when documenting coverage.

If you adapt report generation to containers later, use the [current official image](https://www.zaproxy.org/docs/docker/about/) and mount the report directory at `/zap/wrk`; output in an automatically removed container is not durable evidence. Container localhost is separate from host localhost. The supplied recipe deliberately uses the native local proxy.

References checked 2026-09-15: [Replacer URL scoping](https://www.zaproxy.org/docs/desktop/addons/replacer/), [passive baseline scope and file mounts](https://www.zaproxy.org/docs/docker/baseline-scan/). No ZAP runtime result is claimed by this document.
