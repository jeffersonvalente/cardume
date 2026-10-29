# VPC network (custom mode)

Creates a custom-mode VPC network. Subnets are added separately with the `subnet` module, so each region's address plan stays explicit.

## Usage

```hcl
module "network" {
  source     = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/vpc?ref=v1.0.0"
  project_id = var.project_id
  name       = var.network_name
}
```

Pin `ref` to a release tag of your modules repository and bump it on purpose.

## Inputs

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | `string` | yes | ID of the Google Cloud project that owns the network. |
| `name` | `string` | yes | Network name. Lowercase letters, digits and hyphens, up to 63 characters. |
| `description` | `string` | no | Free-text description shown in the console. |
| `routing_mode` | `string` | no | Dynamic routing scope for Cloud Routers on this network: REGIONAL or GLOBAL. |
| `mtu` | `number` | no | Maximum transmission unit in bytes. 1460 is the Google Cloud default. |
| `delete_default_routes_on_create` | `bool` | no | Remove the default internet route right after the network is created. Use when egress must go through a firewall appliance or NAT you control. |

## Outputs

| Name | Description |
| --- | --- |
| `id` | Fully qualified network ID. |
| `name` | Network name. |
| `self_link` | Network self link, accepted by subnet, firewall and GKE resources. |

## Requirements

Terraform `>= 1.5.0` (or OpenTofu `>= 1.6`) and the `hashicorp/google` provider `>= 6.0`. The calling root module sets the upper bound.

## Provider documentation

- [`google_compute_network`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_network)
