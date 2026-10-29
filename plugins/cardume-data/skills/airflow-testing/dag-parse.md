# DAG parsing: what runs, and when

## Contents

1. Parse lifecycle
2. Top-level code rules
3. Moving a top-level call out (worked example)
4. Parse-time budget
5. Environment parity

---

## 1. Parse lifecycle

In Airflow 3 the **dag-processor** imports every file in the DAGs folder on a loop
(`[dag_processor] min_file_process_interval`, 30 s by default), serializes the DAGs it finds and
stores them in the metadata DB. The scheduler and API server work from the serialized form; workers
re-import the file when they run a task. So module-level code runs:

- on every parse loop, in every dag-processor;
- on every task execution, in the worker;
- in CI, whenever the integrity test builds a `DagBag`.

Only code inside a task's callable / an operator's `execute()` (and Jinja templates) runs at task
run time, once.

## 2. Top-level code rules

| At module level, avoid | Why | Instead |
| :--- | :--- | :--- |
| HTTP calls (`requests.get`, API clients) | Slows every parse; parse fails when the endpoint is down; CI needs network | Fetch inside a task; or store config in a Variable/file read at run time |
| `Variable.get()`, `Connection.get()` / `BaseHook.get_connection()` | A metadata-DB or secrets-backend round trip per parse (Ruff AIR003) | Jinja: `{{ var.value.x }}`, `{{ var.json.cfg.key }}`, `{{ conn.my_conn.host }}`; or call inside the task |
| Cloud SDK calls (BigQuery, GCS clients) | Need credentials at parse; cost; latency | Operators/hooks, which call at run time |
| Heavy imports (`pandas`, ML libs) only used by one task | Import time added to every parse | Import inside the task function |
| `datetime.now()` / `pendulum.now()` in DAG/task args | New DAG version every parse (AIR304) | Fixed `start_date=pendulum.datetime(2026, 1, 1, tz="UTC")` |
| Reading large files, generating thousands of tasks from a DB query | Parse time and memory | Generate from a static config file in the repo |

Small, static work is fine: constants, reading a small YAML that ships with the DAG, building task
lists from it.

## 3. Moving a top-level call out (worked example)

Before: the DAG reads its SQL from an Airflow Variable when the file is imported.

```python
from airflow.sdk import Variable
cfg = Variable.get("orders_config", deserialize_json=True)   # DB/secrets round trip on every parse
```

Options, in order of preference:

1. **Ship the config with the code** (`dags/config/orders.yaml`, reviewed in the PR). Parse reads a
   local file; no network.
2. **Airflow Variable + template**, resolved only when the task runs:

   ```python
   from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

   load = BigQueryInsertJobOperator(
       task_id="load_orders",
       configuration={"query": {"query": "{{ var.json.orders_config.sql }}", "useLegacySql": False}},
   )
   ```

   (`configuration` is a templated field of `BigQueryInsertJobOperator`.) The template is rendered
   when the task runs, so the parse never touches the metadata DB or secrets backend.
3. **Read it in a task and pass via XCom**, when later tasks need values the template cannot reach:

   ```python
   from airflow.sdk import Variable, task

   @task
   def read_config() -> dict:
       return Variable.get("orders_config", deserialize_json=True)
   ```

   and feed `read_config()["sql"]` into the load task (XCom is fine for small payloads only).

SQL kept in a Variable can be changed without review and runs against the warehouse; option 1
keeps it in code review.

## 4. Parse-time budget

Measure each file in CI:

```python
import importlib.util, pathlib, time

def parse_seconds(path: pathlib.Path) -> float:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    start = time.perf_counter()
    spec.loader.exec_module(module)
    return time.perf_counter() - start
```

Default budget: 2 s per file in CI (configurable). CI runners are slower than dag-processors, so a
file near the limit in CI is comfortable in production, and anything above it almost always means a
top-level call or heavy import. `airflow dags report` also prints per-file parse durations.

## 5. Environment parity

- Any `os.environ[...]` or `Variable` the file reads at parse time needs a value in CI. Set safe
  defaults in `tests/dags/conftest.py` (or the CI env block), e.g. `AIRFLOW_VAR_ENVIRONMENT=ci`,
  mirroring the names prod uses.
- Prefer `os.environ.get("X", "dev")` with a safe default over `os.environ["X"]` in DAG files, so a
  missing variable degrades to a known path instead of an import error.
- Pin the same Airflow and provider versions as the target environment (the Composer image's
  package list, or the constraints file).
