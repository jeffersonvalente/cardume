---
name: airflow-testing
description: "Testing and CI for Airflow DAGs (Airflow 3 with 2.x notes, Cloud Composer): DagBag parse tests, DAG property tests, top-level code hazards, Ruff AIR rules, credential-free CI. Use when adding or reviewing a DAG, writing DAG tests or setting up DAG CI."
allowed-tools: Read Grep Glob
---

# Airflow DAG testing

A DAG file is code the scheduler executes over and over, not just when the DAG runs. If it fails to
parse, the DAG vanishes from the UI and nothing runs; if it is slow to parse, every DAG in the
environment is delayed. So the first job of DAG tests is to prove that each file parses quickly,
cleanly and identically in every environment. Behavior tests come second. The detail is in the
sibling files:

| File | Contents |
| :--- | :--- |
| `dag-parse.md` | What runs at parse time, top-level code rules, parse-time budget |
| `pytest-patterns.md` | Integrity test, property tests, `dag.test()`, mocking, fixtures |
| `lint-rules.md` | Ruff configuration, AIR rule families and how to fix them |
| `ci-gate.md` | The four CI steps with a ready workflow |

Related: `cardume-core:python-patterns` (general Python), `cardume-data:lakehouse-architecture`
(what the DAG should build), `cardume-data:bigquery-patterns` (the SQL it runs).

## 1. Know the Airflow version

Read the version from the repo (requirements, `constraints`, Docker image, Composer image string
like `composer-3-airflow-3.x.y`). This skill targets **Airflow 3** (current docs: 3.3) and flags
2.x differences:

| Topic | Airflow 3 | Airflow 2.x |
| :--- | :--- | :--- |
| Who parses DAGs | The separate **dag-processor** component (`airflow dag-processor`) | The scheduler (by default) |
| Authoring imports | `from airflow.sdk import DAG, dag, task, Variable, ...` (old paths deprecated) | `from airflow import DAG`, `airflow.decorators` |
| `DagBag` import | `from airflow.dag_processing.dagbag import DagBag` | `from airflow.models import DagBag` |
| `catchup` default | `False` (`catchup_by_default`) | `True` |
| `schedule` | `schedule=` only | `schedule_interval=` also accepted |
| Serializing DAGs into a test DB | `airflow dags reserialize` (`airflow db migrate` only migrates the schema) | parsing on `db upgrade`/`migrate` in some versions |

Tests should import `DagBag` with a fallback so they survive the upgrade (see
`pytest-patterns.md` §1).

## 2. Non-negotiables

- **Zero unparseable DAGs.** CI must be green before review; a DAG with an import error is a
  production outage waiting for a merge.
- **No masking.** No `try/except ImportError` around DAG imports to "keep the file loading", and no
  `# noqa` without a reason in the same comment. Masking turns a loud failure into a missing DAG.
- **No network, database or cloud calls at module top level.** HTTP requests, `Variable.get()`,
  `Connection` lookups, BigQuery/GCS client calls and heavy imports outside a task run on every
  parse (every ~30 s by default), in every dag-processor, and in CI. They slow the whole
  environment, fail when the endpoint is down, and make the parse test depend on the network. Move
  them into a task, into a templated field (`"{{ var.json.sales_config.sql }}"`), or into an
  operator argument resolved at runtime. See `dag-parse.md`.
- **Same parse everywhere.** Any environment variable a DAG reads at parse time must also be set in
  CI with a safe value, so CI parses the same code path prod does.
- **Deterministic DAG arguments.** No `datetime.now()` / `pendulum.now()` in `start_date` or other
  DAG/task arguments: each parse produces a new DAG version (Ruff AIR304).

## 3. Minimum tests for every DAG

1. **Integrity (all DAG files at once)**: `DagBag(dag_folder=..., include_examples=False)` has no
   `import_errors`; each expected `dag_id` is present; each DAG has at least one task. Cycles are
   detected during the bag load and show up as import errors.
2. **Properties (per DAG or as a parametrized policy test)**: `catchup` set explicitly in code,
   `schedule` set, `tags` non-empty, `owner` set and not the default `airflow`, `retries` ≥ 1 (via
   `default_args` or per task), expected task ids and dependencies.
3. **Parse time**: each file imports in under a budget (default 2 s in CI; configurable).

`pytest-patterns.md` has the code. Use `dag.test()` for a local end-to-end run of a DAG against a
test metadata DB and dev resources; it is an integration test, not a CI unit test.

## 4. What not to test

Keep DAG tests about the DAG file: whether it parses and whether its structure matches intent. Data
correctness, Airflow's own machinery and anything that needs cloud credentials belong elsewhere;
the pitfalls table in `pytest-patterns.md` §7 lists each trap with what to do instead.

## 5. CI gate (summary)

1. **Install with constraints, then `pip check`** — catches provider/core conflicts before they
   reach the environment.
2. **Parse/integrity** — the DagBag test (optionally `airflow dags reserialize` against a throwaway
   SQLite DB).
3. **Lint** — `ruff check` with the `AIR` rules on DAG and plugin code. AIR301/AIR302 (removed in /
   moved out of Airflow 3) must be fixed; AIR311/AIR312 (deprecated, still working) should be
   fixed; AIR0xx/AIR2xx are hygiene.
4. **Tests** — `pytest -n auto`, no cloud credentials.

Ready-to-adapt workflow in `ci-gate.md`.

## 6. Default layout

Follow the repo's existing layout when there is one. Otherwise:

```
dags/                       # DAG files only; shared code in dags/common/ or a package
plugins/                    # custom operators/hooks
tests/dags/conftest.py      # DagBag fixture, env defaults
tests/dags/test_integrity.py
tests/dags/test_<dag_id>.py # structure tests for DAGs that need more than the policy test
```

## 7. Reviewer gates

When reviewing a PR that adds or changes DAGs (used by `lakehouse-reviewer`):

- [ ] CI ran all four steps and is green.
- [ ] A new DAG is covered by the integrity test (expected id list updated) and, if it has
      branching or dynamic tasks, by its own structure test.
- [ ] No top-level network/DB/Variable calls; no `datetime.now()` in DAG arguments.
- [ ] Every `# noqa` names the rule and the reason.
- [ ] Lint scope is DAG and plugin code, not the whole repo's unrelated scripts.
- [ ] Imports use `airflow.sdk` (Airflow 3) or there is a noted reason to stay on legacy paths.
