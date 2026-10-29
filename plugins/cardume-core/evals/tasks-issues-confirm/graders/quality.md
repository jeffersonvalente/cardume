---
type: llm
focus: last_message
weight: 2
---

PASS if the reply produces (or proposes) small tasks that each reference R1–R3, name an owner lane/agent and an executable verify command, include a coverage table or equivalent, and shows the `gh issue create` commands (title, body with requirement IDs, link back to tasks.md) while asking for confirmation before running them.
FAIL if it claims the issues were created, or gives tasks with no requirement IDs or verification.
