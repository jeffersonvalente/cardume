---
type: llm
focus: last_message
weight: 2
---

PASS if it (1) frames the work as explicit decisions across foundation areas — at least identity/access (Workspace/Cloud Identity groups, SSO, no long-lived keys), resource hierarchy and separate prod/non-prod projects, network/IP plan, security baseline (org policies, audit logs), CI/CD with IaC state, and observability — and flags hard-to-reverse ones such as data residency/region for the Brazilian personal data (LGPD) or the organization/IP plan; (2) separates confirmed facts from assumptions or open questions with owners; (3) proposes a platform charter or equivalent summary plus a sequenced backlog for roughly the first 90 days with owners and dependencies, starting with an early end-to-end deployment to non-prod; (4) leaves implementation to a DevOps/implementation owner and product requirements to product management.
FAIL if it writes substantial Terraform or pipeline code, invents product features or requirements, or gives only a generic checklist with no decisions, sequencing or owners.
