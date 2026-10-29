---
name: level0-typo-no-spec
plugins: ["../.."]
tags: [negative, levels]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: "Classify every request by work level before acting and say it in one line. Level 0 trivial (typo, one-line fix): no artifacts. Level 1 small fix: mini-spec in the final report. Level 2 feature: spec -> tasks -> implement -> verify. Level 3 product/phase: prd -> architect -> gate -> release. Record significant technical decisions with the adr skill."
---

In our README there is the sentence "Users recieve an email after signup." Fix the typo and give me the corrected sentence.
