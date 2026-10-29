---
name: level2-feature-spec
plugins: ["../.."]
tags: [trigger, levels]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "Classify every request by work level before acting and say it in one line. Level 0 trivial (typo, one-line fix): no artifacts. Level 1 small fix: mini-spec in the final report. Level 2 feature: spec -> tasks -> implement -> verify. Level 3 product/phase: prd -> architect -> gate -> release. Record significant technical decisions with the adr skill."
---

We need multi-currency support in our invoicing module: each invoice can be issued in BRL, USD or EUR, totals must be converted to the company's base currency with the day's exchange rate, and the monthly report must show both the original and the base-currency amounts. How do we go about it?
