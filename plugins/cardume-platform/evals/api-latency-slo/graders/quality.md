---
type: llm
focus: last_message
weight: 2
---

PASS if it (1) defines user-facing SLIs as good/valid ratios for both availability (non-5xx) and latency (requests under a threshold, computed from histogram buckets, not averages) with a concrete target and window (e.g. 99.9% over 30 days) and the resulting error budget; (2) proposes multi-window multi-burn-rate alerting with concrete rules or expressions (e.g. 14.4x over 1h AND 5m paging, slower burns as tickets) and explains why that would have fired during the incident; (3) treats the CPU alert as a cause-based signal to demote or move to dashboards, and requires paging alerts to carry severity, owner, and a runbook link; (4) addresses the telemetry gaps: trace correlation in logs (trace_id/span_id via OpenTelemetry or the logger integration), exemplars or traces to link the p99 spike to the DB pool wait, and pool saturation as a dashboard/diagnostic signal; (5) does not suggest high-cardinality labels or logging secrets/PII.
FAIL if it only recommends lowering the CPU threshold or alerting on average latency, gives no burn-rate or SLO-based alert, or never addresses log/trace correlation.
