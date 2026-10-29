# Configuration

Cardume works without configuration. This page covers the few settings that exist, how to keep the
plugins updated, and how to use the skills in tools other than Claude Code.

- [Install a subset](#install-a-subset)
- [Updates](#updates)
- [Settings](#settings)
- [MCP servers](#mcp-servers)
- [Other tools (Codex, Cursor, Gemini CLI, Copilot)](#other-tools-codex-cursor-gemini-cli-copilot)

## Install a subset

`cardume-all` installs the seven plugins at once. To install only part of the suite, name the
plugin, for example `/plugin install cardume-data@cardume`. `cardume-core` always comes along, since
it holds the hooks, the delivery flow and the setup command.

## Updates

Third-party marketplaces do not update on their own. Use `/plugin` → Marketplaces →
*Enable auto-update*, or run `claude plugin marketplace update cardume`.

## Settings

- **Organization (`cardume-platform`).** When you enable the plugin, it asks for your Terraform
  modules repository, the state bucket prefix and the default region. To change them later:
  `/config` → cardume-platform.
- **Agent memory.** `debugger`, `code-archaeologist`, `data-engineer-gcp-bigquery` and
  `devops-engineer` keep durable project facts in `.claude/agent-memory-local/<agent>/MEMORY.md`,
  which the setup keeps out of git. Reviewers and auditors have no memory, so they stay read-only.
- **Data reviews (`cardume-data`).** `/cardume-data:review-pr` reads a `data_review` block in the
  project's `CLAUDE.md` (validation environment, GCP project, Tier 2 policy and tolerances). The
  commented example is in
  [`plugins/cardume-core/templates/CLAUDE.md`](../plugins/cardume-core/templates/CLAUDE.md).
- **Environment variables:**

  | Variable | Effect |
  | --- | --- |
  | `CARDUME_SYNTAX_CHECK=0` | turns off the syntax check after edits |
  | `CARDUME_STOP_VERIFY=0` | turns off the security scan and lint before a turn ends |
  | `CARDUME_SPEC_REMINDER=0` | turns off the large-change reminder |
  | `CARDUME_GUARD_BASH=0` | turns off the confirmation before destructive or public commands |
  | `DESIGN_FLOW_LIVE_ALLOWED_ORIGINS` | allows the live design preview on a custom local hostname (comma-separated origins) |
  | `DESIGN_FLOW_LIVE_COPY_AGENT` | `chat` (default) applies live edits in the conversation; `claude`, `codex` or `auto` run a separate agent and send code to its vendor |

  See [SAFETY.md](SAFETY.md#hooks) for what each hook does before you turn it off.

## MCP servers

Cardume does not need any MCP server: every agent and skill that can use one also names a CLI
fallback. [MCP_SETUP.md](MCP_SETUP.md) lists the useful ones (BigQuery, GitHub, Jira, Notion…) with
pinned versions, and [`mcp.example.json`](mcp.example.json) is a ready `.mcp.json`.

## Other tools (Codex, Cursor, Gemini CLI, Copilot)

The skills follow the open **Agent Skills** format
([agentskills.io](https://agentskills.io/specification)), which Codex, Cursor, Gemini CLI, GitHub
Copilot, OpenCode and Windsurf also read. The validator enforces the parts of the format that matter
for portability: the name equals the folder, the description is at most 1,024 characters, and
`allowed-tools` is space-separated.

### Install

With the `skills` installer (vercel-labs). The `skills.sh.json` file at the repository root tells it
where the skills are:

```bash
# list what will be found
npx skills@<version> add jeffersonvalente/cardume --list
# install for Codex, Cursor, Gemini CLI and Copilot (in the current project)
npx skills@<version> add jeffersonvalente/cardume -a codex cursor gemini-cli github-copilot -s '*'
```

Or with the GitHub CLI (`gh` 2.90+, preview feature):

```bash
gh skill install jeffersonvalente/cardume --agent codex --scope project
```

> Pin the installer version (`skills@<version>`) instead of `@latest`, for the same reason the MCP
> server versions are pinned.

Where each tool looks: in the project, `.agents/skills/` works for Codex, Cursor, Gemini CLI, Copilot
and OpenCode. In the user folder, each has its own (`~/.agents/skills`, `~/.cursor/skills`,
`~/.gemini/skills`, `~/.copilot/skills`).

### What works outside Claude Code

| Part | Outside Claude Code |
| --- | --- |
| Skill knowledge (patterns, checklists, references) | works the same |
| Skills marked `compatibility: "Claude Code with the Cardume plugins…"` | the text is useful, but they mention `cardume-*` commands, subagents or plugin paths that do not exist outside Claude Code |
| `setup` and `intelligent-routing` | hidden from the installer (`metadata.internal`), since they only make sense in Claude Code |
| Agents (`agents/*.md`) | not available: there is no common format across tools |
| Hooks (stop check, command guard, syntax check) | not available: they are specific to Claude Code |
| `cardume-*` commands | live in the plugins' `bin/`; outside Claude Code, run the scripts directly from `plugins/*/skills/*/scripts/` |
| `context: fork`, `argument-hint`, `$ARGUMENTS` | ignored; Cursor's `/skill-name` is similar |

### AGENTS.md

Cardume **never writes `AGENTS.md`**. When the project has one, `/cardume-core:setup` makes
`CLAUDE.md` import it (`@AGENTS.md`). The team's rules then stay in one place, apply to Claude Code
and to the other tools (which read `AGENTS.md` natively), and the Cardume block lives only in
`CLAUDE.md`.
