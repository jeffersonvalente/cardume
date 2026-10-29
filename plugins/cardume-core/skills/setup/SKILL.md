---
name: setup
description: "Adds or updates the Cardume conventions block in this project's CLAUDE.md through a deterministic script (backup, diff, only the marked block changes; AGENTS.md is imported, never edited) and suggests stack and code-intelligence plugins."
disable-model-invocation: true
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
metadata:
  internal: "true"
---

# /cardume-core:setup - Install Cardume conventions

$ARGUMENTS

Do not edit `CLAUDE.md`, `AGENTS.md` or `.gitignore` by hand in this command; the script below does
it safely (only the `<!-- cardume:start -->` … `<!-- cardume:end -->` block changes, everything
else is verified byte-for-byte, and originals are backed up to `.cardume/backups/`).

1. Preview: run `cardume-setup-project .` and show the user the diff it prints (dry run, nothing written).
2. If the user agrees, run `cardume-setup-project . --apply` and report the backup path it prints.
   If the script reports malformed markers or a failed safety check, stop and show the message.
3. Suggest plugins for this project:
   - Stack: list enabled Cardume plugins (agents/skills prefixed `cardume-`) and recommend missing
     ones that fit (e.g. `package.json` with React → `cardume-frontend`; `*.tf` → `cardume-platform`;
     BigQuery/Airflow → `cardume-data`), or simply `/plugin install cardume-all@cardume`.
   - Code intelligence: repeat the official LSP plugin suggestions the script printed, including
     the language-server binary install hint when it is missing.
4. If `docs/standards.md` does not exist, suggest `/cardume-core:standards` to capture the
   project's conventions.
