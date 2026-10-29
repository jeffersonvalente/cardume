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

## Use it with a team

Cardume needs no server. The plugins are files in a public marketplace, and Claude Code's own
settings decide who gets them.

### Per repository

Commit `.claude/settings.json` with the marketplace and the plugins the project uses:

```json
{
  "extraKnownMarketplaces": {
    "cardume": {
      "source": { "source": "github", "repo": "jeffersonvalente/cardume" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": { "cardume-all@cardume": true }
}
```

- **Interactive sessions:** the marketplace is registered once a teammate accepts the workspace trust
  dialog for the folder. In an untrusted folder the entry is ignored. Cloud sessions never show that
  dialog, so they ignore it too.
- **Plugins load from the marketplace copy.** Every Cardume plugin is listed in the marketplace by a
  relative path, so nothing else needs installing. Run `/plugin` to confirm what loaded.
- **A subset:** list the plugins you want instead of the bundle, for example
  `"cardume-core@cardume": true` and `"cardume-data@cardume": true`.
- **Updates:** `"autoUpdate": true` keeps the marketplace and its plugins current in the background.
  Without it, third-party marketplaces don't update on their own (see [Updates](#updates)).
- **`claude -p` and CI:** the entries apply only in folders whose trust was already accepted, or whose
  `hasTrustDialogAccepted` flag is set in `~/.claude.json`. Plugins
  install in the background, so set `CLAUDE_CODE_SYNC_PLUGIN_INSTALL=1` to make the run wait for them
  before the first turn.

### Across an organization

Put the same two keys in managed settings to install Cardume on every machine. Managed settings take
precedence over every other scope: a plugin set to `true` there keeps loading even if a user disables it.

- **Managed settings file:** `managed-settings.json` at
  `/Library/Application Support/ClaudeCode/` (macOS), `/etc/claude-code/` (Linux and WSL) or
  `C:\Program Files\ClaudeCode\` (Windows).
- **Server-managed settings:** the claude.ai admin console, under **Organization settings > Claude
  Code > Managed settings** (requires the Owner role). MDM profiles work too.
- **Restrict sources:** `strictKnownMarketplaces` allows plugins only from the listed marketplaces.
  Keep the official marketplace and `{ "source": "skills-dir" }` in the list if your users rely on them:

  ```json
  {
    "strictKnownMarketplaces": [
      { "source": "github", "repo": "anthropics/claude-plugins-official" },
      { "source": "github", "repo": "jeffersonvalente/cardume" },
      { "source": "skills-dir" }
    ]
  }
  ```

- **If your policy sets `allowManagedHooksOnly`:** hooks from plugins that users enable themselves do
  not run. Cardume's safety hooks then run only when the plugins are force-enabled in the managed
  `enabledPlugins`.
- **Check a machine:** `/status` lists `Enterprise managed settings` among the setting sources when
  the policy loaded.

Official references: [Manage plugins for your organization](https://code.claude.com/docs/en/plugins/org)
and [Deploy managed settings](https://code.claude.com/docs/en/managed-settings).

## Updates

Third-party marketplaces do not update on their own. Use `/plugin` → Marketplaces → `cardume` →
*Enable auto-update*, or update by hand: `claude plugin marketplace update cardume` refreshes the
listing, and `claude plugin update <plugin>@cardume` updates an installed plugin.

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
