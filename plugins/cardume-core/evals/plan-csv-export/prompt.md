---
name: plan-csv-export
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

We need to add "Export to CSV" to the orders list in our Django + React admin. Exports can be up to 500k rows, must respect the user's current filters, and must not time out the web request. Before anyone writes code, give me the implementation plan.
