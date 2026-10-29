# Backends, Cost, and RUM Reference

## Backend mapping

Instrument once with OTel, export OTLP to a Collector, and pick exporters. Most backends now
ingest OTLP directly; the Collector still gives you redaction, sampling, and a single switch
point.

| Concern | Prometheus / Grafana stack | Datadog | New Relic | Elastic | GCP | AWS |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Metrics | Prometheus / Mimir / Thanos (PromQL) | Metrics (DD query) | Metrics (NRQL) | Elasticsearch TSDS (ES\|QL, KQL) | Cloud Monitoring (PromQL supported, MQL legacy) | CloudWatch Metrics (Metrics Insights) |
| Traces | Tempo (TraceQL) | APM | Distributed tracing | Elastic APM | Cloud Trace | X-Ray / CloudWatch Application Signals |
| Logs | Loki (LogQL) | Log Management | Logs (NRQL) | Elasticsearch | Cloud Logging | CloudWatch Logs (Logs Insights) |
| SLO objects | Sloth/Pyrra rules, Grafana SLO | SLOs | Service levels | SLOs | Service Monitoring SLOs | Application Signals SLOs |
| OTLP ingest | Native (Prometheus OTLP receiver, Tempo, Loki) | Agent/Collector exporter or OTLP intake | Native OTLP endpoint | Native / APM server | Native OTLP endpoint / Collector exporters | ADOT Collector, native OTLP endpoints |
| Exemplars | Prometheus + Grafana | Trace-metric correlation | Built in | Built in | Built in | Application Signals |

Avoiding lock-in:
- Keep vendor SDKs and vendor-specific attribute names out of application code; use OTel API and
  semantic conventions.
- Keep SLO specs (OpenSLO, Sloth) and dashboards as code in the repo, so they can be regenerated
  for another backend.
- Accept vendor features (anomaly detection, APM service maps) as additive, not as the only
  place a critical alert lives.
- Telemetry goes only to backends the user operates or has chosen; mention data residency when
  the backend region differs from where users' data lives (LGPD/GDPR).

For GCP data-platform diagnostics (Composer, BigQuery, GCS), see
`cardume-data:gcp-observability-patterns`.

## Query equivalents (error ratio, last 5 minutes)

```text
PromQL : sum(rate(http_server_request_duration_seconds_count{job="checkout-api",http_response_status_code=~"5.."}[5m])) / sum(rate(http_server_request_duration_seconds_count{job="checkout-api"}[5m]))
LogQL  : sum(rate({service_name="checkout-api"} | json | status >= 500 [5m])) / sum(rate({service_name="checkout-api"}[5m]))
TraceQL: { resource.service.name = "checkout-api" && status = error }
NRQL   : SELECT percentage(count(*), WHERE error IS true) FROM Span WHERE service.name = 'checkout-api' SINCE 5 minutes ago
Logs Insights: filter status >= 500 | stats count(*) by bin(1m)
```

Treat these as starting points; field names depend on how the data was ingested (Loki, for
example, exposes `service.name` as the `service_name` stream label; Prometheus uses `job`).

## Prometheus OTLP ingestion

The OTLP receiver is off by default (`--web.enable-otlp-receiver`, endpoint
`/api/v1/otlp/v1/metrics`). Resource attributes are mapped as follows
(<https://prometheus.io/docs/guides/opentelemetry/>):

- `service.name` → `job` (as `<service.namespace>/<service.name>` when a namespace is set);
  `service.instance.id` → `instance`.
- Other resource attributes land on one `target_info` series per resource, not on every metric.
  Query them with the `info()` PromQL function or a join, or promote the few you filter on:

```yaml
otlp:
  promote_resource_attributes: [service.version, deployment.environment.name, k8s.namespace.name]
  translation_strategy: UnderscoreEscapingWithSuffixes   # default
```

`translation_strategy` controls names: the default escapes dots to underscores and appends
unit/type suffixes (`http.server.request.duration` → `http_server_request_duration_seconds`);
`NoUTF8EscapingWithSuffixes` and `NoTranslation` keep the OTel names using Prometheus 3 UTF-8
support (queries then quote them: `{"http.server.request.duration"}`). Pick one strategy per
deployment and write rules against it; changing it later renames every series.

Promote only bounded attributes: each promoted attribute is a label on every series.

## RED from spans (`spanmetrics` connector)

The contrib `spanmetrics` connector (alpha) emits `calls` and `duration` metrics under the
namespace `traces.span.metrics` by default, with at least `service.name`, `span.name`,
`span.kind`, and `status.code` as dimensions; durations are in ms by default and exemplars are
off unless `exemplars.enabled: true`. After Prometheus translation expect names like
`traces_span_metrics_calls_total` and `traces_span_metrics_duration_milliseconds_bucket`. These
are not the HTTP semconv metrics (`http.server.request.duration`) the SDK emits, so SLO rules
must target whichever source you chose. Check the connector README for current defaults.

## Cardinality control

1. **Find offenders.** Prometheus: `topk(20, count by (__name__)({__name__=~".+"}))`, then
   `count by (label) (metric)` for the top metrics; the TSDB status page lists top label values.
   Vendors expose a usage/cardinality page; start there.
2. **Classify each label.** Bounded and useful (method, route template, status class, region)
   keeps; unbounded (user ID, order ID, raw URL, IP, error message) moves to spans/logs.
3. **Fix at the source** (instrumentation views/allowlists: OTel SDK `View`s can drop attributes
   or change histogram buckets), and **enforce in the Collector** (`filter`, `attributes`,
   `transform`, `metricstransform`) so a bad deploy can't explode the bill.
4. **Histograms.** Prefer exponential/native histograms (fewer series, better resolution) where
   the backend supports them; otherwise choose a small explicit bucket set around SLO
   thresholds. Prometheus native histograms are stable since v3.8; from v3.9 scraping them
   requires `scrape_native_histograms: true` (global or per scrape config), and remote write
   needs `send_native_histograms`. Exemplar storage is still behind
   `--enable-feature=exemplar-storage`. OTLP exponential histograms arrive as native
   histograms. See <https://prometheus.io/docs/specs/native_histograms/>.

## Retention and log volume

| Signal | Typical hot retention | Notes |
| :--- | :--- | :--- |
| Metrics | 13-15 months, downsampled after ~30 days | Year-over-year capacity planning |
| Traces | 7-14 days | Keep sampled errors/slow traces longer if cheap |
| Application logs | 7-30 days hot, archive to object storage | Compliance may require longer for audit logs |
| Audit logs | As required by policy | Separate pipeline and access control |

Reduce log cost by: dropping health-check and DEBUG logs at the Collector, sampling repetitive
INFO logs, converting high-volume "counting" logs into metrics, and avoiding full payload dumps.

## Sampling decision guide

| Situation | Choose |
| :--- | :--- |
| Low traffic (< ~100 req/s per service) | Keep 100%, no sampling |
| High traffic, simple ops | Head sampling 5-20%, parent-based |
| Need every error and slow request | Tail sampling at a Collector gateway |
| SLIs from traces | Generate metrics from 100% of spans before sampling (`spanmetrics`) |

Always keep the sampling decision consistent across a trace (parent-based) and record the
sampling ratio so backends can extrapolate counts. OTel's consistent probability sampling spec
(status: Development) records the sampling threshold in `tracestate` (`ot=th:...`) so every
tier makes compatible decisions and backends can compute adjusted counts; check SDK and
Collector support before relying on it
(<https://opentelemetry.io/docs/specs/otel/trace/tracestate-probability-sampling/>).

## Frontend / RUM

- Use the OTel browser SDK (or the backend's RUM agent) for document load, fetch/XHR, and user
  interaction spans, and the `web-vitals` library for LCP, INP, CLS (INP replaced FID).
- Good thresholds (75th percentile of page loads): LCP <= 2.5 s, INP <= 200 ms, CLS <= 0.1.
- Propagate `traceparent` only to your own API origins (`propagateTraceHeaderCorsUrls` or the
  agent's allowlist) and allow the header in CORS; never to third-party origins.
- Capture JS errors with source maps uploaded at build time, tagged with release version.
- Sample sessions; session replay masks all inputs and text by default, and never captures
  PII, tokens, or payment fields. Get consent where the jurisdiction requires it.
- Mobile: OTel Android/Swift SDKs or vendor RUM; track app start, crashes, ANRs, network spans.
