---
name: tdd-legacy-bugfix
plugins: ["../..", "../../../cardume-core"]
tags: [trigger, discipline]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Quick one, just fix this bug, no need for ceremony: customers on the last day of a month get the wrong renewal date. E.g. subscribed 2024-01-31 should renew 2024-02-29, but we crash. Project uses pytest.

```python
from datetime import date

def next_renewal(start: date) -> date:
    return start.replace(month=start.month + 1)
```
