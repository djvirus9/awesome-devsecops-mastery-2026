# Phase 6: runtime detection and telemetry health

Use [Lab 05](../../labs/lab-05-runtime-detection/README.md). The required exercise evaluates supplied synthetic events offline; no privileged host sensor or external alert destination is needed.

A useful detection needs a documented source/schema, testable rule, positive and negative examples, grouping/deduplication behavior, service context, accountable owner, and runbook. Add telemetry health independently: no observed alerts may mean no collector.

SRE owns source/delivery health; the detection owner owns rule behavior and noise; the service owner explains expected workload behavior. Definition of done: the fixture yields the expected denial alert and missing-heartbeat alert; routine/duplicate events do not inflate results; invalid input fails visibly. Local owner labels demonstrate routing data, not external delivery.

Live Falco deployment is optional and requires compatible Linux/driver settings, explicit chart/tool versions, benign test evidence, and an actual destination-delivery check. Detection does not itself implement blocking. See [Falco setup](https://falco.org/docs/setup/) and [driver requirements](https://falco.org/docs/setup/download/).

Use [dashboards](../../dashboards/README.md) for metrics and [Phase 7](07-ir-detections.md) for response decisions. Keep observed sensor results separate from offline fixture results.
