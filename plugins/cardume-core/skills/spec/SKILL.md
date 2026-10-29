---
name: spec
description: "Specifies a feature before building it: asks the questions that change the design, then writes docs/specs/<slug>/spec.md with testable EARS requirements, acceptance criteria, design notes and non-goals. Use for level-2 work (a new feature, or a change to more than ~5 files or more than one area; gate optional, on request) before any code is written; not for level 0–1 edits."
argument-hint: "[feature or change to specify]"
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# /cardume-core:spec — Specify before building

$ARGUMENTS

Use this flow for features where getting the requirements wrong is expensive (more than ~5 files or
more than one area, new modules, anything with users or data at stake). When speed matters, use the
quick spec (section 4) rather than skipping the spec. At level 3, each feature listed in
`docs/prd/<slug>-architecture.md` gets its own spec.

## 1. Understand

1. Read the parts of the codebase the request touches (entry points, data models, existing tests)
   so questions are informed rather than generic.
2. Ask the questions whose answers would change the design — purpose, who uses it, scope edges,
   error and empty states, performance or compliance constraints. Group them; 3–7 questions is
   typical. Follow the `brainstorming` skill when the problem itself is still fuzzy.
   - In the main conversation, ask with the `AskUserQuestion` tool: multiple choice, your
     recommended option first and labelled "(recommended)", free text always available — choices
     are faster to answer and show your reasoning.
   - As a subagent (no user to ask), return them under **Open questions** in your report and stop;
     the caller asks the user.
3. Wait for answers. If the user says "you decide", state the assumption you are making in the spec.

## 2. Write `docs/specs/<slug>/spec.md`

`<slug>`: 2–4 lowercase words from the request, hyphen-separated (e.g. `invoice-export`).

Keep it short: the requirement table comes first and the whole spec fits on about one screen.
Detail that does not change what gets tested goes to Design notes or an ADR (`adr` skill), because a
long spec stops being read and starts drifting from the code.

```markdown
# <Feature name>

Status: draft | approved | implemented | superseded (by <link>)
Date: <YYYY-MM-DD>
PRD: <../../prd/<slug>.md — C-IDs covered: C1, C3> (level 3 only)

## Problem
<Who has which problem today, in 2–4 sentences.>

## Requirements
| ID | Requirement | Acceptance criteria (how we will check it) | Property (optional) |
|----|-------------|--------------------------------------------|---------------------|
| R1 | WHEN ... THE <component> SHALL ... | Test/command/observable result | for all valid invoices, total = sum of lines |

## Scope
- In: ...
- Out (non-goals): ...

## Design
- Components and files that change, and why. (Review uses this list to spot drift.)
- Data model / API changes (shapes, migrations).
- Alternatives considered and why they lost (one line each).

## Risks and open questions
- [NEEDS CLARIFICATION: <question>] ...

## Assumptions
- ...
```

### EARS phrasing

Each requirement is testable, has an ID and uses one of these patterns. Name the actual component
(`THE export service`, `THE invoice form`) when that is clearer than `THE SYSTEM`.

- Ubiquitous: THE <system> SHALL <behavior>.
- Event: WHEN <trigger> THE <system> SHALL <behavior>.
- State: WHILE <state> THE <system> SHALL <behavior>.
- Unwanted: IF <condition> THEN THE <system> SHALL <behavior>.
- Optional feature: WHERE <feature is included> THE <system> SHALL <behavior>.
- Combined: WHILE <state> WHEN <trigger> THE <system> SHALL <behavior> — e.g. "WHILE the user is
  offline WHEN they save an invoice THE invoice form SHALL queue it and show 'pending sync'."

Rules for good requirements: one behavior per row; observable from outside the code; no
implementation detail in the requirement column (that goes in Design); every requirement has an
acceptance criterion someone could execute.

**Property column (optional).** Fill it only for an invariant worth property-testing — a rule that
must hold for all inputs, such as totals, parsers and serializers (decode(encode(x)) = x),
idempotency or ordering. Generated inputs find edge cases example tests miss. Tooling: fast-check
(JS/TS), Hypothesis (Python), jqwik (Java), proptest (Rust). `tasks` turns each property into a test
task and `verify` runs it.

Mark anything you do not know as `[NEEDS CLARIFICATION: <question>]` in place, instead of guessing;
a guess written as a requirement looks settled and gets built.

## 3. Self-check

Before asking for approval, read the spec once against this list and fix what fails:

- No vague adjectives ("fast", "simple", "intuitive", "robust") without a number or a test.
- Every requirement has an executable acceptance criterion.
- Error, empty and limit states are covered (bad input, nothing to show, too much data, no permission).
- No conflict with the `## Principles (manual)` section of `docs/standards.md` or with accepted ADRs in
  `docs/adr/` (also a project `SPEC.md` or principles file if the user points to one). If it conflicts,
  say so and propose an ADR instead of quietly overriding the principle.
- Every `[NEEDS CLARIFICATION]` is listed under Risks and open questions.

## 4. Gate

Show the user the requirement table, the open questions and any `[NEEDS CLARIFICATION]` markers, and
ask for approval or changes (or, as a subagent, return them under **Open questions**). A spec with
unresolved markers stays `draft`. When approved, set `Status: approved` and name the next step:
`/cardume-core:tasks docs/specs/<slug>/spec.md` at level 2; at level 3, `software-architect` writes
the tasks.md with the `tasks` skill.

**Quick spec:** when the user wants level-2 work fast, write spec.md and tasks.md (`tasks` skill) in
one pass and ask for a single approval that covers both; set both to `approved` on yes.

**Later statuses:** `verify` sets `implemented` when every requirement passes. When a newer spec
replaces this one, set `superseded (by <link>)` rather than deleting it, so history stays traceable.
