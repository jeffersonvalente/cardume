---
name: plan-writing
description: Principles for writing short, specific plans of 5-10 verifiable tasks with dependencies, project-specific verification scripts, and a final verification phase. Use when breaking down a new project, feature, complex bug fix, or multi-file refactor into a plan file.
allowed-tools: Read Glob Grep
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# Plan Writing

> Source: obra/superpowers

## Overview
This skill provides a framework for breaking down work into clear, actionable tasks with verification criteria.

## Task Breakdown Principles

### 1. Small, Focused Tasks
- Each task should take 2-5 minutes
- One clear outcome per task
- Independently verifiable

### 2. Clear Verification
- How do you know it's done?
- What can you check/test?
- What's the expected output?

### 3. Logical Ordering
- Dependencies identified
- Parallel work where possible
- Critical path highlighted
- **Phase X: Verification is always last**

### 4. Dynamic Naming in `docs/`
- Plan files are saved as `docs/PLAN-{task-slug}.md`
- Name derived from task (e.g., "add auth" → `docs/PLAN-auth-feature.md`)
- Not inside `.claude/` or temp folders, where the user and other agents won't find them

## Planning Principles (Not Templates)

Write each plan for its task rather than filling a fixed template; generic plans hide the decisions that matter.

### Principle 1: Keep It Short

| ❌ Wrong | ✅ Right |
|----------|----------|
| 50 tasks with sub-sub-tasks | 5-10 clear tasks max |
| Every micro-step listed | Only actionable items |
| Verbose descriptions | One-line per task |

> **Rule:** If plan is longer than 1 page, it's too long. Simplify.

---

### Principle 2: Be Specific, Not Generic

| ❌ Wrong | ✅ Right |
|----------|----------|
| "Set up project" | "Run `npx create-next-app`" |
| "Add authentication" | "Install next-auth, create `/api/auth/[...nextauth].ts`" |
| "Style the UI" | "Add Tailwind classes to `Header.tsx`" |

> **Rule:** Each task should have a clear, verifiable outcome.

---

### Principle 3: Dynamic Content Based on Project Type

**For a new project:**
- What tech stack? (decide first)
- What's the MVP? (minimal features)
- What's the file structure?

**For a feature addition:**
- Which files are affected?
- What dependencies needed?
- How to verify it works?

**For a bug fix:**
- What's the root cause?
- What file/line to change?
- How to test the fix?

---

### Principle 4: Scripts Are Project-Specific

Choose verification commands for the project type instead of pasting the full list into every plan.

| Project Type | Relevant Scripts |
|--------------|------------------|
| Frontend/React | `cardume-ux-audit`, `cardume-accessibility-checker` |
| Backend/API | `cardume-api-validator`, `cardume-security-scan` |
| Mobile | `cardume-mobile-audit` |
| Database | `cardume-schema-validator` |
| Full-stack | Mix of above based on what you touched |

**Wrong:** Adding all scripts to every plan
**Right:** Only scripts relevant to this task

---

### Principle 5: Verification is Simple

| ❌ Wrong | ✅ Right |
|----------|----------|
| "Verify the component works correctly" | "Run `npm run dev`, click button, see toast" |
| "Test the API" | "curl localhost:3000/api/users returns 200" |
| "Check styles" | "Open browser, verify dark mode toggle works" |

---

## Plan Structure (Flexible, Not Fixed!)

```
# [Task Name]

## Goal
One sentence: What are we building/fixing?

## Tasks
- [ ] Task 1: [Specific action] → Verify: [How to check]
- [ ] Task 2: [Specific action] → Verify: [How to check]
- [ ] Task 3: [Specific action] → Verify: [How to check]

## Done When
- [ ] [Main success criteria]

## Notes
[Any important considerations]
```

> **That's it.** No phases, no sub-sections unless truly needed.
> Keep it minimal. Add complexity only when required.

---

## Best Practices (Quick Reference)

1. **Start with goal** - What are we building/fixing?
2. **Max 10 tasks** - If more, break into multiple plans
3. **Each task verifiable** - Clear "done" criteria
4. **Project-specific** - No copy-paste templates
5. **Update as you go** - Mark `[x]` when complete

---

## When to Use

- New project from scratch
- Adding a feature
- Fixing a bug (if complex)
- Refactoring multiple files
