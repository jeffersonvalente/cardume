---
name: observability-patterns
description: "Guides vendor-neutral observability: OpenTelemetry instrumentation and Collector pipelines, trace-correlated logs, RED/USE, SLOs with multi-burn-rate alerts, dashboards, sampling and cardinality cost control, and telemetry-driven incident investigation. Use when instrumenting a service, defining SLOs or alerts, designing dashboards, or debugging latency/error spikes."
allowed-tools: Read Grep Glob
---

# Observability Patterns

> Make systems answer "is it broken, for whom, and why" in minutes. OpenTelemetry first,
> backend-agnostic, symptom-based alerting, cost-aware by design.

For GCP data-platform specifics (Composer DAG failures, BigQuery slot/cost spikes, GCS staging,
Cloud Logging MCP calls), use `cardume-data:gcp-observability-patterns` instead of this skill.

## Reference files (load only what the task needs)

| File | Load when |
| :--- | :--- |
| `reference/instrumentation.md` | Adding OTel to Node, Python, Java/Spring, Go; Collector config; log correlation |
| `reference/slo-alerting.md` | Writing SLIs/SLOs, burn-rate rules, alert templates, dashboard layout |
| `reference/backends-and-cost.md` | Mapping to Prometheus/Grafana, Datadog, New Relic, Elastic, GCP, AWS; cardinality, sampling, retention, RUM |
| `reference/incident-investigation.md` | Investigating an active or past incident from telemetry |

---

## 1. OpenTelemetry first

OpenTelemetry (OTel) is the default instrumentation layer: one API/SDK per language, one wire
protocol (OTLP), many backends. It keeps the application code free of vendor SDKs.

- **SDK + auto-instrumentation.** Start with zero-code/auto-instrumentation (HTTP servers and
  clients, gRPC, DB drivers, messaging). Add manual spans only around business operations
  (`checkout.place_order`) and attributes that answer real questions.
- **Resource attributes** identify the emitter on every signal: `service.name`,
  `service.version`, `deployment.environment.name`, plus `k8s.*`/`cloud.*` added by resource
  detectors or the Collector. Set them via `OTEL_SERVICE_NAME` / `OTEL_RESOURCE_ATTRIBUTES`.
- **Semantic conventions.** Use the standard attribute names (`http.request.method`,
  `http.route`, `http.response.status_code`, `db.system.name`, `messaging.system`,
  `error.type`) so backends and dashboards work without custom mapping. Use the route template
  (`/orders/{id}`), never the raw path.
- **Context propagation.** W3C Trace Context (`traceparent`, `tracestate`) across HTTP/gRPC;
  inject/extract headers into message metadata for queues (Kafka, SQS, Pub/Sub) or use span
  links for batch consumers. `baggage` only for small, non-sensitive keys.
- **Collector pipelines.** Apps export OTLP to a Collector (agent per node/sidecar and/or a
  gateway). Pipelines are `receivers → processors → exporters`; standard processors:
  `memory_limiter`, `resourcedetection`/`k8sattributes`, `attributes`/`transform` (OTTL) or
  `redaction` for scrubbing, `filter` for dropping noise, `tail_sampling` at the gateway, and
  batching (`batch` processor after any sampling, or exporter-side `sending_queue` batching). Swapping backends is a
  Collector config change, not a code change.
- **Exemplars** attach a `trace_id` to histogram samples, so a latency spike on a dashboard
  links straight to an example trace. Enable them in the SDK and the metrics backend
  (Prometheus: `--enable-feature=exemplar-storage`; `spanmetrics`: `exemplars.enabled`).
- **Semconv stability.** HTTP, database, and core resource conventions are stable; GenAI/LLM
  conventions (`gen_ai.*`) are still in development, so pin the semconv version and expect
  renames.

## 2. Three signals (plus profiles), and when to use each

| Signal | Answers | Use for | Avoid |
| :--- | :--- | :--- | :--- |
| **Metrics** | How much / how often / how fast, aggregated | SLIs, alerts, dashboards, capacity | Per-user or per-request identity (cardinality) |
| **Traces** | Where did the time/error go in this request | Latency breakdown, dependency failures, fan-out | Long-term aggregates (sampled) |
| **Logs** | What exactly happened, with detail | Errors with context, audit, rare events | Counting things (use metrics) |
| **Profiles** | Which code burns CPU/memory | Hot paths, leaks; correlate via span IDs | First-line alerting |

OTel Profiles entered public alpha in 2026 (<https://opentelemetry.io/blog/2026/profiles-alpha/>):
usable for evaluation, but expect format and Collector changes before GA.

Rule of thumb: alert on metrics, navigate with traces, explain with logs.

## 3. Structured logging with trace correlation

- Emit JSON (or the platform's structured format) with stable keys: `timestamp`, `severity`,
  `message`, `service.name`, `trace_id`, `span_id`, plus event-specific fields.
- Inject `trace_id`/`span_id` from the active span through the logger integration or the OTel
  logs bridge; this is what makes "jump from trace to logs" work in every backend.
- Log events, not narration: one line per meaningful event, with the error type and the
  decision taken. Keep DEBUG off in production by default, switchable at runtime.
- **Never log secrets or personal data** (tokens, passwords, emails, CPF/national IDs, card
  numbers, full request bodies): logs are broadly readable and retained, and under LGPD/GDPR a
  leak there is a reportable incident. Use field allowlists, redact in the SDK, and redact again
  in the Collector as a safety net.

## 4. Golden signals, RED, USE

- **Golden signals (services):** latency, traffic, errors, saturation.
- **RED (request-driven services):** Rate, Errors, Duration, per route/operation. Measure
  duration as a histogram (explicit buckets or exponential/native histograms), never as an
  average.
- **USE (resources: CPU, memory, disks, pools, queues):** Utilization, Saturation, Errors.
  Saturation (queue depth, thread-pool wait, connection-pool wait, throttling) is usually the
  leading indicator.
- Queues/async: consumer lag (age of oldest message), processing rate, DLQ rate.

## 5. SLIs, SLOs, error budgets

1. Pick user journeys, then SLIs as ratios: `good events / valid events` (availability:
   non-5xx/total; latency: requests under threshold/total; freshness for pipelines).
2. Set an SLO target and window (e.g. 99.9% over 28-30 days). Error budget = `1 - target`
   (43 minutes of full outage per 30 days at 99.9%).
3. Agree on a budget policy: what happens when it is exhausted (freeze risky deploys,
   prioritize reliability work).
4. Alert on **burn rate** (how fast the budget is consumed), multi-window and multi-burn-rate:

| Severity | Burn rate | Long window | Short window | Budget consumed |
| :--- | :--- | :--- | :--- | :--- |
| Page | 14.4 | 1h | 5m | 2% |
| Page | 6 | 6h | 30m | 5% |
| Ticket | 3 (example rules) | 1d | 2h | 10% |
| Ticket | 1 | 3d | 6h | 10% |

```promql
# Recording rule: error ratio over a window (repeat for 5m, 30m, 1h, 2h, 6h, 1d, 3d)
job:slo_errors:ratio_rate1h =
  # Prometheus OTLP ingestion maps service.name to the `job` label
sum by (job) (rate(http_server_request_duration_seconds_count{http_response_status_code=~"5.."}[1h]))
/ sum by (job) (rate(http_server_request_duration_seconds_count[1h]))

# Fast-burn page for a 99.9% SLO (error budget 0.001)
(job:slo_errors:ratio_rate1h > (14.4 * 0.001)) and (job:slo_errors:ratio_rate5m > (14.4 * 0.001))
```

Page rows and the 3d/6h row are SRE Workbook Table 5-8; the 1d/2h row comes from its example
rules. The short window makes the alert reset quickly once the problem stops. Latency SLOs use the
same pattern with `good = requests under threshold` from histogram buckets. Full rule set,
latency variant, and generators (Sloth, Pyrra, OpenSLO): `reference/slo-alerting.md`.

## 6. Alert design

- **Page only on symptoms** users feel (SLO burn, total outage, data loss risk). Causes (CPU,
  restarts, disk 80%) go to dashboards or ticket-severity alerts unless they predict imminent
  user impact (disk full in < 4h).
- **Every alert is actionable**: a human must be able to do something now. If the answer is
  "wait and see", it is not a page.
- **Every alert carries**: severity (`page`/`ticket`), owner/team, a summary with the impacted
  journey and current value, a `runbook_url`, and links to the dashboard.
- Use `for:` durations or burn-rate windows to avoid flapping; group and inhibit (a region
  down should not page 40 times).
- Review alerts quarterly: delete or demote any that fired without action.
- **Changing production routing, receivers, silences, or paging schedules needs explicit
  confirmation**: a mis-routed alert fails silently until the next outage.

## 7. Dashboard layout

Per service, top to bottom: (1) SLO status and remaining budget; (2) RED per key route with
p50/p95/p99 from histograms and exemplars; (3) saturation (pools, queues, CPU throttling,
memory); (4) dependencies (outbound RED per downstream); (5) deploy/flag-change annotations.
Use template variables for environment/region/version, consistent units, and keep drill-down
boards separate. Store dashboards as code (JSON/Jsonnet/Terraform) next to the service.

## 8. Cardinality and cost control

- Series count = product of label values. Never use unbounded labels on metrics: user/tenant
  IDs (unless a small fixed set), request IDs, raw URLs, error messages, timestamps.
- Put high-cardinality detail on spans and logs, which are sampled or indexed selectively.
- Drop unused metrics and attributes in the Collector; aggregate before export where possible.
- Set retention per signal (e.g. metrics 13 months downsampled, traces 7-14 days, debug logs
  days) and log levels per environment.
- Estimate the cost impact (new series, GB/day) before shipping a new metric or log stream.

## 9. Sampling

- **Head sampling** (decided at the root, `parentbased_traceidratio`): cheap and simple, but
  blind to outcome, so it drops most errors at low ratios.
- **Tail sampling** (Collector gateway, after the trace completes): keep 100% of errors and slow
  traces, a small percentage of the rest. Needs all spans of a trace routed to the same
  Collector (load-balancing exporter by trace ID) and memory for the decision wait.
- Compute RED metrics before sampling so sampling never distorts SLIs: either SDK HTTP
  semconv metrics (`http.server.request.duration`) or the Collector `spanmetrics` connector
  (alpha; emits `traces.span.metrics.calls`/`.duration` by default, labelled `service.name`,
  `span.name`, `span.kind`, `status.code`). SLO rules must use the names of the source chosen.

## 10. Backends without lock-in

Instrument with OTel, export OTLP to a Collector, and choose exporters per backend:
Prometheus/Grafana/Loki/Tempo (or Mimir), Datadog, New Relic, Elastic, GCP Cloud Monitoring/
Trace/Logging, AWS CloudWatch/X-Ray. All accept OTLP natively or through a Collector
exporter. Mapping table, query-language equivalents, and migration notes:
`reference/backends-and-cost.md`. Telemetry stays in the backends the user operates or has
chosen; do not send production data to third-party tools.

## 11. Frontend / RUM basics

Measure Core Web Vitals (LCP, INP, CLS) and JS errors from real users, propagate
`traceparent` on fetch/XHR to your own APIs (configure CORS allowlists), and sample sessions.
Mask form inputs and never capture PII in session replay. Details in
`reference/backends-and-cost.md`.

## 12. Incident investigation from telemetry

1. **Confirm impact** against the SLO: which journey, how bad, since when.
2. **Scope**: break down by route, region, version, host/pod, tenant tier, dependency.
3. **Find the change**: deploys, flags, config, traffic shifts, dependency incidents.
4. **Follow exemplars** from the latency/error panel into traces; find the slow/failing span.
5. **Read correlated logs** by `trace_id` for the exact error.
6. **Mitigate first** (rollback, flag off, shed load) via the owner, then root cause.
7. **Close the loop**: add the missing signal, alert, or runbook step.

Read-only queries are free; mitigations are changes and go through the user or the owning agent.
Query recipes and a timeline template: `reference/incident-investigation.md`.

## Handover checklist

- [ ] OTel SDK + resource attributes set; traces propagate across every hop, including queues
- [ ] Logs structured with `trace_id`/`span_id`, no secrets or PII
- [ ] SLIs as good/valid ratios, SLO target and budget policy agreed with the owner
- [ ] Burn-rate alerts with severity, owner, runbook link; rules tested
- [ ] Service dashboard with SLO, RED, saturation, dependencies, deploy annotations
- [ ] Cardinality, sampling, and retention decisions written down with expected cost
