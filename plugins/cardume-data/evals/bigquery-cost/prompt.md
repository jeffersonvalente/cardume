---
name: bigquery-cost
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

This scheduled BigQuery query scans about 4 TB every day and is getting expensive. The table `analytics.events` is partitioned by `event_ts` (TIMESTAMP).

```sql
SELECT * FROM analytics.events WHERE DATE(event_ts) = CURRENT_DATE() - 1 AND user_id IS NOT NULL
```

How do I cut the cost?
