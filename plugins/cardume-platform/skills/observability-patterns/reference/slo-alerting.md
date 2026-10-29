# SLOs and Alerting Reference

PromQL is used as the lingua franca; the same logic translates to Datadog SLO monitors,
New Relic service levels, Elastic SLOs, Cloud Monitoring SLOs, and CloudWatch Application
Signals SLOs (see `backends-and-cost.md`). Metric names follow the OTel HTTP semantic
conventions (`http.server.request.duration`) as translated by Prometheus OTLP ingestion with
the default `UnderscoreEscapingWithSuffixes` strategy; adjust to what the service actually
emits. Prometheus maps the resource attribute `service.name` (prefixed by `service.namespace/`
when set) to `job` and `service.instance.id` to `instance`; other resource attributes go to
`target_info` unless promoted (see `backends-and-cost.md`), so filter on `job`, not
`service_name`.

If the SLI comes from the Collector `spanmetrics` connector instead, the series are named after
its namespace (default `traces.span.metrics` → e.g. `traces_span_metrics_calls_total`,
`traces_span_metrics_duration_milliseconds_bucket`, unit ms by default), with labels
`service_name`, `span_name`, `span_kind`, `status_code`; there is no HTTP status label unless
you add it as a dimension. Check the exact names in your backend before writing rules.

## Choosing SLIs

| Journey type | SLI (good / valid) | Notes |
| :--- | :--- | :--- |
| Request/response API | non-5xx / all requests (exclude health checks) | 4xx is usually the client's fault; count 429 as bad if you throttle legit users |
| Latency | requests under threshold / all requests | Pick threshold from user expectation (e.g. 300 ms p-target), one SLO per tier if needed |
| Async pipeline | messages processed within N min / messages | Or freshness: age of newest processed record < N |
| Batch job | runs finished on time and correct / scheduled runs | |
| Frontend | page loads with LCP < 2.5 s / page loads | From RUM |

Measure as close to the user as practical (load balancer or gateway beats the pod; RUM beats
both for the frontend). Write each SLO down: SLI definition, target, window, owner, budget policy.

## Recording rules

```yaml
groups:
  - name: slo-checkout-api
    rules:
      # Error ratio per window
      - record: slo:errors:ratio_rate5m
        expr: |
          sum(rate(http_server_request_duration_seconds_count{job="checkout-api",http_response_status_code=~"5.."}[5m]))
          /
          sum(rate(http_server_request_duration_seconds_count{job="checkout-api"}[5m]))
      # repeat for 30m, 1h, 2h, 6h, 1d, 3d (only the range changes)

      # Latency "bad" ratio: share of requests slower than 0.3 s (le must match a real bucket)
      - record: slo:latency_bad:ratio_rate5m
        expr: |
          1 - (
            sum(rate(http_server_request_duration_seconds_bucket{job="checkout-api",le="0.3"}[5m]))
            /
            sum(rate(http_server_request_duration_seconds_count{job="checkout-api"}[5m]))
          )
```

## Multi-window multi-burn-rate alerts (SLO 99.9%, budget 0.001)

```yaml
  - name: slo-checkout-api-alerts
    rules:
      - alert: CheckoutApiErrorBudgetFastBurn
        expr: |
          (slo:errors:ratio_rate1h > (14.4 * 0.001) and slo:errors:ratio_rate5m > (14.4 * 0.001))
          or
          (slo:errors:ratio_rate6h > (6 * 0.001) and slo:errors:ratio_rate30m > (6 * 0.001))
        labels:
          severity: page
          team: checkout
          slo: checkout-api-availability
        annotations:
          summary: "checkout-api is burning its 30d error budget fast ({{ $value | humanizePercentage }} errors)"
          description: "At this rate the monthly budget is gone in hours. Customers are failing to place orders."
          runbook_url: https://runbooks.acme.internal/checkout-api/error-budget-burn
          dashboard_url: https://grafana.acme.internal/d/checkout-api

      - alert: CheckoutApiErrorBudgetSlowBurn
        expr: |
          (slo:errors:ratio_rate1d > (3 * 0.001) and slo:errors:ratio_rate2h > (3 * 0.001))
          or
          (slo:errors:ratio_rate3d > (1 * 0.001) and slo:errors:ratio_rate6h > (1 * 0.001))
        labels: { severity: ticket, team: checkout, slo: checkout-api-availability }
        annotations:
          summary: "checkout-api is steadily consuming error budget"
          runbook_url: https://runbooks.acme.internal/checkout-api/error-budget-burn
```

Why these numbers: burn rate 14.4 for 1 h consumes 2% of a 30-day budget; 6 for 6 h consumes
5%; 1 for 3 d consumes 10%. These three rows are Table 5-8 of the Google SRE Workbook
("Alerting on SLOs"); the 3x over 1 d (24h)/2 h ticket condition comes from the workbook's
example rules, not the table. The short window (1/12 of the long one) stops the
alert soon after recovery. For low-traffic services, add a minimum request-rate condition or
use longer windows, because a handful of errors creates huge ratios.

Latency SLO: identical rules with `slo:latency_bad:ratio_rate*` and the latency budget.

### Error budget remaining (for dashboards)

Remaining budget = `1 - (bad_30d / valid_30d) / (1 - target)`. Compute it from `increase()` of
the raw counters over the window rather than averaging short-window ratios, which overweights
quiet periods:

```promql
1 - (
  sum(increase(http_server_request_duration_seconds_count{job="checkout-api",http_response_status_code=~"5.."}[30d]))
  /
  sum(increase(http_server_request_duration_seconds_count{job="checkout-api"}[30d]))
) / 0.001
```

A 30-day `increase()` over raw series is expensive; for large services record a 1h bad/valid
count and sum those over 30d instead.

## Generators

Writing these rules by hand is error-prone. Prefer an SLO generator that emits recording and
alerting rules from a short spec: Sloth or Pyrra (Prometheus), the OpenSLO spec for a
vendor-neutral definition, or the backend's native SLO object. Keep the spec in the service
repo and review it like code.

## Testing rules

```bash
promtool check rules slo-checkout-api.yaml
promtool test rules slo-checkout-api.test.yaml   # feed synthetic series, assert alerts fire
```

Test at least: a fast-burn scenario pages, a short blip does not, recovery resolves the alert.

## Alert template checklist

- Name says the symptom and the service (`CheckoutApiErrorBudgetFastBurn`, not `HighErrors`).
- `severity`: `page` (wake someone, user impact now) or `ticket` (business hours).
- `team`/owner label drives routing; routing changes in production need explicit confirmation.
- `summary` with current value; `description` with user impact.
- `runbook_url` and `dashboard_url`.
- Grouping/inhibition: a whole-region outage alert inhibits per-service alerts in that region.

### Runbook skeleton

```markdown
# <Alert name>
Impact: who is affected and how.
Check first: dashboard link, top queries (by route/region/version).
Likely causes: recent deploy, dependency X, saturation of Y.
Mitigate: rollback command/owner, feature flag, shed load. Who can approve.
Escalate: team channel / secondary on-call.
```

## Dashboard layout (service overview)

| Row | Panels |
| :--- | :--- |
| 1. SLO | SLI vs target (30d), budget remaining, current burn rate |
| 2. RED | Request rate, error ratio, p50/p95/p99 latency per route (histograms + exemplars) |
| 3. Saturation | CPU throttling, memory vs limit, GC pauses, DB/HTTP pool waits, queue lag |
| 4. Dependencies | Outbound rate/errors/latency per downstream (client spans or spanmetrics) |
| 5. Changes | Deploy, config, and feature-flag annotations on every panel |

Variables: environment, region, version. Units on every axis. Drill-down boards (per route,
per dependency, runtime internals) live separately and are linked from the overview.
