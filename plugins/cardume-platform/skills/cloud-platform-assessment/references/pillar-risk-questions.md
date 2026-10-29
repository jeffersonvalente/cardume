# Pillar risk questions

Questions that expose failure modes, grouped by Well-Architected pillar. Each question lists
what usually answers it. Pick the questions that fit the scope; nobody needs all of them.

Pillar names differ slightly by provider (Google Cloud uses "Security, privacy and compliance"
and "Performance optimization"; Azure has no Sustainability pillar). Use the provider's wording
in the report.

## Estate foundation (ask first; it sits under every pillar)

Landing-zone guidance answers these better than workload pillars: AWS multi-account strategy
and Control Tower, Google Cloud resource hierarchy and organization policies, Azure Cloud
Adoption Framework landing zones and management groups.

| Question | What answers it |
| :--- | :--- |
| Who can become all-powerful, and how is that use watched? | Root/Global Admin/Organization Admin holders, MFA state, break-glass procedure, alerts on their use |
| Are workloads and environments separated by account, project or subscription, or only by naming? | Organization tree, OU/folder/management-group layout |
| Which guardrails stop a bad change before it lands? | AWS SCPs and RCPs, GCP organization policy constraints, Azure Policy assignments with `Deny` effect |
| Is there one place where audit logs for every account land, and can workload admins delete them? | Organization CloudTrail trail, aggregated GCP log sink, Azure Activity Log diagnostic settings, log bucket retention and lock |
| Can cost be attributed to a team or product? | Tag/label policy, coverage of tags in billing data, cost allocation tags activated |

## Security (and privacy, compliance)

| Question | What answers it |
| :--- | :--- |
| Do humans use long-lived credentials? | IAM users with access keys, key age, user-managed GCP service account keys, Azure app secrets without expiry |
| Is federation with the company identity provider the only way in? | IAM Identity Center / Workforce Identity / Entra ID configuration; local users that bypass it |
| Which resources are reachable from the internet, and should they be? | Public IPs, security groups or firewall rules open to `0.0.0.0/0` on admin ports, public buckets, public database endpoints |
| Would we notice an attacker? | GuardDuty, Security Command Center, Defender for Cloud enabled in all regions/subscriptions, and someone receiving their findings |
| Is data encrypted with keys we control where it matters, and who can use those keys? | KMS/Cloud KMS/Key Vault key policies, CMEK coverage for regulated data |
| How do workloads get secrets? | Secrets Manager / Secret Manager / Key Vault usage vs. env vars and plaintext in IaC or CI |
| How fast are critical vulnerabilities patched on images and nodes? | Image scanning results, node OS and Kubernetes versions, patch policy |

Map serious items to the CIS Foundations Benchmark control for the provider when one exists;
auditors recognize it. NIST CSF 2.0 functions (Govern, Identify, Protect, Detect, Respond,
Recover) help explain coverage to leadership.

## Reliability

| Question | What answers it |
| :--- | :--- |
| If one zone failed, which critical components would stop? | Single-instance databases, single-zone node pools, single NAT gateway, zonal disks |
| If the region failed, what is the plan and was it ever exercised? | DR runbook, cross-region replicas/backups, last DR test date |
| When was the last successful restore of the most critical data store, and how long did it take? | Restore-test records compared with RTO/RPO |
| Are backups protected from the same admin who can delete production? | Backup vault lock / immutable backups, separate account or project for copies |
| Do quotas or limits cap growth before anyone notices? | Service quota usage near limit, IP address exhaustion in subnets |
| Do deploys degrade safely? | Health checks, rolling or canary strategy, PodDisruptionBudgets, rollback procedure |

NIST SP 800-34 frames this well: business impact analysis sets RTO/RPO, and untested plans do
not count as plans.

## Operational excellence

| Question | What answers it |
| :--- | :--- |
| Is the estate described in code, and does the code match reality? | IaC coverage, drift between plan and live state, click-ops changes in audit logs |
| Who is paged when a critical service breaks, and do alerts reach them? | Alert policies, routing, on-call schedule, alerts with owners and runbooks |
| Can the team see user-facing health, not just CPU? | SLOs or golden-signal dashboards for critical services |
| How do changes reach production? | CI/CD pipelines, approvals, who can deploy from a laptop |
| Are platform versions inside vendor support? | Kubernetes, database engine and runtime versions vs. provider support calendars |

## Performance efficiency

| Question | What answers it |
| :--- | :--- |
| Does capacity follow demand or sit at peak all day? | Autoscaling configuration, utilization over 14–30 days |
| Are we on current instance or machine families? | Old generations vs. current (including Arm: Graviton, Tau T2A/Axion, Cobalt) |
| Where is latency spent across regions and networks? | Cross-region calls, missing CDN, chatty services across zones |

## Cost optimization

| Question | What answers it |
| :--- | :--- |
| What are the top cost drivers, and which grew fastest? | Billing export grouped by service, account/project, tag or label, month over month |
| What is idle or orphaned? | Unattached volumes and disks, old snapshots, unused IPs, idle load balancers, stopped instances with storage |
| Is steady usage covered by commitments sized to the rightsized baseline? | Savings Plans/RI coverage and utilization, CUD coverage, Azure reservations and savings plan |
| What does the network bill hide? | NAT data processing, inter-zone and inter-region transfer, internet egress |
| Are budgets and anomaly alerts in place, with owners? | AWS Budgets and Cost Anomaly Detection, GCP budgets with Pub/Sub notifications, Azure Cost Management budgets |

The FinOps Foundation Framework (Inform, Optimize, Operate) is a good frame for cost maturity.
Hand detailed budgeting to `finops-budgeting`.

## Sustainability (AWS and Google Cloud)

| Question | What answers it |
| :--- | :--- |
| Do non-production environments run outside working hours? | Schedules, scale-to-zero |
| Are data retention and storage classes aligned with real access patterns? | Lifecycle rules, storage class mix |
| Is region choice informed by carbon data where latency allows? | Customer Carbon Footprint Tool, Google Cloud region carbon data, Carbon Footprint reports |

## Kubernetes in the estate

Ask these at estate level and hand deeper work to `kubernetes-operations`:

- Are all clusters on a supported minor version, with a known upgrade cadence?
- Is the API endpoint private or restricted to known networks?
- Who holds `cluster-admin`, and is it bound to groups from the corporate IdP?
- Do namespaces enforce Pod Security Standards (`baseline` or `restricted`)?
- Do critical workloads set requests, run more than one replica across zones, and have PDBs?
- Can cluster cost be split by namespace or team?
