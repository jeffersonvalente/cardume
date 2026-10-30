---
name: verify
description: "Runs every acceptance criterion of a spec and records evidence in verify.md, listing gaps. Use after implementing a spec, before calling the feature done or opening its PR."
context: fork
background: false
argument-hint: "[path to spec.md]"
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# /cardume-core:verify — Prove it meets the spec

$ARGUMENTS

You run without the conversation history: work only from the spec, tasks and the repository.

1. Read `spec.md` (most recently modified `docs/specs/*/spec.md` if no path) and `tasks.md` if present.
Evidence is a command with its output, a test result, or a file/recording link. A statement without one
of these is not evidence, and an unverified requirement is not a pass.

2. For **each requirement**, execute its acceptance criterion: run the named test or command, call
   the endpoint, or inspect the observable result. Reading code is supporting evidence, not proof.
   For each filled **Property** cell, run its property-based test (the task's `Verify` command). When
   a property fails, record the shrunk counterexample and list three resolutions — fix the code, fix
   the spec (the invariant was wrong), or fix the test (the generator or assertion was wrong) — with
   the one you recommend. Do not pick one yourself: the caller asks the user, and the choice is
   recorded in verify.md (`Resolution:` line) before the fix starts.
3. Run `cardume-checklist .` (add `--url <URL>` when there is a running app) and the project's test
   suite.
4. Write `docs/specs/<slug>/verify.md`:

```markdown
# Verification — <Feature name>

Date: <YYYY-MM-DD> · Commit: <short sha>

| ID | Result | Evidence |
|----|--------|----------|
| R1 | ✅ pass | `pytest tests/test_x.py::test_r1` → 1 passed |
| R2 | ❌ fail | `curl ...` → 500 (expected 200) |
| R3 | ⚠️ not verifiable here | needs prod data; manual check described below |
| R4 (property) | ❌ fail | `pytest tests/test_totals_props.py` → counterexample `lines=[0.1, 0.2]` |

## Property failures
- R4: counterexample … — options: fix code / fix spec / fix test — recommended: … — Resolution: <pending | code | spec | test>

## Checks
- cardume-checklist: <summary>
- Test suite: <passed/failed counts>

## Drift
- <changed behavior> → amend R<n>: ... | new task T<n>: ...

## Gaps and next steps
- ...
```

5. **Write back drift.** Compare the change (`git diff <default-branch>...HEAD --stat` plus the tasks'
   Files lists) with the spec. For each behavior that changed but no requirement describes, or that
   differs from its requirement, propose either a spec amendment (new or edited R-row, listed under
   `## Drift` as "amend R4: ...") or a new task in tasks.md to bring the code back in
   line. Do not apply amendments yourself (this skill runs forked and cannot get approval): list them
   under **Open questions** in your result; the caller applies them after the user approves, because the
   approved spec is the contract.
   An unrecorded difference between spec and code is how specs go stale.
6. **Status.** When every requirement passes and no drift is open, set the spec's
   `Status: implemented` (and, at level 3, the PRD's, once every feature listed in
   `docs/prd/<slug>-architecture.md` has an implemented spec). This skill owns verify.md and the
   spec's status; `qa-gatekeeper` does not write them.
7. Report back (you run in a forked context; the caller relays to the user): how many requirements pass, each failure with its evidence, and the drift
   found with the amendment or task proposed for each. Do not mark the spec done while any requirement
   fails or is unverified without the user's explicit acceptance.
