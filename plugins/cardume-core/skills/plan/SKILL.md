---
name: plan
description: "Creates a project plan file (docs/PLAN-{task-slug}.md) for the given request using the project-planner agent: clarifying questions, task breakdown, agent assignments, and a verification checklist. Writes no code."
disable-model-invocation: true
argument-hint: "[what to plan]"
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# /cardume-core:plan - Project Planning Mode

$ARGUMENTS

---

Use this lightweight plan for small multi-domain work. For a feature (level 2) use the `spec` skill, and
for a new product or phase (level 3) the `prd` skill — their files are the plan the orchestrator follows.

## Rules

1. **No code writing** — this command produces the plan file only, so the user can review scope before anything is built.
2. **Use the project-planner agent**, not Claude Code's built-in plan mode, so the plan lands in a file other agents can read.
3. **Ask clarifying questions** before planning when the request is ambiguous. project-planner runs as a subagent and returns its questions under **Open questions**; ask the user, then resume it with the answers.
4. **Dynamic naming** — name the plan file after the task.

---

## Task

Use the `project-planner` agent with this context:

```
CONTEXT:
- User Request: $ARGUMENTS
- Mode: PLANNING ONLY (no code)
- Output: docs/PLAN-{task-slug}.md (dynamic naming)

NAMING RULES:
1. Extract 2-3 key words from request
2. Lowercase, hyphen-separated
3. Max 30 characters
4. Example: "e-commerce cart" → PLAN-ecommerce-cart.md

RULES:
1. Follow project-planner's Conversation Context step
2. Follow project-planner's Phase 0 (context check, clarifying questions)
3. Create docs/PLAN-{slug}.md with task breakdown
4. Don't write any code files
5. Report the exact file name created
```

---

## Expected Output

| Deliverable | Location |
|-------------|----------|
| Project Plan | `docs/PLAN-{task-slug}.md` |
| Task Breakdown | Inside plan file |
| Agent Assignments | Inside plan file |
| Verification Checklist | Phase X in plan file |

---

## After Planning

Tell user:
```
[OK] Plan created: docs/PLAN-{slug}.md

Next steps:
- Review the plan
- Implement from the plan (the orchestrator coordinates multi-domain work)
- Or modify plan manually
```

---

## Naming Examples

| Request | Plan File |
|---------|-----------|
| `/cardume-core:plan e-commerce site with cart` | `docs/PLAN-ecommerce-cart.md` |
| `/cardume-core:plan mobile app for fitness` | `docs/PLAN-fitness-app.md` |
| `/cardume-core:plan add dark mode feature` | `docs/PLAN-dark-mode.md` |
| `/cardume-core:plan fix authentication bug` | `docs/PLAN-auth-fix.md` |
| `/cardume-core:plan SaaS dashboard` | `docs/PLAN-saas-dashboard.md` |

---

## Usage

```
/cardume-core:plan e-commerce site with cart
/cardume-core:plan mobile app for fitness tracking
/cardume-core:plan SaaS dashboard with analytics
```
