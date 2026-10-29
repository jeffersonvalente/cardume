---
type: llm
focus: last_message
weight: 2
---

PASS if the plan is a short list (roughly 5-10) of concrete tasks, each with a verifiable done-criterion, explicit dependencies/order, and covers: an async/background job (e.g. Celery/RQ) with streaming or chunked writes rather than building 500k rows in memory, reuse of the existing filter logic so the export matches the list, storage + download link or notification when ready, permission checks, frontend trigger/progress state, and a final verification phase (tests and a run with a large dataset).
FAIL if it is a vague essay without checkable tasks, proposes generating the CSV synchronously in the request, or ignores filters/permissions.
