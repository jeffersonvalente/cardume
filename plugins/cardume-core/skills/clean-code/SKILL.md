---
name: clean-code
description: Pragmatic coding standards (SRP, DRY, KISS, YAGNI, naming, small functions, no needless comments or over-engineering) plus a pre-edit dependency check, a completion self-check, and which cardume-* verification script each agent runs. Use when writing, editing, or finishing code changes.
allowed-tools: Read Write Edit
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# Clean Code - Pragmatic AI Coding Standards

> Be **concise, direct, and solution-focused**.

---

## Core Principles

| Principle | Rule |
|-----------|------|
| **SRP** | Single Responsibility - each function/class does ONE thing |
| **DRY** | Don't Repeat Yourself - extract duplicates, reuse |
| **KISS** | Keep It Simple - simplest solution that works |
| **YAGNI** | You Aren't Gonna Need It - don't build unused features |
| **Boy Scout** | Leave code cleaner than you found it |

---

## Naming Rules

| Element | Convention |
|---------|------------|
| **Variables** | Reveal intent: `userCount` not `n` |
| **Functions** | Verb + noun: `getUserById()` not `user()` |
| **Booleans** | Question form: `isActive`, `hasPermission`, `canEdit` |
| **Constants** | SCREAMING_SNAKE: `MAX_RETRY_COUNT` |

> **Rule:** If you need a comment to explain a name, rename it.

---

## Function Rules

| Rule | Description |
|------|-------------|
| **Small** | Max 20 lines, ideally 5-10 |
| **One Thing** | Does one thing, does it well |
| **One Level** | One level of abstraction per function |
| **Few Args** | Max 3 arguments, prefer 0-2 |
| **No Side Effects** | Don't mutate inputs unexpectedly |

---

## Code Structure

| Pattern | Apply |
|---------|-------|
| **Guard Clauses** | Early returns for edge cases |
| **Flat > Nested** | Avoid deep nesting (max 2 levels) |
| **Composition** | Small functions composed together |
| **Colocation** | Keep related code close |

---

## AI Coding Style

| Situation | Action |
|-----------|--------|
| User asks for feature | Write it directly |
| User reports bug | Fix it, don't explain |
| No clear requirement | Ask, don't assume |

---

## Anti-Patterns (DON'T)

| ❌ Pattern | ✅ Fix |
|-----------|-------|
| Comment every line | Delete obvious comments |
| Helper for one-liner | Inline the code |
| Factory for 2 objects | Direct instantiation |
| utils.ts with 1 function | Put code where used |
| "First we import..." | Just write code |
| Deep nesting | Guard clauses |
| Magic numbers | Named constants |
| God functions | Split by responsibility |

---

## Before Editing a File, Think First

**Before changing a file, ask yourself:**

| Question | Why |
|----------|-----|
| **What imports this file?** | They might break |
| **What does this file import?** | Interface changes |
| **What tests cover this?** | Tests might fail |
| **Is this a shared component?** | Multiple places affected |

**Quick Check:**
```
File to edit: UserService.ts
└── Who imports this? → UserController.ts, AuthController.ts
└── Do they need changes too? → Check function signatures
```

> Edit the file and all dependent files in the same task, so you don't leave broken imports or half-applied interface changes behind.

---

## Summary

| Do | Don't |
|----|-------|
| Write code directly | Write tutorials |
| Let code self-document | Add obvious comments |
| Fix bugs immediately | Explain the fix first |
| Inline small things | Create unnecessary files |
| Name things clearly | Use abbreviations |
| Keep functions small | Write 100+ line functions |

> **Remember: The user wants working code, not a programming lesson.**

---

## Self-Check Before Completing

**Before saying "task complete", verify:**

| Check | Question |
|-------|----------|
| ✅ **Goal met?** | Did I do exactly what user asked? |
| ✅ **Files edited?** | Did I modify all necessary files? |
| ✅ **Code works?** | Did I test/verify the change? |
| ✅ **No errors?** | Lint and TypeScript pass? |
| ✅ **Nothing forgotten?** | Any edge cases missed? |

> If any check fails, fix it before reporting completion.

---

## Verification Scripts

After completing work, each agent runs the scripts for its own domain (plus the "any agent" checks), so results land with the agent that can act on them.

### Agent → Script Mapping

| Agent | Script | Command |
|-------|--------|---------|
| **frontend-specialist** | UX Audit | `cardume-ux-audit .` |
| **frontend-specialist** | A11y Check | `cardume-accessibility-checker .` |
| **backend-specialist** | API Validator | `cardume-api-validator .` |
| **mobile-developer** | Mobile Audit | `cardume-mobile-audit .` |
| **database-architect** | Schema Validate | `cardume-schema-validator .` |
| **security-auditor** | Security Scan | `cardume-security-scan .` |
| **seo-specialist** | SEO Check | `cardume-seo-checker .` |
| **seo-specialist** | GEO Check | `cardume-geo-checker .` |
| **performance-optimizer** | Lighthouse | `cardume-lighthouse-audit <url>` |
| **test-engineer** | Test Runner | `cardume-test-runner .` |
| **test-engineer** | Playwright | `cardume-playwright-runner <url>` |
| **Any agent** | Lint Check | `cardume-lint-runner .` |
| **Any agent** | Type Coverage | `cardume-type-coverage .` |
| **Any agent** | i18n Check | `cardume-i18n-checker .` |

> ❌ **Wrong:** `test-engineer` running `cardume-ux-audit`
> ✅ **Correct:** `frontend-specialist` running `cardume-ux-audit`

---

### Script Output Handling (Read → Summarize → Ask)

When running a validation script:

1. **Run the script** and capture all output
2. **Parse the output** - identify errors, warnings, and passes
3. **Summarize to user** in this format:

```markdown
## Script Results: [script name]

### ❌ Errors Found (X items)
- [File:Line] Error description 1
- [File:Line] Error description 2

### ⚠️ Warnings (Y items)
- [File:Line] Warning description

### ✅ Passed (Z items)
- Check 1 passed
- Check 2 passed

**Should I fix the X errors?**
```

4. **Wait for user confirmation** before fixing
5. **After fixing** → Re-run script to confirm

Running a script and ignoring its output means the task isn't verified. Don't auto-fix script findings without asking, since some findings are intentional or out of scope. The order is: read the output → summarize → ask → then fix.

