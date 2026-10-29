---
name: api-latency-slo
plugins: ["../..", "../../../cardume-core"]
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Yesterday our checkout API p99 latency jumped from ~250 ms to ~3 s for about 40 minutes and nobody got paged; customers told us first. Our only alert is "CPU > 80% for 10 min" and it never fired. From Prometheus: http_server_request_duration_seconds p50 stayed around 80 ms, request rate was flat at ~900 req/s, 5xx went from 0.1% to 2.5%, and the DB connection pool wait time metric spiked at the same time. Logs show lots of "timeout acquiring connection" errors but they don't have trace IDs. How do we set up SLOs and alerts that would have caught this, and what should we fix in our telemetry?
