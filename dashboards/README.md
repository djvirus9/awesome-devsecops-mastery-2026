# Metrics dashboard demo

[Grafana JSON](grafana-devsecops.json) contains three Prometheus queries for the included [fictional incident cohort](../metrics-templates/README.md). No production SLA or SBOM coverage is fabricated. The fixture covers January 2026; changing Grafana's time picker changes scrape history, not cohort membership.

## Local setup

Prerequisites: Python 3.12+, an installed Prometheus server and Grafana with the built-in Prometheus datasource. Use services on the same host for this example.

1. At repository root, run `python3 scripts/metrics.py --serve` in a terminal.
2. Start Prometheus with `prometheus --config.file=dashboards/prometheus.yml --web.listen-address=127.0.0.1:9090`. The supplied config scrapes `127.0.0.1:9108` every 15 seconds.
3. In Grafana, add a Prometheus datasource with URL `http://127.0.0.1:9090`. Test the connection.
4. Import `grafana-devsecops.json`, then select that datasource in the dashboard's Prometheus dropdown.
5. Confirm `up{job="devsecops-demo"}` is 1 in Prometheus. Expected panels: 18 hours resolution, 20 minutes acknowledgment, 2 incidents. An empty cohort yields no mean; missing telemetry must not be interpreted as zero risk.

For containers, localhost belongs to each container. A native loopback exporter is not generally reachable via Docker bridge networking, including `host.docker.internal`. Either run the three processes natively as above, or supply a deliberate network design in your own deployment. On Linux, host networking can preserve loopback reachability; it is not a portable Docker Desktop assumption. Do not solve reachability by exposing the demo exporter publicly.

Stop the exporter and foreground Prometheus with Ctrl-C; remove the imported dashboard/datasource through Grafana when no longer needed. Fixture arithmetic and query-presence tests alone do not prove a successful Grafana import/render. Record actual versions and results when performing the acceptance check below.

## Isolated Linux CI acceptance check

`python3 scripts/validate_dashboard.py` runs the fixture with a Linux-container Docker daemon. It pulls pinned official Python, Prometheus, Grafana and Grafana Image Renderer images, then creates four task-named containers on a temporary internal network. **No service ports are published.** The containers share the exporter's network namespace, so the existing loopback-only exporter does not need a public bind. Grafana API and rendering requests run through a bounded HTTP helper inside that namespace, returning evidence through Docker exec. This avoids relying on host port publishing, which Docker does not establish for an internal-only bridge. No host network, Docker-socket mount, host sensor, production dataset, or existing Grafana installation is used.

The script provisions the committed dashboard and a temporary datasource, asserts scrape health and all three values through both Prometheus and Grafana, and requests three PNGs through Grafana's server-side rendering integration. It records a fresh `reports/dashboard/<run-id>/` directory containing image pins/resolved digests, service/query evidence, `panel-1.png` through `panel-3.png`, logs, and `summary.json`. A failure exits nonzero; earlier runs are not overwritten. Containers and the network created by that invocation are removed, while evidence and downloaded image cache remain. It does not prune unrelated resources. It rejects a non-local Docker endpoint, fixes the selected context for cleanup, and handles normal cancellation signals. Use an ephemeral runner: forced termination or lost Docker connectivity can prevent cleanup.

Inspect all three PNGs before recording **visual** acceptance: expected values are 18 hours, 20 minutes, and 2 incidents, with no error or empty-data state. PNG structure and numeric API assertions alone do not establish readable rendering. This verifies only the fictional cohort, not production SLA measurement. The script has offline tests:

```bash
python3 -m unittest discover -s tests -p test_dashboard_validation.py
```

The pins were checked against official release metadata and Docker Registry manifests on 2026-09-15: Grafana 13.2.1, Image Renderer 5.12.3, Prometheus 3.14.0, Python 3.12.14/Alpine 3.24. Pins identify test infrastructure bytes, not vulnerability-free images or trusted provenance. Review upstream releases and repeat the acceptance run when updating them. Grafana supports only its latest renderer release; do not leave this pin unmaintained.

Upstream recommends at least 16 GiB/4 CPUs for rendering. This bounded check renders one small panel at a time and caps the renderer at 8 GiB/2 CPUs; these are test resource limits, not production sizing advice. Use an adequately provisioned runner and treat resource/time-limit failures as failed validation. The renderer uses its upstream browser sandbox default inside the restricted disposable container; it never accepts an arbitrary external rendering target here.

References: [Grafana image rendering service and sizing](https://grafana.com/docs/grafana/latest/setup-grafana/image-rendering/), [renderer configuration](https://grafana.com/docs/grafana/latest/setup-grafana/image-rendering/flags/), [Grafana provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/), [Docker shared network namespaces](https://docs.docker.com/engine/network/#container-networks).

References: [Prometheus configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/), [Grafana Prometheus datasource](https://grafana.com/docs/grafana/latest/datasources/prometheus/configure/), [KPI definitions](kpi-definitions.md).
