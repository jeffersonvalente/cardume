# pytest patterns for DAGs

All examples run without GCP credentials and without network access. Adjust `DAGS_DIR` and the
expected ids to the repo.

## Contents

1. Shared fixture (`conftest.py`)
2. Integrity test
3. Policy test (properties every DAG must have)
4. Structure test for one DAG
5. Testing task callables and mocking hooks
6. `dag.test()` for local runs
7. Pitfalls

---

## 1. Shared fixture (`tests/dags/conftest.py`)

```python
import functools
import os
import pathlib

import pytest

# Parse-time values the DAGs read; same names as production, safe values.
os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
os.environ.setdefault("AIRFLOW__CORE__UNIT_TEST_MODE", "True")
os.environ.setdefault("AIRFLOW_VAR_ENVIRONMENT", "ci")

try:  # Airflow 3
    from airflow.dag_processing.dagbag import DagBag
except ImportError:  # Airflow 2.x
    from airflow.models import DagBag

DAGS_DIR = pathlib.Path(__file__).resolve().parents[2] / "dags"


@functools.cache
def load_dagbag() -> DagBag:
    return DagBag(dag_folder=str(DAGS_DIR), include_examples=False)


@pytest.fixture(scope="session")
def dagbag() -> DagBag:
    return load_dagbag()
```

The cache parses the folder once per test process, for fixtures and parametrization alike.

## 2. Integrity test (`tests/dags/test_integrity.py`)

```python
import pytest

EXPECTED_DAG_IDS = {"orders_daily", "sales_model_daily"}   # update when adding a DAG


def test_no_import_errors(dagbag):
    # import_errors maps file path -> traceback; print them all, not just the count.
    assert not dagbag.import_errors, "\n\n".join(
        f"{path}:\n{err}" for path, err in dagbag.import_errors.items()
    )


def test_expected_dags_present(dagbag):
    missing = EXPECTED_DAG_IDS - set(dagbag.dag_ids)
    assert not missing, f"DAGs not loaded: {sorted(missing)}"


@pytest.mark.parametrize("dag_id", sorted(EXPECTED_DAG_IDS))
def test_dag_has_tasks(dagbag, dag_id):
    assert dagbag.get_dag(dag_id).tasks, f"{dag_id} has no tasks"
```

A DAG with a cycle fails to load and shows up in `import_errors`, so the first test also covers
cycles.

## 3. Policy test (`tests/dags/test_policy.py`)

One parametrized test enforces team rules on every DAG, including ones added later.

```python
import pytest

from tests.dags.conftest import load_dagbag

REQUIRED_TAG_PREFIXES = ("layer:", "team:")   # configurable team convention
ALL_DAGS = [load_dagbag().get_dag(dag_id) for dag_id in sorted(load_dagbag().dag_ids)]


@pytest.fixture(params=ALL_DAGS, ids=lambda d: d.dag_id)
def dag(request):
    return request.param


def test_catchup_is_explicit(dag):
    # The default changed between Airflow 2 (True) and 3 (False); state it in code.
    source = open(dag.fileloc, encoding="utf-8").read()
    assert "catchup=" in source, f"{dag.dag_id}: set catchup explicitly"


def test_has_schedule(dag):
    assert "schedule=" in open(dag.fileloc, encoding="utf-8").read(), f"{dag.dag_id}: set schedule"


def test_tags(dag):
    assert dag.tags, f"{dag.dag_id}: add tags"
    for prefix in REQUIRED_TAG_PREFIXES:
        assert any(t.startswith(prefix) for t in dag.tags), f"{dag.dag_id}: missing tag {prefix}*"


def test_owner_and_retries(dag):
    for t in dag.tasks:
        assert t.owner and t.owner != "airflow", f"{dag.dag_id}.{t.task_id}: set owner in default_args"
        assert t.retries >= 1, f"{dag.dag_id}.{t.task_id}: set retries >= 1"
```

The source checks for `catchup=` and `schedule=` are deliberately simple: the parsed value of
`catchup` is always a boolean, so only the source shows whether someone chose it. Ruff AIR002 also
enforces an explicit `schedule`.

## 4. Structure test for one DAG (`tests/dags/test_orders_daily.py`)

```python
def test_orders_daily_structure(dagbag):
    dag = dagbag.get_dag("orders_daily")
    assert set(dag.task_ids) == {"fetch_config", "load_orders", "check_orders"}
    assert dag.get_task("load_orders").upstream_task_ids == {"fetch_config"}
    assert dag.get_task("check_orders").upstream_task_ids == {"load_orders"}


def test_load_orders_is_configured(dagbag):
    load = dagbag.get_dag("orders_daily").get_task("load_orders")
    query = load.configuration["query"]
    assert query["useLegacySql"] is False
    assert "{{" in query["query"], "SQL should be templated, not fetched at parse time"
```

These assert on operator arguments; nothing is sent to BigQuery.

## 5. Testing task callables and mocking hooks

Keep logic in plain functions (or `@task` functions) and test them directly:

```python
from unittest import mock

from dags.orders_daily import fetch_config


def test_fetch_config_raises_on_http_error():
    with mock.patch("requests.get") as get:
        get.return_value.raise_for_status.side_effect = RuntimeError("503")
        try:
            fetch_config.function()       # .function is the undecorated callable
        except RuntimeError:
            pass
        else:
            raise AssertionError("expected the task to fail on HTTP errors")
```

For code that uses a provider hook, patch the hook class where the module imports it
(`mock.patch("dags.common.loaders.BigQueryHook")`) and assert on the calls. Never construct a real
client in CI.

## 6. `dag.test()` for local runs

```python
if __name__ == "__main__":
    dag.test()   # python dags/orders_daily.py
```

`dag.test()` runs every task in one process against the local metadata DB, with real connections:
use it on a developer machine pointed at the dev project, never in CI. It is the quickest way to
debug a DAG end to end; `airflow tasks test DAG_ID TASK_ID 2026-10-27` does the same for one task
without recording state.

## 7. Pitfalls

| Pitfall | Effect | Fix |
| :--- | :--- | :--- |
| `include_examples=True` (or default load_examples) | Slow, unrelated example failures | `include_examples=False` and `AIRFLOW__CORE__LOAD_EXAMPLES=False` |
| Hardcoded "today" dates in tests | Tests break next month | Fixed past dates or relative to `start_date` |
| Asserting only `len(import_errors) == 0` | Failures show no traceback | Print every error (§2) |
| Building a new `DagBag` per test | Minutes of repeated parsing | Session fixture |
| Tests or CI steps that call BigQuery or need a key/ADC | CI is credential-free by design; such steps fail, cost money, or tempt someone to add a key | Build operators without executing them and assert on their arguments; mock hooks where a callable must run |
| One giant test for all DAGs | First failure hides the rest | Parametrize by DAG id |
| Checking query output, row counts or SQL logic in pytest | Needs a warehouse, still proves nothing about production data | Dry runs and before/after data checks (`cardume-data:bigquery-patterns`) |
| Re-testing the scheduler, executor or a provider operator's internals | Slow tests of code you do not own | Trust upstream tests; assert only on the arguments your DAG passes |
