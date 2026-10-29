# Platform charter and first-90-days backlog

## Platform charter (`docs/platform/charter.md`)

Keep it to roughly one page. It summarizes the decision log; it does not replace it.

```markdown
# Platform charter — <system name>
Last updated: <date> · Decision log: docs/platform/decision-log.md

## Why this platform exists
<2–3 sentences: what the product needs from the platform — users/regions, data sensitivity,
availability expectation, release cadence. Link the PRD if there is one.>

## Out of scope
- Product requirements and prioritization (owned by product management)
- <anything deliberately deferred, e.g. multi-region, data platform>

## Guardrails (non-negotiable)
- <e.g. no long-lived cloud credentials for humans or pipelines>
- <e.g. every resource created through IaC; prod changes only through the pipeline>
- <e.g. personal data stays in <region>>

## Shape at a glance
| Item | Choice | Entry |
| --- | --- | --- |
| Cloud / organization | | TEN-01 |
| Environments | | HIE-01 |
| Network | | NET-01 |
| Runtime | | RUN-01 |
| IaC + CI/CD | | DLV-01 |
| Telemetry | | OBS-01 |

## Open decisions
| Entry | Question | Owner | Decide by | Blocks |
| --- | --- | --- | --- | --- |

## Ownership
| Area | Accountable | Executes |
| --- | --- | --- |
| Foundations (TEN/IAM/HIE/NET) | | devops-engineer |
| Security baseline | | security-auditor review |
| Observability | | observability-engineer |
| Cost | | finops-architect |

## How we will know it works
- Lead time from merge to prod; deployment frequency; change failure rate; time to restore (DORA)
- Time for a new engineer to ship a change to non-prod
- Share of spend with complete cost labels; budget variance
- SLO attainment for the first journey
```

## First-90-days backlog (`docs/platform/backlog-90d.md`)

Organize by milestone, where each milestone is an observable outcome, not a calendar phase. Dates
are targets; the order comes from dependencies.

| Milestone | Observable outcome | Typical target |
| :--- | :--- | :--- |
| **Skeleton live** | A trivial service is built, deployed to non-prod by the pipeline, authenticated with the real identity model, and emits traces | ~day 30 |
| **Production gate** | Prod environment exists with the security baseline, backups tested, an SLO and on-call defined; a go-live checklist passes | ~day 60 |
| **Operating** | First real workloads in prod; budget alerts, cost allocation and runbooks in use; open decisions closed or re-dated | ~day 90 |

Item format:

| ID | Item | Area | Owner | Depends on | Done when |
| :--- | :--- | :--- | :--- | :--- | :--- |

### Worked seed (GCP example, small team, one product)

Adapt rather than copy; delete rows that the decision log made irrelevant.

| ID | Item | Area | Owner | Depends on | Done when |
| :--- | :--- | :--- | :--- | :--- | :--- |
| B-01 | Folder structure `prod`/`non-prod`/`shared` and project factory | HIE | devops-engineer | TEN-01, HIE-01 | Projects created only through IaC; labels enforced |
| B-02 | Billing export (detailed) to BigQuery in `shared` | GOV | devops-engineer | TEN-01 | Yesterday's costs queryable |
| B-03 | Groups and role bindings from the IdP; break-glass accounts | IAM | devops-engineer | IAM-01 | No user holds roles directly; break-glass login alerts |
| B-04 | Remote state bucket per env, versioned, locked down | DLV | devops-engineer | HIE-01 | `terraform init` works from CI only |
| B-05 | CI with OIDC federation to the cloud; plan on PR, apply on merge | DLV | devops-engineer | B-03, B-04 | No service-account keys exist |
| B-06 | Shared VPC per env class, IP plan, Cloud NAT, private service access | NET | devops-engineer | NET-01, NET-02 | Connectivity test from a workload project passes |
| B-07 | Org policies baseline (no public buckets, no external IPs, no SA keys, region restriction) | SEC | devops-engineer | B-01 | Policy violations blocked in a test project |
| B-08 | Audit log sink to locked logging project | SEC | devops-engineer | B-01 | Admin activity from all projects visible there |
| B-09 | Walking-skeleton service through the pipeline to non-prod | RUN | devops-engineer | B-05, B-06 | URL responds; deploy reproducible from repo |
| B-10 | OTel Collector and backend; traces from B-09 | OBS | observability-engineer | B-09 | A request's trace is visible end to end |
| B-11 | Budgets per env with alert thresholds and notification channel | GOV | finops-architect | B-02 | Test alert reaches the owner |
| B-12 | Prod environment from the same modules | HIE | devops-engineer | B-07, B-08 | Prod plan shows only expected differences from non-prod |
| B-13 | Backup policy and restore test | RES | devops-engineer | RES-01 | Restore completed and timed |
| B-14 | First SLO and paging route with runbook | OBS/OPS | observability-engineer | B-10, OPS-02 | Synthetic burn triggers the right page |
| B-15 | Security baseline review before go-live | SEC | security-auditor | B-07, B-08, B-12 | Findings triaged; criticals fixed |
| B-16 | Hand-off checklist and ownership transfer | OPS | platform lead | all above | Admin roles held by the owning team only |

Mark B-09 as the critical path: if the walking skeleton slips, everything after it slips too.
