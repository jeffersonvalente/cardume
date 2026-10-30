---
name: implement
description: "Builds an approved tasks.md one task at a time, with a fresh subagent, a verification command and a separate reviewer. Use to implement level-2/3 work once its tasks are approved."
argument-hint: "[path to tasks.md] [task id to start from]"
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# /cardume-core:implement — Build task by task

$ARGUMENTS

Read `tasks.md` and its `spec.md`. If no path was given, use the most recently modified
`docs/specs/*/tasks.md`.

## Before starting

Check both status lines. Start only when tasks.md says `Status: approved` and its spec says
`approved` (or `implemented`, for follow-up tasks). Otherwise stop and tell the user exactly what is
missing — e.g. "spec.md is draft with 2 [NEEDS CLARIFICATION] markers; tasks.md has no approval" —
and the command that fixes it. Building on unapproved plans is the most common source of rework.

Then loop over unchecked tasks in order, respecting `Depends on`.

## Per task

1. **Delegate to a fresh subagent** (the task's `Agent`). Give it only what it needs: the task block,
   the requirement rows it covers from spec.md, the relevant Design notes and the files list. Fresh
   context per task keeps earlier mistakes from leaking forward.
   Tasks with no dependency between them may run in parallel; give each its own worktree
   (`isolation: worktree`) when they touch overlapping files.
2. **Test first for logic.** For tasks that change logic, the subagent adds or names the test for the
   requirement, runs it before the fix and shows it failing, then shows it passing after. A test that
   never failed may not test the change.
3. **Verify.** Run the task's `Verify` command yourself and read the output. A task is done only
   when the command shows the expected result — not when the subagent says so.
4. **Independent review.** Send the diff, the task block and its requirement rows to a separate
   reviewer subagent that did not write the code: `test-engineer` for test-only tasks, otherwise a
   general-purpose subagent using the `code-review-checklist` skill. Ask for two verdicts:
   - **Spec compliance:** does it do what the requirement rows say, nothing more, nothing missing?
   - **Code quality:** correctness, tests, `docs/standards.md` conventions.
   Each verdict is pass or fail with specific findings (`file:line`, problem, fix).
5. **Fix loop.** On a fail, send the findings back to the implementing subagent and review again.
   Cap it at 2 rounds; if the task still fails, stop and show the user the findings and what was tried.
6. **Record.** Tick the checkbox and append under the task:
   `  - Evidence: <command> → <result summary>` and, for logic tasks,
   `  - Test-first: <test> failed before (<message>) → passes after`.

## When something goes wrong

- Verification fails twice for the same reason → stop the loop, show the user the failure and what
  was tried; the task or the spec probably needs adjusting.
- The task reveals the spec is wrong or incomplete → stop and propose the spec change; do not
  silently implement something different from the approved requirement.

## Finish

When all tasks are ticked, run `cardume-checklist .` and a final whole-branch review with the
`review` skill (`/cardume-core:review`), since per-task reviews miss problems between tasks. Report
both results, then suggest `/cardume-core:verify docs/specs/<slug>/spec.md`.
