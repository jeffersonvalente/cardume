# Cloud SQL for PostgreSQL

Creates a Cloud SQL for PostgreSQL instance with no public IP, Private Service Connect, encrypted-only connections, automated backups, point-in-time recovery, optional high availability and deletion protection.

## Usage

```hcl
module "orders_db" {
  source                        = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/postgres?ref=v1.0.0"
  project_id                    = var.project_id
  name                          = var.db_instance_name
  region                        = var.region
  tier                          = var.db_tier
  psc_allowed_consumer_projects = var.psc_consumer_projects
}
```

Pin `ref` to a release tag of your modules repository and bump it on purpose.

## Inputs

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | `string` | yes | ID of the project that hosts the instance. |
| `name` | `string` | yes | Instance name. Cloud SQL reserves a deleted name for about a week, so pick names you will not need to reuse right away. |
| `region` | `string` | yes | Region of the instance. |
| `database_version` | `string` | no | PostgreSQL major version, for example POSTGRES_16. |
| `edition` | `string` | no | Cloud SQL edition: ENTERPRISE or ENTERPRISE_PLUS. The tier must match the edition. |
| `tier` | `string` | yes | Machine tier, for example db-custom-2-7680 (Enterprise) or db-perf-optimized-N-2 (Enterprise Plus). |
| `high_availability` | `bool` | no | Run a standby in a second zone (REGIONAL availability). |
| `backup_start_time` | `string` | no | Daily backup window start, HH:MM in UTC. |
| `retained_backups` | `number` | no | Number of automated backups to keep. |
| `point_in_time_recovery` | `bool` | no | Keep transaction logs for point-in-time recovery. |
| `psc_allowed_consumer_projects` | `list(string)` | yes | Projects allowed to create Private Service Connect endpoints to this instance. |
| `maintenance_day` | `number` | no | Maintenance day, 1 (Monday) to 7 (Sunday). |
| `maintenance_hour` | `number` | no | Maintenance hour in UTC, 0 to 23. |
| `deletion_protection` | `bool` | no | Protect the instance from deletion both in Terraform and in the Cloud SQL API. |

## Outputs

| Name | Description |
| --- | --- |
| `name` | Instance name. |
| `connection_name` | project:region:instance string used by the Cloud SQL connectors. |
| `psc_service_attachment_link` | Service attachment that consumer projects target with a PSC endpoint. |
| `dns_name` | DNS name to use with the PSC endpoint. |

## Requirements

Terraform `>= 1.5.0` (or OpenTofu `>= 1.6`) and the `hashicorp/google` provider `>= 6.0`. The calling root module sets the upper bound.

## Provider documentation

- [`google_sql_database_instance`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/sql_database_instance)
