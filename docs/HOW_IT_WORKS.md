# How Cardume works

This page explains the working rules that `/cardume-core:setup` installs in a project's `CLAUDE.md`,
and what happens between your request and "done". The rules live in
[`plugins/cardume-core/templates/CLAUDE.md`](../plugins/cardume-core/templates/CLAUDE.md); the hooks
that enforce part of them are described in [SAFETY.md](SAFETY.md).

- [Routing](#routing)
- [Work levels](#work-levels)
- [Rules at any level](#rules-at-any-level)
- [Feature flow (level 2)](#feature-flow-level-2)
- [Delivery chain (level 3)](#delivery-chain-level-3)
- [Project standards](#project-standards)
- [Who does what in visual work](#who-does-what-in-visual-work)
- [Context and cost](#context-and-cost)

## Routing

You describe the task; you do not pick an agent. Claude Code already chooses agents and skills by
their descriptions, and the Cardume block in `CLAUDE.md` tells Claude to classify the work level
first and then choose the specialist whose description matches. The
[`routing_reminder`](../plugins/cardume-core/hooks/routing_reminder.py) hook repeats this before
each request, because a rule read once at the start of a session is easy to skip. With several
matches, process skills come before implementation skills, and Claude says in one line which one it
is using.
When the choice is not obvious
(a vague request, or one that spans several areas), Claude consults the
[`intelligent-routing`](../plugins/cardume-core/skills/intelligent-routing/SKILL.md) table, which maps
every area to its agent. Work across several areas goes to the `orchestrator` agent once there is an
approved plan. If you name an agent (`@backend-specialist`, "use the debugger"), that wins.

The validator checks that every agent appears in the routing table, so a new agent cannot be
forgotten there.

## Work levels

Before acting, Claude classifies the request and says so in one line (for example, "Level 2 —
feature: …").

| Level | When | What happens |
| --- | --- | --- |
| **0 — Trivial** | typo, copy change, config value, question, one-line fix | Done directly, no document. |
| **1 — Small** | bug fix or small change: up to ~5 files in one area | A **mini-spec** in the PR or final report: problem, 2–3 acceptance criteria and how it was verified. A bug fix starts with a test that reproduces it, and lists the behavior that must not change. |
| **2 — Feature** | new feature, or more than ~5 files or more than one area | `spec` → `tasks` → `implement` → `verify` (in `docs/specs/<slug>/`) → `review`. Gate only on request. In a hurry: quick spec (spec and tasks in one approval). |
| **3 — Product, new project or phase** | new system, new product phase, multi-team work | PRD → architecture → each feature through the level-2 flow → gate → release (see the [delivery chain](#delivery-chain-level-3)). |

**Risk raises the level.** Authentication or permissions, money, data migration or deletion, public
APIs or contracts, and anything irreversible are at least level 1, and level 2 when they touch more
than one file or area. If a task grows mid-way, Claude stops and reclassifies.

**You are in charge.** "Just do it" skips the process; "I want a full spec" forces the whole flow.

The classification is an instruction to the model, not a check. Three things back it up: the
`routing_reminder` hook repeats it before each request, the `spec_reminder` hook warns you once when
a change reaches 8+ files or 400+ lines with no spec, PRD or ADR, and the `levels` eval cases check
that a risky "one-line" permission change is not treated as level 0 (see [EVALS.md](EVALS.md)).

## Rules at any level

- **ADRs are recorded as you go.** Every relevant technical decision (database, framework, library,
  integration pattern, data model, accepted trade-off) becomes a record in `docs/adr/`, in MADR
  format, through the [`adr`](../plugins/cardume-core/skills/adr/SKILL.md) skill.
- **Whoever builds does not approve.** Verification runs in a separate context and only accepts
  evidence: a command with its output, a test, a file. The builder's word does not count. The
  `verify` skill runs forked (`context: fork`, without the conversation history), and the
  `qa-gatekeeper` agent is limited by a hook to writing reports.
- **When you are called:**
  - gate decisions;
  - changes to an approved spec, PRD or standards;
  - blockers listed in the PRD;
  - irreversible or public actions (release, tag, publish, delete, posts).

  Claude decides the rest, records the reason and moves on. Open questions come batched rather
  than one at a time; the `spec` and `prd` skills ask them as multiple choice with a recommended
  option. Subagents never talk to you directly: they return their
  questions to Claude under **Open questions**, and Claude asks you and resumes the work.

## Feature flow (level 2)

| Step | Skill | Produces | Gate |
| --- | --- | --- | --- |
| 1 | `spec` | `spec.md`: EARS requirements (`WHEN … THE SYSTEM SHALL …`) with acceptance criteria; open points marked `[NEEDS CLARIFICATION]` | you approve the spec |
| 2 | `tasks` | `tasks.md`: commit-sized tasks, each with requirement, owner and verification command, plus the coverage table | you approve the tasks |
| 3 | `implement` | code: a fresh subagent per task, a failing test before and a passing one after, an independent reviewer per task | starts only with approved tasks |
| 4 | `verify` | `verify.md`: each requirement with the evidence that was executed; detects where the code drifted from the spec | closes only when everything passes |
| 5 | `review` | parallel reviewers (correctness, tests and, depending on the files, security, frontend, data, infra); each finding is checked against the code | — |

Optional:

- **A Property column in the spec**, with invariants ("for every valid input, total = sum of the
  lines") that become property-based tests (fast-check, Hypothesis, jqwik, proptest).
- **`/cardume-core:tasks --issues`**, which opens GitHub issues from the tasks, only after you
  confirm.

## Delivery chain (level 3)

```text
PRD (product-manager): problem, success metrics, verifiable criteria, risks, appetite
 → software-architect: contracts and fixtures first, ADRs, feature list
   (docs/prd/<slug>-architecture.md)
   → for each feature: approved spec → software-architect writes tasks.md
     → agents of each lane in parallel (backend, frontend, data, infra…)
       → verify → review
         → qa-gatekeeper: checks every PRD criterion with evidence and writes
           docs/gates/GATE-<id>.md with a recommendation
           → you approve or reject the gate
             → release-manager: CHANGELOG, version, tag, release and post
               (publishes only after you confirm)
```

## Project standards

`/cardume-core:standards` reads the repository and writes `docs/standards.md` with the project's
real conventions and the evidence for each one. The `Principles (manual)` section is yours: it holds
the team's rules, which the spec and the gate consult and which are never rewritten automatically.

The `data_review` block that `/cardume-data:review-pr` reads (validation environment, GCP project,
Tier 2 policy and tolerances) is also set in the project's `CLAUDE.md`; the commented example is in
[`plugins/cardume-core/templates/CLAUDE.md`](../plugins/cardume-core/templates/CLAUDE.md).

Some manual commands in more detail:

- `release`: only you call it, or the `release-manager` agent.
- `plan`: a light plan for work across several areas, with no spec or PRD.
- `create`: only for creating a new app from scratch.
- `help`: reads the project and suggests the next step. It only suggests, and it changes no files.

## Who does what in visual work

- **`design-flow`** is the designer: visual direction, palette, typography, critique and polish. It
  can also be called as `/cardume-frontend:design-flow`.
- **`site-builder`** handles the whole website (brief, sitemap, content, SEO, LGPD/GDPR, launch) and
  calls `design-flow` for the design.
- **`frontend-specialist`** implements the engineering (state, performance, framework).

## Context and cost

| Where the cost shows up | How the suite controls it |
| --- | --- |
| Fixed, every session: about 6k tokens with the whole suite | Only skill and agent descriptions load; manual commands stay out. The validator caps the skill listing at 14,000 characters and agent descriptions at 12,000. On a 200k context window the listing needs a larger budget: see [Use it alongside other plugins](CONFIGURATION.md#use-it-alongside-other-plugins) |
| Each time an agent runs | Lean body, reference material read on demand, and few preloaded skills (usually 1–2) |
| What an agent returns | The full text when the request is an analysis, plan, review or document. After executed work, a short report; logs and long output go to a file (`docs/` or `.cardume/reports/`) |
| Heavy skills | `verify` and `standards` run in a separate context, and only the result comes back |

To measure it: `claude plugin details cardume-<plugin>@cardume`, and `/context` inside a session.
