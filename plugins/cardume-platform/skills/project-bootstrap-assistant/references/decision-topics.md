# Decision topics by design area

For each area: the questions that decide it, a default that fits most small-to-medium teams, the
per-cloud building blocks, and the traps that make the decision expensive later. Use the
questions to fill decision-log entries; do not paste the whole list at the user.

Reversibility hints: **(1W)** one-way door, **(C)** costly to change, **(ch)** cheap.

---

## TEN — Tenancy and billing

Questions
- Does the company already have an organization/tenant? Who administers it? **(1W)**
- Which billing account pays, and does finance need costs split by product, team or customer?
- Is this a client engagement where the client owns the tenant? Who holds the admin credentials at the end?

Default: build inside the existing organization under a dedicated folder/OU/management group;
enable billing export on day one.

| AWS | GCP | Azure |
| :--- | :--- | :--- |
| AWS Organizations, management account kept empty, Control Tower optional | Organization node tied to Cloud Identity / Workspace domain, Cloud Billing account | Microsoft Entra tenant, management groups, EA/MCA billing scopes |

Traps: creating a stand-alone account/project "for now" outside the organization and migrating it
later; a consultant's personal account as owner of anything.

## IAM — Identity and access

Questions
- Which IdP is authoritative for humans (Entra ID, Google Workspace, Okta)? **(1W)**
- How do engineers get production access — standing roles, just-in-time elevation, or none?
- How do CI pipelines and workloads authenticate to the cloud?
- Who holds break-glass access and how is its use detected?

Default: SSO from the corporate IdP, groups mapped to roles, no user access keys, read-only by
default in prod with time-bound elevation; OIDC federation from CI; workload identity for pods.

| AWS | GCP | Azure |
| :--- | :--- | :--- |
| IAM Identity Center, permission sets, IAM roles for CI via OIDC, IRSA / EKS Pod Identity | Cloud Identity groups, IAM at folder level, Workload Identity Federation, GKE Workload Identity | Entra ID groups, PIM, workload identity federation, AKS workload identity |

Traps: granting roles to individuals instead of groups; service-account keys in CI secrets; owner
role used as the everyday developer role.

## HIE — Resource hierarchy and environments

Questions
- How many environments, and what is each for (dev, staging, prod, sandbox, perf)? **(C)**
- One account/project per environment, or per environment × workload?
- Where do shared services live (CI runners, registries, DNS, logging, networking hosts)?
- Naming convention and mandatory labels/tags?

Default: folder/OU per environment class (`prod`, `non-prod`, `shared`), one account/project per
environment and workload, mandatory labels `env`, `team`, `service`, `cost-center`.

| AWS | GCP | Azure |
| :--- | :--- | :--- |
| OUs (Security, Infrastructure, Workloads/Prod, Workloads/NonProd, Sandbox) | Folders per env, projects per workload/env, project factory | Management groups (platform, landing zones/corp, online, sandbox), subscriptions per env |

Traps: environments as namespaces in one project (shared quotas, shared IAM, shared bill);
names that encode things that change (team names, vendor names).

## NET — Network

Questions
- Is there on-premises or another cloud to connect to? Bandwidth and latency needs? **(1W)**
- IP ranges already in use anywhere the new network might ever peer with? **(1W)**
- Public ingress pattern (global LB, CDN, WAF)? Do workloads need outbound internet?
- Private access to managed services required?

Default: hub-and-spoke (or Shared VPC on GCP) per environment class, documented non-overlapping
CIDR plan with room for more regions, private endpoints for managed services, egress through a
managed NAT, single ingress path with WAF for public endpoints.

| AWS | GCP | Azure |
| :--- | :--- | :--- |
| VPCs + Transit Gateway, PrivateLink, NAT Gateway, ALB/CloudFront + WAF | Shared VPC, Private Service Connect, Cloud NAT, global external LB + Cloud Armor | Hub VNet + spokes or Virtual WAN, Private Link, NAT Gateway, Front Door/App Gateway + WAF |

Traps: `10.0.0.0/16` everywhere; GKE/EKS pod ranges sized too small; cross-zone and cross-region
traffic left unpriced (it shows up later as egress cost).

## SEC — Security baseline

Questions
- Which regulations or frameworks apply (LGPD/GDPR, PCI DSS, HIPAA, SOC 2, ISO 27001)?
- Where must data reside? **(1W for regulated data)**
- Customer-managed encryption keys required, or provider-managed acceptable?
- Secrets management tool? Vulnerability scanning of images and dependencies?

Default: CIS Foundations Benchmark controls; org policies denying public buckets, external IPs on
VMs, service-account key creation, and non-approved regions; centralized audit logs in a locked
account/project; secrets in the cloud secret manager; image scanning in the registry.

| AWS | GCP | Azure |
| :--- | :--- | :--- |
| SCPs, CloudTrail org trail, Security Hub, GuardDuty, KMS, Secrets Manager | Organization Policy constraints, Cloud Audit Logs to a log sink, Security Command Center, Cloud KMS, Secret Manager | Azure Policy, Defender for Cloud, Activity Log to Log Analytics, Key Vault |

Traps: "we'll add security later"; turning on detective tools without anyone triaging findings.

## DLV — Delivery path

Questions
- Repo strategy (mono vs. multi), and where infrastructure code lives?
- IaC tool (Terraform/OpenTofu, Pulumi, Bicep, CDK) and state backend? **(C)**
- CI/CD platform? Promotion model between environments? Who approves prod?
- Artifact registry and image signing?

Default: Terraform/OpenTofu with remote state per environment and stack, plan on PR and apply from
the pipeline only; trunk-based development; build once and promote the same artifact; prod
approval gate; dependency and image scanning in CI.

Traps: one giant state for everything; applying from laptops; a different build per environment.

## RUN — Workload runtime

Questions
- What does the first release run: a few HTTP services, batch jobs, event consumers, ML?
- Does the team already operate Kubernetes well? If not, does the workload need it? **(C)**
- Primary data stores and their managed equivalents? Primary region? **(1W for data)**

Default: the least-operational option that fits — managed containers (Cloud Run, App Runner,
Azure Container Apps) or serverless for a small team; managed Kubernetes when there are many
services, specific scheduling needs, or an existing platform team. Managed databases over
self-hosted.

Traps: Kubernetes chosen for résumé reasons; multi-region active-active before there is a
second customer region.

## OBS — Observability and management

Questions
- Existing telemetry backend or vendor contract?
- What is the first user journey worth an SLO? Who is paged?
- Log retention requirements (legal vs. operational)?

Default: OpenTelemetry SDKs → Collector → chosen backend; one SLO per first journey; alerts on
symptoms; retention set per signal. Detailed design belongs to `observability-engineer`.

## RES — Resilience and data protection

Questions
- RPO/RTO per data store and per journey? What happens to the business if a region is lost?
- Backups isolated from the production account/project? Restore ever tested?

Default: automated backups with point-in-time recovery on managed databases, backups copied to a
separate account/project, a restore test before launch, single-region with zonal redundancy
unless RTO demands otherwise (NIST SP 800-34 for contingency planning structure).

## GOV — Governance and cost

Questions
- Budget envelope for the first year? Who receives budget alerts?
- Policy-as-code (OPA/Conftest, Sentinel, Azure Policy) on IaC changes?
- Tagging enforcement mechanism?

Default: budgets per environment with alerts at 50/90/100% of actual and 100% of forecast;
billing export to a queryable store; tag policy enforced in IaC review and by org policy where
supported. Ongoing budgeting goes to `finops-budgeting`.

## OPS — Operating model

Questions
- Who owns the platform after kickoff: a platform team, the product team, an external partner?
- On-call: who, which hours, which tool? Escalation path?
- Change process for prod: PR approval only, or a change board?
- What does hand-off look like if a consultancy built it?

Default: "you build it, you run it" for product services with a small platform owner group for
shared foundations; on-call defined before the first production user; runbooks for every paging
alert; documented hand-off checklist (credentials rotated, ownership transferred, docs current).

Traps: launching with nobody on call; a consultant still holding org-admin months after hand-off.
