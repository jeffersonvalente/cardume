# Orchestrator Reference: Boundaries and Examples

Detailed domain-boundary and file-ownership tables plus worked orchestration examples for the `orchestrator` agent. Read when routing writes across agents or when unsure how to sequence a run.

## Domain Boundaries

| Agent | Can Do | Should Not Do |
|-------|--------|---------------|
| `frontend-specialist` | Components, UI, styles, hooks | Test files, API routes, DB |
| `backend-specialist` | API, server logic, DB queries | UI components, styles |
| `test-engineer` | Test files, mocks, coverage | Production code |
| `mobile-developer` | RN/Flutter components, mobile UX | Web components |
| `database-architect` | Schema, migrations, queries | UI, API logic |
| `security-auditor` | Audit, vulnerabilities, auth review | Feature code, UI |
| `devops-engineer` | CI/CD, deployment, infra config | Application code |
| `performance-optimizer` | Profiling, optimization, caching | New features |
| `seo-specialist` | Meta tags, SEO config, analytics | Business logic |
| `documentation-writer` | Docs, README, comments | Code logic; auto-invoking without an explicit request |
| `project-planner` | Its plan file in `docs/`, task breakdown | Code files |
| `software-architect` | Contracts, fixtures, ADRs, architecture file, level-3 tasks.md | Feature code |
| `debugger` | Bug fixes, root cause | New features |
| `explorer-agent` | Codebase discovery | Write operations |
| `penetration-tester` | Security testing | Feature code |

## File Type Ownership

| File Pattern | Owner Agent | Others |
|--------------|-------------|--------|
| `**/*.test.{ts,tsx,js}` | `test-engineer` | Route to owner |
| `**/__tests__/**` | `test-engineer` | Route to owner |
| `**/components/**` | `frontend-specialist` | Not backend, test |
| `**/api/**`, `**/server/**` | `backend-specialist` | Not frontend |
| `**/prisma/**`, `**/drizzle/**` | `database-architect` | Not frontend |

## Routing Rule

```
WHEN an agent is about to write a file:
  IF file.path matches another agent's domain:
    → stop
    → invoke the owning agent for that file
    → don't write it yourself
```

## Example

```
❌ Wrong:
frontend-specialist writes: __tests__/TaskCard.test.tsx
→ Test files belong to test-engineer

✅ Correct:
frontend-specialist writes: components/TaskCard.tsx
→ then invokes test-engineer
test-engineer writes: __tests__/TaskCard.test.tsx
```

If you see an agent writing files outside its domain, stop and re-route.

---

## Agent States

| State | Icon | Meaning |
|-------|------|---------|
| PENDING | ⏳ | Waiting to be invoked |
| RUNNING | 🔄 | Currently executing |
| COMPLETED | ✅ | Finished successfully |
| FAILED | ❌ | Encountered error |

---

## Example Orchestration

**User**: "Review and improve the authentication system"

**Orchestrator Response**:
```
Pre-flight: review/analysis task — no plan file required. Agent assignments valid.

I'll coordinate multiple agents for a comprehensive review:

1. First, using explorer-agent to map auth-related code...
   [Agent executes, returns findings]

2. Now using security-auditor to review security posture...
   [Agent executes, returns findings]

3. Having backend-specialist review implementation...
   [Agent executes, returns findings]

4. Finally, test-engineer to check test coverage...
   [Agent executes, returns findings]

## Synthesis Report
[Combined findings and recommendations]
```

---

### Example: Plan Missing

**User**: "Build me an e-commerce site"

**Wrong**: directly invoke frontend-specialist and backend-specialist with no plan — they will make incompatible assumptions about structure and scope.

**Correct**:
```
Pre-flight: no approved PRD, spec/tasks.md or plan found in docs/.
→ Classify the level: a new product is level 3.
→ "No plan yet — writing the PRD first." (prd skill → software-architect architecture file
   → a spec per feature → software-architect writes each tasks.md)
→ Resume orchestration from the approved docs/specs/<slug>/tasks.md files
   (a project-planner plan file only for small multi-domain work with no spec or PRD)
```

---

