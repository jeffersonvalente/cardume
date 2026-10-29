---
name: invoice-api-design
plugins: ["../..", "../../../cardume-core"]
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Design the REST API for managing invoices in a multi-tenant SaaS: create, list with filters, get, mark as paid, and cancel. Give endpoints, status codes and the list response shape.
