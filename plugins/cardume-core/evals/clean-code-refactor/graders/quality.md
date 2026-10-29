---
type: llm
focus: last_message
weight: 2
---

PASS if the refactor (1) uses intention-revealing names for the function, parameters and the 1.1 constant (e.g. TAX_RATE), (2) flattens the nested ifs with guard clauses or a small predicate helper, (3) removes the duplicated tax/append branch, (4) replaces `f == True` with a clearly named boolean, and (5) preserves behaviour exactly, including that `t == 'all'` matches every type, deleted items are excluded, and non-positive amounts are only dropped when the flag is set. It should mention how to verify equivalence (e.g. a quick characterization test).
FAIL if behaviour changes (e.g. negative amounts filtered unconditionally, 'all' dropped), if it introduces needless abstractions (classes, strategy pattern) for a 10-line function, or if names stay cryptic.
