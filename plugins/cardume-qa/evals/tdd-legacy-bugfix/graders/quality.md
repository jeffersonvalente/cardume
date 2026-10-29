---
type: llm
focus: last_message
weight: 2
---

PASS if, despite the user's "no ceremony", it writes a failing regression test that reproduces the reported bug (2024-01-31 -> 2024-02-29) BEFORE showing the fix, then gives a fix that also handles December -> January of the next year (month 12 + 1 crashes too) and end-of-month clamping (e.g. via calendar.monthrange or dateutil.relativedelta), and adds tests for those edge cases (Dec 31, Jan 31 in a non-leap year -> Feb 28, a mid-month date unchanged). It may be brief, but the test-first order must be visible.
FAIL if the fix is shown before any test, if no test is written, or if the December rollover crash is not handled.
