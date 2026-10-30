---
name: api-patterns
description: "Chooses REST, GraphQL or tRPC and sets versioning, pagination, auth and rate limits. Use when designing an API or reviewing endpoint contracts."
allowed-tools: Read Write Edit Glob Grep
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# API Patterns

> API design principles and decision-making, aligned with current standards
> (RFC 9457 Problem Details, OpenAPI 3.1/3.2, IETF HTTPAPI drafts).
> **Learn to think, not copy fixed patterns.**

## 🎯 Selective Reading Rule

**Read only the files relevant to the request.** Check the content map, find what you need.

---

## 📑 Content Map

| File | Description | When to Read |
|------|-------------|--------------|
| `api-style.md` | REST vs GraphQL vs tRPC decision tree | Choosing API type |
| `rest.md` | Resource naming, HTTP methods, status codes, idempotency keys | Designing REST API |
| `response.md` | Envelope pattern, RFC 9457 errors, pagination | Response structure |
| `graphql.md` | Schema design, when to use, security | Considering GraphQL |
| `trpc.md` | TypeScript monorepo, type safety | TS fullstack projects |
| `versioning.md` | URI/Header/Query versioning | API evolution planning |
| `auth.md` | JWT, OAuth, Passkey, API Keys | Auth pattern selection |
| `rate-limiting.md` | Token bucket, sliding window, `RateLimit` headers | API protection |
| `documentation.md` | OpenAPI 3.1/3.2 best practices | Documentation |
| `security-testing.md` | OWASP API Top 10, auth/authz testing | Security audits |

---

## 🔗 Related Skills

| Need | Skill |
|------|-------|
| API implementation (Node.js / Java) | `cardume-backend:nodejs-best-practices`, `cardume-backend:java-spring-patterns` |
| Data structure | `cardume-core:database-design` |
| Security details | `cardume-qa:vulnerability-scanner` |

---

## ✅ Decision Checklist

Before designing an API:

- [ ] **Asked user about API consumers?**
- [ ] **Chosen API style for THIS context?** (REST/GraphQL/tRPC)
- [ ] **Defined consistent response format?** (errors as RFC 9457 `application/problem+json`)
- [ ] **Retry-safe writes?** (idempotency keys on POST/PATCH that clients may retry)
- [ ] **Planned versioning strategy?**
- [ ] **Considered authentication needs?**
- [ ] **Planned rate limiting?**
- [ ] **Documentation approach defined?**

---

## ❌ Anti-Patterns

**DON'T:**
- Default to REST for everything
- Use verbs in REST endpoints (/getUsers)
- Return inconsistent response formats
- Expose internal errors to clients
- Skip rate limiting

**DO:**
- Choose API style based on context
- Ask about client requirements
- Document thoroughly
- Use appropriate status codes

---

## Script

| Script | Purpose | Command |
|--------|---------|---------|
| `cardume-api-validator` (wraps `scripts/api_validator.py`) | API endpoint validation | `cardume-api-validator <project_path>` |

