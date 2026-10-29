---
type: llm
focus: last_message
weight: 2
---

PASS if it provides pytest code for a DagBag import/parse test (no import_errors, DAG id present, expected tasks), and checks of DAG properties (catchup explicitly set, default_args/retries/owner, tags, no cycles). It must flag the top-level `requests.get` as a parse-time network call that slows/breaks the scheduler and makes the parse test flaky, and recommend moving it into a task/Variable/templated config. It should also mention CI steps such as dependency validation, ruff lint (incl. Airflow AIR3xx rules), and running tests without GCP credentials (mocking or not executing BigQuery).
FAIL if it only shows a generic DagBag test and does not mention the top-level network call.
