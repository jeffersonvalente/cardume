---
name: finops-budgeting
description: "Builds and reviews cloud budgets, forecasts and guardrails with the FinOps Inform/Optimize/Operate model: FOCUS cost data, variance bridges, unit economics, forecast worksheet, commitments. Use when setting a cloud budget, explaining a bill spike, or adding cost guardrails."
---

# FinOps Budgeting

> A cloud budget is a forecast with owners attached. Get the data right, explain the last change
> before predicting the next one, and make every number traceable to a driver someone controls.

This skill follows the FinOps Foundation Framework's three phases. They are not a sequence you
finish; mature teams cycle through them continuously. Use them to check that an answer is
complete: a budget without **Inform** is a guess, without **Optimize** it bakes in waste, and
without **Operate** nobody notices when it breaks.

| Phase | Question it answers | What you produce here |
| :--- | :--- | :--- |
| **Inform** | Where is the money going, who owns it, and why did it change? | Clean cost data, allocation, variance bridge, unit costs |
| **Optimize** | What could we pay less for, at what risk? | Ranked levers with savings estimates |
| **Operate** | How do we keep it on track? | Forecast worksheet, budgets and alerts, cadence, showback |

Workload design trade-offs (is this the right service at all?) belong to
`cloud-architecture-best-practices`. Implementing budgets, labels or policies in Terraform belongs
to `devops-engineer`; describe the configuration, let it write the code.

---

## Inform

### Get the data before the opinion

Never set a number from the invoice total alone. Start from line-item billing data:

| Cloud | Source | Notes |
| :--- | :--- | :--- |
| GCP | Cloud Billing export to BigQuery — **detailed usage cost** (resource-level) plus **pricing** export | Not retroactive: enable it now if it is off. Net cost = `cost` + sum of `credits.amount`. GKE cost allocation adds namespace/label breakdown |
| AWS | Data Exports — CUR 2.0 or the FOCUS export, to S3, queried with Athena | Use amortized cost for commitments; split by linked account and cost-allocation tags (activate them first) |
| Azure | Cost Management exports (FOCUS format available) to a storage account | Scope at billing account or management group; amortized view for reservations |

Prefer the **FOCUS** schema (FinOps Open Cost and Usage Specification) when the provider offers it
or when more than one cloud is involved, so the same queries work everywhere. The columns that
matter most for budgeting: `BilledCost` (what the invoice says), `EffectiveCost` (amortized, after
discounts — use it for trends and unit costs), `ListCost` (for savings math), `ChargeCategory`
(usage, purchase, tax, credit, adjustment), `ServiceName`/`ServiceCategory`, `SubAccountId`
(project/account/subscription), `ResourceId`, `Tags`, `PricingCategory` (on-demand, commitment,
dynamic), `CommitmentDiscountId`, `ChargePeriodStart`.

Starter query on the GCP detailed export (adapt the dataset, months and label key):

```sql
SELECT
  invoice.month                                   AS month,
  service.description                             AS service,
  project.id                                      AS project,
  (SELECT value FROM UNNEST(labels) WHERE key = 'team') AS team,
  ROUND(SUM(cost) + SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)), 2) AS net_cost,
  SUM(usage.amount_in_pricing_units)              AS usage_units   -- meaningful per SKU only
FROM `billing_ds.gcp_billing_export_resource_v1_XXXXXX`
WHERE invoice.month BETWEEN '202607' AND '202609'
GROUP BY month, service, project, team
ORDER BY month, net_cost DESC;
```

Repeat grouped by `sku.description` for the top services; the cause usually lives at SKU level
(e.g. "BigQuery Analysis" vs. "Active Logical Storage", "Spot" vs. "Core" compute).

### Allocate

Report the share of spend with a complete owner (`team`, `service`, `env`, `cost-center` labels
or an account/project that maps to one). Below ~80% allocated, fixing allocation is the first
action, because no one manages cost they are not shown. Shared costs (networking hubs, shared
clusters, support plans) get an explicit rule: proportional to direct spend, proportional to a
usage measure (CPU-hours, requests), or a fixed split. Write the rule down; showback disputes are
almost always about undocumented shared-cost rules.

### Explain the change: the variance bridge

For each service (and each project/team inside the top services), split the change between two
periods into:

| Bucket | How to compute | What it means |
| :--- | :--- | :--- |
| **Volume** | (usage now − usage before) × old unit rate | More traffic, data or environments |
| **Rate** | (unit rate now − unit rate before) × usage now | Price changes, lost or new discounts, commitment expiry |
| **New / removed** | Cost of SKUs or resources absent in one period | New services, new projects, decommissions |
| **One-off** | Credits ending, refunds, purchases, back-charges | Not run-rate; exclude from the baseline |

The bridge tells you which part of the increase is growth the business wanted, which part is
waste, and which part is accounting noise. Present it as a table from the old total to the new
total before proposing any budget.

### Unit economics

Pick one or two unit metrics the business already tracks: cost per active customer, per 1,000
API requests, per order, per TB processed. Plot unit cost alongside total cost. Total cost rising
while unit cost is flat or falling is healthy growth; unit cost rising is an efficiency problem.
Budget growth should be expressed as "expected units × target unit cost", which is the language
finance and product can both argue with.

---

## Optimize

Separate the two kinds of lever, because they have different owners and risks:

- **Usage levers** (use less): rightsize, schedule, delete idle, change storage class, fix
  architecture. Owned by engineering; savings persist; need testing.
- **Rate levers** (pay less per unit): commitments, Spot/preemptible, edition/tier choice,
  negotiated discounts. Owned by FinOps/finance; savings depend on usage staying put.

Do usage levers on the stable part of the estate before buying commitments, or you commit to
waste. For each lever, record: estimated monthly saving and how it was computed, confidence
(high/medium/low), effort, risk to reliability, owner, and reversibility. Rank by saving ×
confidence ÷ effort.

### GCP levers worth checking first

| Service | Lever | Evidence to look at |
| :--- | :--- | :--- |
| GKE | Rightsize requests from VPA recommendations or observed usage; HPA on real load; cluster autoscaler with the `optimize-utilization` profile; node auto-provisioning | Requested vs. used CPU/memory per namespace (GKE cost allocation, Cloud Monitoring) |
| GKE | Spot node pools for stateless, fault-tolerant and batch workloads; Autopilot for spiky low-utilization clusters | Workload restart tolerance, PodDisruptionBudgets |
| GKE / Compute | Committed use discounts: resource-based (vCPU/memory, 1 or 3 years) or flexible spend-based CUDs, sized to the stable floor | Minimum hourly usage over the last 30–90 days, after rightsizing |
| BigQuery | Partitioning and clustering; `require_partition_filter`; `maximum_bytes_billed` on jobs; stop `SELECT *` on wide tables; materialized views for repeated aggregates | `INFORMATION_SCHEMA.JOBS`: `total_bytes_billed`, top users and queries |
| BigQuery | On-demand vs. capacity pricing (editions with autoscaling reservations, baseline slots, optional slot commitments) | Compare monthly on-demand spend to `total_slot_ms` converted to slot-hours at edition rates |
| BigQuery | Custom quotas — query usage per day per project and per user — to cap runaway on-demand scans | Largest daily scan totals per user/service account |
| Cloud Storage | Lifecycle rules to Nearline/Coldline/Archive or delete; Autoclass for unknown access patterns; expire noncurrent versions | Access frequency; mind minimum storage durations (30/90/365 days) and retrieval fees |
| Networking | Review internet egress, inter-region and inter-zone traffic, Cloud NAT processing; co-locate chatty services; CDN for static content | Billing SKUs for egress; VPC Flow Logs / Network Intelligence Center top talkers |

AWS equivalents: Compute Optimizer, Savings Plans (Compute vs. EC2 Instance), Reserved Instances
for RDS/ElastiCache, Spot, S3 Intelligent-Tiering and lifecycle, NAT Gateway and inter-AZ data
transfer review. Azure: Advisor, savings plans and reservations, Spot VMs, Azure Hybrid Benefit,
Blob access tiers and lifecycle management.

### Commitment sizing rule

Commit to the floor, not the average: take hourly eligible usage after planned rightsizing, find
a low percentile (for example the 10th) over the last 30–90 days, and cover that. Ladder purchases
(several smaller commitments over months) rather than one big one, so coverage tracks the estate.
Track **coverage** (share of eligible usage under commitment) and **utilization** (share of the
commitment actually used); low utilization means you bought too much. Commitments are financial
contracts: recommend them, never purchase them.

---

## Operate

### Forecast worksheet

Build the next-period budget from drivers, one worksheet per top-level owner (project, team or
business unit), then sum. Each line has a named source so the number can be challenged line by
line.

| Line | What goes in | Source |
| :--- | :--- | :--- |
| **A. Run-rate** | Last 30 days of effective cost, excluding one-offs, × days in the period ÷ 30 | Billing export (bridge "one-off" bucket removed) |
| **B. Growth** | A × expected change in the unit metric (users, requests, data volume) | Product/business forecast; recent unit-metric trend |
| **C. Known events** | Launches, migrations, new environments, decommissions, each with a date and a monthly cost | Roadmap, engineering leads |
| **D. Planned savings** | − Σ (lever saving × confidence factor × months active in the period) | Optimize list; use 1.0 / 0.6 / 0.3 for high / medium / low confidence |
| **E. Rate changes** | Commitment expiries, announced price changes, currency effects | Commitment inventory, provider notices |
| **F. Forecast** | A + B + C + D + E | — |
| **G. Contingency** | F × buffer: past forecast error if known, otherwise 5–10% | Previous budgets vs. actuals |
| **Budget** | F + G, phased by month (growth and savings ramp, they do not start on day 1) | — |

Present it as a range, not a point: a **low** case (savings land fully, growth at the bottom of the
range) and a **high** case (savings slip, growth at the top). Finance gets one budget number plus
the range and the assumptions that move it. Record actuals against each line every month; the
lines that keep missing tell you which assumption to fix.

### Guardrails

Budgets and alerts are the mechanism that prevents the next surprise. Set them per owner, not
only on the billing account, so the alert reaches someone who can act.

**GCP**
- Cloud Billing budgets scoped per project (or per label/service where useful), with thresholds on
  **actual** spend at 50%, 90% and 100% and on **forecasted** spend at 100%.
- Programmatic notifications to a **Pub/Sub** topic, consumed by a function or chat integration
  that posts to the owning team's channel and opens a ticket. Email to billing admins alone gets
  ignored. Automatic billing disablement exists but stops every resource in the project; reserve it
  for sandboxes.
- BigQuery custom quotas per project and per user, and `maximum_bytes_billed` defaults in shared
  tooling; reservations with a max-slots cap when on capacity pricing.
- Organization policy and IaC review that require the cost labels; a weekly report of unlabelled
  spend.

**AWS:** AWS Budgets per account/tag with actual and forecasted thresholds, SNS/Chatbot
notifications, budget actions (apply an SCP or IAM policy) for sandboxes; Cost Anomaly Detection
monitors per service and per cost-allocation tag; tag policies.
**Azure:** budgets per subscription/resource group with action groups; anomaly alerts in Cost
Management; Azure Policy requiring tags.

Anomaly detection complements budgets: budgets catch slow drift against a plan, anomaly
detection catches a sudden spike days before a monthly threshold would.

### Showback, chargeback and cadence

Start with **showback** (each team sees its allocated cost and unit cost) and move to
**chargeback** only once allocation is above ~90% and shared-cost rules are agreed; charging teams
for numbers they cannot explain destroys trust in the data. Keep a light rhythm: anomalies and
alert triage weekly, budget vs. actual by owner monthly, forecast refresh and commitment review
quarterly. Each review ends with named owners for the levers that moved.

---

## Shape of a good answer

When asked for a budget or why a bill grew, respond in this order: what data you used (or need),
the variance bridge with the main drivers, the forecast worksheet with low/expected/high, the
guardrails to configure, and the ranked levers with owners. State assumptions where data is
missing and say which query would replace each one. Do not quote provider prices from memory as
facts; mark them as approximate and point to the pricing page or the pricing export.

## Sources

- FinOps Foundation — FinOps Framework (phases, domains, capabilities, maturity): finops.org/framework
- FOCUS specification: focus.finops.org
- Google Cloud: Cloud Billing export to BigQuery; Create, edit, or delete budgets and budget
  alerts; Programmatic budget notifications (Pub/Sub); Committed use discounts; BigQuery pricing,
  editions and reservations; BigQuery custom quotas; Best practices for running cost-optimized
  Kubernetes applications on GKE; GKE cost allocation; Cloud Storage lifecycle and Autoclass
- AWS: Well-Architected Cost Optimization pillar; AWS Budgets; Cost Anomaly Detection; Savings
  Plans; Data Exports (CUR 2.0, FOCUS)
- Azure: Well-Architected cost optimization; Cost Management budgets, exports and anomaly alerts
