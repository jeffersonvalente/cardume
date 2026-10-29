---
type: llm
focus: last_message
weight: 2
---

PASS if it (1) starts with variance analysis by service/project/label using billing export to BigQuery to find the actual drivers before setting numbers; (2) proposes a concrete next-quarter budget with a forecast method (baseline + expected growth + optimization savings), not just one number; (3) sets guardrails: GCP budgets with alert thresholds (e.g. 50/90/100% actual and forecasted) per project, Pub/Sub-driven notifications, labeling/showback by team, BigQuery custom quotas or slot reservations/editions; (4) lists service-specific levers: GKE rightsizing/autoscaling/committed-use or spot node pools, BigQuery partitioning/clustering and on-demand vs. capacity pricing, Storage lifecycle/classes, egress review.
FAIL if it only gives a generic list of cost-saving tips without a budget structure, or no alerting/guardrail mechanism.
