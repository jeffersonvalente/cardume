# Incident Investigation from Telemetry

Read-only queries and dashboards are free to run. Anything that changes the system (rollback,
restart, scaling, feature flag, config push, silencing an alert) is a mitigation decision that
goes to the user or the owning agent (`kubernetes-copilot` for live cluster actions,
`devops-engineer` for pipelines/infra).

## Workflow

### 1. Confirm impact (2-5 min)
- Which SLO is burning? Error ratio and latency percentiles vs. target, current burn rate.
- Who is affected: all users, one route, one region, one tenant tier, one client version?
- Start time: find the first bad minute, not the alert time (alerts lag by their window).

```promql
# p99 latency by route, to see where the spike is
histogram_quantile(0.99, sum by (le, http_route) (rate(http_server_request_duration_seconds_bucket{job="checkout-api"}[5m])))
# error ratio by version, to spot a bad release (needs service.version promoted via
# otlp.promote_resource_attributes; otherwise join target_info or use the info() function)
sum by (service_version) (rate(http_server_request_duration_seconds_count{job="checkout-api",http_response_status_code=~"5.."}[5m]))
/ sum by (service_version) (rate(http_server_request_duration_seconds_count{job="checkout-api"}[5m]))
```

### 2. Scope by dimension
Break the bad signal down by route, region/zone, version, pod/host, dependency, and request
size. The dimension where the bad part concentrates is the strongest lead. If everything is bad
equally, suspect a shared dependency or the edge.

### 3. Find the change
Line up the start time with: deploys and config changes (annotations), feature flags, traffic
shape (rate, payload size, a new client), autoscaling events, dependency status pages, and
certificate or credential rotations.

### 4. Follow exemplars into traces
From the latency panel, open exemplar traces at the spike. In the trace, find the span that owns
the time or the error: a slow DB query, a retry storm, a lock, a cold cache, a downstream
timeout. Compare with a healthy trace of the same route (TraceQL / APM comparison).

```text
{ resource.service.name = "checkout-api" && span.http.route = "/orders" && duration > 2s }
```

### 5. Read correlated logs
Query logs by the `trace_id` of the bad trace, then widen to the same error type across the
time window to count occurrences.

### 6. Check saturation (USE)
Connection-pool waits, thread pools, queue lag, CPU throttling, memory near limit, GC pauses,
DB locks and slow queries. Saturation often explains p99 spikes that p50 hides.

### 7. Mitigate, then explain
Propose the least risky mitigation with its blast radius and rollback (rollback the release,
disable a flag, shed or rate-limit traffic, scale a pool). Wait for the user's go-ahead. Then
verify recovery on the same SLO panel that showed the impact.

### 8. Close the loop
Every incident should leave the system more observable:
- Did an SLO burn-rate alert fire, and how early? If not, add or tune it.
- Was a signal missing (no span on the DB call, no `trace_id` in logs, no version label)?
- Was the runbook accurate? Update it.

## Common patterns

| Symptom | Likely cause | Confirm with |
| :--- | :--- | :--- |
| p99 up, p50 flat | Saturation, GC, lock contention, one slow dependency, noisy tenant | Pool wait metrics, exemplar traces, breakdown by tenant |
| Errors only on new version | Bad deploy | Error ratio by `service.version` |
| Errors in one zone | Infra/zone issue or bad node | Breakdown by zone/node |
| Latency up after traffic jump | Capacity, autoscaling lag | Request rate vs. replicas vs. CPU throttling |
| Timeouts cascade across services | Retry storm, missing deadlines | Trace fan-out, retry counts, client timeouts |
| Gaps in traces | Broken propagation (queue, proxy, thread pool) | Orphan spans, missing parent IDs |

## Timeline template

```markdown
## Incident: <title>   Severity: <SEV>   Status: <investigating|mitigated|resolved>
Impact: <journey, % of requests/users, region>, from <start UTC> to <end UTC>
Detection: <alert name> at <time> (first bad minute <time>)

| Time (UTC) | Event | Evidence (query/link) |
| --- | --- | --- |
| 14:02 | Deploy checkout-api 1.43.0 | deploy annotation |
| 14:05 | p99 /orders 300 ms -> 2.4 s | p99 by route panel |
| 14:11 | Fast-burn page fired | alert link |
| 14:20 | Exemplar traces show DB pool wait 2 s | trace links |
| 14:26 | Rollback approved and done | change record |

Root cause: <...>
Follow-ups: alert/SLO changes, missing signals, runbook updates, owners and dates.
```
