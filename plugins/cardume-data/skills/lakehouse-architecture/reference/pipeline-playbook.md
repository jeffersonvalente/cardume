# Pipeline playbook

Companion to `cardume-data:lakehouse-architecture`. It follows one model through its life:
**source → staging → marts → tests and docs**, then covers changing a model (§6), reporting (§7),
orchestration (§8) and debugging (§9). Section numbers are cited by the skill; keep them stable.
"Reference §N" below means `reference/sql-patterns.md` §N in `cardume-data:bigquery-patterns`.

It maps the medallion layers onto the dbt project structure most teams already know, and the gold
layer onto Kimball dimensional modeling. If the project uses Dataform, SQL files run by Airflow, or
another tool, the same stages apply with different file names. The rules file's values (dataset
names, prefixes, governance file, environments) always win over the defaults here.

Sources: dbt "How we structure our dbt projects" and testing/contracts docs; Kimball Group
dimensional modeling techniques; Databricks medallion architecture; Google Cloud BigQuery and
Cloud Composer best-practice docs.

## 1. Lifecycle map

| Stage | Medallion layer | dbt folder / prefix | Responsibility | Done when |
| :--- | :--- | :--- | :--- | :--- |
| Source | Bronze (`*_raw`) | `sources:` in YAML | Land data as delivered, add load metadata | Freshness and row-count checks pass |
| Staging | Silver (`*_clean`) | `models/staging/<source>/stg_<source>__<object>` | Rename, cast, normalize nulls, dedupe; 1:1 with a source object | Grain test passes; cast failures counted |
| Intermediate | Silver or gold (internal) | `models/intermediate/int_<entity>_<verb>` | Reusable joins and business logic, not exposed | Used by ≥ 1 mart; not queried by BI |
| Marts | Gold (`*_mart`) | `models/marts/<domain>/dim_*`, `fct_*` | Conformed dimensions and facts | Grain, keys and relationships tested |
| Serve | Consumption (`*_serve`) | views or exposures | Audience-specific shape | Reads gold only |

Each model has exactly one stage. A model that both cleans source columns and applies business
rules cannot be tested for either; split it.

## 2. Source

- **Declare it.** Every external table the pipeline reads appears once in a source declaration
  (dbt `sources:`, Dataform `declarations`, or a documented list in the repo). Undeclared reads
  are invisible to lineage and to freshness checks.
- **Land as delivered.** Bronze columns are `STRING` (or `JSON`), append-only, partitioned by
  ingestion date, with `_ingested_at` and `_source_file` / `_batch_id`. This makes bronze a replay
  log: a parsing bug is fixed by rebuilding silver, not by re-extracting.
- **Freshness.** Define how late the source may be (dbt `freshness: warn_after / error_after` on a
  `loaded_at_field`, or an Airflow sensor/check). A pipeline that runs green on yesterday's file is
  the most common silent failure.
- **Volume.** Compare today's row count with the trailing average; a drop beyond the tolerance in
  the rules file (default: flag when below 50% of the 7-day median) stops downstream models.

## 3. Staging

One staging model per source object, and only these operations:

- rename to `snake_case` and the column conventions (`_id`, `_key`, `_date`, `_at`, `_amount`);
- cast with `SAFE_CAST` / `SAFE.PARSE_*` and count failures (`cardume-data:bigquery-patterns`
  reference §4);
- normalize empty strings and sentinel values to `NULL`;
- deduplicate to one row per business key (reference §5);
- add `record_source` (or the rules file's `origin_column`).

No joins between sources and no business rules here. Staging is materialized as a view when it is
cheap to recompute, or as an incremental table partitioned on a business date when the source is
large.

## 4. Marts (Kimball)

Design in the Kimball order: **business process → grain → dimensions → facts**.

**Facts** (`fct_<process>`): one table per business process at the most atomic grain available.
Choose the fact type explicitly:

| Fact type | Grain | Typical measures | Load pattern |
| :--- | :--- | :--- | :--- |
| Transaction | one row per event/line | additive amounts, quantities | append or partition MERGE |
| Periodic snapshot | one row per entity per period | balances, levels (semi-additive) | replace the period partition |
| Accumulating snapshot | one row per process instance | milestone dates, lag measures | MERGE on the instance key |
| Factless | one row per event or coverage | counts only | append |

Semi-additive measures (balances) must not be summed across time; say so in the column
description. Degenerate dimensions (order number on an order-line fact) stay in the fact.

**Dimensions** (`dim_<entity>`): wide, descriptive, conformed (one `dim_customer` shared by every
fact that mentions customers). Pick the slowly-changing-dimension type per attribute:

| SCD type | Behavior | Use when |
| :--- | :--- | :--- |
| 0 | never changes | original values (signup date) |
| 1 | overwrite | corrections; history irrelevant |
| 2 | new row with `valid_from` / `valid_to` / `is_current` | history must be reproducible (region at time of sale) |

dbt snapshots implement Type 2 from a staging model (`strategy: timestamp` or `check`). Facts join
to a Type 2 dimension on the natural key and the event date within the validity window, or on the
surrogate key captured at load time.

**Keys:** deterministic surrogate keys (hash of the natural key, plus `valid_from` for Type 2) so
rebuilds produce the same values; an unknown member for late or missing references.

**Bus matrix:** keep a table of processes (rows) × conformed dimensions (columns) in the docs. It
shows which facts can be compared, and which dimension a new fact must reuse instead of copying.

## 5. Tests and docs

Every mart ships with tests and descriptions in the same change. Minimum per model:

| Test | Where | Catches |
| :--- | :--- | :--- |
| `unique` + `not_null` on the grain key(s) | every staging model, dim and fact | duplicates, fan-out |
| `relationships` from each fact FK to its dimension | facts | orphans (or count rows routed to unknown) |
| `accepted_values` on status/type columns | staging and dims | new source codes nobody mapped |
| Row-count / sum reconciliation against the previous layer | facts | rows lost or doubled in joins |
| Freshness | sources | stale inputs |

Severity: `error` for grain and key tests (they block the run), `warn` for drift signals.
In dbt 1.8+ add **unit tests** for non-trivial transformations (fixed input rows → expected
output) and **model contracts** (`contract: enforced: true`) on marts that other teams consume, so
a column type or name change fails the build instead of a dashboard. Without dbt, the same checks
are SQL assertions run after each load (`cardume-data:bigquery-patterns` reference §1–3).

Docs: the schema governance file (the rules file names it) holds one description per model and
per column, including the grain sentence, units and currency, and the SCD type for dimension
attributes. BigQuery column descriptions are populated from it (dbt `persist_docs`), so the catalog
and lineage views show the same text.

## 6. Changing a model

A change is safe when every model and consumer downstream of it has been looked at. Find them
before editing:

- **Graph selection**: with dbt, `dbt ls --select <model>+` lists every downstream node;
  `--select state:modified+` with the production manifest lists what a branch changes. Without
  dbt, search the repo for the table name and every explicit column list that selects from it.
- **Outside the repo**: lineage in Knowledge Catalog (Data Lineage API), views in
  `INFORMATION_SCHEMA.VIEWS`, scheduled queries, and BI sources named in the rules file.

Then classify the change and treat each class accordingly:

| Change | Risk | Handling |
| :--- | :--- | :--- |
| Add a column | Low, but often stops one layer short | carry it through each downstream model that should expose it, describe it in the governance file, and show it arrives (fill % per layer) |
| Rename / retype | Breaks consumers | add the new column, keep the old one as an alias for a deprecation period, announce, then remove; contracts and versions (dbt `versions:`) make this explicit |
| Change grain or join | Changes numbers | before/after profile (reference §1) and grain test; quantify each difference |
| Remove | Breaks consumers | confirm no dependents remain, then drop in a separate change |

Backfills: rebuild only the affected partitions, oldest first, idempotently (§8), and profile the
result against the pre-change snapshot.

## 7. Report shape for an analysis

Use this order when presenting a design, an investigation or a change:

1. **Answer** — the diagnosis or design in two or three sentences.
2. **Environment** — project and dataset the numbers came from; time window.
3. **Evidence** — the queries run and their results (counts, sums, grain test output), trimmed.
4. **Change** — files and models touched, with the stage of each (§1).
5. **Verification** — tests run and their outcome; before/after profile.
6. **Impact** — downstream models and consumers found (§6), and who should be told.
7. **Open items** — what still needs a decision or a check, and by whom.

## 8. Orchestration and idempotency

- **One task, one model or one stage**, so a failure is visible at the right place and a rerun
  repeats only that piece. With dbt in Airflow, run `dbt build --select <tag or path>` per stage,
  or one task per model with a tool such as Cosmos when the graph is small enough to display.
- **Parameterize by the logical date**, never `CURRENT_DATE()` inside the SQL. A rerun of
  2026-10-27 must produce exactly what the original run should have produced.
- **Idempotent writes**: partition replace or MERGE on the business key (`cardume-data:bigquery-patterns`
  reference §10, §15). An `INSERT` without a delete is a duplicate waiting for a retry.
- **Retries** with backoff for transient errors; no retries for data-quality failures (they will
  fail the same way).
- **Ordering across DAGs** with datasets/assets or explicit sensors, not with schedule offsets
  ("run at 06:30 because the load usually finishes by 06:00").
- DAG tests and CI: `cardume-data:airflow-testing`.

## 9. Debugging a wrong number

Walk the lifecycle backwards and stop at the first stage where the number is already wrong:

1. Reproduce the wrong value in serve/marts with the exact filter the user sees.
2. Compute the same measure from the fact table alone, then from the staging model it reads, then
   from bronze. The stage where the value diverges owns the bug.
3. At that stage, check the usual suspects in this order: grain broken (duplicates, reference §2),
   join fan-out or orphans (reference §3), cast failures (reference §4), late or missing source data (freshness, row
   counts by ingestion date), and a filter that changed.
4. Check history: `INFORMATION_SCHEMA.JOBS_BY_PROJECT` for the job that last wrote the table, and
   time travel to compare the table before and after that job (reference §14).

State which stage owns the bug and the query that proves it before proposing a fix.
