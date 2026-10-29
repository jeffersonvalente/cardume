---
type: llm
focus: last_message
weight: 2
---

PASS if the reply keeps the level-3 chain: it proposes the architecture step (contracts, ADRs, a feature list mapping C1–C3 to features) and a spec per feature before tasks, offering a quick spec (spec + tasks in one approval) as the fast path, and flags payments as risky.
FAIL if it writes a task list directly from the PRD criteria with no feature specs, or drops acceptance criteria.
