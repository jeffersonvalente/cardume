---
name: architecture
description: "Weighs trade-offs and picks patterns (monolith or microservices, layering, events). Use when choosing an architecture or reviewing a system design."
allowed-tools: Read Glob Grep
---

# Architecture Decision Framework

> "Requirements drive architecture. Trade-offs inform decisions. ADRs capture rationale."

## Selective Reading

Read only the files relevant to the request, using this map, to keep context small.

| File | Description | When to Read |
|------|-------------|--------------|
| `context-discovery.md` | Questions to ask, project classification | Starting architecture design |
| `trade-off-analysis.md` | Trade-off framework (record the result with the `adr` skill) | Weighing options |
| `pattern-selection.md` | Decision trees, anti-patterns | Choosing patterns |
| `examples.md` | MVP, SaaS, Enterprise examples | Reference implementations |
| `patterns-reference.md` | Quick lookup for patterns | Pattern comparison |

---

## 🔗 Related Skills

| Skill | Use For |
|-------|---------|
| `database-design` | Database schema design |
| `api-patterns` (cardume-backend, if installed) | API design patterns |
| `deployment-procedures` (cardume-platform, if installed) | Deployment architecture |
| `adr` | Recording the decision in `docs/adr/` |

---

## Core Principle

**"Simplicity is the ultimate sophistication."**

- Start simple
- Add complexity only when proven necessary
- You can always add patterns later
- Removing complexity is much harder than adding it

---

## Validation Checklist

Before finalizing architecture:

- [ ] Requirements clearly understood
- [ ] Constraints identified
- [ ] Each decision has trade-off analysis
- [ ] Simpler alternatives considered
- [ ] ADRs written for significant decisions (`adr` skill, `docs/adr/`)
- [ ] Team expertise matches chosen patterns
