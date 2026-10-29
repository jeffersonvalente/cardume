---
name: gate-phase-ready
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Is phase 2 ready to approve? The PRD criteria are: C1 'CSV export of invoices works for 10k rows in under 5s' (verify: `pnpm test export.perf`), C2 'export respects tenant isolation' (verify: `pnpm test export.tenancy`), C3 'export button is keyboard accessible' (verify: manual script step 4). The developer says everything is done and tested. Here is the only CI output we have: `export.perf: 1 passed (3.2s)`. Prepare the gate.
