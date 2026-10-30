---
name: generator-pr-description
description: "Drafts a PR title and body from the branch's full diff, then creates or updates the PR after confirmation. Use when asked to create a PR or write a PR description (criar PR, descrição de PR)."
argument-hint: "<base-branch> (optional — detected automatically if omitted)"
---

# Pull request description

A PR description is read three times: by the reviewer deciding how to approach the change, by
whoever skims notifications, and, months later, by someone running `git log` or `git blame`
to learn why the code looks the way it does. Write for all three. Google's guidance on
[change descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html)
puts it simply: the first line says *what* is being done and stands on its own; the body says
*why*, gives the context a reader cannot get from the diff, and points out anything surprising.

This skill turns a branch into that description, shows it, and touches GitHub only after the
user says yes.

## 1. Pin down the range

Everything depends on comparing against the right base. A wrong base produces a description
of someone else's work.

**The argument is the base.** Accept any of these forms:

- nothing → detect the base (below);
- `main`, `master`, `develop`, a release branch → use it;
- another feature branch, including ticket-style names such as `feat/PAY-120-refund-model` →
  the user is stacking PRs; use it as the base.

If the argument is the current branch, or matches no local or `origin/` ref, say so and ask
which base they meant instead of guessing.

**Detecting the base when none is given**, in order of trust:

1. An open PR for this branch already has one: `gh pr view --json number,url,baseRefName,isDraft`.
   If it exists, this run *updates* that PR.
2. Where the branch came from: `git reflog show --no-abbrev <branch>` often ends with
   `branch: Created from <ref>` ([git reflog](https://git-scm.com/docs/git-reflog)). Reflogs
   are local and expire, so treat this as a hint.
3. The repository default: `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`,
   or `git symbolic-ref --short refs/remotes/origin/HEAD`.
4. If `develop` exists too and the branch has fewer commits ahead of `develop` than of the
   default (`git rev-list --count <candidate>..HEAD`), the branch probably forked from
   `develop`. Say which base you picked and why when it is not obvious.

Then fetch the base so the comparison is current (`git fetch origin <base>`) and compare
against `origin/<base>`.

**Use the merge base, not the tip.** `git diff origin/<base>...HEAD` (three dots) diffs from the
common ancestor ([git diff](https://git-scm.com/docs/git-diff),
[git merge-base](https://git-scm.com/docs/git-merge-base)), so commits that landed on the base
after the branch forked do not show up as if this branch reverted them.

Before going further, check two things and mention them if they apply:

- Uncommitted or unpushed work (`git status --short`, `git rev-list --count @{u}..HEAD`). It
  will not be in the PR until committed and pushed.
- An empty range. Nothing to describe; stop and say so.

## 2. Gather the evidence

Read, in this order:

1. **Shape:** `git diff --stat origin/<base>...HEAD` and `--name-status`. This tells you which
   areas changed and which files are mechanical (lockfiles, generated code, renames).
2. **Commits:** `git log --no-merges --format='%h %s%n%b' origin/<base>..HEAD`
   ([git log](https://git-scm.com/docs/git-log)). Messages carry intent the diff does not.
3. **The diff itself**, area by area. For a large diff, read per directory or per file
   instead of all at once, and skim generated and vendored files.
4. **Tests touched** in the diff, and any test or CI output the user already shared.

From that, extract:

- **Type and scope.** If the commits follow
  [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), the dominant type
  (`feat`, `fix`, `refactor`…) and scope become the title prefix. A `!` after the type or a
  `BREAKING CHANGE:` footer in any commit is a breaking change and must appear in the body.
- **Linked work.** Look in the branch name and commit messages for:
  GitHub references (`#123`, `owner/repo#123`, `GH-123`);
  tracker keys in the `ABC-123` form used by Jira, Linear and others;
  full issue URLs from any tracker.
  Link only what you can link honestly: a full URL that appears in the text, or a key whose
  base URL is written somewhere in the repository (README, CONTRIBUTING, `CLAUDE.md`, the PR
  template). Otherwise write the bare key; a guessed URL is worse than none.
- **The why.** Commit bodies, the issue text if the user shared it, code comments added in the
  diff. If the motivation is nowhere to be found, ask for it rather than inventing one.

## 3. Pick the template

GitHub reads a PR template from the repository root, `docs/` or `.github/`, and supports
several templates in a `PULL_REQUEST_TEMPLATE/` directory
([GitHub: pull request templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository)).
Look for `pull_request_template.md` (any case) in those three places and for that directory.

- One template: follow it exactly: its headings, order and checklists. Tick a checklist item
  only when the evidence shows it is done.
- Several: pick the one that matches the change (bugfix, feature, release) and say which.
- None: use the built-in [default template](assets/default-template.md).

## 4. Choose the language

Write in the language the user is using with you. If the repository clearly has a different
convention (the template's language, or recent PRs: `gh pr list --state merged --limit 5
--json title,body`), follow the project and mention it. Keep identifiers, commands, file paths
and Conventional Commit types as they are; translate everything around them.

## 5. Write it

**Title.** One line, ideally under about 70 characters, in the imperative ("add", "fix",
"remove"; in Portuguese, "adiciona", "corrige", or whatever the project uses). Prefix with the
Conventional Commit type and scope when the repository uses them, and with the ticket key when
recent PR titles do.

**Opening paragraph.** Before the first heading, one or two sentences that summarise the
change and its reason. Google's test: could a reader understand it without the diff, years
from now?

**Body.** Fill the template from the evidence:

- Describe the **end state of the branch**, grouped by behaviour or area. Fixup commits,
  reverted experiments and review rounds are history, not content.
- Explain *why* and the trade-offs taken; the diff already shows *how*.
- Name what is deliberately **not** done, and where it is tracked.
- Call out anything a reviewer must not miss: migrations, config or env changes, feature
  flags, breaking API changes, security-sensitive code, performance impact, rollback.
- Under verification, list the tests that exist in the diff and the checks the user told you
  they ran. Never claim a test passed that you did not see pass.
- For a GitHub issue this PR fully resolves, use a closing keyword (`Closes #123`) so it
  closes on merge
  ([GitHub: linking a PR to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue));
  for partial work or other trackers, a plain "Refs" line.

Keep it as long as the change needs and no longer. A one-line typo fix gets a one-line body.

## 6. Show the draft and save it out of the way

Save the draft where it cannot be committed by accident and where another branch's draft is not
overwritten: inside the git directory, one file per branch.

```bash
draft="$(git rev-parse --git-path cardume/pr-description)/$(git branch --show-current | tr '/' '_').md"
mkdir -p "$(dirname "$draft")"
```

The file holds the body only; the title goes on the command line. If a draft from an earlier
run exists, read it first: the user may have edited it, and their wording wins wherever the
facts have not changed.

Then show the user, in the chat, the title and the full body exactly as they will be
submitted, followed by **one** plain-text question that states the whole proposed action, for
example:

> Create the PR from `feat/refund-webhooks` into `main`, as ready for review, with this title
> and body? I will push the branch first because it has no upstream. Reply "yes", or tell me
> what to change (title, body, base, draft, reviewers).

Choose sensible defaults for that proposal instead of asking one question at a time: draft if
commit messages say WIP or tests are knowingly missing, otherwise ready; the base from step 1;
no reviewers or assignees unless the user asked. When a PR already exists, the question is
whether to replace its title and body.

## 7. Create or update, only after a yes

Do nothing on GitHub until the user confirms. Edits they request go into the draft, and the
updated version is shown again before acting.

Check the CLI is usable with `gh auth status`. If `gh` is missing or not logged in, stop here:
tell the user where the draft file is so they can paste it, and how to authenticate.

Then:

- No upstream yet: `git push -u origin HEAD` (this was part of the confirmed action).
- New PR ([gh pr create](https://cli.github.com/manual/gh_pr_create)):
  `gh pr create --base <base> --title "<title>" --body-file "$draft"`, plus `--draft`,
  `--reviewer`, `--assignee` or `--label` only if agreed.
- Existing PR ([gh pr edit](https://cli.github.com/manual/gh_pr_edit)):
  `gh pr edit <number> --title "<title>" --body-file "$draft"`.

Keep the draft file; it is the starting point if the branch changes and the user runs this
again.

Finish with the PR URL and one line on anything the user should still do, such as filling in a
template field you could not answer or adding the motivation you had to leave as a question.

## When running as a subagent

You cannot ask the user directly. Do steps 1 to 6, then end with the draft and an
**Open questions** section containing the confirmation question and anything you could not
determine (base, motivation, issue links). Stop there; the caller asks the user and runs step 7
only after a yes.

## Things that make a description worse

- Restating the diff file by file. The reviewer has the diff; give them the map and the reasons.
- Copying commit subjects as bullets, including "fix typo" and "address review".
- Vague titles ("updates", "fix bug", "melhorias"). Name the behaviour that changed.
- Invented context: motivation, ticket links, test results or performance numbers that the
  evidence does not support.
