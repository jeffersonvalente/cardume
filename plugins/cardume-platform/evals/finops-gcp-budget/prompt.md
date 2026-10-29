---
name: finops-gcp-budget
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Our GCP bill went from $18k to $31k per month over the last quarter. Main services: GKE (~55% of spend), BigQuery on-demand (~25%), Cloud Storage (~10%), rest is networking. Finance wants a budget for next quarter and guardrails so we don't get surprised again. Where do I start and what should the budget look like?
