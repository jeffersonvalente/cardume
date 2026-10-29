# Subnet with optional Cloud NAT

Creates a regional subnet with Private Google Access, optional secondary ranges and flow logs. When `enable_nat` is true it also creates a Cloud Router and Cloud NAT, with logging and, optionally, reserved static egress IPs.

## Usage

```hcl
module "subnet" {
  source           = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/subnet?ref=v1.0.0"
  project_id       = var.project_id
  region           = var.region
  network          = var.network_self_link
  name             = var.subnet_name
  ip_cidr_range    = var.subnet_cidr
  secondary_ranges = var.secondary_ranges
  enable_nat       = var.enable_nat
}
```

Pin `ref` to a release tag of your modules repository and bump it on purpose.

## Inputs

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | `string` | yes | ID of the Google Cloud project that owns the subnet. |
| `region` | `string` | yes | Region of the subnet, router and NAT, for example us-central1. |
| `network` | `string` | yes | Self link or ID of the parent VPC network. |
| `name` | `string` | yes | Subnet name. Also the base for the router and NAT names when those are not set. |
| `ip_cidr_range` | `string` | yes | Primary IPv4 range of the subnet, for example 10.10.0.0/20. |
| `secondary_ranges` | `map(string)` | no | Secondary ranges keyed by range name, for example GKE pods and services. |
| `private_ip_google_access` | `bool` | no | Let VMs without external IPs reach Google APIs. |
| `flow_logs` | `bool` | no | Turn on VPC Flow Logs for the subnet. |
| `flow_logs_sampling` | `number` | no | Fraction of flows to sample when flow logs are on, between 0 and 1. |
| `enable_nat` | `bool` | no | Create a Cloud Router and Cloud NAT so private VMs in this subnet get outbound internet access. |
| `router_name` | `string` | no | Cloud Router name. Defaults to the subnet name with an -rtr suffix. |
| `nat_name` | `string` | no | Cloud NAT name. Defaults to the subnet name with a -nat suffix. |
| `nat_static_ip_names` | `list(string)` | no | Names of regional static external IPs to reserve for NAT. Leave empty to let Google allocate addresses automatically. |
| `nat_logging` | `bool` | no | Send Cloud NAT logs to Cloud Logging. |
| `nat_log_filter` | `string` | no | Which NAT events to log: ERRORS_ONLY, TRANSLATIONS_ONLY or ALL. |

## Outputs

| Name | Description |
| --- | --- |
| `id` | Fully qualified subnet ID. |
| `name` | Subnet name. |
| `self_link` | Subnet self link. |
| `ip_cidr_range` | Primary IPv4 range. |
| `secondary_range_names` | Names of the secondary ranges, useful for the GKE ip_allocation_policy. |
| `nat_ip_addresses` | Static external IPs reserved for NAT, empty when NAT allocates automatically. |

## Requirements

Terraform `>= 1.5.0` (or OpenTofu `>= 1.6`) and the `hashicorp/google` provider `>= 6.0`. The calling root module sets the upper bound.

## Provider documentation

- [`google_compute_subnetwork`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_subnetwork)
- [`google_compute_router`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_router)
- [`google_compute_router_nat`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_router_nat)
- [`google_compute_address`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_address)
