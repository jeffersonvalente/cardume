# Project audit playbook

A read-only audit of one Google Cloud project that hosts data or AI/ML workloads. It answers four
questions in order, and each one builds on the previous:

1. **Inventory** — what is in the project?
2. **Exposure** — who and what can reach it, and how far?
3. **Data flow** — how does data enter, move and leave, and is it governed on the way?
4. **Recommendations** — what should change, ranked by risk and effort?

Used by `gcp-project-auditor-data-and-ia`; the investigation recipes live in
`cardume-data:gcp-observability-patterns`, SQL hygiene in `cardume-data:bigquery-patterns`.

Sources: Google Cloud security best practices and the IAM Recommender / Active Assist docs;
Cloud Asset Inventory; Cloud Audit Logs; BigQuery and Vertex AI access-control docs; Security
Command Center; CIS Google Cloud Platform Foundation Benchmark (sections cited as "CIS n.x"; check
the benchmark version the organization uses).

## 0. Ground rules

- **Read-only.** Every command below lists, describes, gets or queries metadata. Do not enable an
  API to make a command work; record "API not enabled" as a fact. Do not export data.
- **Scope.** One project, named explicitly with `--project` on every call. Read the project id,
  region, environment and any expected exceptions from the rules file (`CLAUDE.md` /
  `docs/standards.md`) first.
- **Permissions.** Ideal: `roles/viewer`, `roles/iam.securityReviewer`,
  `roles/cloudasset.viewer`, `roles/bigquery.metadataViewer`, `roles/recommender.iamViewer`. A
  `PERMISSION_DENIED` is a gap in the audit, recorded in the report, never a reason to escalate.
- **Cost.** `INFORMATION_SCHEMA` metadata queries are cheap but still billed by bytes: dry run any
  `JOBS` query over long windows.
- **Evidence.** Keep each finding tied to the command and the output line that shows it.

## 1. Inventory

Start broad, then go per service. Cloud Asset Inventory gives one list across services:

```bash
gcloud services list --enabled --project P --format="value(config.name)"
gcloud asset search-all-resources --scope=projects/P \
  --format="table(assetType.basename(), name.basename(), location)" | sort | uniq -c
```

Per service, only for the APIs that are enabled:

| Area | Commands |
| :--- | :--- |
| BigQuery | `bq ls --project_id=P --max_results=1000`; per dataset `bq show --format=prettyjson P:DS` (location, default expiration, labels, access); table sizes via `INFORMATION_SCHEMA.TABLE_STORAGE` |
| Storage | `gcloud storage buckets list --project P --format="table(name,location,storage_class,uniform_bucket_level_access,public_access_prevention,retention_policy)"` |
| Orchestration | `gcloud composer environments list --locations L --project P`; Dataform repositories; scheduled queries (`bq ls --transfer_config --transfer_location=L --project_id=P`) |
| Processing | Dataflow jobs (`gcloud dataflow jobs list --region L --status=active`), Dataproc clusters, Cloud Run jobs and functions |
| AI/ML | `gcloud ai models list --region L`, `gcloud ai endpoints list --region L`, notebooks / Workbench instances, Vertex AI pipelines; BigQuery ML models (`bq ls --models P:DS`) |
| Governance | `gcloud dataplex lakes list --location L`, entry groups, data scans, policy tag taxonomies (`gcloud data-catalog taxonomies list --location L`) |
| Identities | `gcloud iam service-accounts list --project P`; per account `gcloud iam service-accounts keys list --iam-account SA --managed-by=user` |

Size and activity for BigQuery in one pass:

```sql
SELECT table_schema, COUNT(*) AS tables,
       ROUND(SUM(total_logical_bytes) / POW(1024, 4), 3) AS logical_tib,
       MAX(storage_last_modified_time) AS last_write
FROM `region-{region}`.INFORMATION_SCHEMA.TABLE_STORAGE_BY_PROJECT
GROUP BY table_schema
ORDER BY logical_tib DESC
```

Output of this phase: a table of resources with owner (from labels), location, size and last
activity. Unlabelled, unowned or inactive resources are themselves findings.

## 2. Exposure

Work from the outside in: public access first, then broad grants, then identities.

**Policies to collect**

```bash
gcloud projects get-iam-policy P --format=json > iam.json   # into .cardume/reports/, not docs/
gcloud asset search-all-iam-policies --scope=projects/P \
  --query="policy:(allUsers OR allAuthenticatedUsers)"
gcloud storage buckets get-iam-policy gs://BUCKET   # per bucket of interest
bq show --format=prettyjson P:DS | jq '.access'     # per dataset
```

**What to look for, and why it matters**

| Signal | Why | Benchmark |
| :--- | :--- | :--- |
| `allUsers` / `allAuthenticatedUsers` on a bucket, dataset or function | data readable by anyone | CIS 5.1, 7.1 |
| Basic roles (Owner/Editor/Viewer) granted to people or service accounts | thousands of permissions across every service; least privilege lost | CIS 1.x (IAM) |
| User-managed service account keys, especially old ones | long-lived credentials that leak | CIS 1.4, 1.7 |
| `roles/iam.serviceAccountUser` / `serviceAccountTokenCreator` at project level | lets the holder act as every service account | CIS 1.6 |
| Default compute service account used by Composer, Dataflow or notebooks | broad default grants, shared identity | CIS 4.1 |
| Buckets without uniform bucket-level access or public access prevention | ACLs bypass IAM review | CIS 5.2 |
| Datasets granting `projectReaders`/`projectWriters` special groups | access follows basic roles silently | — |
| Vertex AI endpoints or notebooks with public IPs, no VPC Service Controls | data exfiltration path for training data | — |

**Use the recommender rather than guessing.** IAM role recommendations compare granted permissions
with the last 90 days of usage:

```bash
gcloud recommender recommendations list --project P --location global \
  --recommender google.iam.policy.Recommender \
  --format="table(name.basename(), description, primaryImpact.securityProjection.details)"
gcloud recommender insights list --project P --location global \
  --insight-type google.iam.policy.Insight
gcloud recommender insights list --project P --location global \
  --insight-type google.iam.serviceAccount.Insight   # unused service accounts
```

If Security Command Center is active for the organization, list its active findings for the
project (`gcloud scc findings list ... --filter="state=\"ACTIVE\""`) and cite them instead of
re-deriving.

**Logging coverage** belongs here because missing logs hide exposure: are Data Access audit logs
enabled for Cloud Storage and other sensitive services (`auditConfigs` in `iam.json`)? What is the
retention of `_Default`? Is there a sink to a central project (`gcloud logging sinks list`)?

## 3. Data flow

Trace data end to end, so the inventory becomes a picture of how the platform works:

1. **Ingress.** Landing buckets and their writers (bucket IAM, Composer/Dataflow/transfer configs),
   external connections (`bq ls --connection --project_id=P --location=L`), Datastream or Pub/Sub
   subscriptions.
2. **Movement.** Which jobs write which tables: `INFORMATION_SCHEMA.JOBS_BY_PROJECT` grouped by
   `destination_table` and `user_email` over 30 days; Data Lineage links for the main tables.
3. **Egress.** Exports to buckets, cross-project reads (`referenced_tables` from other projects),
   authorized views and Analytics Hub listings, BI service accounts, Vertex AI training reads.
4. **Governance on the way.** Sensitive columns with or without policy tags; CMEK on datasets and
   buckets that the rules file marks sensitive (`defaultEncryptionConfiguration`, `encryption`);
   table expiration on scratch datasets; data quality scans on critical tables.

```sql
SELECT destination_table.dataset_id AS ds, destination_table.table_id AS tbl,
       user_email, COUNT(*) AS writes, MAX(creation_time) AS last_write
FROM `region-{region}`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND destination_table.table_id IS NOT NULL
  AND NOT STARTS_WITH(destination_table.dataset_id, '_')   -- skip anonymous result tables
GROUP BY ds, tbl, user_email
ORDER BY writes DESC
LIMIT 200
```

Record the flow as a short diagram or table: source → landing → layers → consumers, with the
identity that performs each hop. A hop performed by a person's account, not a service account, is
a finding (it breaks when that person leaves).

For AI/ML specifically: where training data comes from and whether it is a governed gold table;
where model artifacts live; who can call endpoints; whether prompts or predictions are logged and
where (they may contain personal data).

## 4. Recommendations

Rank every finding with two labels and sort by risk:

| Risk | Meaning |
| :--- | :--- |
| **Critical** | data exposed outside the organization now, or a credential that grants broad access |
| **High** | broad internal access, missing audit trail on sensitive data, no recovery path |
| **Medium** | least-privilege drift, missing governance on non-sensitive data, cost waste |
| **Low** | hygiene: labels, naming, documentation |

Effort: **S** (one command, reversible), **M** (a change with a test), **L** (a project).

For each recommendation give the finding, the evidence, the proposed change as a command or
Terraform resource **for the owner to apply**, the expected side effects (which jobs could break
when a role is narrowed), and how to verify afterwards. Prefer the narrowest fix: a predefined or
custom role on one resource over a project-level grant; workload identity or attached service
accounts over keys; an IAM Recommender suggestion over a hand-built role.

## 5. Report

One report per audit, in the language of the rules file:

```
# Audit — <project id> (<environment>), <date>
## Summary            — 5 lines: scope, coverage gaps, top three risks
## Inventory          — table from §1
## Exposure           — findings from §2 with evidence
## Data flow          — diagram/table from §3
## Recommendations    — ranked table from §4
## Coverage and limits — APIs not enabled, permissions missing, what was not checked
```

Save it as `docs/audits/<project>-<yyyy-mm-dd>.md` when the user wants a deliverable, otherwise
under `.cardume/reports/`. Raw command output stays in `.cardume/reports/`, never in `docs/`, since
policies and account names are sensitive.
