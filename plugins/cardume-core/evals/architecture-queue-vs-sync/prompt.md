---
name: architecture-queue-vs-sync
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Our checkout service (Python, Postgres, ~200 orders/minute at peak) currently calls the email, invoicing and loyalty-points services synchronously over HTTP inside the request. When the loyalty service is slow, checkout times out. Two options on the table:

A) Keep HTTP calls but add timeouts, retries and a circuit breaker.
B) Write an `OrderPlaced` event to an outbox table in the same transaction and have a worker publish it to a queue that the three services consume.

Which should we choose? Write it up as a decision we can keep in the repo.
