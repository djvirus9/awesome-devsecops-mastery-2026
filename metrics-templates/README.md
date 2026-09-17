# Incident metric fixtures

[JSON](incident-metrics.json) and [CSV](incident-metrics.csv) describe the same **fictional, closed incident cohort**. They are not evidence of this repository's performance.

Each row requires a unique nonempty incident ID; severity Critical/High/Medium/Low; timezone-aware ISO 8601 detection, acknowledgment and resolution timestamps in that order; root-cause text; and numeric `mttr_hours`. The legacy column name means **detection-to-resolution hours per incident**, not a mean and not a vulnerability-remediation SLA. The exporter recomputes duration from events and rejects inconsistent stored values. Open incidents are outside this demo schema; do not use it to calculate compliance or backlog health.

From the repository root:

```bash
python3 scripts/metrics.py
python3 -m unittest discover -s tests -p test_metrics.py
python3 scripts/metrics.py --serve --port 9108
```

The default input also checks CSV/JSON parity. `--input path.json` validates a separate dataset using the same schema. The server binds only to loopback and loads a fixed snapshot on startup; restart it after editing the dataset. It exports aggregate counts/durations, never incident IDs or root causes. Ctrl-C stops it.

Expected fixture totals: 2 incidents, 129600 resolution seconds and 2400 acknowledgment seconds; means are **18 hours** and **20 minutes**. See [dashboard setup](../dashboards/README.md) and [metric definitions](../dashboards/kpi-definitions.md).
