# Ingress firewall rule

Creates one ingress allow rule scoped by source ranges, ports and target tags. A precondition rejects `0.0.0.0/0` unless `allow_internet_source` is set on purpose.

## Usage

```hcl
module "allow_iap_ssh" {
  source        = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/firewall?ref=v1.0.0"
  project_id    = var.project_id
  network       = var.network_name
  name          = var.iap_ssh_rule_name
  source_ranges = var.iap_source_ranges
  target_tags   = var.ssh_target_tags
  allow         = var.iap_ssh_allow
}
```

Pin `ref` to a release tag of your modules repository and bump it on purpose.

## Inputs

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | `string` | yes | ID of the Google Cloud project that owns the network. |
| `network` | `string` | yes | Name or self link of the VPC network the rule applies to. |
| `name` | `string` | yes | Firewall rule name. |
| `description` | `string` | no | Why the rule exists. Reviewers read this first. |
| `priority` | `number` | no | Rule priority from 0 (highest) to 65535. |
| `source_ranges` | `list(string)` | yes | Source CIDR blocks allowed to connect, for example the IAP range 35.235.240.0/20. |
| `target_tags` | `list(string)` | no | Network tags of the instances the rule targets. An empty list targets every instance in the network. |
| `allow` | `list(object(...))` | yes | Protocols and ports to allow, for example [{ protocol = "tcp", ports = ["443"] }]. |
| `logging` | `bool` | no | Record connections matched by this rule in Firewall Rules Logging. |
| `allow_internet_source` | `bool` | no | Explicit opt-in for 0.0.0.0/0 in source_ranges. |

## Outputs

| Name | Description |
| --- | --- |
| `id` | Firewall rule ID. |
| `name` | Firewall rule name. |

## Requirements

Terraform `>= 1.5.0` (or OpenTofu `>= 1.6`) and the `hashicorp/google` provider `>= 6.0`. The calling root module sets the upper bound.

## Provider documentation

- [`google_compute_firewall`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_firewall)
