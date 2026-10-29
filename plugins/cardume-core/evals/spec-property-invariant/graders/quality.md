---
type: llm
focus: last_message
weight: 2
---

PASS if the reply asks design-changing questions or presents EARS-style requirements with acceptance criteria, and states at least one invariant as a property for all inputs (e.g. "for all carts, total >= 0" or "total = sum of discounted lines - coupon") to be checked with a property-based testing tool such as Hypothesis.
FAIL if it writes implementation code first, or only gives example-based criteria with no invariant stated for all inputs.
