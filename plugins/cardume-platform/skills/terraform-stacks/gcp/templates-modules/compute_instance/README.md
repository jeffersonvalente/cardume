# Compute Engine VM

Creates a Shielded VM with a CMEK-encrypted boot disk, a dedicated service account, optional external IP, a startup script and an optional start/stop schedule. OS Login is on unless `ssh_keys` is set; prefer OS Login so access follows IAM.

## Usage

```hcl
module "bastion" {
  source                = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/compute_instance?ref=v1.0.0"
  project_id            = var.project_id
  name                  = var.vm_name
  region                = var.region
  zone                  = var.zone
  machine_type          = var.machine_type
  image                 = var.image
  kms_key_self_link     = var.kms_key_self_link
  subnetwork            = var.subnet_self_link
  service_account_email = var.vm_service_account
  schedule              = var.vm_schedule
}
```

Pin `ref` to a release tag of your modules repository and bump it on purpose.

## Inputs

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | `string` | yes | ID of the project that hosts the VM. |
| `name` | `string` | yes | Instance name. |
| `region` | `string` | yes | Region of the zone, used for the schedule policy. |
| `zone` | `string` | yes | Zone of the instance, for example us-central1-a. |
| `machine_type` | `string` | yes | Machine type, for example e2-medium. |
| `image` | `string` | yes | Boot image, for example debian-cloud/debian-12. |
| `disk_size_gb` | `number` | no | Boot disk size in GB. |
| `disk_type` | `string` | no | Boot disk type: pd-standard, pd-balanced or pd-ssd. |
| `kms_key_self_link` | `string` | yes | Cloud KMS key used to encrypt the boot disk (CMEK). The Compute Engine service agent needs roles/cloudkms.cryptoKeyEncrypterDecrypter on it. |
| `subnetwork` | `string` | yes | Self link of the subnet for the primary interface. |
| `external_ip` | `bool` | no | Attach an ephemeral external IP. Keep false and use IAP TCP forwarding or Cloud NAT where possible. |
| `network_tags` | `list(string)` | no | Network tags used by firewall rules. |
| `ssh_keys` | `string` | no | Instance-level ssh-keys metadata, one USERNAME:KEY_TYPE KEY_VALUE COMMENT entry per line. Leave null to use OS Login instead. |
| `service_account_email` | `string` | yes | Dedicated service account the VM runs as. |
| `scopes` | `list(string)` | no | OAuth scopes. Keep cloud-platform and control access with IAM roles on the service account. |
| `startup_script` | `string` | no | Script run on every boot. |
| `schedule` | `object(...)` | no | Optional start/stop schedule. Cron expressions in the given IANA time zone; start_cron may be omitted for stop-only schedules. |
| `deletion_protection` | `bool` | no | Refuse deletion of the instance while true. |

## Outputs

| Name | Description |
| --- | --- |
| `id` | Instance ID. |
| `self_link` | Instance self link. |
| `internal_ip` | Primary internal IP address. |
| `external_ip` | Ephemeral external IP, null when none is attached. |

## Requirements

Terraform `>= 1.5.0` (or OpenTofu `>= 1.6`) and the `hashicorp/google` provider `>= 6.0`. The calling root module sets the upper bound.

## Provider documentation

- [`google_compute_instance`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance)
- [`google_compute_resource_policy`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_resource_policy)
