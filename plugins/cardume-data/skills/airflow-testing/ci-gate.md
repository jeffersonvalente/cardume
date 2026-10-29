# CI gate for DAG repositories

Four steps, in order, each cheap enough to run on every pull request. Later steps assume earlier
ones passed, so fail fast.

| Step | Catches | Command core |
| :--- | :--- | :--- |
| 1. Constrained install + `pip check` | Provider/core version conflicts, missing packages | `pip install -c constraints.txt ...` then `pip check` |
| 2. Parse / integrity | Import errors, cycles, missing DAGs, slow parses | `pytest tests/dags/test_integrity.py` (optional `airflow dags reserialize`) |
| 3. Lint | Airflow 3 incompatibilities, top-level `Variable.get`, unused imports | `ruff check` with `AIR` |
| 4. Tests | Structure and logic regressions | `pytest -n auto` |

No step has GCP credentials. If a test needs them, the test is wrong (see `pytest-patterns.md`).

## 1. Install with constraints, then `pip check`

Install exactly what the target environment runs:

- **Self-managed Airflow**: the official constraints file for the Airflow and Python version,
  `https://raw.githubusercontent.com/apache/airflow/constraints-<airflow-version>/constraints-<python-version>.txt`.
- **Cloud Composer / Managed Airflow**: the package list of the environment's image (Composer
  publishes it per version) exported as `constraints.txt` in the repo, plus the PyPI packages the
  environment adds.

`pip check` then fails the build on any broken requirement, which is the same conflict the
environment would hit when the packages are installed there.

## 2. Parse / integrity

Run the integrity tests first, separately, so a parse failure is the first and clearest red mark.
For an extra check of serialization (what the dag-processor stores), migrate a throwaway SQLite DB
and reserialize:

```bash
export AIRFLOW_HOME="$RUNNER_TEMP/airflow" AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__DAGS_FOLDER="$PWD/dags"
airflow db migrate
airflow dags reserialize
```

## 3. Lint

```bash
ruff check dags/ plugins/ tests/dags/
ruff format --check dags/ plugins/ tests/dags/   # only if the repo uses the Ruff formatter
```

Policy for which AIR codes fail the build is in `lint-rules.md` §2.

## 4. Tests

```bash
pytest tests/ -n auto -q          # pytest-xdist; the DagBag is cached per worker
```

## Example workflow (GitHub Actions)

```yaml
name: dags-ci
on:
  pull_request:
    paths: ["dags/**", "plugins/**", "tests/**", "requirements*.txt", "constraints.txt", "pyproject.toml"]

jobs:
  check:
    runs-on: ubuntu-latest
    env:
      AIRFLOW__CORE__LOAD_EXAMPLES: "False"
      AIRFLOW__CORE__UNIT_TEST_MODE: "True"
      AIRFLOW_VAR_ENVIRONMENT: ci          # same variable names as prod, safe values
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"           # match the runtime
      - name: Install (constrained) and check dependencies
        run: |
          pip install -r requirements.txt -r requirements-dev.txt -c constraints.txt
          pip check
      - name: Parse and integrity
        run: pytest tests/dags/test_integrity.py -q
      - name: Lint
        run: ruff check dags/ plugins/ tests/dags/
      - name: Tests
        run: pytest tests/ -n auto -q
```

`requirements-dev.txt` holds `pytest`, `pytest-xdist` and a pinned `ruff`. Keep the action versions
pinned the way the repo pins its other workflows.

## When the gate fails

| Failure | Usual cause | Next step |
| :--- | :--- | :--- |
| `pip check` | A provider version incompatible with the core or another provider | Align with the environment's package list; do not loosen constraints to pass |
| `import_errors` non-empty | Missing package, syntax error, top-level call failing without network | Read the printed traceback; for top-level calls see `dag-parse.md` §3 |
| Expected DAG missing | DAG id changed, or the DAG object is created inside a function never called | Fix the id list or the file |
| AIR301/302 | Code written for Airflow 2 | Fix per `lint-rules.md` §4 |
| Tests time out | Network calls in tests or parse | Mock them; move them out of top level |
