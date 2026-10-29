# Lint rules (Ruff, including Airflow AIR rules)

Ruff replaces flake8 (and its plugins) for DAG code: one fast tool, and it ships rules written for
Airflow's 2 → 3 migration. The Airflow upgrade guide recommends Ruff 0.13.1 or newer for these.

## Contents

1. Configuration
2. AIR rule families and how strict to be
3. Fix workflow
4. Common findings in DAG code
5. `# noqa` policy

---

## 1. Configuration

In `pyproject.toml` (or `ruff.toml`), scoped to DAG and plugin code:

```toml
[tool.ruff]
target-version = "py312"         # match the Airflow runtime's Python
include = ["dags/**/*.py", "plugins/**/*.py", "tests/dags/**/*.py"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "AIR"]
ignore = ["E501"]                # let the formatter own line length
```

Some AIR rules may still be in preview in a given Ruff version; run `ruff rule AIR311` to check,
and add `preview = true` under `[tool.ruff.lint]` (or `--preview`) if a rule you rely on does not
fire. Pin the Ruff version in CI so new rules arrive by a deliberate upgrade, not a surprise red
build.

## 2. AIR rule families and how strict to be

| Codes | What they catch | CI policy |
| :--- | :--- | :--- |
| AIR301 | Names removed in Airflow 3 (e.g. `schedule_interval`, old context keys, removed modules) | **Must fix** — the DAG will not run on Airflow 3 |
| AIR302 | Names moved from core into provider packages in Airflow 3 | **Must fix** — import from the provider and add it to requirements |
| AIR303 | Function signatures changed in Airflow 3 | **Must fix** |
| AIR304 | Runtime-varying values (e.g. `now()`) in DAG/task arguments | **Must fix** — creates a new DAG version every parse |
| AIR311 | Deprecated in Airflow 3, still works, will be removed (e.g. legacy import paths → `airflow.sdk`) | **Should fix** now; fail CI once the team has migrated |
| AIR312 | Moved to a provider, old path still works for now | **Should fix** |
| AIR321 | Moved in Airflow 3.1 | **Should fix** when on 3.1+ |
| AIR001–AIR004 | Hygiene: variable name ≠ `task_id`, missing explicit `schedule`, `Variable.get()` outside a task, branch that could be a short-circuit | Fix; AIR002 and AIR003 are correctness issues for parsing |
| AIR201–AIR202 | XCom/TaskFlow style (`.output` instead of `xcom_pull` in templates, implicit `multiple_outputs`) | Fix when touching the file |

Run the migration-critical subset on its own while upgrading:

```bash
ruff check dags/ plugins/ --select AIR301,AIR302,AIR303,AIR304
```

## 3. Fix workflow

1. **Preview**: `ruff check --select AIR,F401 --diff dags/ plugins/` prints the safe fixes as a
   diff without writing, including imports that a migration would leave unused.
2. **Apply safe fixes in one pass**: `ruff check --select AIR,F401 --fix dags/ plugins/`. Ruff
   repeats fixing until nothing changes, so imports made unused by an AIR rewrite (old paths
   replaced by `airflow.sdk` or a provider) are removed in the same run; no separate clean-up step
   is needed.
3. **Review unsafe fixes one by one**: `ruff check --select AIR --unsafe-fixes --diff dags/` shows
   them without writing; apply after reading the diff. Unsafe fixes can change behavior (renamed
   arguments, context keys with different semantics), so each needs a human look.
4. **Verify**: re-run the integrity test and the full `ruff check` before committing.

## 4. Common findings in DAG code

| Finding | Rule | Fix |
| :--- | :--- | :--- |
| `from airflow import DAG` / `from airflow.decorators import task` | AIR311 | `from airflow.sdk import DAG, task` |
| `schedule_interval="@daily"` | AIR301 | `schedule="@daily"` |
| `DAG(...)` with no `schedule` | AIR002 | Set `schedule=` explicitly (`None` for manual-only) |
| `Variable.get("x")` at module level | AIR003 | Template `{{ var.value.x }}` or read inside the task |
| `start_date=datetime.now()` | AIR304 | Fixed timezone-aware date |
| `load = BigQueryInsertJobOperator(task_id="load_sales")` | AIR001 | Name the variable like the task: `load_sales = ...` |
| Unused import after migration | F401 | Remove |

## 5. `# noqa` policy

- Always name the code and the reason: `# noqa: AIR311 — provider X not yet on Airflow 3 path, see ACME-123`.
- Never a bare `# noqa`, and never on AIR301/302/303/304: those break on Airflow 3.
- Reviewers reject unexplained suppressions; a list of them in a PR is a sign the migration is
  being postponed, which should be a visible decision instead.
