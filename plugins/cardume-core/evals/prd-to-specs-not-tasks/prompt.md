---
name: prd-to-specs-not-tasks
tags: [levels]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "Classify every request by work level before acting and say it in one line. Level 2 feature: spec -> tasks -> implement -> verify -> review. Level 3 product/phase: prd -> software-architect writes contracts, ADRs and the feature list in docs/prd/<slug>-architecture.md -> per feature: spec -> software-architect writes tasks.md -> implement -> verify -> review -> gate -> user decides -> release."
---

PRD for phase 2 is approved (`docs/prd/PHASE-2.md`): C1 customers can pay invoices by card, C2 receipts are emailed within 1 minute, C3 the finance dashboard shows paid vs unpaid. Break the PRD into implementation tasks for the team so we can start this week.
