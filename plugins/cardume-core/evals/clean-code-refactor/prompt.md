---
name: clean-code-refactor
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Refactor this function so it's readable and maintainable. Keep behaviour identical.

```python
def proc(d, t, f=False):
    r = []
    for i in d:
        if i['type'] == t or t == 'all':
            if i['status'] != 'deleted':
                if f == True:
                    if i['amount'] > 0:
                        x = i['amount'] * 1.1  # add tax
                        r.append({'id': i['id'], 'amount': x, 'type': i['type']})
                else:
                    x = i['amount'] * 1.1  # add tax
                    r.append({'id': i['id'], 'amount': x, 'type': i['type']})
    return r
```
