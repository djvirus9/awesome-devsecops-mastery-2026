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

Stop the exporter and foreground Prometheus with Ctrl-C; remove the imported dashboard/datasource through Grafana when no longer needed. This repository tests fixture arithmetic and query presence; a successful Grafana import/render is a separate manual acceptance check. Record actual versions and results when performing it.

References: [Prometheus configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/), [Grafana Prometheus datasource](https://grafana.com/docs/grafana/latest/datasources/prometheus/configure/), [KPI definitions](kpi-definitions.md).
