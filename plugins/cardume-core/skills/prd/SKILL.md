---
name: prd
description: "Writes a PRD in docs/prd/ with metrics, acceptance criteria, no-gos, risks and blockers. Use for level-3 work: a new system or product phase, or when the user asks for a PRD; feature-level work uses spec."
allowed-tools: Read Glob Grep Write Edit
---

# PRD — Product requirements for a product or phase

A PRD answers *what* and *why* for a whole product or phase, with acceptance criteria someone can
check without asking the author. Features inside it get their own spec later (`spec` skill).

## Before writing

1. Read what exists: README, `docs/standards.md`, previous PRDs in `docs/prd/`, the last gate report
   in `docs/gates/` (the last approved gate tells which phase comes next), research notes.
2. Ask the user what you cannot infer (or, as a subagent, return the questions under **Open
   questions** and stop; the caller asks the user): who the users are, the outcome that makes this
   phase a success, hard constraints (deadline, budget, compliance, platforms), and what is
   explicitly out. In the main conversation, use the `AskUserQuestion` tool — multiple choice, the
   recommended option first, free text always available. Follow the `brainstorming` skill when the
   idea is still fuzzy.

## Write `docs/prd/<slug>.md` (or `docs/prd/PHASE-N.md` for phased projects)

```markdown
# PRD — <Product or phase name>

Status: draft | approved | implemented | superseded (by <link>) · Date: <YYYY-MM-DD> · Owner: <user>

## Problem and evidence
<Who has which problem today and how we know: data, support tickets, interviews, observed behavior.
If there is no evidence yet, say so — that is a value risk below.>

## Objective
<One sentence: the outcome this delivers.>

## Success metrics
| Metric | Baseline | Target | When measured |
|--------|----------|--------|---------------|
| <outcome, e.g. invoices paid within 30 days> | 61% | 75% | 60 days after release |

## Appetite
<How much time/effort this phase is worth (e.g. "2 weeks, one developer"). When the work outgrows
it, cut scope rather than extend the budget.>

## User stories
- As a <user>, I want <capability> so that <benefit>. (justification: <link or reason>)

## Acceptance criteria
| ID | Criterion | How to verify | Who verifies |
|----|-----------|---------------|--------------|
| C1 | <observable result with a number when it is about speed/size/quality> | <command, test, or written script step> | QA / user / automated |

## Out of scope
- <explicitly not in this phase, and where it goes instead>

## Rabbit holes and no-gos
- <tempting detail or edge case that would blow the appetite, and the decision taken to avoid it>

## Risks
- [value | usability | feasibility | viability] <risk> — early warning sign: <concrete signal> — mitigation: <…>

## Human test script
<Required when real users must validate the phase: step by step, what to observe, what to ask afterwards.>

## Blockers
- <decisions only the user can make; the PRD stays draft while this list is not empty>
```

## Rules for criteria

- Every criterion is checkable by a command/test or by a written script someone can follow.
  Words like "intuitive", "fast", "works well" need a number or a test, or they are not criteria.
- One behavior per criterion; IDs are stable so specs, tasks and gate reports can reference them.
- A phase PRD does not pull in deliverables from the next phase — note them under Out of scope.
- Success metrics are outcomes measured after release (adoption, conversion, time saved); acceptance
  criteria are what the gate checks before release. Keep them apart, because shipping every criterion
  does not prove the outcome happened.
- Tag each risk with its type — value (will they want it), usability (can they use it), feasibility
  (can we build it), viability (does it work for the business: cost, legal, support) — so the
  riskiest kind gets tested first.

## After

Show the user the criteria table, the out-of-scope list and the blockers, and ask for approval (or,
as a subagent, return them under **Open questions**). When approved: set `Status: approved`
(`verify` later sets `implemented`; a replaced PRD becomes `superseded`), record significant
product/technical decisions with the `adr` skill, and hand the PRD to `software-architect`, which
writes contracts, ADRs and the feature list in `docs/prd/<slug>-architecture.md`. Every feature
then gets its own spec (`spec` skill; quick spec for small ones) — a PRD is never broken into tasks
directly.
