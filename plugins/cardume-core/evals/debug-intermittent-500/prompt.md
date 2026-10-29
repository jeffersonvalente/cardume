---
name: debug-intermittent-500
plugins: ["../.."]
tags: [trigger, smoke]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Flask endpoint `/orders` returns HTTP 500 roughly once every 50 requests, only in production under load. Locally every request works. The log line is `sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached`. How should I find and fix the root cause?
