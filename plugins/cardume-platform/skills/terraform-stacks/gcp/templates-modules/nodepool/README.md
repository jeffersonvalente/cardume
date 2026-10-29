# GKE autoscaling node pool

Adds an autoscaling node pool with auto-repair, auto-upgrade, surge upgrades, Shielded nodes and the GKE metadata server for Workload Identity.

## Usage

```hcl
module "general_pool" {
  source                = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/nodepool?ref=v1.0.0"
  project_id            = var.project_id
  name                  = var.node_pool_name
  location              = var.region
  cluster               = module.cluster.name
  machine_type          = var.machine_type
  min_nodes             = var.min_nodes
  max_nodes             = var.max_nodes
  service_account_email = var.node_service_account
}
```

Pin `ref` to a release tag of your modules repository and bump it on purpose.

## Inputs

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | `string` | yes | ID of the project that hosts the cluster. |
| `name` | `string` | yes | Node pool name. |
| `location` | `string` | yes | Location of the parent cluster (region or zone). |
| `cluster` | `string` | yes | Name of the parent cluster. |
| `machine_type` | `string` | yes | Compute Engine machine type for the nodes, for example e2-standard-4. |
| `min_nodes` | `number` | no | Minimum nodes per zone for the autoscaler. |
| `max_nodes` | `number` | no | Maximum nodes per zone for the autoscaler. |
| `max_surge` | `number` | no | Extra nodes created during a surge upgrade. |
| `disk_size_gb` | `number` | no | Boot disk size per node in GB. |
| `disk_type` | `string` | no | Boot disk type: pd-standard, pd-balanced or pd-ssd. |
| `spot` | `bool` | no | Use Spot VMs. Cheaper, but nodes can be reclaimed at any time. |
| `service_account_email` | `string` | yes | Dedicated, minimally privileged service account for the nodes. Avoid the Compute Engine default account. |

## Outputs

| Name | Description |
| --- | --- |
| `id` | Node pool ID. |
| `name` | Node pool name. |
| `instance_group_urls` | Managed instance groups backing the pool. |

## Requirements

Terraform `>= 1.5.0` (or OpenTofu `>= 1.6`) and the `hashicorp/google` provider `>= 6.0`. The calling root module sets the upper bound.

## Provider documentation

- [`google_container_node_pool`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/container_node_pool)
