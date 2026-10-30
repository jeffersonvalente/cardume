---
name: project-bootstrap-assistant
description: "Plans the platform foundation of a new or inherited system, ending in a charter and 90-day backlog. Use when preparing the technical foundation for a kickoff (not the PRD)."
---

# Project Bootstrap Assistant

> A platform foundation is a set of decisions, most of them cheap to make early and expensive to
> change later. This skill makes those decisions explicit, records who made them and on what
> evidence, and turns them into work someone else can execute.

## What this skill is and is not

| In scope | Goes elsewhere |
| :--- | :--- |
| Deciding environments, tenancy, identity, resource hierarchy, network, security baseline, delivery path, observability, operating model | — |
| Writing the **platform charter** and the **first-90-days backlog** | — |
| Recording what an inherited estate already has before deciding to keep or change it | Deep estate health review → `cloud-platform-assessment` |
| — | Product goals, users, features, acceptance criteria → `product-manager` (PRD) |
| — | Writing Terraform, pipelines, Helm charts, Dockerfiles → `devops-engineer` |
| — | Workload-level design trade-offs → `cloud-architecture-best-practices` |
| — | Budgets and cost forecasts beyond a first estimate → `finops-budgeting` |

Do not write infrastructure code here, even a "quick sketch". Code written before the decisions
are settled anchors the team on whatever the sketch assumed. Hand the backlog to `devops-engineer`.

If the product itself is still undefined (no idea who the users are or what the first release
does), say so and route to `product-manager` first. The platform can only be sized against a
product shape: expected load, data sensitivity, regions, and release cadence.

## The core artifact: the decision log

Everything in this skill hangs off one document, `docs/platform/decision-log.md`. Each entry is a
decision about one topic. Topics come from the landing-zone design areas that Azure CAF and
Google Cloud both publish, regrouped in the order decisions constrain each other
(`references/decision-topics.md` has the questions, defaults and per-cloud mapping for each).

| Area code | Design area | Typical first decisions |
| :--- | :--- | :--- |
| `TEN` | Tenancy and billing | Which organization/tenant, who pays, billing account structure |
| `IAM` | Identity and access | Identity provider, human access path, workload identity, break-glass |
| `HIE` | Resource hierarchy and environments | Account/project/subscription layout, environment count, naming, labels |
| `NET` | Network | Topology, IP plan, ingress/egress, private access, hybrid links |
| `SEC` | Security baseline | Org policies/SCPs, encryption, secrets, logging of admin activity, CIS baseline |
| `DLV` | Delivery path | Repos, IaC tool and state, CI/CD, artifact registry, promotion between environments |
| `RUN` | Workload runtime | Compute model (Kubernetes, serverless, VMs), data stores, regions |
| `OBS` | Observability and management | Telemetry stack, SLOs for the first journeys, alert routing |
| `RES` | Resilience and data protection | Backups, RPO/RTO per data store, DR posture |
| `GOV` | Governance and cost | Budgets, tagging policy, policy-as-code, compliance scope |
| `OPS` | Operating model | Who owns the platform, on-call, change process, support hand-off |

You do not have to fill every area. A three-person team shipping one service needs real answers in
`IAM`, `HIE`, `DLV`, `RUN` and `SEC`, and short defaults elsewhere. Scale the depth to the team
size, the data sensitivity, and the blast radius of a mistake, and say which areas you kept thin.

### Entry format

```markdown
### NET-02 — Shared VPC owned by a host project, one per environment
- Question: How do workloads in different projects share a network?
- Options: (a) Shared VPC per env, (b) VPC per project + peering, (c) single VPC for all envs
- Decision: (a) — or OPEN until <date>
- Basis: stated (platform lead, kickoff call) | observed (`gcloud compute shared-vpc list-associated-resources`) | assumed
- Reversibility: one-way | costly | cheap
- Owner: <role or name>          Decide by: <date or milestone>
- Consequences: needs HIE-01 host projects; backlog B-11, B-12
```

Three fields carry most of the value:

- **Basis.** `observed` means you saw it in config, console output or a command result;
  `stated` means someone told you; `assumed` means nobody has confirmed it. Assumptions are fine
  as long as they are labelled — they become questions in the charter instead of silent risks.
- **Reversibility.** Spend discussion time on one-way doors (IP ranges that will be peered,
  organization/tenant choice, identity provider, primary region for regulated data) and decide
  cheap ones quickly with a sensible default. That is where kickoff time pays back.
- **Consequences.** Every accepted decision should point at backlog items; a decision with no
  work attached is either already done or not really decided.

## How to work

Work topics roughly in the table's order, because later areas depend on earlier ones: you cannot
draw a network without knowing how many environments exist, and you cannot design CI/CD
permissions without the identity model. Within that order, follow the conversation — users
rarely present information in sequence.

**Gather the shape of the product, not its features.** Ask for (or read from a PRD in the
repo) expected users and regions, data classification (personal data, payments, health),
availability expectations, team size and skills, release cadence, compliance obligations, hard
deadlines, and the cloud(s) already contracted. These are the inputs every decision is sized
against. Ask a handful of questions at a time, grouped by area; a 40-question form gets skimmed.

**For an inherited system, observe before deciding.** Record what exists as `observed`
entries before proposing changes, using read-only commands such as:

```bash
gcloud organizations list; gcloud resource-manager folders list --organization=<ORG_ID>
gcloud projects list --format="table(projectId,parent.id,labels)"
aws organizations list-accounts; aws organizations list-organizational-units-for-parent --parent-id <ROOT_ID>
az account management-group list; az account list -o table
terraform -chdir=<dir> state list   # read-only; never plan/apply against someone else's state without asking
```

Each inherited topic ends in one of: keep as is, change (with a reason and a backlog item), or
retire. Changing something that works needs a better reason than "it is not how I would do it".

**Draft entries, then challenge them.** For each area, propose a default from
`references/decision-topics.md`, adapted to the inputs, and check it against the constraints you
already logged. Show the user the one-way-door entries explicitly and ask them to confirm; fill
the cheap ones with defaults and mark them `assumed` so they can be revisited.

**Write the charter and backlog, then hand off.** Templates and a worked backlog seed are in
`references/charter-and-backlog.md`. The charter is one page a new engineer reads on day one; the
backlog is what `devops-engineer` and the other owners execute. When handing off, list items by
owner, flag every OPEN decision with its deadline, and say which items each decision blocks.

These activities overlap and loop; the decision log is the state, not a stage you pass through.

## Defaults worth starting from

These are starting points that hold for most small-to-medium teams. Depart from them when the
inputs give a reason, and record the reason.

- **Environments:** separate accounts/projects/subscriptions per environment (at least non-prod
  and prod), not namespaces in one account. Isolation at the billing and IAM boundary is the
  cheapest blast-radius control available.
- **Identity:** humans sign in through the corporate IdP with SSO and MFA; no long-lived user
  keys. Workloads and pipelines use federated identity (OIDC from the CI provider, workload
  identity on Kubernetes) instead of exported keys. Two break-glass accounts, monitored.
- **Infrastructure as code from the first resource.** State remote, encrypted, versioned, with
  locking, one state per environment and stack. Console-created resources in prod are drift.
- **One delivery path:** build once, promote the same artifact through environments; production
  deploys need an approval and are reproducible from the repo.
- **Security baseline:** start from the CIS Foundations Benchmark for the chosen cloud,
  organization-level policies that deny public storage and external IPs by default, audit logs
  centralized in a separate account/project with restricted access.
- **Observability:** an OpenTelemetry-based pipeline and one SLO for the first user journey
  before launch, owned by `observability-engineer`.
- **Cost:** labels/tags for `env`, `team`, `service`, `cost-center` enforced from day one,
  billing export enabled, and a budget with alerts per environment. Retro-tagging later is slow.
- **IP plan:** reserve non-overlapping ranges for every environment and future region now, even
  if only one exists. Re-addressing a peered network is one of the most painful changes there is.

## Outputs

Write to the repo, not only to the chat, so the decisions survive the conversation:

| File | Content |
| :--- | :--- |
| `docs/platform/decision-log.md` | All entries, grouped by area code |
| `docs/platform/charter.md` | One-page platform charter |
| `docs/platform/backlog-90d.md` | First-90-days backlog with owners and dependencies |

If the user only wants a conversational answer, give the charter summary and the top of the
backlog inline and offer to write the files.

## Quality bar before handing over

- Every one-way-door decision is either accepted by a named owner or OPEN with a date.
- Every `assumed` entry appears as a question in the charter's open-decisions list.
- Every backlog item has an owner, a "done when" that someone could verify, and its dependencies.
- The first milestone is a **walking skeleton**: one trivial service deployed to non-prod through
  the real pipeline, with telemetry and the real identity model. It flushes out integration
  problems while they are cheap.
- Nothing in the backlog asks this skill to write code; implementation items name
  `devops-engineer` (or `security-auditor`, `observability-engineer`, `finops-architect`) as owner.
- Product scope questions found along the way are routed to `product-manager`, not decided here.

## Sources

- Microsoft Cloud Adoption Framework — Azure landing zone design areas:
  learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-areas
- Google Cloud — Landing zone design in Google Cloud: cloud.google.com/architecture/landing-zones
  and the enterprise foundations blueprint
- AWS — Organizing your AWS environment using multiple accounts; AWS Control Tower
- AWS / Google Cloud / Azure Well-Architected and Architecture Frameworks
- CIS Foundations Benchmarks (AWS, GCP, Azure); NIST CSF 2.0
- Michael Nygard, "Documenting Architecture Decisions" (ADR format)
