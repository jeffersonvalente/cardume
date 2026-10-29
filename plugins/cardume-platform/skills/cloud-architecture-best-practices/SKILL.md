---
name: cloud-architecture-best-practices
description: "Reviews or proposes cloud workload designs as short decision records weighing cost, complexity, reliability and operability, with provider-grounded cost levers for AWS, GCP and Azure. Use when choosing services or compute, sizing, scaling, resiliency or network design, or cutting cost without hurting reliability."
---

# Cloud Architecture Best Practices

> Every design choice spends money, complexity or risk. Make the trade visible, pick the
> simplest option that meets the requirement, and say what would change the answer.

Use this skill for **one workload or one design decision**: a proposed architecture, a service
choice (Cloud Run vs. GKE, Lambda vs. ECS, Azure Functions vs. Container Apps), a scaling or
resiliency question, or "this design costs too much".

Route elsewhere when the scope differs:

- Reviewing a whole estate or platform for risks: `cardume-platform:cloud-platform-assessment`.
- Budgets, forecasts, showback, commitment purchase plans: `cardume-platform:finops-budgeting`.
- Writing or reviewing the Terraform for the chosen design: `cardume-platform:terraform-stacks`.

Stay read-only while reviewing: read IaC, diagrams, metrics and billing data; recommend
changes, do not apply them.

## Start from requirements, not services

Before comparing options, write down what the design must satisfy. Missing numbers are the
most common reason architecture advice goes wrong, so ask for them or state the assumption:

- **Load shape:** steady, daily cycle, spiky, or batch; peak vs. average ratio; growth.
- **Targets:** latency (p95/p99), availability, RTO and RPO. A 99.9% target and a 99.99%
  target usually lead to different architectures and very different bills.
- **Data:** size, growth, access pattern, residency, retention.
- **Team:** what they already run well. Operability is a real cost; a platform the team cannot
  debug at 3 a.m. is expensive at any price.
- **Constraints:** compliance, existing contracts or commitments, region, deadline.
- **Unit of value:** cost per request, per tenant, per order. Unit cost turns "the bill went up"
  into "we got more efficient or less".

## Write the answer as a decision record

Keep it short enough to read in five minutes. Four parts:

**1. Context.** The problem, the requirements above, and the current state with real numbers
(utilization, monthly cost by service, traffic). Note which numbers are assumed.

**2. Options.** Two to four realistic options, always including "improve what exists" when
something exists. Compare them in one table:

| | Option A | Option B | Option C |
| :--- | :--- | :--- | :--- |
| Monthly cost (order of magnitude, with the assumption) | | | |
| Cost behaviour as load grows or drops | | | |
| Build and migration effort | | | |
| Operational load (patching, upgrades, on-call skills) | | | |
| Reliability against the target (failure domains, recovery) | | | |
| Security surface | | | |
| Lock-in and reversibility | | | |

Price options with the provider's calculator or published prices and show the arithmetic,
for example "6 × m7g.xlarge on-demand ≈ 6 × $0.163 × 730 h ≈ $715/month (us-east-1 list price
at time of writing; verify)". Round; precision you do not have misleads.

**3. Recommendation.** The option, why it wins for *these* requirements, and what it gives up.
Sequence the change so the cheapest, most reversible steps come first.

**4. Consequences and revisit triggers.** What the team must now operate, what to measure, and
the conditions that would flip the decision ("if sustained load exceeds ~40 vCPU for three
months, re-price GKE Standard with CUDs against Cloud Run").

Save longer records as an ADR in `docs/` when the user wants one kept; otherwise answer inline.

## Trade-off lenses

Use the provider's Well-Architected framework (AWS, Google Cloud, Azure) as the vocabulary, and
test each option against these questions:

- **Cost.** What is fixed and what scales with use? What sits idle at night? Which line items
  hide in networking (NAT processing, cross-zone and cross-region transfer, internet egress)?
- **Reliability.** Which single zone, instance or dependency stops the service? Does the
  recovery path meet RTO/RPO, and has it been exercised?
- **Operability.** Who patches, upgrades and scales it? Managed and serverless services shift
  that work to the provider at a price per unit; self-managed shifts it to the team at a price
  in hours and incidents.
- **Security.** What is exposed, which identities can change it, where do secrets live?
- **Performance.** Does capacity follow demand? Are there cold starts, connection limits or
  noisy neighbours that matter for the latency target?

When two lenses conflict, say which one the requirements favour and quantify the gap: "Multi-AZ
doubles the database line (~$900 → ~$1,800/month) and removes the only single-zone component
on the checkout path; the 99.9% target needs it."

## Choosing compute

A rough default order, to be overruled by requirements:

1. **Managed or serverless first** for spiky, low or unpredictable traffic and small teams:
   Lambda, Cloud Run, Azure Functions or Container Apps. Pay per use, scale to zero, little to
   operate. Watch per-request cost at sustained high load, cold starts, and execution limits.
2. **Managed containers** (ECS on Fargate or EC2, Cloud Run with minimum instances, GKE
   Autopilot, Azure Container Apps) for steady services that want container packaging without
   running a cluster platform.
3. **Kubernetes you operate** (EKS, GKE Standard, AKS) when there are many services, a team
   that can run it, and needs that managed options do not meet (custom scheduling, GPUs,
   operators, portability). The control plane is the cheap part; the team time is not.
4. **VMs** for licensed or stateful software, special hardware, or lift-and-shift with a plan.

Moving platforms to save money rarely pays for itself unless the current fleet is first
rightsized and autoscaled; compare against "same platform, done well".

## Cost levers, grounded in provider docs

Apply in this order: remove waste, rightsize, make capacity elastic, then commit to the
remaining steady baseline. Committing first locks in today's waste.

| Lever | AWS | Google Cloud | Azure |
| :--- | :--- | :--- | :--- |
| Find waste and rightsizing | Compute Optimizer, Cost Explorer rightsizing, Trusted Advisor | Active Assist / Recommender (machine type, idle VM, idle disk) | Azure Advisor cost recommendations |
| Elastic capacity | Auto Scaling groups, ECS/EKS autoscaling, Karpenter; scheduled scale-down | Managed instance group autoscaling, GKE cluster autoscaler and node auto-provisioning, Cloud Run min/max instances | VM Scale Sets, AKS cluster autoscaler, Container Apps scale rules |
| Interruptible capacity for fault-tolerant work | Spot Instances (large discounts, 2-minute notice) | Spot VMs (large discounts, no max runtime, preemptible on short notice) | Spot VMs (eviction on capacity or price) |
| Commit to the steady baseline | Compute Savings Plans (flexible across EC2, Fargate, Lambda), EC2 Instance Savings Plans, Reserved Instances for RDS, ElastiCache, OpenSearch, Redshift | Committed use discounts (resource-based and spend-based / flexible), sustained use discounts on some machine series | Azure savings plan for compute, Reservations |
| Cheaper processors | Graviton (Arm) instances | Arm machine series (Tau T2A, Axion-based) and newer generations | Arm-based Cobalt and Ampere VMs |
| Storage tiers and lifecycle | S3 lifecycle rules, Intelligent-Tiering, gp3 instead of gp2, snapshot cleanup | GCS lifecycle rules and Autoclass, storage classes, balanced vs. SSD persistent disks | Blob lifecycle management, access tiers, managed disk types |
| Network | S3 and DynamoDB gateway endpoints (no charge) instead of NAT, interface endpoints for ECR and other APIs, keep chatty traffic in one AZ, CloudFront for egress | Private Google Access, Cloud NAT sizing, Cloud CDN, avoid cross-region data movement | Private endpoints and service endpoints, NAT Gateway sizing, Azure Front Door/CDN |
| Analytics | Athena partitioning and columnar formats; Redshift RIs or Serverless | BigQuery partitioning and clustering, on-demand vs. editions with reservations, custom quotas | Synapse/Fabric capacity sizing, pausing |
| Guardrails | AWS Budgets, Cost Anomaly Detection, cost allocation tags | Budgets with Pub/Sub notifications, labels, Billing export to BigQuery | Cost Management budgets and alerts, tags, Azure Policy |

Discount sizes and prices change; quote them from the current pricing pages and treat any
figure in a recommendation as "at time of writing".

Size commitments from usage history after rightsizing, aim to cover the steady floor rather
than the peak, and leave the variable part on-demand or Spot. Hand the purchase plan to
`finops-budgeting`.

## Traps worth naming

- **Paying NAT for traffic to the provider's own services.** Image pulls and object storage
  traffic through a NAT gateway are billed per GB processed; gateway or private endpoints
  often remove most of it.
- **Cross-zone chatter.** Zonal redundancy is good; services that call each other across zones
  on every request pay transfer both ways. Prefer zone-aware routing where the platform offers it.
- **Over-provisioned "just in case".** Low average utilization on fixed fleets is the classic
  sign. Autoscale on a demand signal and keep headroom explicit.
- **High availability by duplication only.** Two of everything in one zone, or replicas that
  were never failed over, cost double without the protection.
- **Kubernetes as the default.** It is powerful and expensive in people. Choose it for its
  capabilities, not for fashion or a hoped-for saving.
- **No unit metric.** Without cost per request, tenant or order, nobody can tell growth from waste.

## Public sources

- AWS Well-Architected Framework, especially the Cost Optimization pillar; AWS pricing pages,
  Savings Plans and Spot documentation; VPC endpoint and NAT gateway pricing.
- Google Cloud Well-Architected Framework (cost optimization pillar); committed use discounts,
  Spot VMs, GKE cost-optimization best practices, BigQuery pricing and editions, Cloud Storage
  lifecycle documentation.
- Azure Well-Architected Framework (cost optimization pillar), Azure savings plan and
  Reservations documentation, Azure Advisor.
- FinOps Foundation Framework (unit economics, rate and usage optimization).
