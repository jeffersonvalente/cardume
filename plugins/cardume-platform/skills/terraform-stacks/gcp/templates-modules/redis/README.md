# Memorystore for Redis

Creates a Memorystore for Redis instance reachable through private services access, with in-transit TLS, AUTH and a weekly maintenance window. The VPC needs a private services access connection (`google_service_networking_connection`) before this applies.

## Usage

```hcl
module "cache" {
  source         = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/redis?ref=v1.0.0"
  project_id     = var.project_id
  name           = var.redis_name
  region         = var.region
  memory_size_gb = var.redis_memory_gb
  network        = var.network_id
}
```

Pin `ref` to a release tag of your modules repository and bump it on purpose.

## Inputs

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | `string` | yes | ID of the project that hosts the instance. |
| `name` | `string` | yes | Instance name. |
| `region` | `string` | yes | Region of the instance. |
| `tier` | `string` | no | BASIC (single node) or STANDARD_HA (replicated with automatic failover). |
| `memory_size_gb` | `number` | yes | Memory capacity in GB. |
| `redis_version` | `string` | no | Redis version, for example REDIS_7_2. |
| `network` | `string` | yes | ID of the VPC network that clients connect from. It needs an existing private services access connection. |
| `reserved_ip_range` | `string` | no | Name of the allocated range for private services access. Null lets Google pick one from the existing allocation. |
| `maintenance_day` | `string` | no | Maintenance day, for example SUNDAY. |
| `maintenance_hour` | `number` | no | Maintenance start hour in UTC, 0 to 23. |

## Outputs

| Name | Description |
| --- | --- |
| `host` | Private IP clients connect to. |
| `port` | TLS port. |
| `server_ca_certs` | CA certificates clients use to verify the TLS connection. |
| `auth_string` | AUTH string. Store it in Secret Manager rather than passing it around in outputs. |

## Requirements

Terraform `>= 1.5.0` (or OpenTofu `>= 1.6`) and the `hashicorp/google` provider `>= 6.0`. The calling root module sets the upper bound.

## Provider documentation

- [`google_redis_instance`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/redis_instance)
