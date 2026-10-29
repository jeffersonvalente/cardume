---
name: review
description: "Reviews a change with parallel specialist reviewers chosen from the touched files, drops low-confidence findings, verifies each remaining one against the code, and flags specs left outdated by the change. Use before merging any non-trivial change or when the user asks for a code review (PR number/URL, branch, or current diff)."
argument-hint: "[PR number/URL | branch | empty for current changes] [--comment]"
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# /cardume-core:review — Multi-reviewer code review

$ARGUMENTS

## 1. Collect the change

- PR number or URL → `gh pr diff <pr>` and `gh pr view <pr> --json title,body,baseRefName,files`.
- Branch name → `git diff <default-branch>...<branch>`.
- Nothing → `git diff <default-branch>...HEAD` plus `git diff HEAD` (uncommitted work).

If the diff is empty, say so and stop. Note the list of changed files and the intent (PR title/body
or recent commit messages). If `docs/standards.md` exists, it is part of the review criteria.

## 2. Pick reviewers

Always:
- **Correctness** — a general-purpose subagent using the `code-review-checklist` skill: logic
  errors, edge cases, error handling, broken contracts with callers of changed code.
- **Tests** — `test-engineer`: are the changed behaviors covered, do tests assert the right thing,
  missing regression tests.

When the files call for it:
- **Security** (`security-auditor`) — auth, input handling, SQL/queries, secrets, dependencies,
  file/network access.
- **Frontend** (`frontend-specialist`) — UI components, styles, accessibility.
- **Data** (`lakehouse-reviewer`) — SQL models, DAGs, BigQuery.
- **Infra** (`iac-reviewer`) — Terraform, Kubernetes manifests, CI pipelines.
- **Standards** — a general-purpose subagent checking the diff against `docs/standards.md`.

Skip reviewers whose plugin is not installed. Small diffs (under ~50 lines) need only Correctness
and Tests unless security-sensitive.

## 3. Run them in parallel

Launch all reviewers in one message. Give each the diff (or the file list plus instructions to read
the diff), the change intent, and this contract:

> Review only the changed code and what it directly affects. Do not edit files. Return at most 10
> findings, each as: `file:line` · severity (blocker / major / minor) · confidence 0–100 ·
> what is wrong · evidence (the code or behavior that proves it) · suggested fix. Skip style
> nits a linter would catch. Return "no findings" if there are none.

## 4. Filter and verify

1. Merge duplicates (same location and root cause) and keep the strongest wording.
2. Drop findings with confidence below 80, and anything that only restates a linter rule.
3. **Verify each remaining finding yourself**: open the code at `file:line`, check the claim against
   the actual code and its callers. Keep it only if you can confirm it; note how. Reviewers are
   wrong often enough that unverified findings cost more trust than they add.

## 4b. Spec and ADR drift

- If the change alters behavior described in a `docs/specs/*/spec.md` or contradicts an accepted ADR
  in `docs/adr/`, report it as a finding ("spec R3 now outdated" / "contradicts ADR-004").
- For every spec whose `## Design` lists files this diff touches, check that the diff also changes
  that spec (an amended requirement, Design note or status), or that the spec still describes the new
  behavior accurately. A code change in a spec's files with no matching spec change is a finding
  ("src/export/csv.ts changed; docs/specs/invoice-export/spec.md not updated").
- Specs marked `superseded` are skipped; check the one that replaced them.

The docs must be updated, or the change reconsidered, in the same PR, because a spec that no longer
matches the code misleads the next agent that reads it.

## 5. Report

Group confirmed findings by severity (blockers first). For each: location, problem, evidence, fix.
End with what was reviewed (reviewers run, files) and a one-line verdict: ready / ready after
fixes / needs rework.

With `--comment` and a PR target: show the comments you would post and ask the user before posting
them with `gh pr review` / `gh pr comment`. Never post without that confirmation.
