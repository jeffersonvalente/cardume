---
type: llm
focus: last_message
weight: 2
---

PASS if the reply produces (or shows the content of) a numbered ADR under docs/adr/ with Status, Context (polling delays and rate limits), Options considered (at least polling vs webhooks), Decision, and Consequences that include webhook security (signature verification), idempotency/duplicate events and the nightly reconciliation fallback.
FAIL if it is only a prose summary without the ADR structure, or omits the consequences.
