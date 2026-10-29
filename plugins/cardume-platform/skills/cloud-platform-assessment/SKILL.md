---
name: cloud-platform-assessment
description: "Runs a read-only, risk-based review of a whole cloud estate (AWS, GCP, Azure, Kubernetes) along the provider's Well-Architected pillars and returns evidence-backed risks plus a 30/60/90-day plan. Use when asked for a platform health check, maturity or hardening review, or a prioritized roadmap."
---

# Cloud Platform Assessment

> Look at the estate the way an incident would find it. Ask the provider's own Well-Architected
> questions, check the answers against real configuration, and hand back the few risks that
> matter most with a plan someone can start on Monday.

This skill is for a **whole-estate or platform review**: an organization, a set of accounts or
projects, a landing zone, or the shared platform that many workloads sit on.

Route elsewhere when the scope is narrower:

- A data and AI inventory of a single GCP project (BigQuery, Composer, Vertex AI, Dataflow):
  `cardume-data:gcp-project-auditor-data-and-ia`.
- Deep or live Kubernetes posture, cluster inventory, troubleshooting or RCA:
  `cardume-platform:kubernetes-operations`. This skill only asks how clusters fit the platform.
- Choosing or reviewing the design of one workload, with cost trade-offs:
  `cardume-platform:cloud-architecture-best-practices`.
- Budgets, forecasts and commitment planning: `cardume-platform:finops-budgeting`.

## Reference files (load only what the task needs)

| File | Load when |
| :--- | :--- |
| `references/pillar-risk-questions.md` | Choosing which questions to ask per pillar, and mapping them to AWS, Google Cloud and Azure framework names |
| `references/read-only-evidence.md` | Collecting evidence with CLI or console on AWS, GCP, Azure or Kubernetes without changing anything |
| `references/writeup-format.md` | Writing the final report: summary, risk register entries, 30/60/90 plan, worked example |

---

## Ground rules

- **Read-only, always.** Use `describe`, `list`, `get` and reporting APIs only. Never create,
  modify, tag, restart or delete anything, and never run "fix" commands even when the fix is
  obvious; write the fix into the plan instead. A review that changes the estate can no longer
  explain what it found.
- **Least-privilege credentials.** Ask for a viewer or audit role (AWS `SecurityAudit` plus
  `ViewOnlyAccess`, GCP `roles/viewer` plus `roles/iam.securityReviewer`, Azure `Reader` plus
  `Security Reader`). If the session has broader rights, say so in the report and still behave
  read-only.
- **Never surface secrets.** Do not print secret values, Kubernetes `Secret` data, access keys
  or connection strings. Record that a secret exists and where, not what it is.
- **Evidence over assumption.** Every risk states how it was checked. When something could not
  be observed, say that plainly and phrase the item as a question for the owner instead of a
  finding.
- **Name the provider from what you see.** Identify AWS, GCP or Azure from configuration,
  account IDs, IaC providers, or what the user tells you; ask when it is genuinely unclear.

## How the review runs

### 1. Frame the scope

Agree on these before collecting anything, because they decide what "risk" means:

- Which organization, accounts, projects or subscriptions, and which environments are in scope.
- Which workloads are business-critical, and their stated or implied RTO/RPO.
- Regulatory or contractual constraints (PCI DSS, HIPAA, LGPD/GDPR, SOC 2).
- What access is available: live read-only credentials, IaC repositories, exported reports,
  or only interviews and documents.
- Known pain: recent incidents, cost spikes, audit findings. Start there; it is where the
  owners already suspect risk.

When working as a subagent, list unanswered scope questions under **Open questions**, state the
assumption you used, and continue with what is observable.

### 2. Pick the lens from the provider's own framework

Use the framework the team already recognizes so the findings land in their vocabulary:

| Provider | Framework | Pillars |
| :--- | :--- | :--- |
| AWS | AWS Well-Architected Framework | Operational excellence, Security, Reliability, Performance efficiency, Cost optimization, Sustainability |
| Google Cloud | Google Cloud Well-Architected Framework | Operational excellence; Security, privacy and compliance; Reliability; Cost optimization; Performance optimization; Sustainability |
| Azure | Azure Well-Architected Framework (plus Cloud Adoption Framework for landing zones and governance) | Reliability, Security, Cost optimization, Operational excellence, Performance efficiency |
| Multi-cloud or hybrid | Use the pillars of the provider hosting the critical workloads; note gaps between estates | |

Kubernetes is not a separate pillar. Treat each cluster as part of the estate and ask the
pillar questions of it (node and control-plane versions, workload resilience, access, cost
allocation), using the Kubernetes production guidance on kubernetes.io.

For governance and identity at estate level, the landing-zone guidance (AWS Control Tower and
multi-account strategy, Google Cloud resource hierarchy and organization policies, Azure CAF
landing zones) gives better questions than workload pillars do.

### 3. Ask risk questions, not checklist items

For each pillar, start from questions that expose failure modes, such as "If the primary region
or zone failed tonight, what would be lost and how long would recovery take?" rather than "is
Multi-AZ enabled". `references/pillar-risk-questions.md` lists the questions worth asking and
the configuration that answers each one.

Spend effort where blast radius is largest: identity and the organization root first, then
shared networking and logging, then the critical workloads, then everything else. Sample the
long tail instead of enumerating it.

### 4. Check the answers against evidence

Collect evidence with read-only commands (`references/read-only-evidence.md`), IaC in the repo,
provider assessment tools (AWS Well-Architected Tool and Trusted Advisor, Security Hub CSPM
with the CIS Foundations Benchmark, Google Security Command Center and Recommender, Azure
Advisor, Microsoft Defender for Cloud and the Azure Well-Architected Review), and the team's
own runbooks.

Write down **how it was checked** in plain words for every item: the command and filter, the
file and line, the console page, or "stated by the platform lead, not verified". Tool findings
are leads, not conclusions: confirm that a flagged item is real and in scope before it becomes
a risk.

Compare declared state with observed state. A Terraform module that enables backups proves
nothing if `describe` shows retention at zero on the instance that actually runs production.

### 5. Express each finding as a risk

Write every finding as a risk statement with cause, event and consequence:

> Because **<condition observed>**, **<event>** can happen, which would **<business
> consequence>**.

Then rate it on two plain axes and derive the priority:

| | **Impact: severe** (data loss, breach, prolonged outage of a critical service, regulatory exposure) | **Impact: material** (degraded service, recoverable incident, notable waste) | **Impact: minor** (inconvenience, small waste) |
| :--- | :--- | :--- | :--- |
| **Likely** (already happening, or exposed with no compensating control) | Act now | Act now | Next quarter |
| **Plausible** (needs one more failure or mistake) | Act now | Next quarter | Backlog |
| **Remote** (needs several unlikely events) | Next quarter | Backlog | Backlog |

Explain the rating in one sentence. Note compensating controls that lower likelihood (for
example SCPs or organization policies that block public buckets) so owners see why something
is not urgent.

Combine symptoms that share a root cause into one risk. Ten public buckets created by the same
pipeline are one risk about the pipeline and its guardrails, not ten findings.

### 6. Turn risks into a plan

Order the work by priority, then by dependency, then by effort:

- **First 30 days:** contain the "act now" risks with the smallest safe change (for example
  remove public access from an exposed bucket, revoke or lock down a powerful credential,
  route a missing budget or security alert to someone who answers it, prove that the most
  important backup really restores).
- **Days 31–60:** fix the causes behind them (guardrails as policy, backup plans as code,
  multi-zone for critical tiers, alert routing with owners).
- **Days 61–90:** raise the baseline (landing-zone alignment, tagging and showback, DR
  exercise against stated RTO/RPO, version-upgrade cadence, cost commitments sized to the
  rightsized baseline).

Each plan item names an owner role, a measurable done-condition ("anonymous read of the export
bucket returns 403 and the organization policy is in place"), and the risks it retires.

### 7. Write the report

Follow `references/writeup-format.md`: executive summary, top risks, 30/60/90-day plan,
then a risk register and the scope and limits of the review. Keep the summary to what an
engineering leader needs to decide; detail belongs in the register.

## What good looks like

- Ten or fewer top risks, each traceable to evidence a reviewer could re-run.
- Strengths noted briefly, so the plan does not undo things that work.
- Unknowns listed as questions with an owner, not padded into findings.
- Cost items carry an order-of-magnitude figure from billing data when it is available
  (for example from the Cost and Usage Report, Cloud Billing export to BigQuery, or Azure Cost
  Management exports, ideally normalized with the FinOps FOCUS specification).
- The plan fits the team's capacity; a 90-day plan with forty items is a wish list.

## Pitfalls

- **Scanner dumps.** Pasting hundreds of CSPM findings hides the five that matter. Triage,
  group by cause, and rate.
- **Config without context.** Single-zone is a risk for the checkout database and a sensible
  saving for a nightly dev batch. Rate against the workload's criticality.
- **Ignoring recovery.** Backups that were never restored are a hope, not a control. Ask for
  the last restore test (NIST SP 800-34 treats testing as part of contingency planning).
- **Treating the cluster as a black box.** A cluster on an unsupported version or with
  `cluster-admin` bound to a broad group is an estate risk; hand the deep dive to
  `kubernetes-operations`.
- **Recommendations without an owner.** Every plan item needs a role that will carry it.

## Public sources

- AWS Well-Architected Framework and Tool; AWS Security Reference Architecture; AWS multi-account strategy whitepaper.
- Google Cloud Well-Architected Framework; resource hierarchy and organization policy docs.
- Azure Well-Architected Framework and Review; Microsoft Cloud Adoption Framework.
- CIS Foundations Benchmarks for AWS, Google Cloud and Azure; CIS Kubernetes Benchmark.
- NIST Cybersecurity Framework 2.0; NIST SP 800-34 Rev. 1 (contingency planning).
- Kubernetes documentation: production environment, configuration good practices, Pod Security Standards.
- FinOps Foundation Framework and FOCUS specification for cost evidence.
