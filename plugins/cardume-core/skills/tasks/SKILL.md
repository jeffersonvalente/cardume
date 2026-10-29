---
name: tasks
description: "Breaks an approved spec into small ordered tasks in docs/specs/<slug>/tasks.md, each with requirement IDs, an owner agent/lane, contracts it depends on and a verification command; --issues also opens GitHub issues after confirmation. Use after a spec is approved, before implementing level-2/3 work."
argument-hint: "[path to spec.md] [--issues]"
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# /cardume-core:tasks — Plan the work

$ARGUMENTS

**Who writes tasks.md.** At level 2, whoever runs this skill (usually the main session). At level 3,
`software-architect` writes it for each feature once that feature's spec is approved, using these
rules and the contracts in `docs/prd/<slug>-architecture.md`. The input is always a spec: a PRD is
never broken into tasks directly — each feature in it gets a spec first (`spec` skill; its quick spec
when speed matters).

1. Read the spec. If no path was given, use the most recently modified `docs/specs/*/spec.md`.
   If its status is not `approved`, show the open questions and stop — tasks built on an
   unapproved spec get redone. (Quick spec, see the `spec` skill: spec and tasks are written in one
   pass and approved together.) If you were given a PRD, stop and name the features that need a spec.
2. Read the files listed in the spec's Design section to ground the breakdown in the real code.
3. Write `docs/specs/<slug>/tasks.md`:

```markdown
# Tasks — <Feature name>

Spec: ./spec.md
Status: draft | approved

- [ ] T1 — <imperative title>
  - Requirements: R1, R3
  - Lane / agent: backend / backend-specialist
  - Contracts: <types/schema/fixture this task uses or defines>
  - Files: src/..., tests/...
  - Steps: <2–5 short concrete steps, each naming the exact file it touches>
  - Verify: `<command that proves it>` (test name, curl, script) + expected result
  - Depends on: —
  - Issue: #<n> (only with --issues)
```

## Breakdown rules

- **Small.** A task is one focused commit a fresh subagent can finish and verify in one session,
  written as short concrete steps with exact file paths. Split anything that touches unrelated areas.
- **Contracts first.** When tasks in different lanes (backend, frontend, data, infra) meet, add an
  early task that defines the contract between them (types, API/JSON schema, event format) and a
  fixture with sample data. Later tasks depend on the contract, never on "wait for the other task",
  so lanes can run in parallel. At level 3, reuse the contracts already defined in the architecture file.
- **Owner lane** per task (`Lane: backend | frontend | data | infra | content | qa`) next to the agent.
- **Test first where it fits.** For logic, the first task (or first step of a task) adds a failing
  test for the requirement; the implementation makes it pass.
- **Properties get a task.** Each filled **Property** cell in the spec gets a task (or a step) that
  writes a property-based test with the project's library (fast-check, Hypothesis, jqwik, proptest);
  its `Verify` runs that test.
- **Every requirement is covered.** End the file with a coverage table `R-ID → tasks` (mark property
  tests, e.g. `R2 → T3, T5 (property)`); a requirement with no task is a gap to fix now.
- **Order by dependency**, then by risk (riskiest first, so surprises come early).
- **Agent** is the Cardume agent best suited (see `intelligent-routing`); use `general-purpose`
  when none fits.
- **Verify** must be executable — never "check it works".
- **Decisions** made while breaking down (technology, pattern, trade-off) go into an ADR via the `adr` skill.

## Analyze before approval

Read spec.md and tasks.md side by side once and fix what fails, because gaps found here cost minutes
and gaps found during implement cost a redo:

- Every requirement (R-ID) and every property is covered by at least one task.
- No task lacks a requirement — work without one is scope creep or a missing requirement; add the
  requirement to the spec (and tell the user) or drop the task.
- Every contract is defined by an earlier task than the first task that uses it.
- No unresolved `[NEEDS CLARIFICATION]` remains in the spec.

4. Show the user the task list, the coverage table and the analyze result, and ask for approval (or,
   as a subagent, return them under **Open questions** for the caller to get it). When approved, set
   `Status: approved`. Next step: `/cardume-core:implement docs/specs/<slug>/tasks.md`.

## Optional: `--issues` (GitHub issues)

Only when `--issues` was passed or the user asks for it — never by default, because creating issues
is visible to other people. After tasks.md is approved:

1. Check `gh auth status` and that the repo has a GitHub remote; if not, say so and stop.
2. Prepare one `gh issue create` command per unchecked task: `--title "<slug> T<n>: <title>"`,
   `--body` with the requirement IDs, the Verify command, the dependencies and a link back to
   `docs/specs/<slug>/tasks.md`, and `--label` for the lane (only labels that exist — check with
   `gh label list`).
3. Show the commands and ask the user to confirm (as a subagent, return them under **Open
   questions** and stop). Run them only after a yes.
4. Write each issue number back into its task (`- Issue: #<n>`), so tasks.md stays the source of truth.
