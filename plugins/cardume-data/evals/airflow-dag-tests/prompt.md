---
name: airflow-dag-tests
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

I'm adding this DAG to our Composer repo. What tests and CI checks should it have? Show the pytest code.

```python
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime
import requests

cfg = requests.get("https://config.internal/dags/sales").json()

with DAG("sales_daily", start_date=datetime(2024, 1, 1), schedule="@daily") as dag:
    load = BigQueryInsertJobOperator(
        task_id="load_sales",
        configuration={"query": {"query": cfg["sql"], "useLegacySql": False}},
    )
```
