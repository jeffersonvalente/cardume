# Project custom role

Defines a project-level custom IAM role with an explicit permission list. Grant the role separately, to groups or service accounts, never to individual users where a group would do.

## Usage

```hcl
module "log_reader_role" {
  source      = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/iam?ref=v1.0.0"
  project_id  = var.project_id
  role_id     = var.role_id
  title       = var.role_title
  permissions = var.role_permissions
}
```

Pin `ref` to a release tag of your modules repository and bump it on purpose.

## Inputs

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | `string` | yes | ID of the project where the custom role is defined. |
| `role_id` | `string` | yes | Role ID. Letters, digits, underscores and periods only, 3 to 64 characters. |
| `title` | `string` | yes | Human-readable role title. |
| `description` | `string` | no | What the role is for and who should hold it. |
| `permissions` | `list(string)` | yes | Exact permissions granted, for example storage.objects.get. Keep the list to what the workload calls. |
| `stage` | `string` | no | Launch stage of the role: ALPHA, BETA, GA, DEPRECATED, DISABLED or EAP. |

## Outputs

| Name | Description |
| --- | --- |
| `id` | Full role name, for example projects/my-project/roles/logReader_role. |
| `role_id` | Short role ID. |

## Requirements

Terraform `>= 1.5.0` (or OpenTofu `>= 1.6`) and the `hashicorp/google` provider `>= 6.0`. The calling root module sets the upper bound.

## Provider documentation

- [`google_project_iam_custom_role`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_custom_role)
