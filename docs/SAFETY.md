# Safety and privacy

Part of what Cardume promises is enforced by Claude Code hooks, not by instructions to the model.
A hook is a script that the harness runs around a tool call or at the end of a turn; the model
cannot skip it. This page lists every hook, what it blocks, how to turn it off, and what Cardume
does and does not touch on your machine.

- [Hooks](#hooks)
- [Security and privacy](#security-and-privacy)
- [Verification commands](#verification-commands)

## Hooks

All hooks ship in `cardume-core` and are declared in
[`plugins/cardume-core/hooks/hooks.json`](../plugins/cardume-core/hooks/hooks.json).

| Hook | When | What it does | Turn off |
| --- | --- | --- | --- |
| [`syntax_check.py`](../plugins/cardume-core/hooks/syntax_check.py) | after every Edit/Write | checks the syntax of the changed `.py`, `.js`/`.mjs`/`.cjs`, `.sh`/`.bash` and `.json` file and hands the error back to Claude immediately | `CARDUME_SYNTAX_CHECK=0` |
| [`stop_verify.py`](../plugins/cardume-core/hooks/stop_verify.py) | when Claude is about to end a turn with uncommitted changes in a git repository (it does nothing outside git) | runs the security scan and lint (`cardume-checklist --critical-only`) **only on the changed files of the git working tree** (yours included; the security scan needs `cardume-qa`); if they fail, the turn does not end and Claude keeps working. After 3 blocks on the same set of files in a session, the decision goes back to you. Pre-existing problems elsewhere in the project never block, and lint never downloads packages | `CARDUME_STOP_VERIFY=0` |
| [`spec_reminder.py`](../plugins/cardume-core/hooks/spec_reminder.py) | when a turn ends with a large change (8+ files or 400+ lines) and no spec, PRD or ADR | warns you, once per change; does not block | `CARDUME_SPEC_REMINDER=0` |
| [`guard_bash.py`](../plugins/cardume-core/hooks/guard_bash.py) | before a destructive or public shell command | asks for confirmation for `terraform apply`/`destroy`, `kubectl delete`/`drain`, cloud `delete` commands, `bq rm`, `DROP`/`TRUNCATE`, `DELETE` without `WHERE`, `rm -r` on `/` or `~`, `git push --force`, pushing tags, `gh release`, `gh workflow run`, `npm`/`uv`/`cargo`/`mvn` publish, `docker push` and others. A `--dry-run` of a publish or release command passes without asking | `CARDUME_GUARD_BASH=0` |
| [`restrict_verifier_writes.py`](../plugins/cardume-core/hooks/restrict_verifier_writes.py) | when the `qa-gatekeeper` agent writes a file or runs a command | allows writes only under `docs/gates/` and `.cardume/reports/`, and denies shell commands that change files or git state or install packages. It can still run tests, builds, linters and `git log`/`diff` | — |

The two `PreToolUse` hooks (`guard_bash` and `restrict_verifier_writes`) run with
`onFailure: "block"`: if Python is missing or the script crashes, the command is blocked, never let
through without a question.

What the hooks do not do:

- `stop_verify` checks security and lint on changed files. It does not run your test suite and does
  not prove that a feature meets its spec; that is the job of the `verify` skill and the
  `qa-gatekeeper` agent.
- `guard_bash` matches command patterns. It asks; it does not sandbox. A command it does not know
  runs under your normal Claude Code permissions.
- `restrict_verifier_writes` is best effort. An interpreter can still write files
  (`python -c …`); the agent's instructions forbid that, but no hook catches every case.

Local state (the last passing change set, the block counter, backups) lives in `.cardume/`, which the
setup adds to `.gitignore`.

## Security and privacy

- **No telemetry.** No script sends usage or session data anywhere. The validator also blocks
  known update or phone-home hosts from entering the repository.
- **Your files:**
  - installing or updating plugins writes nothing to your project; once installed, the hooks keep
    small state files in `.cardume/` (setup adds it to `.gitignore`);
  - in `CLAUDE.md`, only the `<!-- cardume:start -->` … `<!-- cardume:end -->` block changes. The
    setup shows the diff first and writes only after you confirm, keeps a backup in
    `.cardume/backups/`, and checks byte by byte that everything outside the block is unchanged
    (on a mismatch it restores the backup);
  - `AGENTS.md` is never written: if it exists, the block imports it (`@AGENTS.md`);
  - Claude's auto memory is not touched.
- **Public and irreversible actions always ask.** The `release-manager` prepares the commands and
  hands them to you to confirm.
- **Live design preview (`design-flow live`):**
  - listens on `127.0.0.1` only and rejects requests whose `Host` is not local (DNS-rebinding
    protection);
  - grants CORS to local origins only;
  - requires a per-session token;
  - does not serve hidden files;
  - by default applies edits through the current conversation. Running a separate agent
    (`DESIGN_FLOW_LIVE_COPY_AGENT=claude|codex|auto`) is opt-in and sends code to that agent's
    vendor.

  Details in
  [`plugins/cardume-frontend/skills/design-flow/reference/live.md`](../plugins/cardume-frontend/skills/design-flow/reference/live.md#security-model-cardume-port).
- **Pinned external dependencies:** CI actions by SHA (kept current by Dependabot), the example MCP
  servers by version, and the Docker image by digest.

## Verification commands

Claude Code puts each plugin's `bin/` on the PATH, so these scripts become commands. Claude uses
them, and you can run them yourself:

| Command | Plugin | Use |
| --- | --- | --- |
| `cardume-checklist . [--url URL]` | core | audit by priority: security → lint → schema → tests → UX → SEO (→ Lighthouse/E2E) |
| `cardume-verify-all . --url URL` | core | full suite before a deploy |
| `cardume-setup-project . [--apply]` | core | the same as `/cardume-core:setup` (without `--apply`, it only shows the diff) |
| `cardume-security-scan`, `cardume-test-runner`, `cardume-playwright-runner` | qa | security, tests, E2E |
| `cardume-ux-audit`, `cardume-accessibility-checker`, `cardume-seo-checker`, `cardume-lighthouse-audit`… | frontend | UI audits |
| `cardume-design-flow <script.mjs>` | frontend | design-flow scripts (detector, live preview, palette) |

Checks from plugins that are not installed, and from linters that are not on the machine, are
skipped.
