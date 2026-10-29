---
name: adr
description: "Records an Architecture Decision Record in docs/adr/ (MADR-style: drivers, options, decision, consequences, confirmation) and keeps the index current. Use when a significant technical decision is made or changed, at any task size: choosing a database, framework, library, integration pattern, data model, infra component, or accepting a notable trade-off."
allowed-tools: Read Glob Grep Write Edit
---

# ADR — Architecture Decision Records

Decisions are the documentation that goes missing first: the code shows *what* was built, never
*why* the alternative lost. Write an ADR at the moment the decision is made, even inside a small task.

## When it is an ADR

Write one when the decision is expensive to reverse or someone will later ask "why is it like this?":
- choosing or replacing a database, framework, runtime, major library, cloud service
- integration and communication patterns (sync vs queue, REST vs events, polling vs webhook)
- data model and ownership choices, multi-tenancy, consistency model
- security/compliance posture (auth approach, where personal data lives)
- deliberately accepting a trade-off or tech debt ("we skip X for now because Y")

Not an ADR: naming, formatting, choosing between two equivalent ways to write the same code, anything
a linter or `docs/standards.md` already decides.

## How

1. `ls docs/adr/` — find the next number (`ADR-001`, `ADR-002`, …). Create the folder if missing.
2. Check for an existing ADR on the same topic, including rejected ones: a `rejected` ADR records
   why an option lost, so it should stop the same debate from restarting. Changing a past decision
   means a **new** ADR that supersedes it; set the old one's status to `superseded by ADR-NNN`.
   Never rewrite history.
3. Write `docs/adr/ADR-NNN-short-slug.md` (sections follow MADR 4, https://adr.github.io/madr/):

```markdown
# ADR-NNN: <decision as a short statement>

- Status: proposed | rejected | accepted | deprecated | superseded by ADR-XXX
- Date: <YYYY-MM-DD>
- Deciders: <who approved — the user, or "delegated" when the agent decided within its authority>
- Consulted: <optional — people whose input was sought>
- Informed: <optional — people who need to know>
- Related: <spec/PRD/task/PR links>

## Context
<The forces at play: requirements, constraints, what hurts today. 3–8 lines.>

## Decision drivers
- <quality, constraint or concern that the choice must satisfy, e.g. "confirmations < 1 min">

## Options considered
1. **<Option A>** — pros / cons against the drivers
2. **<Option B>** — pros / cons against the drivers
3. **Do nothing / defer** — when relevant

## Decision
<What was chosen and the main reason, in 2–4 sentences. Confidence: high | medium | low.>

## Consequences
- Positive: …
- Negative / accepted costs: …

## Confirmation and follow-ups
- Confirmation: <how compliance is checked — a test, fitness function, lint rule, or review step>
- Follow-ups: <tasks this creates>
- Revisit when: <the observation that reopens it — required when confidence is low>
```

4. Update `docs/adr/README.md` (create it if missing): one table row per ADR — number, title, status,
   date.
5. Link the ADR from the PR description that implements it, and, where a reader of the code would
   otherwise "fix" the choice, from a short comment at the decision point
   (`// See docs/adr/ADR-007-webhooks.md`).

## Status and who decides

- If the user decided, or the decision is reversible and inside the task's scope, mark `accepted`
  and note "delegated" when you made the call.
- If it changes the project's spec/standards, affects other teams, or costs real money, mark
  `proposed` and ask the user (or, as a subagent, return the question under **Open questions**)
  before building on it.
- An option that was seriously considered and turned down can get its own `rejected` ADR when the
  question is likely to come back.
- Low confidence is fine to record; give it a concrete revisit trigger so the decision gets
  re-examined on evidence rather than by whoever objects next.

Keep it short — one page. Detailed trade-off analysis belongs to the `architecture` skill
(`trade-off-analysis.md`); link to it instead of pasting it.
