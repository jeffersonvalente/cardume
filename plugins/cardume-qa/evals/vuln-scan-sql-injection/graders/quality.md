---
type: llm
focus: last_message
weight: 2
---

PASS if it ranks SQL injection as critical in BOTH the `name` LIKE clause and the `ORDER BY {sort}` clause, and fixes them correctly: a bound parameter for name (with LIKE wildcards escaped or added in the bound value) and an allow-list mapping for the sort column (because identifiers cannot be bound as parameters). It must also flag sensitive data exposure (password_hash and emails returned), missing authentication/authorization on a user search endpoint, and suggest rate limiting/pagination for enumeration, mapped to OWASP categories.
FAIL if it only parameterizes `name` and leaves ORDER BY injectable, or misses that password_hash is returned.
