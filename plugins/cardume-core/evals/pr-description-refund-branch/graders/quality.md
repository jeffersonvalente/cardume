---
type: llm
focus: last_message
weight: 2
---

PASS if the reply shows a ready-to-use PR title and body where: the title is one specific line in the imperative naming the behaviour (ideally Conventional Commits style such as `feat(refunds)!: ...`); an opening summary states what changes and why (refund status delayed up to 10 minutes by polling, support tickets); the changes are consolidated by behaviour rather than copied commit by commit (no "wip", "fix typo" or "address review comments" bullets); it flags the breaking change (poller and `GET /refunds/sync` removed), the database migration and the new `REFUND_WEBHOOK_SECRET` env var; it covers signature verification and idempotent handling of duplicate deliveries; verification lists the new unit tests without claiming anything beyond "pass locally"; it references PAY-142 without inventing a tracker URL. It must ask for confirmation (or say the PR will only be created after the user approves) rather than claiming the PR was already created.
FAIL if it claims the PR was opened, invents a URL for PAY-142, omits the breaking change, or lists commit subjects as the change list.
