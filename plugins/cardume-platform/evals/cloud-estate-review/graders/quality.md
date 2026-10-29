---
type: llm
focus: last_message
weight: 2
---

PASS if it (1) ranks a small set of top risks (not a flat checklist) and puts the payments root user without MFA but with access keys, the absence of organization-wide audit logging (single-region CloudTrail stored in a workload account) and the never-restored single-AZ `orders-db` at or near the top; (2) states each top risk in terms of consequence (what could happen and to whom) with an explicit likelihood and impact or equivalent rationale, and says how each was checked, citing the evidence given and flagging what was not verified (for example the restore history or which data lives in which account); (3) delivers a 30/60/90-day plan where the first 30 days contain the most urgent risks (remove root keys and enable MFA, organization CloudTrail to a protected log account, timed restore test of `orders-db`, close public SSH and restrict the EKS endpoint) and later windows fix causes (SCPs or guardrails, federation instead of IAM users, Multi-AZ or a decided RTO/RPO, GuardDuty org-wide in all regions, EKS upgrade from 1.28 to a supported version, budgets, tagging, cleanup of unattached volumes); (4) gives plan items an owner role or a verifiable done-condition; (5) stays read-only, recommending changes rather than claiming to run them.
FAIL if it is an unprioritized list of best practices, misses the root credential issue, recommends buying Savings Plans or Reserved Instances before rightsizing and cleanup, or proposes running mutating commands itself.
