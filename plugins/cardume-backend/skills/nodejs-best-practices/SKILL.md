---
name: nodejs-best-practices
description: "Node.js decision guide: framework selection, async patterns, error handling, security, and project architecture, focused on reasoning over copy-paste templates. Use when starting or reviewing a Node.js backend or choosing between Node frameworks and runtimes."
allowed-tools: Read Write Edit Glob Grep
---

# Node.js Best Practices

> Principles and decision-making for modern Node.js development (LTS lines verified
> against nodejs.org/en/about/previous-releases — re-check before pinning versions).
> **Learn to think, not memorize code patterns.**

---

## ⚠️ How to Use This Skill

This skill teaches **decision-making principles**, not fixed code to copy.

- Ask the user for preferences when unclear
- Choose framework/pattern based on context
- Don't default to same solution every time

---

## 1. Framework Selection

### Decision Tree

```
What are you building?
│
├── Edge/Serverless (Cloudflare, Vercel)
│   └── Hono (zero-dependency, ultra-fast cold starts)
│
├── High Performance API
│   └── Fastify (2-3x faster than Express)
│
├── Enterprise/Team familiarity
│   └── NestJS (structured, DI, decorators)
│
├── Legacy/Stable/Maximum ecosystem
│   └── Express (mature, most middleware)
│
└── Full-stack with frontend
    └── Next.js API Routes or tRPC
```

### Comparison Principles

| Factor | Hono | Fastify | Express |
|--------|------|---------|---------|
| **Best for** | Edge, serverless | Performance | Legacy, learning |
| **Cold start** | Fastest | Fast | Moderate |
| **Ecosystem** | Growing | Good | Largest |
| **TypeScript** | Native | Excellent | Good |
| **Learning curve** | Low | Medium | Low |

### Selection Questions to Ask:
1. What's the deployment target?
2. Is cold start time critical?
3. Does team have existing experience?
4. Is there legacy code to maintain?

---

## 2. Runtime Considerations

### Release Lines (check https://nodejs.org/en/about/previous-releases)

| Line | Status (late Oct 2026) | End of life |
|------|------------------------|-------------|
| **Node 26** | Active LTS (from 2026-10-28) | 2029-04-30 |
| **Node 24** "Krypton" | Maintenance LTS | 2028-04-30 |
| **Node 22** "Jod" | Maintenance LTS | 2027-04-30 |
| Node 20 "Iron" | **EOL** (2026-03-24) — upgrade | — |
| Node 18 and older | EOL | — |

- Production: Active or Maintenance LTS only; odd lines (e.g. 25) are short-lived.
- From **Node 27** the cadence changes: one major per year, every major becomes LTS
  after its Current phase (no separate Maintenance phase).
- Pin with `engines.node` in `package.json` and `.nvmrc`/`.node-version`.

### Native TypeScript (type stripping)

| Version | Status |
|---------|--------|
| 22.6 | Added behind `--experimental-strip-types` |
| 22.18 / 23.6 | **On by default** (no flag) |
| 24.12 / 25.2 | **Stable** |
| 26.0 | `--experimental-transform-types` removed |

```
node src/server.ts        # runs directly on supported lines
├── Only erasable syntax: no enum, runtime namespace, parameter properties,
│   import aliases, decorators; tsconfig "paths" ignored; no .tsx
├── Use `import type` and explicit .ts extensions in imports
├── tsconfig: "erasableSyntaxOnly", "verbatimModuleSyntax",
│   "rewriteRelativeImportExtensions", "noEmit" (TS 5.8+)
├── Still run `tsc --noEmit` in CI — Node does NOT type-check
└── Need full TS features or path aliases? use tsx or a build step (tsc/esbuild)
```

### Built-ins That Replace Dependencies

| Need | Built-in | Replaces |
|------|----------|----------|
| `.env` loading | `node --env-file=.env app.js` (stable since 24.10 / 22.21; `--env-file-if-exists` for optional files) | dotenv |
| HTTP client | Global `fetch` (Undici) | node-fetch, axios (for simple cases) |
| Tests | `node:test` + `node --test` (stable since Node 20) | Jest/Mocha for many projects |
| Watch mode | `node --watch` | nodemon |
| Sandboxing | `--permission` (stable since 23.5 / 22.13) with `--allow-fs-read`, `--allow-fs-write`, `--allow-net`, `--allow-child-process`, `--allow-worker` | — |

The **permission model** is defense-in-depth for scripts/CLIs and untrusted
inputs (denied operations throw `ERR_ACCESS_DENIED`; `--permission-audit` logs
instead). It is not a substitute for container/OS isolation.

### Module System Decision

```
ESM (import/export) — default for new code
├── "type": "module" in package.json (or .mjs)
├── Top-level await, standard across runtimes and browsers
└── Use for: all new projects and libraries

CommonJS (require) — legacy, still supported
├── Existing codebases; migrate incrementally
└── require(esm) works without flags since 22.12 / 20.19 (not experimental
    since 25.4) — CJS can load synchronous ESM, so ESM-only dependencies
    no longer force a full migration. Fails with ERR_REQUIRE_ASYNC_MODULE if
    the module graph uses top-level await (use import() there).

Libraries: publishing ESM-only is now reasonable when targeting supported
Node lines; dual CJS+ESM packages risk the "dual package hazard".
```

### Runtime Selection

| Runtime | Best For |
|---------|----------|
| **Node.js** | General purpose, largest ecosystem |
| **Bun** | Performance, built-in bundler |
| **Deno** | Security-first, built-in TypeScript |

---

## 3. Architecture Principles

### Layered Structure Concept

```
Request Flow:
│
├── Controller/Route Layer
│   ├── Handles HTTP specifics
│   ├── Input validation at boundary
│   └── Calls service layer
│
├── Service Layer
│   ├── Business logic
│   ├── Framework-agnostic
│   └── Calls repository layer
│
└── Repository Layer
    ├── Data access only
    ├── Database queries
    └── ORM interactions
```

### Why This Matters:
- **Testability**: Mock layers independently
- **Flexibility**: Swap database without touching business logic
- **Clarity**: Each layer has single responsibility

### When to Simplify:
- Small scripts → Single file OK
- Prototypes → Less structure acceptable
- Always ask: "Will this grow?"

---

## 4. Error Handling Principles

### Centralized Error Handling

```
Pattern:
├── Create custom error classes
├── Throw from any layer
├── Catch at top level (middleware)
└── Format consistent response
```

### Error Response Philosophy

```
Client gets:
├── Appropriate HTTP status
├── Error code for programmatic handling
├── User-friendly message
└── NO internal details (security!)

Logs get:
├── Full stack trace
├── Request context
├── User ID (if applicable)
└── Timestamp
```

### Status Code Selection

| Situation | Status | When |
|-----------|--------|------|
| Bad input | 400 | Client sent invalid data |
| No auth | 401 | Missing or invalid credentials |
| No permission | 403 | Valid auth, but not allowed |
| Not found | 404 | Resource doesn't exist |
| Conflict | 409 | Duplicate or state conflict |
| Validation | 422 | Schema valid but business rules fail |
| Server error | 500 | Our fault, log everything |

---

## 5. Async Patterns Principles

### When to Use Each

| Pattern | Use When |
|---------|----------|
| `async/await` | Sequential async operations |
| `Promise.all` | Parallel independent operations |
| `Promise.allSettled` | Parallel where some can fail |
| `Promise.race` | Timeout or first response wins |

### Event Loop Awareness

```
I/O-bound (async helps):
├── Database queries
├── HTTP requests
├── File system
└── Network operations

CPU-bound (async doesn't help):
├── Crypto operations
├── Image processing
├── Complex calculations
└── → Use worker threads or offload
```

### Avoiding Event Loop Blocking

- Never use sync methods in production (fs.readFileSync, etc.)
- Offload CPU-intensive work
- Use streaming for large data

---

## 6. Validation Principles

### Validate at Boundaries

```
Where to validate:
├── API entry point (request body/params)
├── Before database operations
├── External data (API responses, file uploads)
└── Environment variables (startup)
```

### Validation Library Selection

| Library | Best For |
|---------|----------|
| **Zod** | TypeScript first, inference |
| **Valibot** | Smaller bundle (tree-shakeable) |
| **ArkType** | Performance critical |
| **Yup** | Existing React Form usage |

### Validation Philosophy

- Fail fast: Validate early
- Be specific: Clear error messages
- Don't trust: Even "internal" data

---

## 7. Security Principles

### Security Checklist (Not Code)

- [ ] **Input validation**: All inputs validated
- [ ] **Parameterized queries**: No string concatenation for SQL
- [ ] **Password hashing**: bcrypt or argon2
- [ ] **JWT verification**: Always verify signature and expiry
- [ ] **Rate limiting**: Protect from abuse
- [ ] **Security headers**: Helmet.js or equivalent
- [ ] **HTTPS**: Everywhere in production
- [ ] **CORS**: Properly configured
- [ ] **Secrets**: Environment variables only
- [ ] **Dependencies**: Regularly audited

### Security Mindset

```
Trust nothing:
├── Query params → validate
├── Request body → validate
├── Headers → verify
├── Cookies → validate
├── File uploads → scan
└── External APIs → validate response
```

---

## 8. Testing Principles

### Test Strategy Selection

| Type | Purpose | Tools |
|------|---------|-------|
| **Unit** | Business logic | node:test, Vitest |
| **Integration** | API endpoints | Supertest |
| **E2E** | Full flows | Playwright |

### What to Test (Priorities)

1. **Critical paths**: Auth, payments, core business
2. **Edge cases**: Empty inputs, boundaries
3. **Error handling**: What happens when things fail?
4. **Not worth testing**: Framework code, trivial getters

### Built-in Test Runner (`node:test`, stable since Node 20)

```
node --test "src/**/*.test.ts"
├── No external dependency; glob patterns supported
├── .ts tests run via type stripping on current LTS lines
├── Built-in coverage reporting (flag name varies by line; check `node --help`)
└── --watch for watch mode
```

---

## 10. Anti-Patterns to Avoid

### ❌ DON'T:
- Use Express for new edge projects (use Hono)
- Use sync methods in production code
- Put business logic in controllers
- Skip input validation
- Hardcode secrets
- Trust external data without validation
- Block event loop with CPU work

### ✅ DO:
- Choose framework based on context
- Ask user for preferences when unclear
- Use layered architecture for growing projects
- Validate all inputs
- Use environment variables for secrets
- Profile before optimizing

---

## 11. Decision Checklist

Before implementing:

- [ ] **Asked user about stack preference?**
- [ ] **Chosen framework for THIS context?** (not just default)
- [ ] **Considered deployment target?**
- [ ] **Planned error handling strategy?**
- [ ] **Identified validation points?**
- [ ] **Considered security requirements?**

---

> **Remember**: Node.js best practices are about decision-making, not memorizing patterns. Every project deserves fresh consideration based on its requirements.
