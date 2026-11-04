---
name: help
description: "Reads the project state and suggests the next Cardume command or skill for the request at hand. Use when you don't know what to run next, or automatic routing picked nothing."
disable-model-invocation: true
argument-hint: "[what you want to do]"
allowed-tools: Read Glob Grep Bash(git status *) Bash(git log *) Bash(git branch --show-current)
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# /cardume-core:help - What should I do next?

$ARGUMENTS

This command only reads and suggests. It does not start the next step, and it changes no files.

## 1. Read the project state

Check these, and treat anything missing as a fact to report, not an error:

- **Setup:** does `CLAUDE.md` contain `<!-- cardume:start -->`?
- **Standards:** does `docs/standards.md` exist?
- **Specs:** for each folder in `docs/specs/`, which of `spec.md`, `tasks.md` and `verify.md` exist, the
  `Status:` line of the spec and of `tasks.md`, and how many `- [ ]` boxes remain? Skip specs marked
  `implemented` or `superseded`.
- **Product and gates:** files in `docs/prd/`, and in `docs/gates/` the `## Decision` section of the
  latest report. The recommendation is not a decision: only the user's answer there counts.
- **Recent work:** in a git repository, the current branch, `git status --short` and `git log --oneline -5`.

## 2. Pick the next step

If the user described a request, classify its level and use the first table. If not, use the second.
Project state still applies: unfinished work comes up first, in one line.

| The request is | Level | Suggest |
| --- | --- | --- |
| A typo, config value or question | 0 | Just ask for it; no command needed |
| A bug fix or small change, up to ~5 files in one area | 1 | Just describe it. For an unclear bug, `/cardume-core:debug` |
| A new feature, or more than ~5 files or more than one area | 2 | `/cardume-core:spec`, after `/cardume-core:standards` if `docs/standards.md` is missing |
| A new system or product phase | 3 | `/cardume-core:prd` |
| A vague idea | - | `/cardume-core:brainstorm` |
| A new app from scratch | - | `/cardume-core:create` |
| A change for review before merging | - | `/cardume-core:review` |

| The project state shows | Suggest |
| --- | --- |
| No Cardume block in `CLAUDE.md` | `/cardume-core:setup` |
| Level 2 or 3 work ahead and no `docs/standards.md` | `/cardume-core:standards` |
| An approved PRD with no `docs/prd/<slug>-architecture.md` | The `software-architect` agent, for contracts, ADRs and the feature list |
| An architecture file with features that have no spec | `/cardume-core:spec` for the next feature |
| A spec in `draft` | Finish and approve it with `/cardume-core:spec` |
| An approved spec without `tasks.md` | `/cardume-core:tasks`, or the `software-architect` agent at level 3 |
| A `tasks.md` in `draft` | Review and approve it |
| An approved `tasks.md` with open boxes | `/cardume-core:implement` |
| All boxes ticked and no `verify.md` | `/cardume-core:verify` |
| A `verify.md` and an open change | `/cardume-core:review` |
| A phase finished with no gate report | `/cardume-core:gate` |
| A gate report with an empty `## Decision` | Ask the user to decide |
| An approved gate, or the user's explicit OK to release | `/cardume-core:release` |
| Nothing open | Ask what the user wants to do |

The tables name only `cardume-core` commands, which are always available. For a stack skill, suggest
only one listed in this session. A skill from a plugin that isn't installed is an install suggestion,
for example `/plugin install cardume-frontend@cardume`, not a command to run.

## 3. Answer

Keep it under ten lines:

- **Where you are:** two or three facts from step 1. Say so if the project has no Cardume setup or
  isn't a git repository.
- **Next step:** one exact command or request to type, and why.
- **Then:** the one or two steps that follow.
- **The levels**, only when the user seems new to them: 0 trivial, 1 small, 2 feature, 3 product. The
  level sets how much process a change gets.
