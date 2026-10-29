# Cloud Storage bucket

Creates a private bucket: uniform bucket-level access and public access prevention are always on. Versioning, CMEK, labels and lifecycle rules are inputs.

## Usage

```hcl
module "app_logs" {
  source          = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/storage?ref=v1.0.0"
  project_id      = var.project_id
  name            = var.bucket_name
  location        = var.region
  versioning      = var.versioning
  lifecycle_rules = var.lifecycle_rules
}

variable "lifecycle_rules" {
  type = list(object({
    action = string
    age    = optional(number)
  }))
  default = [{ action = "Delete", age = 30 }]
}
```

Pin `ref` to a release tag of your modules repository and bump it on purpose.

## Inputs

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | `string` | yes | ID of the project that owns the bucket. |
| `name` | `string` | yes | Bucket name. Globally unique, 3 to 63 characters, lowercase letters, digits, hyphens, underscores and dots. |
| `location` | `string` | yes | Region (us-central1), dual-region or multi-region (US, EU) of the bucket. |
| `storage_class` | `string` | no | Default storage class: STANDARD, NEARLINE, COLDLINE or ARCHIVE. |
| `versioning` | `bool` | no | Keep noncurrent object versions after overwrite or delete. |
| `kms_key_name` | `string` | no | Cloud KMS key for default encryption (CMEK). Null keeps Google-managed keys. The Cloud Storage service agent needs encrypt/decrypt on the key. |
| `lifecycle_rules` | `list(object(...))` | no | Lifecycle rules. action is Delete, SetStorageClass or AbortIncompleteMultipartUpload; storage_class is required only for SetStorageClass. |
| `labels` | `map(string)` | no | Labels for cost allocation, for example { env = "prd", team = "payments" }. |

## Outputs

| Name | Description |
| --- | --- |
| `name` | Bucket name. |
| `url` | gs:// URL of the bucket. |
| `self_link` | Bucket self link. |

## Requirements

Terraform `>= 1.5.0` (or OpenTofu `>= 1.6`) and the `hashicorp/google` provider `>= 6.0`. The calling root module sets the upper bound.

## Provider documentation

- [`google_storage_bucket`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket)
