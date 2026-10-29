---
name: gcp-composer-failure-investigation
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Since last night our Composer DAG `orders_to_bq` fails on the `load_orders` task with a generic "Task exited with return code 1". Yesterday a teammate also changed the service account permissions on the staging bucket `gs://acme-staging-orders`. Using Cloud Logging / Monitoring and gcloud, how do I find the real cause? Give me the exact queries and commands, but don't change anything yet.
