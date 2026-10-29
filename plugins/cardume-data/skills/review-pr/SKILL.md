---
name: review-pr
description: "Reviews a data/analytics PR: SQL, grain, cost and DAG risks plus data evidence from a configured non-production environment, then drafts a review the user approves before anything is posted. Use when a data pipeline PR needs review."
disable-model-invocation: true
argument-hint: "[PR number or URL]"
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# /cardume-data:review-pr — Data pull request review

$ARGUMENTS

Review one pull request that changes a BigQuery lakehouse (SQL models, dbt/Dataform files, DAGs,
schemas). The checks and the data evidence are done by the `lakehouse-reviewer` subagent; this
command sets up the review, relays questions, and turns the result into a review the user approves.
Nothing is posted to the PR without that approval.

## 1. Read the team's review settings

Look in the project's rules file (`CLAUDE.md`, then `docs/standards.md`) for a `data_review`
block. Teams that want unattended reviews should write it once:

```yaml
data_review:
  validation_environment: staging          # where PR code is deployed for testing
  validation_project: my-data-staging      # optional; GCP project of that environment
  tier2_policy: request-changes            # or "comment": whether Tier 2 findings block the merge
  tolerances:                              # optional; per table family (glob on the table name)
    fct_*:
      duplicates: 0                        # max duplicate rows on the grain
      row_delta_pct: 0                     # max row-count delta, %, when the PR claims no data change
      sum_delta: 0                         # max absolute delta of key sums, same condition
      fill_pct_min: 95                     # min fill % of a new column (default: source-layer rate)
```

- **Validation environment** (`data_review.validation_environment`): the environment where data
  evidence is collected. If the key is missing, ask the user which environment and project to use,
  and offer a diff-only review as the alternative. **Never validate against production**, even when
  asked or when the setting names it: say so, and fall back to a diff-only review unless the user
  names a non-production environment.
- **Validation project** (`data_review.validation_project`): the GCP project of that environment;
  when missing, take it from the rules file's project-per-environment list or ask.
- **Tier 2 policy** (`data_review.tier2_policy`): `request-changes` (default) or `comment`.
- **Tolerances** (`data_review.tolerances`): passed through. The subkeys are the four above; their
  defaults are in `lakehouse-reviewer` §4.

## 2. Collect the PR

Resolve the argument to a PR (none given: the PR of the current branch, `gh pr view`). Then:

```bash
gh pr view N --json number,title,body,url,baseRefName,headRefName,headRefOid,files,statusCheckRollup
gh pr diff N
```

Note the head commit. Data evidence only counts if the validation environment runs that commit, so
ask the reviewer to confirm it from deployment evidence (CI deploy job, Composer bucket file
contents, dbt/Dataform run metadata). If it runs an older commit or nothing, the review is
diff-only and says so.

## 3. Delegate the review

Start `lakehouse-reviewer` with: the PR reference and head commit, the validation environment and
project (or "diff-only"), the Tier 2 policy, any tolerances, and the path of the rules file. It
returns a proposed verdict, a checks table, the evidence queries with results, and draft review
text. When it reports **Open questions** (missing access, unclear environment, an expected delta
it cannot judge), ask the user and resume the reviewer with the answers.

For a finding that needs a deeper investigation than a review allows, offer to hand it to
`data-engineer-gcp-bigquery` after the review instead of extending the review.

## 4. Hand-off to the user

Present, in this order and in the user's language:

1. **Proposed verdict** (approve, request changes, comment only) and the one-line reason.
2. **Findings by severity**: *Blocking* (Tier 1), *Should fix* (Tier 2), *Suggestions* (Tier 3),
   each with file:line, the problem and the suggested fix. Empty groups are omitted.
3. **Evidence**: environment, commit validated, and the before/after numbers with their tolerance.
   State plainly what could not be checked.
4. **Draft review**, exactly as it would be posted: a summary body plus inline comments by file and
   line. Write it to the author as a peer, in neutral wording, with no @-mentions. Save the summary
   body to `.cardume/reports/review-N.md` (N is the PR number) and list the inline comments below
   it in the same file, so the post step and a declined review both have the draft on disk.

Then ask the user to approve, edit or discard the draft. Only after an explicit approval of the
final text, post it:

```bash
gh pr review N --request-changes --body-file .cardume/reports/review-N.md   # or --approve / --comment
```

Inline comments go in the same review through `gh api repos/{owner}/{repo}/pulls/N/reviews` with
`event`, `body` and a `comments` array (`path`, `line`, `body`), so the author gets one
notification. If the user edits the verdict or text, post their version, not the draft. After
posting, show the review URL. If the user declines, leave the draft file in `.cardume/reports/`
and post nothing.
