---
name: bigquery-patterns
description: "BigQuery SQL discipline: dry runs, byte caps, pruning, safe joins, integrity checks. Use when writing, reviewing or optimizing BigQuery SQL, or when a query is slow or expensive."
allowed-tools: Read Write Edit
---

# BigQuery patterns

In BigQuery the expensive and the wrong decisions are both made in the SQL text: what it reads
decides the bill, how it joins decides whether the numbers are right, and a write cannot be taken
back by cancelling the job. This skill is organised by the question you are answering: what will
it cost, is it correct, is it fast enough, is it safe to run, and did the change keep the data
intact. Copy-ready SQL is in `reference/sql-patterns.md` (cited as reference §N).

The project's rules file (`CLAUDE.md`, `docs/standards.md`) overrides the defaults here: the
confirmation threshold, the projects per environment, required labels and naming.

## 1. Cost control

**The byte-estimate rule.** Before running a query, get its estimate with
`bq query --use_legacy_sql=false --dry_run` (or `QueryJobConfig(dry_run=True)`; reference §6). The
estimate is free and is the only input to this rule:

- **Estimate at or above the confirmation threshold** (default **100 GiB**; a rules-file value such
  as `bigquery_confirm_bytes: 50GiB` wins): show the query, the estimate and the project it will
  bill, and wait for the user's go-ahead.
- **Below the threshold**: run it, with `--maximum_bytes_billed` set a little above the estimate
  (about 1.5×) so a change between dry run and run fails instead of billing more.
- **No estimate possible** (permissions, a tool without a dry-run flag): treat it as above the
  threshold and say why.

On-demand pricing bills the estimate; capacity (editions) pricing bills slot time instead, but
bytes read still drive slot use, so the same rule applies.

**Read less.** In order of usual payoff:

1. **Columns.** BigQuery is columnar: `SELECT *` reads every column, and `LIMIT` does not reduce
   bytes. Name the columns the result needs; `SELECT * EXCEPT (...)` only for exploration.
2. **Partitions.** Filter the partition column against constants or parameters so the planner can
   prune (reference §7). On a `TIMESTAMP`-partitioned table write a half-open range
   (`ts >= TIMESTAMP(d) AND ts < TIMESTAMP(DATE_ADD(d, INTERVAL 1 DAY))`); functions on the column
   or bounds from a subquery may prevent pruning. Confirm with the dry-run estimate, which drops to
   roughly one partition's size when pruning works.
3. **Clustering.** Columns that are filtered or joined on often (`user_id`, `customer_id`,
   `country`) as cluster keys cut bytes further within each partition; the dry run cannot show
   that saving, the billed bytes afterwards can.
4. **Do the work once.** A scheduled query that re-aggregates raw events every day should usually
   become an incremental table that processes only the new partition (reference §10), or a
   materialized view when the shape fits.

Guard tables against accidental full scans with `require_partition_filter = TRUE` on large
partitioned tables, and give scratch datasets a default table expiration.

## 2. Correctness

Most wrong numbers in BigQuery come from five places. Check each one a query touches:

| Risk | What goes wrong | Defence |
| :--- | :--- | :--- |
| Join fan-out | A key assumed unique on one side is not, rows multiply, sums inflate | Prove uniqueness of the join key before joining (reference §2–3); compare row counts before and after the join |
| Lost rows | `INNER JOIN` or a `WHERE` on the right side of a `LEFT JOIN` silently drops unmatched rows | Count orphans; keep unmatched rows with an explicit unknown member |
| Casts | `CAST` aborts on bad input; `SAFE_CAST` turns it into `NULL` without telling anyone | `SAFE_CAST` plus a count of values that were non-null before and null after (reference §4) |
| `NULL` logic | `col != 'x'` excludes `NULL`; `NOT IN` with a `NULL` in the list returns nothing; `COUNT(col)` skips `NULL` | `IS DISTINCT FROM`, `NOT EXISTS`, and say which count you mean |
| Time | `CURRENT_DATE()` is UTC; `DATE(ts)` uses UTC unless given a zone; reruns on another day give another answer | Pass the run's logical date as a parameter; name the time zone (`DATE(ts, 'America/Sao_Paulo')`) |

Also: deduplicate on a business key with a deterministic tie-break (reference §5), use `NUMERIC`
or `BIGNUMERIC` for money rather than `FLOAT64`, and compare floating values with a tolerance.

## 3. Performance

Slow queries are usually doing more work than the answer needs, not short of slots.

- **Reduce early.** Filter and aggregate before joining; join the smaller, pre-aggregated side.
- **Avoid repeated work.** A CTE referenced several times may be evaluated several times; persist
  an expensive intermediate result in a temporary table inside a script when reused.
- **Window functions** with `PARTITION BY` on a skewed key put one huge group on one worker; check
  the key distribution first.
- **Approximate when allowed**: `APPROX_COUNT_DISTINCT` for exploration, exact counts for reported
  figures.
- **Design the table for its queries**: partition by the date most queries filter on, cluster by
  up to four columns most queries filter or join on (reference §9).
- **Read the plan**: the job's execution details (stage timings, records read and written, skew
  between average and maximum worker time) show which stage to fix. Find the costliest jobs with
  `INFORMATION_SCHEMA.JOBS` (reference §12).

## 4. Running statements safely

- **Environment first.** Every query names its project and dataset explicitly; never rely on the
  default project. Do not run exploratory or test statements against production; prepare them for
  the owner or the deployment pipeline instead.
- **Writes need approval each time.** `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `TRUNCATE`, `DROP`,
  `CREATE OR REPLACE` and `ALTER`: state the target table, environment and expected rows affected,
  then wait for the user. `DELETE` and `UPDATE` always carry a `WHERE` that you have counted first
  with a `SELECT COUNT(*)` using the same predicate.
- **Keep a way back.** Before changing a table that matters, take a snapshot or note the time for
  `FOR SYSTEM_TIME AS OF` within the dataset's time-travel window (reference §14).
- **All or nothing.** Several dependent statements go in one script with
  `BEGIN TRANSACTION ... COMMIT TRANSACTION`, and values go in as query parameters, not string
  concatenation (reference §15).
- **Bound the runtime.** Set a job timeout (`jobTimeoutMs` / `job_timeout_ms`, or the operator's
  timeout) so a runaway job stops on its own; watch running jobs and cancel only after telling the
  user (reference §13).
- **Label jobs** with the labels the rules file requires (team, pipeline, environment) so cost can
  be attributed later.

## 5. Proving a change kept the data intact

A query that runs is not a query that is right. For every table a change writes, profile it before
and after on the same partitions and filter (reference §1):

- row count and distinct count of the grain key (duplicates must stay at zero);
- null count of every added or changed column;
- sum of each key measure, compared exactly when no change was intended;
- orphan count for each fact-to-dimension join.

Report the numbers, the deltas, and the explanation for each delta. "Looks the same" is not
evidence.

## Worked example: a churn list that comes back empty

A weekly job lists customers with no order this quarter from `crm.customers` and
`sales.orders` (partitioned by `order_date`):

```sql
SELECT customer_id, email
FROM crm.customers
WHERE customer_id NOT IN (
  SELECT customer_id FROM sales.orders WHERE order_date >= DATE_TRUNC(CURRENT_DATE(), QUARTER))
```

It returned rows for months, then zero after guest checkout started writing orders with a `NULL`
`customer_id`.

1. Diagnose before fixing: `SELECT COUNTIF(customer_id IS NULL) FROM sales.orders` over the same
   partitions. One `NULL` in the subquery makes every `NOT IN` comparison unknown (§2).
2. Rewrite as `NOT EXISTS` (or a `LEFT JOIN ... WHERE o.customer_id IS NULL` on a deduplicated
   order side), which ignores `NULL` keys and keeps the intent.
3. Replace `CURRENT_DATE()` with the run's logical date passed as a parameter, so a rerun on
   another day gives the same list, and check that the subquery still prunes partitions in the
   dry run (§1).
4. Prove it (§5): the row count of the new result against the old query run on a week before the
   first `NULL` appeared, and a count of guest orders now excluded on purpose.

Related: `cardume-data:lakehouse-architecture` (layer contracts and modelling),
`cardume-data:gcp-observability-patterns` (finding costly or failing jobs from telemetry).
