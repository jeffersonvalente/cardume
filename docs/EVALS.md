# Evals

Every plugin ships behavioral eval cases for `claude plugin eval`, in `plugins/<plugin>/evals/`.
There are 40 cases across the seven plugins. This page explains what they measure, what they do not,
and how to run them.

## What a case looks like

Each case is a folder with a realistic prompt and a set of graders:

```text
plugins/cardume-core/evals/level1-risky-escalation/
├── prompt.md          # frontmatter (tags, runs, max_turns, allowed tools) + the user's request
└── graders/
    └── escalated.md   # one grader per file
```

Three kinds of grader are used:

| Grader | Checks | Example |
| --- | --- | --- |
| `tool_used` | whether a tool was called, and with what input | the `terraform-stacks` skill loaded; `terraform apply` was **never** run (`max: 0`); no spec skill fired for a typo |
| `llm` | the answer against a written PASS/FAIL rubric, scored by a judge model | a "one-line" change to who can issue refunds is classified as at least level 1 and comes with acceptance criteria |
| `regex` | a pattern in the final message | the corrected sentence is present |

Cases are tagged by what they test: `trigger` (the right skill fires), `negative` (nothing fires
for a request outside the plugin's domain, or no spec for a typo), `levels` (work-level
classification), `safety` (no destructive command runs), and a few more.

By default `claude plugin eval` runs each case in two arms, with the plugin and without it, and reports the
score difference. That baseline is the point: a skill that does not beat plain Claude on its own
domain is not earning its context cost.

## What they measure

- **Routing:** whether the matching skill fires for a realistic request, and whether nothing fires
  when it should not.
- **Answer quality:** whether the final answer meets the case's rubric, compared with the same model
  without the plugin.
- **Behavioral safety:** in the cases that allow `Bash`, that Claude does not run `terraform apply`,
  publish a release or open GitHub issues without confirmation.

## What they do not measure

- **The hooks.** `stop_verify`, `guard_bash` and the other hooks are deterministic scripts; no eval
  case exercises them end to end. Read them in
  [`plugins/cardume-core/hooks/`](../plugins/cardume-core/hooks/) and see [SAFETY.md](SAFETY.md).
- **Edits to a real codebase.** Each case is one request with a turn limit and no project fixture.
  37 of the 40 cases allow only `Read`, `Glob`, `Grep` and `Skill` (three also allow `Bash`), so they
  grade what Claude says and which skills it loads, not files it writes.
- **Long projects.** A full level-3 delivery (PRD to release) is not run end to end.
- **The installed `CLAUDE.md` block.** The four work-level cases inject the level rules through the
  case's `append_system_prompt` instead of running `/cardume-core:setup` first.
- **Exact correctness.** `llm` graders are scored by a judge model, so a borderline answer can flip
  between runs. Every case runs three times (`runs: 3`) to reduce that noise, not remove it.

No pass rates are published yet. When there are numbers, they will come from the CI workflow below,
with the model and judge named.

## Run them locally

From a plugin folder:

```bash
cd plugins/cardume-qa
claude plugin eval . --runs 3 --no-publish
```

Useful options: `--case <glob>` to run one case, `--tag trigger` to run only routing cases,
`--json results.json` for the full per-run result, and `--max-cost-usd <n>` for a hard spending
limit. Each run is a real Claude session on your own credentials, so it costs money. Results go to
`evals/results/`, which is ignored by git.

To score routing on its own, run the `trigger` cases in a single arm. In the default two-arm mode,
`tool_used: Skill` graders are reported only as an indicator that the plugin fired, not as part of
the score:

```bash
claude plugin eval . --ablation none --tag trigger --runs 3 --no-publish
```

## In CI

The [Evals workflow](../.github/workflows/evals.yml) runs every week and on demand (Actions → Evals →
*Run workflow*):

- it needs the `ANTHROPIC_API_KEY` repository secret, and skips the run without it;
- each plugin runs the full suite with the baseline, then the `trigger` cases in a single arm, so a
  broken route fails the job;
- the judge is Sonnet, with a pass threshold of 0.67;
- spending is capped at US$ 14 per plugin per run (US$ 8 for the full suite, US$ 6 for the trigger
  run), and only one run happens at a time;
- results are scanned for credential-like strings before they are uploaded as artifacts.

## Adding a case

A new model-invoked skill needs at least one case. Copy an existing folder, write a prompt a real
user would send, and add a `tool_used` grader for the skill plus an `llm` grader with a concrete
PASS/FAIL rubric. See [CONTRIBUTING.md](../CONTRIBUTING.md).
