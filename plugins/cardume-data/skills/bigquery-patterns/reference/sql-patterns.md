# BigQuery SQL patterns

Copy-ready templates for `cardume-data:bigquery-patterns`, grouped by the goal they serve:
**correctness** (§1–5), **cost** (§6–8), **performance** (§9–11) and **safe execution** (§12–15).
Placeholders are in `{braces}`; take project, dataset and region values from the project rules file.
Section numbers are stable because other skills cite them (§1 integrity, §12 top jobs).

Sources: Google Cloud BigQuery docs (cost and performance best practices, partitioned and
clustered tables, dry runs, `INFORMATION_SCHEMA.JOBS`, time travel, `MERGE`, transactions).

## Correctness

### 1. Before/after integrity profile

Run the same profile, with the same filter, in the same environment, before and after a change.
Save both result rows; the comparison is the evidence.

```sql
SELECT
  COUNT(*)                                   AS total_rows,
  COUNT(DISTINCT {business_key})             AS distinct_keys,
  COUNTIF({changed_col} IS NULL)             AS null_{changed_col},
  ROUND(100 * COUNTIF({changed_col} IS NOT NULL) / NULLIF(COUNT(*), 0), 2) AS fill_pct,
  SUM({amount_col})                          AS sum_{amount_col}
FROM `{project}.{dataset}.{table}`
WHERE {partition_col} BETWEEN DATE '{start}' AND DATE '{end}'
```

To compare two versions of a table side by side (for example the current table and a rebuilt
copy in a scratch dataset), profile each in a CTE and `CROSS JOIN` the two one-row results, adding
`after.total_rows - before.total_rows AS delta_rows` and the same for each sum. For a per-key diff:

```sql
SELECT COALESCE(b.k, a.k) AS k,
       b.v AS before_v, a.v AS after_v
FROM (SELECT {business_key} AS k, SUM({amount_col}) AS v FROM `{before_table}` GROUP BY k) b
FULL OUTER JOIN
     (SELECT {business_key} AS k, SUM({amount_col}) AS v FROM `{after_table}` GROUP BY k) a
  ON a.k = b.k
WHERE b.k IS NULL OR a.k IS NULL OR b.v != a.v
LIMIT 100
```

Empty result: the change kept every key and every sum. Otherwise the rows are the explanation to
give (or the bug to fix).

### 2. Prove the grain

A table whose grain is "one row per X" must pass this with zero rows returned:

```sql
SELECT {grain_cols}, COUNT(*) AS n
FROM `{project}.{dataset}.{table}`
WHERE {partition_filter}
GROUP BY {grain_cols}
HAVING n > 1
ORDER BY n DESC
LIMIT 20
```

For SCD Type 2 dimensions, also check that validity windows do not overlap:

```sql
SELECT {natural_key}, valid_from, valid_to,
       LEAD(valid_from) OVER (PARTITION BY {natural_key} ORDER BY valid_from) AS next_from
FROM `{dim_table}`
WHERE TRUE  -- older engines require WHERE/GROUP BY/HAVING alongside QUALIFY
QUALIFY next_from < valid_to
```

### 3. Joins: fan-out and orphans

A many-to-one join must not change the left row count, and unmatched keys must be counted, not
silently dropped.

```sql
WITH base AS (SELECT * FROM `{fact_source}` WHERE {partition_filter}),
joined AS (
  SELECT b.*, d.{dim_key}
  FROM base b
  LEFT JOIN `{dim_table}` d ON d.{natural_key} = b.{fk_col}
)
SELECT
  (SELECT COUNT(*) FROM base)                  AS rows_before,
  (SELECT COUNT(*) FROM joined)                AS rows_after,      -- must equal rows_before
  (SELECT COUNTIF({dim_key} IS NULL) FROM joined) AS orphan_rows   -- report; route to unknown member
```

Run this as a dry run first if `{fact_source}` is large; the `SELECT *` inside the CTE is pruned to
the referenced columns by the optimizer, but the dry run proves it. Before joining, confirm both key
columns have the same type:

```sql
SELECT table_name, column_name, data_type
FROM `{project}.{dataset}`.INFORMATION_SCHEMA.COLUMNS
WHERE column_name IN ('{left_key}', '{right_key}')
```

### 4. Casting and counting what failed

`SAFE_CAST` and the `SAFE.` prefix return `NULL` instead of failing the job. That is only safe when
the failures are counted afterwards:

```sql
SELECT
  COUNTIF(raw_amount IS NOT NULL AND SAFE_CAST(raw_amount AS NUMERIC) IS NULL)          AS bad_amount,
  COUNTIF(raw_date   IS NOT NULL AND SAFE.PARSE_DATE('%Y-%m-%d', raw_date) IS NULL)      AS bad_date,
  ARRAY_AGG(IF(SAFE_CAST(raw_amount AS NUMERIC) IS NULL AND raw_amount IS NOT NULL,
               raw_amount, NULL) IGNORE NULLS LIMIT 5)                                    AS sample_bad
FROM `{bronze_table}`
WHERE {ingestion_partition_filter}
```

Use `NUMERIC` (or `BIGNUMERIC`) for money and `PARSE_DATE`/`PARSE_TIMESTAMP` with an explicit
format for text dates, because `CAST` accepts only the canonical format.

### 5. Deduplicate to one row per key

Keep the latest version of each key, with a deterministic tie-breaker so reruns pick the same row:

```sql
SELECT *
FROM `{bronze_table}`
WHERE {ingestion_partition_filter}
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY {business_key}
  ORDER BY {updated_at} DESC, _ingested_at DESC, _source_file DESC
) = 1
```

## Cost

### 6. Dry run and byte cap

```bash
bq query --use_legacy_sql=false --dry_run "$(cat query.sql)"
# → "Query successfully validated. ... will process N bytes"
bq query --use_legacy_sql=false --maximum_bytes_billed={estimate_x_1_5} "$(cat query.sql)"
```

In the Python client, `QueryJobConfig(dry_run=True, use_query_cache=False)` returns
`total_bytes_processed`; set `maximum_bytes_billed` on the real job. Through an MCP tool without a
dry-run flag, run the dry run with `bq` instead of guessing.

### 7. Partition pruning forms

Pruning needs the partition column compared to constants or parameters.

| Partitioning | Prunes | May not prune |
| :--- | :--- | :--- |
| `TIMESTAMP` column | `ts >= TIMESTAMP('2026-10-27') AND ts < TIMESTAMP('2026-10-28')` | `DATE(ts) = '2026-10-27'` (function on the column; verify with a dry run) |
| `DATE` column | `d = DATE '2026-10-27'`, `d BETWEEN @start AND @end` | `d = (SELECT MAX(d) FROM t)` (subquery bound) |
| Ingestion time | `_PARTITIONDATE = '2026-10-27'` / `_PARTITIONTIME >= ...` | filters on a payload date column only |

For "yesterday" in a scheduled query, compute the bounds as constants:

```sql
DECLARE d DATE DEFAULT DATE_SUB(CURRENT_DATE('{timezone}'), INTERVAL 1 DAY);
SELECT {needed_cols}
FROM `{project}.{dataset}.events`
WHERE event_ts >= TIMESTAMP(d, '{timezone}') AND event_ts < TIMESTAMP(DATE_ADD(d, INTERVAL 1 DAY), '{timezone}')
```

Partition sizes, without scanning data: `{dataset}.INFORMATION_SCHEMA.PARTITIONS`
(`partition_id`, `total_rows`, `total_logical_bytes`) filtered on `table_name`.

### 8. Read fewer columns and fewer rows

- Name columns; for "everything but a few", `SELECT * EXCEPT (payload_json, raw_blob)` still reads
  every other column, so prefer an explicit list on wide tables.
- Look at data for free with `bq head -n 20 {project}:{dataset}.{table}` or the console preview.
- `TABLESAMPLE SYSTEM (1 PERCENT)` reads a fraction of blocks for exploration; it is not a
  statistically uniform sample, so do not report its numbers as totals.
- Cache: identical queries over unchanged tables are served from cache for free for about 24 h;
  non-deterministic functions (`CURRENT_TIMESTAMP()`) disable it.

## Performance

### 9. Partitioned and clustered tables

```sql
CREATE TABLE `{project}.{dataset}.{table}`
(
  event_ts TIMESTAMP NOT NULL,
  user_id  STRING,
  country  STRING,
  amount   NUMERIC
)
PARTITION BY DATE(event_ts)
CLUSTER BY country, user_id
OPTIONS (require_partition_filter = TRUE, partition_expiration_days = {days_or_omit},
         description = 'One row per event. Grain: event_id.');
```

Order cluster columns by how often they are filtered, most common first; up to four. Partitions
should hold enough data (on the order of 1 GB or more each) to be worth it; for small tables,
clustering alone is often better than daily partitions.

### 10. Incremental loads instead of full rebuilds

Replace one partition idempotently (safe to rerun):

```sql
MERGE `{target}` t
USING (SELECT {cols} FROM `{staging}` WHERE {partition_col} = @run_date) s
ON t.{business_key} = s.{business_key} AND t.{partition_col} = @run_date
WHEN MATCHED THEN UPDATE SET {col_assignments}
WHEN NOT MATCHED BY TARGET THEN INSERT ({cols}) VALUES ({s_cols})
WHEN NOT MATCHED BY SOURCE AND t.{partition_col} = @run_date THEN DELETE
```

The `t.{partition_col} = @run_date` predicates limit the target scan to one partition. An
alternative is writing the query result to the partition decorator
(`--destination_table '{dataset}.{table}$20261027' --replace`), which swaps the partition
atomically. For pre-aggregations that many dashboards read, consider a materialized view.

### 11. Query shape

- Filter and aggregate in CTEs before joining, so joins move fewer rows.
- Avoid self-joins for running totals or "previous row" logic; use window functions.
- `APPROX_COUNT_DISTINCT` (HyperLogLog++) for dashboards where ±1% is acceptable; exact
  `COUNT(DISTINCT)` for reconciliation.
- Avoid `ORDER BY` without `LIMIT` on large outputs; the final sort runs on a single worker.
- Skew (one key, often `NULL` or `''`, holding most rows) shows as one slow stage in the job's
  `statistics.query.queryPlan` (`bq show --format=prettyjson -j {job_id}`); split that key out.

## Safe execution

### 12. Top jobs by slot time and bytes

```sql
SELECT
  job_id, user_email, job_type, statement_type,
  ROUND(total_bytes_billed / POW(1024, 4), 3)          AS tib_billed,
  ROUND(total_slot_ms / 1000 / 3600, 2)                AS slot_hours,
  TIMESTAMP_DIFF(end_time, start_time, SECOND)          AS duration_s,
  query_info.query_hashes.normalized_literals           AS query_hash,
  (SELECT STRING_AGG(CONCAT(l.key, '=', l.value)) FROM UNNEST(labels) l) AS labels,
  LEFT(query, 200)                                      AS query_head
FROM `region-{region}`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time BETWEEN TIMESTAMP('{start}') AND TIMESTAMP('{end}')
  AND job_type = 'QUERY' AND state = 'DONE'
ORDER BY total_slot_ms DESC
LIMIT 20
```

Group by `query_hash` (sum `slot_hours`, `tib_billed`, count runs) to find one query repeated by a
schedule or dashboard. `JOBS_BY_PROJECT` needs `bigquery.jobs.listAll` (for example
`roles/bigquery.resourceViewer`); without it, use `JOBS_BY_USER`. History is kept 180 days.

### 13. Running jobs: watch, then cancel

```sql
SELECT job_id, user_email, state,
       TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), creation_time, SECOND) AS running_s,
       total_bytes_processed, total_slot_ms
FROM `region-{region}`.INFORMATION_SCHEMA.JOBS_BY_USER
WHERE state != 'DONE' AND creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
ORDER BY creation_time
```

`bq cancel --location={location} {job_id}` (tell the user first). Set `jobTimeoutMs` /
`job_timeout_ms` on jobs you start so a runaway query stops itself.

### 14. Before any DML or DDL: a way back

- **Snapshot** the target first (cheap: stores only later changes):

  ```sql
  CREATE SNAPSHOT TABLE `{project}.{scratch_dataset}.{table}_pre_{yyyymmdd}`
  CLONE `{project}.{dataset}.{table}`
  OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 7 DAY));
  ```

- **Time travel** reads a table as it was, within the dataset's window (default 7 days, settable
  2–7):

  ```sql
  SELECT COUNT(*) FROM `{project}.{dataset}.{table}`
  FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 HOUR)
  ```

  A dropped table can be restored with `bq cp {dataset}.{table}@{epoch_ms} {dataset}.{table}`
  within the same window.
- **Preview the impact**: run the `WHERE` clause of an `UPDATE`/`DELETE` as a `SELECT COUNT(*)`
  first and show the number with the statement.

### 15. Atomic multi-statement changes and parameters

```sql
BEGIN TRANSACTION;
  DELETE FROM `{target}` WHERE {partition_col} = @run_date;
  INSERT INTO `{target}` ({cols}) SELECT {cols} FROM `{staging}` WHERE {partition_col} = @run_date;
COMMIT TRANSACTION;
```

If any statement fails, the transaction rolls back. Pass values as query parameters
(`bq query --parameter=run_date:DATE:2026-10-27`, `@run_date` in SQL) rather than string
formatting, which avoids injection and keeps the query text stable for caching and for grouping
by `query_hash`.
