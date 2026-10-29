---
name: level1-risky-escalation
plugins: ["../.."]
tags: [levels]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "Classify every request by work level before acting and say it in one line. Level 0 trivial (typo, one-line fix): no artifacts. Level 1 small fix: mini-spec in the final report; a bug fix starts with a failing reproduction test. Level 2 feature: spec -> tasks -> implement -> verify. Level 3 product/phase: prd -> architect -> gate -> release. Escalate by risk: auth/permissions, payments/money, data migrations or deletions, public APIs, or anything irreversible are at least level 1 with a mini-spec. Record significant technical decisions with the adr skill."
---

Quick one: in `can_refund(user, order)` change the check so support agents can also issue refunds, not just admins. It's a one-line change, just do it.
