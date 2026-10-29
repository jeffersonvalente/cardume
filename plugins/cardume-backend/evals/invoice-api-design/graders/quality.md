---
type: llm
focus: last_message
weight: 2
---

PASS if endpoints are resource-oriented (e.g. /invoices, /invoices/{id}), state changes like pay/cancel are modeled deliberately (sub-resource or action endpoint with rationale), status codes are specific (201/200/404/409/422), the list endpoint has pagination, and tenant isolation is addressed. FAIL if it uses verb URLs throughout or omits pagination and tenancy.
