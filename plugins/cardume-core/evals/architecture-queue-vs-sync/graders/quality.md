---
type: llm
focus: last_message
weight: 2
---

PASS if it produces an ADR-style record (context, options, decision, consequences) that compares A and B on concrete trade-offs: coupling/availability of checkout, consistency (outbox gives atomicity with the order write; A risks partial side effects or double sends on retry), idempotency of consumers, operational cost of running a queue + worker, latency of side effects, and team/ops maturity. It must make an explicit recommendation tied to the stated facts (slow loyalty service breaking checkout, 200 orders/min) and state what would change the decision.
FAIL if it just lists generic pros/cons of microservices or event-driven systems, omits idempotency/duplicate delivery, or gives no clear decision.
