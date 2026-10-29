---
type: llm
focus: last_message
weight: 2
---

PASS if the answer identifies connection-pool exhaustion as the likely mechanism, proposes concrete evidence to gather or a way to reproduce under load before changing code (e.g. pool metrics, load test, checking for sessions not being closed/returned), and only then suggests fixes (session lifecycle, pool sizing, timeouts).
FAIL if it jumps straight to 'increase pool_size' without investigating why connections are not returned, or ignores the log line.
