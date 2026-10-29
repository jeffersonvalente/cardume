# MCP servers for Cardume

Cardume works without any MCP server: every agent and skill that can use one also names a CLI
fallback (`gh`, `gcloud`, `bq`, a local Playwright install). A server is worth adding when you want
structured, permission-scoped tool calls instead of shell commands, or when the CLI is not
installed on the machine.

[`mcp.example.json`](mcp.example.json) is a ready `.mcp.json` with the servers below. Versions were
checked on **2026-10-28** against each project's own release page or registry; see
[Pinned versions](#pinned-versions).

## Which servers, and who uses them

| Server key | Used by | Why |
| --- | --- | --- |
| `github` | `cardume-data:review-pr`, `cardume-core:tasks` | read PR metadata, diffs, CI status, issues |
| `bigquery` | `cardume-data:bigquery-patterns`, `cardume-data:gcp-observability-patterns`, `cardume-data:gcp-project-auditor-data-and-ia` | `execute_sql` for metadata, `INFORMATION_SCHEMA` and dry runs |
| `gcloud` | `cardume-data:gcp-observability-patterns`, `cardume-data:gcp-project-auditor-data-and-ia` | `run_gcloud_command` for read-only `list` / `describe` calls |
| `gcp-observability` | `cardume-data:gcp-observability-patterns`, `cardume-data:gcp-project-auditor-data-and-ia` | Cloud Logging, Monitoring, Trace and Error Reporting reads |
| `gcp-storage` | `cardume-data:gcp-observability-patterns`, `cardume-data:gcp-project-auditor-data-and-ia` | bucket and object listings, IAM on buckets |
| `playwright` | `cardume-qa:webapp-testing` | browser automation through the accessibility tree |
| `atlassian` | `cardume-core:product-owner`, `cardume-core:product-manager` (optional) | Jira backlog and Confluence pages when the team keeps them there |
| `notion` | `cardume-core:product-owner`, `cardume-core:product-manager` (optional) | backlog, PRDs and specs kept in Notion |

The server keys matter: the GCP skills call tools as `mcp__gcloud__*`, `mcp__gcp-storage__*`,
`mcp__gcp-observability__*` and `mcp__bigquery__*`. If you rename a key, the skills fall back to
the CLI.

## Quick start

1. Copy the example to your project root and delete the servers you do not need:

   ```bash
   cp docs/mcp.example.json /path/to/your-project/.mcp.json
   ```

2. Set the variables the file references, in your shell profile or a secret manager, never in the
   file:

   | Variable | Needed by | Notes |
   | --- | --- | --- |
   | `CARDUME_GITHUB_PAT` | `github` | fine-grained token, read-only (see below) |
   | `BIGQUERY_PROJECT` | `bigquery` | default project for jobs |
   | `BIGQUERY_LOCATION` | `bigquery` | optional, e.g. `US`, `EU`, `southamerica-east1` |
   | `BIGQUERY_MAXIMUM_BYTES_BILLED` | `bigquery` | optional; defaults to 10 GiB per query |

   The Google servers use Application Default Credentials; the Atlassian and Notion servers sign
   in with OAuth. Neither needs a variable.

3. Start Claude Code in the project. It asks once whether to trust the servers in `.mcp.json`
   (reset that choice with `claude mcp reset-project-choices`).

4. Check them:

   ```bash
   claude mcp list          # each server with Connected / Needs authentication / Failed to connect
   claude mcp get github    # the resolved command, scope and any missing-variable warning
   ```

   Inside a session, `/mcp` shows the same status, lists each server's tools and runs the OAuth
   sign-in for remote servers.

Prerequisites: Docker (for `github`), Node.js 20 or newer (for the `npx` servers), and the gcloud CLI
(for the Google servers).

## Servers

### `github` — GitHub's official server

[github/github-mcp-server](https://github.com/github/github-mcp-server), run locally from GitHub's
container image, pinned by tag and digest.

- **What the agents get:** pull request metadata, files and diffs, commits, issues, Actions runs.
  The example enables only the `context`, `repos`, `issues`, `pull_requests` and `actions`
  toolsets (`GITHUB_TOOLSETS`) and turns on read-only mode (`GITHUB_READ_ONLY=1`), which drops
  every write tool even if a toolset contains one.
- **Auth:** a [fine-grained personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
  limited to the repositories you review, with **read-only** repository permissions: Metadata,
  Contents, Pull requests, Issues, Actions and Commit statuses. The token reaches the container
  through `CARDUME_GITHUB_PAT`, a name of your own, so it is never written to the file.
- **Writes:** `cardume-core:tasks --issues` opens issues with `gh` after you confirm, so the MCP
  server can stay read-only. Only remove `GITHUB_READ_ONLY` if you want agents to write through
  MCP, and then add Issues: read and write to the token, nothing broader.
- **Untrusted content:** on public repositories, consider `GITHUB_LOCKDOWN_MODE=1` (add it to
  `env` and as another `-e` in `args`). It hides content from authors without push access. GitHub
  documents it as a prompt-injection filter, not an authorization boundary.
- **Alternative:** GitHub also hosts the server at `https://api.githubcopilot.com/mcp/` (HTTP,
  OAuth). It is always the latest version, so it cannot be pinned.
- **Check:** `claude mcp get github` shows Connected; in `/mcp`, the tool list should contain no
  `create_*`, `update_*` or `merge_*` tools.

### `bigquery` — Google's MCP Toolbox for Databases

[googleapis/genai-toolbox](https://github.com/googleapis/genai-toolbox), npm package
`@toolbox-sdk/server`, with its prebuilt BigQuery configuration (`--prebuilt=bigquery`).

- **What the agents get:** `execute_sql`, `list_dataset_ids`, `list_table_ids`,
  `get_dataset_info`, `get_table_info`, `search_catalog`, plus analysis tools (`forecast`,
  `analyze_contribution`, `ask_data_insights`) that Cardume does not rely on.
- **Guards set in the example:** `BIGQUERY_READONLY=true` blocks DML and DDL in every tool, and
  `BIGQUERY_MAXIMUM_BYTES_BILLED` makes any query that would scan more than the cap fail before it
  runs, at no cost. The skills still dry run first.
- **Auth:** Application Default Credentials (`gcloud auth application-default login`), or set
  `BIGQUERY_IMPERSONATE_SERVICE_ACCOUNT` to act as a dedicated service account (your principal
  needs `roles/iam.serviceAccountTokenCreator` on it).
- **Least privilege:** Google's page for this configuration lists BigQuery User and Metadata
  Viewer for reads. For Cardume's metadata-first work, `roles/bigquery.jobUser` on the job
  project plus `roles/bigquery.metadataViewer` is enough; add `roles/bigquery.resourceViewer` to
  read `INFORMATION_SCHEMA.JOBS_BY_PROJECT`, and `roles/bigquery.dataViewer` only on the datasets
  an agent must actually read. Leave out `roles/bigquery.dataEditor`.
- **Projects:** `BIGQUERY_PROJECT` is only the default. The skills pass the project explicitly on
  every call, so a wrong default cannot silently point a query elsewhere.
- **Check:** `claude mcp get bigquery` has no missing-variable warning for `BIGQUERY_PROJECT`.

### `gcloud`, `gcp-observability`, `gcp-storage` — Google Cloud's MCP servers

All three come from [googleapis/gcloud-mcp](https://github.com/googleapis/gcloud-mcp). Google marks
them as preview and not covered by the Google Cloud Terms of Service, so keep them pinned and read
their changelog before upgrading.

- **`gcloud`** (`@google-cloud/gcloud-mcp`) exposes one tool, `run_gcloud_command`. It runs
  with the permissions of the active gcloud account, minus a built-in deny list of interactive
  and arbitrary-input commands. You can add your own allow or deny list with `-c /absolute/path/config.json`
  (one of `allow` or `deny`, each a list of command groups).
- **`gcp-observability`** (`@google-cloud/observability-mcp`) is read-only by design:
  `list_log_entries`, `list_log_names`, `list_buckets`, `list_views`, `list_sinks`,
  `list_time_series`, `list_metric_descriptors`, `list_alert_policies`, `list_traces`,
  `get_trace`, `list_group_stats`.
- **`gcp-storage`** (`@google-cloud/storage-mcp`) enables only non-destructive tools unless
  started with `--enable-destructive-tools`. The example does not pass that flag.
- **Auth:** run both `gcloud auth login` (used by `gcloud`) and
  `gcloud auth application-default login` (used by the other two). API calls are billed to the
  ADC quota project; set it with `gcloud auth application-default set-quota-project PROJECT_ID`,
  and enable the Logging, Monitoring and Storage APIs there.
- **Least privilege:** Google's advice for `gcloud` is to
  [impersonate a service account](https://cloud.google.com/sdk/docs/authorizing#impersonation)
  that holds only limited roles. For Cardume's read-only investigations, give that account viewer
  roles such as `roles/logging.viewer`, `roles/monitoring.viewer`, `roles/storage.bucketViewer`
  for bucket metadata (`roles/storage.objectViewer` only on buckets whose objects must be listed)
  and `roles/iam.securityReviewer` for IAM policy reads. No `*.admin` or `*.editor` role is
  needed.
- **Check:** `claude mcp list` shows all three Connected; a `PERMISSION_DENIED` on the first tool
  call means a missing role, which the skills report instead of retrying.

### `playwright` — Microsoft's Playwright server

[microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp), npm package
`@playwright/mcp`.

- **What the agents get:** navigation, clicks, form input and page snapshots through the
  accessibility tree, used by `cardume-qa:webapp-testing` for exploratory checks.
- **Flags in the example:** `--headless` (no window) and `--isolated` (profile kept in memory, so no
  cookies or logins persist between sessions, and parallel sessions do not fight over one
  profile).
- **Optional:** `--allowed-origins` / `--blocked-origins` narrow what the browser requests, but
  Playwright documents them as a convenience, not a security boundary. Extra capabilities
  (`--caps=vision,pdf,devtools`) are off unless you add them.
- **Auth:** none. If a test needs credentials, pass them with `--secrets <dotenv file>` kept
  outside the repository.
- **Check:** `/mcp` lists `browser_navigate`, `browser_snapshot` and the other `browser_*` tools.

### `atlassian` — Atlassian Rovo MCP Server (optional)

Atlassian's hosted server for Jira and Confluence at `https://mcp.atlassian.com/v2/mcp`.

- **When:** your backlog or specs live in Jira or Confluence and you want `product-owner` or
  `product-manager` to read and refine them there instead of in `docs/backlog.md`.
- **Auth:** OAuth 2.1. Run `/mcp`, choose `atlassian` and sign in in the browser. The server acts
  with your own Jira and Confluence permissions. Site admins can restrict or disable it, and can
  enable API-token sign-in instead, in the Atlassian administration settings.
- **Pinning:** hosted, so there is no version to pin; the URL selects the API generation (v2).
- **Moving from v1:** point the URL at `https://mcp.atlassian.com/v2/mcp` and sign in again
  (`/mcp`); v2 is a separate OAuth resource, so v1 credentials do not carry over. If v2 gives
  trouble, `https://mcp.atlassian.com/v1/mcp` still works for now (API-token sign-in is documented
  only for v1), but Atlassian says existing v1 use starts exposing the v2 tools on 1 March 2027
  ([upgrade guide](https://support.atlassian.com/atlassian-ai-gateway/docs/how-to-upgrade-from-atlassian-rovo-mcp-v1-to-atlassian-rovo-mcp-v2/)).
- **Check:** `claude mcp list` moves from Needs authentication to Connected after sign-in.

### `notion` — Notion's hosted server (optional)

Notion's hosted server at `https://mcp.notion.com/mcp` (Streamable HTTP).

- **When:** PRDs, specs or the backlog live in Notion.
- **Auth:** OAuth through `/mcp`. Access follows your own Notion permissions in the workspace you
  pick; guests cannot connect. Business and Enterprise owners can issue an MCP token instead of
  OAuth. Notion no longer maintains its open-source local server and recommends the hosted one.
- **Pinning:** hosted, so there is no version to pin.
- **Check:** `claude mcp list` shows Connected after sign-in.

## Pinned versions

Checked on 2026-10-28.

| Server | Pin | Source |
| --- | --- | --- |
| `github` | `ghcr.io/github/github-mcp-server:v2.0.3@sha256:250bc6ce70788207608ef74cef4397230ff2e8481218da74d6093e4bd9101132` | GitHub release `v2.0.3` (2026-10-21); digest of the multi-arch image index read from the `ghcr.io` registry API |
| `bigquery` | `@toolbox-sdk/server@1.15.0` | `npm view`; GitHub release `v1.15.0` of googleapis/genai-toolbox (2026-10-23) |
| `gcloud` | `@google-cloud/gcloud-mcp@0.5.3` | `npm view`; release `gcloud-mcp-v0.5.3` (2026-01-05) |
| `gcp-observability` | `@google-cloud/observability-mcp@0.2.3` | `npm view`; release `observability-mcp-v0.2.3` (2026-02-11) |
| `gcp-storage` | `@google-cloud/storage-mcp@0.6.0` | `npm view`; release `storage-mcp-v0.6.0` (2026-05-06) |
| `playwright` | `@playwright/mcp@0.0.83` | `npm view`; GitHub release `v0.0.83` of microsoft/playwright-mcp (2026-09-28) |
| `atlassian` | hosted, `/v2/mcp` | Atlassian Rovo MCP Server documentation |
| `notion` | hosted | Notion developer documentation |

To upgrade, read the release notes, change the version (and, for `github`, both the tag and the
digest), then run `claude mcp list` again. Avoid `@latest` and bare image tags: they change what
runs without a change to the file.

## Security notes

- **Read-only first.** Every pinned server here starts in its read-only or non-destructive mode
  where it has one (`GITHUB_READ_ONLY`, `BIGQUERY_READONLY`, storage without
  `--enable-destructive-tools`). For `gcloud`, which has no such mode, the identity's IAM roles are
  the boundary, so use a viewer-only service account.
- **Credentials are the real limit.** Toolset filters, lockdown mode and allowlists reduce what the
  model sees; the token or IAM role decides what can actually happen. Scope both.
- **Never commit secrets.** `.mcp.json` holds only `${VAR}` references. Keep the values in your
  shell, a secret manager or a `.env` file listed in `.gitignore`. An unset variable does not
  break the file: `claude mcp list` warns about it and leaves the text unexpanded.
- **Choose the scope deliberately.** Project scope (`.mcp.json` at the repository root) is shared
  through version control and asks each person to approve it. Local scope (the default for
  `claude mcp add`) and user scope live in `~/.claude.json` and are private to you; use them for a
  server only you need or one whose configuration contains a literal credential.
- **Block tools you never want called.** Claude Code permission rules take MCP tool names, for
  example a `deny` entry for `mcp__gcloud__run_gcloud_command` in a project where agents should
  stick to the dedicated observability and storage tools.
- **Treat tool output as untrusted.** Issues, PR comments, web pages, log lines and Notion pages
  can contain text written to steer a model. The agents treat it as data; review any write they
  propose before approving it.
