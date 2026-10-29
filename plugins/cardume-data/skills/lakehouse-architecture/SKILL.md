---
name: lakehouse-architecture
description: "Medallion lakehouse design on BigQuery: layer contracts, naming, dimensional modeling (dim_/fct_ defaults), lineage and change propagation. Use when designing, extending, debugging or reviewing layered pipelines, datasets, dimensions or fact tables."
allowed-tools: Read Write Edit
---

# Lakehouse architecture on BigQuery

The point of a lakehouse is that people can trust a number in the gold layer without knowing how
it was built. Two disciplines make that possible: **dimensional modelling**, which fixes what one
row means, and **layer contracts**, which fix what each layer promises to whoever reads it. This
skill covers both and how to change a model without breaking either. The step-by-step life of a
model (source, staging, marts, tests, orchestration, debugging) is in
`reference/pipeline-playbook.md` (cited as playbook §N); SQL, cost and integrity queries are in
`cardume-data:bigquery-patterns`.

The project's rules file (`CLAUDE.md`, `docs/standards.md`) wins over every default here: dataset
names, prefixes, environments, the schema governance file and the modelling tool (dbt, Dataform,
plain SQL run by Airflow).

## 1. Dimensional modelling (Kimball)

Design every mart in this order; skipping a step is how marts end up with ambiguous rows.

1. **Business process.** Name the event the organisation measures (an order line is placed, a
   payment settles, a stock level is counted), not a report or a department.
2. **Grain.** Write one sentence that says what one row is: "one row per order line per order
   version". The grain is declared before any column is chosen, and every later decision is
   checked against it. If two facts are needed to describe it, there are two business processes.
3. **Dimensions.** The who, what, where, when and how around the event. Each becomes a `dim_`
   table keyed by a surrogate key.
4. **Facts.** The numeric measures true at that grain. A measure that is only true at a coarser
   grain (an order-level shipping fee on an order-line fact) is either allocated with a stated
   rule or kept in its own fact.

**Fact types.** Choose one explicitly and say it in the model description (detail and load
patterns in playbook §4):

- **Transaction**: one row per event; measures are fully additive.
- **Periodic snapshot**: one row per entity per period; levels and balances are semi-additive and
  must never be summed across time.
- **Accumulating snapshot**: one row per process instance, updated as milestones happen; good for
  lags between steps.
- **Factless**: records that something happened or was eligible; counts only.

**Conformed dimensions.** One `dim_customer`, `dim_product` and `dim_date` shared by every fact
that mentions customers, products or dates, with the same keys and attribute values. Conformance
is what lets two facts be compared side by side ("drill across"). A team that copies a dimension
into its own mart with slightly different rules has created two answers to the same question.
Keep a bus matrix (business processes × conformed dimensions) in the docs; a new fact reuses the
dimensions its row in the matrix names.

**Slowly changing dimensions.** Decide per attribute, not per table:

- **Type 0** keeps the original value (first purchase date).
- **Type 1** overwrites; history of that attribute is lost, which is right for corrections.
- **Type 2** adds a new row with validity dates and a current flag, so a fact can be reported with
  the attribute as it was at the time of the event (the customer's region when the order was
  placed).

Facts must join a Type 2 dimension on the surrogate key captured at load time, or on the natural
key plus the event date inside the validity window. Joining on the natural key alone multiplies
fact rows by the number of versions.

**Keys.** Deterministic surrogate keys (a hash of the natural key, plus the validity start for
Type 2) so rebuilds reproduce them; an explicit unknown member (`-1` or a hash of `'unknown'`) so a
late or missing reference keeps its fact row instead of vanishing in an inner join. Degenerate
dimensions such as an order number stay on the fact.

## 2. Layer contracts

Each layer makes promises to its readers. A layer that breaks its promise without saying so is the
root of most data incidents, so write the contract in the model's description and test it.

**Bronze (raw landing, e.g. `*_raw`).** Promises: data exactly as the source delivered it, plus load
metadata (ingestion time, source file or batch id); nothing is dropped, so any later layer can be
rebuilt from it. Does not promise: types, uniqueness or meaning. Readers: only the staging layer.

**Silver (clean, conformed, e.g. `*_clean`).** Promises: one model per source object, consistent
names and types, normalised nulls and codes, a declared and tested key with duplicates removed,
and a count of rows or values that failed casting rather than silent loss. Does not promise
business rules or cross-source integration. Readers: marts and intermediate models; not BI.

**Gold (marts, e.g. `*_mart`).** Promises: `fct_` and `dim_` tables at a declared grain, conformed
dimensions, tested relationships between facts and dimensions, documented measures with units,
currency and additivity, and a stable schema: columns are not renamed, retyped or removed without
a deprecation period. Readers: analysts, BI, ML features, other teams.

**Serving (optional, e.g. `*_serve` views).** Promises: an audience-specific shape (a dashboard's
pre-aggregated table, a secured view) that reads only from gold, so business logic lives in one
place.

Rules that keep the contracts honest:

- Data flows one way, upward. A layer never reads from a layer above it, and BI never reads
  bronze or silver.
- A model belongs to exactly one layer; a model that both cleans source fields and applies
  business rules cannot be tested for either.
- Contracts are checked by tests that block the run (grain and key tests at severity `error`),
  not by convention (playbook §5).

## 3. Names

Defaults, used when the rules file names nothing else:

- Facts `fct_<business_process>` (`fct_order_line`), dimensions `dim_<entity>` (`dim_customer`),
  staging `stg_<source>__<object>`, intermediate `int_<entity>_<verb>`.
- Surrogate keys `<entity>_key`, natural keys `<entity>_id`, flags `is_`/`has_`, dates `_date`,
  timestamps `_at` (UTC unless the name says otherwise), money with its currency in the name or in
  a companion column.
- Datasets per layer and domain (`sales_raw`, `sales_clean`, `sales_mart`); environments by
  project, not by dataset suffix, when the rules file allows it.

## 4. Changing a model: grain and fan-out first

Most harmful changes alter what a row means or how many rows a join returns, and both pass every
syntax check. Before editing, find every consumer (playbook §6: dbt graph selection, repo search,
lineage, views, scheduled queries, BI sources). Then work through these questions for the change:

- **Does the grain sentence still hold?** If a new column, join or filter makes one row mean
  something else, this is a new model or a new version, not an edit.
- **Is every new join many-to-one?** Prove the key is unique on the dimension side for the same
  partitions the job reads, and compare the row count before and after the join. Any increase is
  fan-out until explained.
- **Can the join drop rows?** An inner join, or a filter on the joined side, removes facts whose
  dimension row is late or missing. Route them to the unknown member and count them.
- **Does a Type 2 dimension enter the join?** Then the join needs the validity window or the
  captured surrogate key, or every historical version duplicates the fact.
- **Do consumers aggregate a measure whose meaning changed?** A semi-additive measure, a new row
  type (refunds, adjustments) or a new currency changes downstream sums even when this model's
  tests pass. List those consumers and tell their owners.
- **Does a new attribute reach every layer that should expose it?** Carry it through each
  downstream model and the governance file, and show its fill rate per layer.
- **What is the evidence?** A before/after profile on the same partitions (row count, distinct
  grain keys, key sums, orphans), with each difference explained (`cardume-data:bigquery-patterns`
  §5 and reference §1).

Backfills after a grain or join change rebuild only the affected partitions, idempotently, and are
profiled against a snapshot taken before the change (playbook §6 and §8).

Related: `cardume-data:bigquery-patterns` (SQL, cost, integrity checks),
`cardume-data:airflow-testing` (DAG tests and CI), `cardume-data:gcp-observability-patterns`
(diagnosing a pipeline from telemetry).
