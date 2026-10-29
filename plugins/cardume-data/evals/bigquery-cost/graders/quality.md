---
type: llm
focus: last_message
weight: 2
---

PASS if it replaces SELECT * with the needed columns, rewrites the partition filter so pruning is guaranteed (e.g. a TIMESTAMP range on event_ts) or explains how to confirm pruning with a dry run / bytes estimate, and suggests clustering or an aggregated/incremental table where relevant. FAIL if it misses the SELECT * problem.
