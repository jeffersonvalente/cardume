# GKE Standard cluster

Creates a VPC-native GKE Standard cluster on a release channel, with private nodes by default, optional private endpoint, control plane authorized networks, Workload Identity and deletion protection. The default node pool is removed; add pools with the `nodepool` module.

## Usage

```hcl
module "cluster" {
  source              = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/gke?ref=v1.0.0"
  project_id          = var.project_id
  name                = var.cluster_name
  location            = var.region
  network             = var.network_self_link
  subnetwork          = var.subnet_self_link
  pods_range_name     = var.pods_range_name
  services_range_name = var.services_range_name
  master_cidr         = var.master_cidr
  authorized_networks = var.authorized_networks
}
```

Pin `ref` to a release tag of your modules repository and bump it on purpose.

## Notes

Google provider 8.x marks `remove_default_node_pool` as deprecated for GKE 1.36.4-gke.1469000 and later, where `initial_node_count = 0` replaces it. The module keeps the older pattern because it still works across the whole `>= 6.0` provider range; switch once every caller is on provider 8.x and a recent GKE version.

## Inputs

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | `string` | yes | ID of the project that hosts the cluster. |
| `name` | `string` | yes | Cluster name, up to 40 characters. |
| `location` | `string` | yes | A region for a regional (highly available) control plane, or a zone for a zonal one. |
| `network` | `string` | yes | Self link or name of the VPC network. |
| `subnetwork` | `string` | yes | Self link or name of the subnet the nodes use. |
| `release_channel` | `string` | no | GKE release channel: RAPID, REGULAR, STABLE or EXTENDED. |
| `pods_range_name` | `string` | no | Name of an existing secondary range on the subnet for pods. Takes precedence over pods_cidr. |
| `services_range_name` | `string` | no | Name of an existing secondary range on the subnet for services. Takes precedence over services_cidr. |
| `pods_cidr` | `string` | no | CIDR for pods when no secondary range name is given, for example 10.20.0.0/16. |
| `services_cidr` | `string` | no | CIDR for services when no secondary range name is given, for example 10.30.0.0/20. |
| `private_nodes` | `bool` | no | Give nodes internal IPs only. Pair with Cloud NAT for outbound traffic. |
| `private_endpoint` | `bool` | no | Expose the control plane on its internal IP only. Requires a path into the VPC (VPN, Interconnect or a bastion). |
| `master_cidr` | `string` | no | A /28 range for the control plane when private_nodes is true, for example 172.16.0.0/28. |
| `authorized_networks` | `list(object(...))` | no | CIDR blocks allowed to reach the control plane endpoint. |
| `deletion_protection` | `bool` | no | Block terraform destroy and replacement of the cluster until this is set to false and applied. |

## Outputs

| Name | Description |
| --- | --- |
| `id` | Cluster ID. |
| `name` | Cluster name, used by node pools and kubectl contexts. |
| `location` | Region or zone of the control plane. |
| `endpoint` | Control plane endpoint. |
| `ca_certificate` | Base64-encoded cluster CA certificate. |
| `pods_cidr` | IPv4 range assigned to pods. |
| `services_cidr` | IPv4 range assigned to services. |
| `master_cidr` | Control plane range for private clusters, null otherwise. |

## Requirements

Terraform `>= 1.5.0` (or OpenTofu `>= 1.6`) and the `hashicorp/google` provider `>= 6.0`. The calling root module sets the upper bound.

## Provider documentation

- [`google_container_cluster`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/container_cluster)
