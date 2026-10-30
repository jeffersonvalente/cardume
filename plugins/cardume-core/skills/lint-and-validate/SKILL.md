---
name: lint-and-validate
description: "Lint, type-check and security-scan commands per ecosystem, with a fix-and-rerun loop. Use after changing code, before calling a task done, or when asked to run static analysis."
allowed-tools: Read Glob Grep Bash
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# Lint and Validate Skill

> Run the appropriate validation tools after each code change, and finish a task only once they pass — lint and type errors found later cost more to trace back.

### Procedures by Ecosystem

#### Node.js / TypeScript
1. **Lint/Fix:** `npm run lint` or `npx eslint "path" --fix`
2. **Types:** `npx tsc --noEmit`
3. **Security:** `npm audit --audit-level=high`

#### Python
1. **Linter (Ruff):** `ruff check "path" --fix` (Fast & Modern)
2. **Security (Bandit):** `bandit -r "path" -ll`
3. **Types (MyPy):** `mypy "path"`

## The Quality Loop
1. **Write/Edit Code**
2. **Run Audit:** `npm run lint && npx tsc --noEmit`
3. **Analyze Report:** Check the "FINAL AUDIT REPORT" section.
4. **Fix & Repeat:** Resolve "FINAL AUDIT" failures before submitting code.

## Error Handling
- If `lint` fails: Fix the style or syntax issues immediately.
- If `tsc` fails: Correct type mismatches before proceeding.
- If no tool is configured: Check the project root for `.eslintrc`, `tsconfig.json`, `pyproject.toml` and suggest creating one.

---
Don't commit code or report it as done until these checks pass.

---

## Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `cardume-lint-runner` | Unified lint check | `cardume-lint-runner <project_path>` |
| `cardume-type-coverage` | Type coverage analysis | `cardume-type-coverage <project_path>` |

