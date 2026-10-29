---
name: gate
description: "Runs a phase or milestone gate: checks every acceptance criterion of the PRD/spec against executed evidence, writes docs/gates/GATE-<id>.md with a pass/fail table and an APPROVE/REJECT recommendation, and leaves the decision to the user. Use when a level-3 phase or milestone ends, or when the user asks whether something is ready to approve or release."
---

# Gate — evidence-based approval of a phase

The gate is the checkpoint between "built" and "approved/released". The agent prepares the decision;
**the user decides**. Gates are required at the end of a level-3 phase or milestone; at level 2 they
are optional, run on request.

**Who runs the checks.** When the main session runs this skill, it delegates steps 2–3 to the
`qa-gatekeeper` agent, so the verifier is not the one who built the work. When `qa-gatekeeper` runs
it (the skill is preloaded there), it executes the checks directly — it does not delegate to itself.

## 1. Find the criteria

- Level 3: the PRD for the phase (`docs/prd/`) and the specs under it.
- Level 2: the feature's `docs/specs/<slug>/spec.md` requirements and its `verify.md` if it exists.
- Principles: the `## Principles (manual)` section of `docs/standards.md`, plus the rest of that file
  as conventions. Do not hunt for other principle files; use a project `SPEC.md` or similar only when
  the user points to it.
- Drift: the `## Drift` section of each `verify.md` and the drift findings of the last `review`
  (`review` skill, step 4b). Open drift — code that no longer matches its approved spec — is a ❌,
  because the gate would otherwise approve criteria that describe different software.
- Gate id: `PHASE-N` for phased projects, otherwise the spec slug or version (`GATE-v1.2`).

If there is no PRD or spec, say so and stop: a gate without written criteria is an opinion.

## 2. Verify

The main session gives `qa-gatekeeper` the criteria file(s) and the scope (branch, PR list,
version). The gatekeeper runs the checks itself — tests, validators, builds, scripts,
`cardume-checklist .` — and pastes the relevant output. It reads `verify.md` as input but does not
edit it or any spec status; those belong to the `verify` skill.

Evidence rules:
- Evidence is a command with its output, a test name with its result, or a link to a file/recording in
  the repo. A statement without one of these is not evidence.
- Each criterion is ✅ (evidence shows it passes), ❌ (evidence shows it fails) or ⚠️ (could not be
  verified here — say what is needed).
- There is no "approved with caveats": any ❌ or unresolved ⚠️ means REJECT, with the list of what is missing.

## 3. Write `docs/gates/GATE-<id>.md`

```markdown
# Gate <id> — <phase/feature name>

Date: <YYYY-MM-DD> · Scope: <branch / PRs / version> · Verified by: qa-gatekeeper

## Criteria
| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| C1 | ... | ✅ | `pnpm test -- invoice` → 12 passed |

## Standards and principles
- <each item of Principles (manual) and each standards section that applies> — ✅/❌ — how it was checked

## Spec drift
- <spec> — in sync ✅ / drift ❌ (<what differs>)

## Recommendation
APPROVE | REJECT — <one paragraph; for REJECT, the exact list of what is missing>

## Decision
<!-- Left blank for the user: APPROVED or REJECTED, date, notes. -->
```

## 4. Hand over

Show the user the criteria table and the recommendation, and ask for the decision (or, as a
subagent, return the recommendation and the decision request under **Open questions**; the caller
asks the user). The main session writes the user's answer under `## Decision`, only when they give it. After an approved
gate, the next steps are the next phase's PRD or a release: the `release-manager` agent (or the user
runs `/cardume-core:release`).
