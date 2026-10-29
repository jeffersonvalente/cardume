---
name: adr-webhooks-decision
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

We just decided to replace polling the payment provider every 5 minutes with webhooks for payment confirmations, because polling is delaying confirmations and hitting rate limits. We'll keep a nightly reconciliation job as a fallback. Please record this decision properly for the team.
