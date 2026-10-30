---
name: gcp-observability-patterns
description: "Read-only GCP investigation: Composer failures, BigQuery job errors, slot and cost spikes, missing files, audit logs. Use when diagnosing a GCP data platform from telemetry."
allowed-tools: Read Bash
---

# GCP observability for data platforms

Google Cloud already records most of what you need to explain a failure: what the code printed
(logs), how the system behaved over time (metrics), who changed what (audit logs), and what exists
right now (resource state and metadata). This skill reads those four signals. It never writes:
`Bash` is here only for read commands (`gcloud ... list|describe|read|get-iam-policy`, `bq show`,
`bq ls`, `SELECT` on `INFORMATION_SCHEMA`, HTTP `GET` on Google APIs). Anything that creates,
updates, deletes, grants, reruns, clears or cancels is out of scope until the evidence names a cause
and the user approves a fix.

For a whole-project audit (inventory, exposure, data flow, ranked recommendations) follow
`reference/project-audit-playbook.md` instead. SQL cost and safety rules come from
`cardume-data:bigquery-patterns`; layer semantics from `cardume-data:lakehouse-architecture`.

## Ground rules

- **Name the project on every call** (`--project P`, `--project_id=P`, the MCP `project`
  argument). A default gcloud configuration pointing elsewhere is the most common reason an
  investigation finds "nothing".
- **Bound every read in time.** Start from the first failure and look back to the last success;
  widen only if needed. Unbounded log reads are slow and `INFORMATION_SCHEMA.JOBS` scans are billed.
- **Keep evidence.** Every claim in the answer cites the command or filter and the line it
  returned. Raw dumps go to `.cardume/reports/`, not into the conversation.
- **Never fix to learn.** Granting a broad role, rerunning a task or clearing state to "see if it
  helps" overwrites the evidence and can hide a second problem. Broad roles (Owner, Editor,
  Storage Admin, BigQuery Admin) are never the fix.
- **Prefer MCP tools when configured**: `mcp__gcp-observability__list_log_entries`,
  `mcp__gcp-observability__list_time_series`, `mcp__gcp-observability__list_group_stats` (Error
  Reporting), `mcp__gcloud__run_gcloud_command`, `mcp__gcp-storage__*`, `mcp__bigquery__execute_sql`.
  The CLI forms below are equivalent.

## Which signal answers which question

| Question | Signal | Section |
| :--- | :--- | :--- |
| What error did the task, job or worker actually hit? | Logs | 1 |
| When did behaviour change, and is it still happening? | Metrics | 2 |
| Who changed a permission, config or resource, and when? | Audit logs | 3 |
| Does the file, table, binding or setting exist as expected now? | State and metadata | 4 |
| Which jobs cost or ran the most? | BigQuery job metadata | 4 |

A generic error ("return code 1", "task failed") usually needs two signals: logs to find the
underlying exception, then audit logs or state to explain why it started.

## 1. Logs (Cloud Logging)

Read with `gcloud logging read 'FILTER' --project P --freshness=2d --limit=50 --order=desc
--format=json`, or with an explicit window inside the filter:
`timestamp>="2026-10-27T18:00:00Z" AND timestamp<"2026-10-28T09:00:00Z"`.

**Composer / Airflow.** Task logs carry the DAG, task, run and try in their labels:

```text
resource.type="cloud_composer_environment"
resource.labels.environment_name="ENV"
resource.labels.location="REGION"
log_id("airflow-worker")
labels.workflow="DAG_ID"
labels."task-id"="TASK_ID"
severity>=WARNING
```

Other Composer logs: `airflow-scheduler` (task never queued, zombie detection), the DAG processor
logs (`dag-processor-manager`, or `airflow-dag-processor` on newer images: import errors, parse
timeouts) and `airflow-webserver`. A "return code 1" line is the wrapper; the real exception is usually a few
lines earlier in the same try (`labels."try-number"`), often a Python traceback, a `403`/`404` from
a client library, or a BigQuery job id with its error.

**Other services**, same pattern with a different resource:

| Service | Filter start |
| :--- | :--- |
| BigQuery jobs | `resource.type="bigquery_project" protoPayload.metadata.jobChange.job.jobStatus.errorResult.code:*` (from the BigQuery audit stream) |
| Dataflow | `resource.type="dataflow_step" resource.labels.job_id="JOB_ID" severity>=ERROR` (`log_id("dataflow.googleapis.com/worker")` for user code) |
| Cloud Run job or function | `resource.type="cloud_run_job"` / `"cloud_run_revision"` with `resource.labels.job_name` or `service_name` |
| Cloud Storage | Data Access audit logs only (section 3); buckets do not write request logs by default |

Group repeated errors before reading them one by one: Error Reporting
(`list_group_stats`) or `gcloud logging read ... --format="value(jsonPayload.message)" | sort |
uniq -c | sort -rn | head`.

## 2. Metrics (Cloud Monitoring)

Metrics answer "since when" and "how much", which logs answer badly. Read them in Metrics Explorer
(MQL or PromQL), with `list_time_series`, or with a read-only API call:

```bash
curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://monitoring.googleapis.com/v3/projects/P/timeSeries?filter=$(printf %s \
  'metric.type="storage.googleapis.com/api/request_count" AND resource.labels.bucket_name="BUCKET"' \
  | jq -sRr @uri)&interval.startTime=2026-10-26T00:00:00Z&interval.endTime=2026-10-28T12:00:00Z"
```

| Area | Metrics worth reading | What a change means |
| :--- | :--- | :--- |
| Composer | `composer.googleapis.com/workflow/run_count` and `workflow/task/run_count` (by `state`), `environment/dag_processing/total_parse_time`, `environment/unfinished_task_instances`, `environment/worker/pod_eviction_count`, `environment/healthy` | Failures across many DAGs at once point at the environment (parse time, evictions, database), not at one DAG |
| Cloud Storage | `storage.googleapis.com/api/request_count` by `response_code` and `method` | A jump in `PERMISSION_DENIED` or `NOT_FOUND` on a bucket dates an access change or a missing upstream file |
| BigQuery | `bigquery.googleapis.com/query/count`, `query/execution_times`, `storage/stored_bytes` | Concurrency or latency changes; for per-job cost use section 4 |
| Dataflow | `dataflow.googleapis.com/job/system_lag`, `job/data_watermark_age`, `job/is_failed` | A streaming job falling behind versus one that stopped |

Compare the failure window with the same window a day or a week earlier; a metric is evidence
only relative to its normal level.

## 3. Audit logs (who changed what)

Admin Activity audit logs are always on and record configuration and IAM changes. Data Access logs
(reads and writes of data, including permission-denied reads) are off by default for most
services, including Cloud Storage; check `auditConfigs` in `gcloud projects get-iam-policy P
--format=json` before concluding "nobody read it".

Bucket IAM change:

```text
logName="projects/P/logs/cloudaudit.googleapis.com%2Factivity"
resource.type="gcs_bucket"
resource.labels.bucket_name="BUCKET"
protoPayload.methodName="storage.setIamPermissions"
```

Project, dataset or service account IAM change: `protoPayload.methodName:"SetIamPolicy"` (substring
match, since some services prefix the method) with `resource.type="project"`, `"bigquery_dataset"`
or `"service_account"`; dataset ACL edits can also appear as `UpdateDataset` / `PatchDataset`. Read
`protoPayload.authenticationInfo.principalEmail` (who), `timestamp` (when) and
`protoPayload.serviceData.policyDelta.bindingDeltas` (what was added or removed; for BigQuery the
delta sits under `protoPayload.metadata`).

Denials, when Data Access logs are on:

```text
logName="projects/P/logs/cloudaudit.googleapis.com%2Fdata_access"
protoPayload.status.code=7
protoPayload.authenticationInfo.principalEmail="SA_EMAIL"
```

`status.code=7` is `PERMISSION_DENIED`; `protoPayload.authorizationInfo` names the permission that
failed. Policy Denied logs (`cloudaudit.googleapis.com%2Fpolicy`) cover VPC Service Controls and
organization policy denials, which look like IAM errors but are not fixed by a role.

## 4. State and metadata (what is true now)

**Identity and access**

```bash
gcloud composer environments describe ENV --location REGION --project P \
  --format="value(config.nodeConfig.serviceAccount)"
gcloud storage buckets get-iam-policy gs://BUCKET --project P --format=json
gcloud projects get-iam-policy P --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:SA_EMAIL" --format="table(bindings.role)"
gcloud policy-intelligence troubleshoot-policy iam \
  //storage.googleapis.com/projects/_/buckets/BUCKET \
  --principal-email=SA_EMAIL --permission=storage.objects.get
```

The troubleshooter explains whether a principal has a permission on a resource and which binding
(or deny policy) decides it, without anyone testing access by trial.

**Storage**: `gcloud storage ls -l gs://BUCKET/PREFIX/` (did the landing file arrive, when, what
size), `gcloud storage objects describe gs://BUCKET/OBJECT`, and `gcloud storage buckets describe
gs://BUCKET` (uniform access, retention, lifecycle rules that may have deleted objects).

**BigQuery jobs**: `bq show --format=prettyjson -j --project_id=P --location=LOC JOB_ID` gives
`status.errorResult` and `errors`. Across many jobs (recent Google provider versions label jobs
from Airflow with `airflow-dag` and `airflow-task`; filter on them when present):

```sql
SELECT creation_time, job_id, user_email, error_result.reason, error_result.message,
       ROUND(total_bytes_billed / POW(1024, 3), 1) AS gib_billed, total_slot_ms
FROM `region-REGION`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time BETWEEN TIMESTAMP('2026-10-27 00:00:00') AND TIMESTAMP('2026-10-28 12:00:00')
  AND (error_result IS NOT NULL
       OR EXISTS (SELECT 1 FROM UNNEST(labels) l WHERE l.key = 'airflow-dag' AND l.value = 'DAG_ID'))
ORDER BY creation_time DESC
LIMIT 100
```

For cost or slot spikes, rank jobs by `total_slot_ms` and `total_bytes_billed` and group by query
hash (`cardume-data:bigquery-patterns` reference §12). Table freshness and size without scanning
data: `INFORMATION_SCHEMA.PARTITIONS` and `TABLE_STORAGE`. Lineage, when the Data Lineage API is
enabled, shows which process last wrote a table.

**Airflow state**, read-only subcommands only:
`gcloud composer environments run ENV --location REGION --project P dags list-runs -- -d DAG_ID`
and `... tasks states-for-dag-run -- DAG_ID RUN_ID`. Never `tasks clear`, `dags trigger` or
`dags backfill` during an investigation.

## Correlate, then propose

1. **Timeline.** Put the last success, the first failure, and every change found in section 3 on
   one line, in UTC. A change after the first failure is not the cause.
2. **One explanation for all symptoms.** If the bucket binding was removed at 18:40 and the task
   started failing at 19:00 with a `403` on `storage.objects.get` for the Composer service account,
   the chain is closed. If one symptom is left unexplained, keep looking.
3. **Smallest fix, proposed not applied.** Name the principal, the narrowest role and the single
   resource (for example `roles/storage.objectViewer` on that bucket for that service account),
   the command the owner would run, its side effects, and how to verify afterwards (the troubleshooter
   again, then one rerun of the failed task by the owner).
4. **Report** in this shape: cause in one sentence; timeline; evidence (filter or command plus the
   line it returned); proposed fix; what was not checked and why (missing permission, Data Access
   logs off, API disabled).
