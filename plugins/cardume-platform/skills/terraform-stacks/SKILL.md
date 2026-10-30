---
name: terraform-stacks
description: "Generates Terraform root modules from bundled GCP templates, without running apply. Use when asked for Terraform for a GCP resource, a new stack or HCP Terraform Stacks."
metadata:
  copyright: "Copyright (c) Cardume contributors. MIT License."
compatibility: "Needs Claude Code with the Cardume plugins for template paths and user_config values; the guidance itself is portable to any Terraform or OpenTofu workflow."
---

# Terraform stacks

Write Terraform that a person reviews, plans and applies. This skill produces files (or an inline draft) and checks them offline. It never runs `terraform apply`, `terraform destroy` or any state-mutating command, because those change real infrastructure and the person who owns the cloud account must make that call with the plan in front of them.

"Stack" here means a root module: one directory with its own state that composes reusable modules for one concern in one environment (a network, a cluster, a bucket). HCP Terraform Stacks, the product, is covered separately at the end.

## Inputs you already have

The plugin's user configuration supplies three values. Read them before asking the user anything:

| Value | Used for | Placeholder default |
| --- | --- | --- |
| `${user_config.terraform_modules_repo}` | Git source of the shared modules (`<repo>.git//gcp/<module>?ref=<tag>`) | `git@github.com:YOUR_ORG/terraform-modules` |
| `${user_config.terraform_state_bucket_prefix}` | Fallback state bucket name `<prefix>-tfstate-<env>`, used only when the user or the repository gives no full bucket name | `YOUR_ORG` |
| `${user_config.default_region}` | Region when the user names none | `us-central1` |

A value still equal to its placeholder means "not configured". Treat it as unknown rather than writing `YOUR_ORG` into code that someone might apply.

## Bundled templates

Everything lives under `${CLAUDE_PLUGIN_ROOT}/skills/terraform-stacks/gcp/`.

Reusable modules, in `gcp/templates-modules/<name>/` (each has `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf` and a `README.md` with inputs, outputs and a usage block):

| Module | Creates | Safe defaults built in |
| --- | --- | --- |
| `vpc` | Custom-mode VPC | No auto subnets |
| `subnet` | Subnet, optional Cloud Router + NAT | Private Google Access on, flow logs optional |
| `firewall` | One ingress rule | Internet sources refused unless `allow_internet_source` |
| `iam` | Custom project role | Explicit permission list |
| `compute_instance` | VM | OS Login unless SSH keys are passed, no external IP, Shielded VM |
| `gke` | Regional GKE cluster | Private nodes, release channel, Workload Identity, deletion protection |
| `nodepool` | Autoscaled node pool | Dedicated service account, surge upgrades |
| `postgres` | Cloud SQL for PostgreSQL | Private Service Connect, backups, PITR, deletion protection |
| `redis` | Memorystore for Redis | Private network, maintenance window |
| `storage` | Cloud Storage bucket | Uniform bucket-level access, `public_access_prevention = "enforced"`, `force_destroy = false` |

Root-module templates, in `gcp/templates-stack/`: `storage/`, `networking/vpc/`, `networking/subnet/`, `compute/gke/`. Each holds `providers.tf` (terraform block, GCS backend, provider), `main.tf` (module calls), `variables.tf` and `outputs.tf`. For Cloud SQL, Memorystore, firewalls, VMs or custom roles there is no stack template yet: build the root module from the module's README usage block, in the same shape.

AWS templates (`gcp/`'s sibling `aws/`) do not exist yet. For an AWS request, say so and ask whether to write plain `hashicorp/aws` resources from the provider documentation before improvising.

## Workflow

### 1. Read the repository first

Look for existing Terraform before you copy a template: `Glob` for `**/*.tf`, `**/*.tfvars`, `.terraform.lock.hcl`, `.tflint.hcl`. When the repository already has a layout, a naming scheme, a backend convention or a modules source, follow it; consistency inside one codebase matters more than any template. Use the templates when the repository is empty or the user asks for a fresh stack.

### 2. Decide the shape

Google's best-practices guide recommends one directory per environment (for example `environments/dev`, `environments/prd`) that calls shared modules, and keeping each root module small enough that a plan stays readable and a mistake stays local. Follow that:

- One root module per concern per environment. A cluster and the VPC it sits in are separate stacks; pass the VPC's self links in as variables (or read them with `terraform_remote_state` or data sources if the repository already does).
- Prefer environment directories over CLI workspaces when environments differ in credentials, projects or shape. HashiCorp notes that CLI workspaces share one backend and one configuration, so they do not isolate credentials or access.
- File layout follows HashiCorp's standard module structure: `main.tf`, `variables.tf`, `outputs.tf`, plus `providers.tf` or `versions.tf` for the terraform and provider blocks. Add a `README.md` for anything others will maintain.
- Per-environment values go in `terraform.tfvars` (or `<env>.tfvars`) beside the root module. Never put secrets in tfvars or variable defaults; reference Secret Manager or pass them through the CI environment.

### 3. Resolve the values

List every input the stack needs and sort it into: given by the user, derivable (region from config, environment from the directory), or unknown. Ask about unknowns that change what gets built or what it costs (machine sizes, HA, CIDR ranges, who needs access). Leave cosmetic or reviewer-owned values as variables with a clear `description` instead of inventing them.

Names: use the repository's convention. With none, propose a predictable pattern such as `<project>-<env>-<purpose>` and keep resource-type suffixes consistent; Cloud Storage bucket names are global, so include something project-specific.

### 4. Generate

- Call the shared modules from `${user_config.terraform_modules_repo}` and pin `?ref=` to a release tag, never a branch, so a plan today and a plan next month build the same thing.
- Copy the template's `required_version` and provider range (`>= 6.0, < 9.0` for `hashicorp/google`). Both bounds matter: the lower bound guarantees the arguments exist, the upper bound keeps a major release from changing behaviour under you.
- Backend: `backend "gcs"` with the state bucket the user names (or the one the repository already uses), taken exactly as given. Only when no full name is known, fall back to `bucket = "${user_config.terraform_state_bucket_prefix}-tfstate-<env>"`, and ask instead if the prefix is still the placeholder. Give the backend a `prefix` unique to this stack and environment. Match an existing prefix scheme if there is one. GCS state locking needs no extra configuration. When bucket or prefix differ per environment, a partial configuration (`-backend-config=backend-<env>.hcl`) keeps one code tree for all of them.
- Labels on every resource that takes them (`env`, `team`, `stack` at least) so billing exports can attribute cost.
- Keep the safe defaults of the modules. If the user asks to turn one off (public bucket, external IP, public GKE endpoint, `deletion_protection = false`), do it only on an explicit request, and say in the hand-over what it exposes.
- Pass identities in as variables; do not create service account keys. CI should authenticate with Workload Identity Federation (GitHub Actions OIDC, HCP Terraform dynamic credentials).

### 5. Check offline

Run only commands that need no cloud credentials and touch no state:

```bash
terraform fmt -recursive
terraform init -backend=false
terraform validate
tflint --recursive        # if installed
```

`init -backend=false` downloads providers and modules (it needs network access to the modules repository) but does not touch the backend. Commit the generated `.terraform.lock.hcl`; HashiCorp recommends versioning it so every run uses the same provider builds. If a check fails because a tool or the modules repository is not reachable, say so instead of claiming the code validated.

`terraform plan` reads real state and calls cloud APIs. Run it only if the user asks and credentials are already set up, and show the summary of adds, changes and destroys.

### 6. Hand over

Tell the user the files written, what they create, the values left as variables, the checks run and their result, and the commands for them to run:

```bash
terraform init -backend-config=backend-prd.hcl   # if using partial config
terraform plan -out=tfplan
terraform apply tfplan
```

Point out any resource the plan will replace or delete if you can tell from the change.

Once the code is accepted, you may offer a short architecture write-up of the stack, in whatever format the team uses (Markdown by default). `references/design-doc.md` has the outline; write it only if the user wants it.

## Review-only inline draft

When the user wants code to review and gives only some of the facts (for example a project and a region, but no modules repository, state bucket or naming scheme), do not stop to ask and do not write files. Reply with a self-contained draft in the message:

- Use `google_*` resources directly, mirroring the bundled module's safe defaults, unless a real modules repository is configured.
- Put the given facts in variable defaults or a `terraform.tfvars` block; make every unknown a variable without a default.
- Leave out the `backend` block and say that state storage is still to be decided; local state is fine for reviewing a plan, not for a shared environment.
- State that nothing was applied and list the commands for the user to run.
- Spell out every expiry or retention the user asked for as an explicit rule (a lifecycle or cleanup policy with the exact age), and keep the private-by-default settings from the security baseline below.

For example, a Docker repository in Artifact Registry for a staging project in `europe-west1`, where untagged images older than 14 days are cleaned up but the ten newest versions are always kept, comes out like this:

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.0, < 9.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type    = string
  default = "northwind-builds-stg"
}

variable "region" {
  type    = string
  default = "europe-west1"
}

variable "repository_id" {
  description = "Repository name, unique within the project and region."
  type        = string
}

variable "labels" {
  type    = map(string)
  default = {}
}

resource "google_artifact_registry_repository" "images" {
  repository_id          = var.repository_id
  location               = var.region
  format                 = "DOCKER"
  description            = "Container images built by CI"
  labels                 = var.labels
  cleanup_policy_dry_run = false

  docker_config {
    immutable_tags = true
  }

  cleanup_policies {
    id     = "delete-old-untagged"
    action = "DELETE"
    condition {
      tag_state  = "UNTAGGED"
      older_than = "1209600s" # 14 days
    }
  }

  cleanup_policies {
    id     = "keep-recent"
    action = "KEEP"
    most_recent_versions {
      keep_count = 10
    }
  }
}

output "repository_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.images.repository_id}"
}
```

Then say in the reply what the draft deliberately leaves out and why: here, no IAM grants (the repository stays private; give CI a writer role and runtimes a reader role with `google_artifact_registry_repository_iam_member`, never `allUsers`), and that `KEEP` policies win over `DELETE`. For a Cloud Storage bucket the same pattern applies with `uniform_bucket_level_access`, `public_access_prevention = "enforced"` and a `lifecycle_rule` whose `condition { age = N }` matches the retention asked for; mention that with object versioning on, an age-based delete only makes objects noncurrent, so versioned buckets need a noncurrent-version rule as well.

## Security baseline for GCP

These come from Google's Terraform and security guidance and the CIS Google Cloud Foundations Benchmark. Generate them by default; explain any departure.

- Buckets: uniform bucket-level access and public access prevention enforced.
- IAM: grant roles to groups or service accounts with `google_project_iam_member` (additive). Use `_binding` or `_policy` resources only when the user wants Terraform to own every member of a role, since those remove grants made elsewhere. No `roles/owner` or `roles/editor` for workloads.
- No service account keys and no `allUsers`/`allAuthenticatedUsers` members.
- Compute: no external IP unless required, OS Login instead of metadata SSH keys, Shielded VM.
- GKE: private nodes, a release channel, Workload Identity, a node service account with minimal roles.
- Databases: private connectivity, automated backups, deletion protection.
- Firewall: no `0.0.0.0/0` sources on admin ports (22, 3389); scope by tags or service accounts.

## HCP Terraform Stacks

Use these only when the user is on HCP Terraform and asks for Stacks (`.tfcomponent.hcl` and `.tfdeploy.hcl` files). The bundled modules work as Stack components unchanged, since they contain no provider blocks.

| Need | Read |
| --- | --- |
| `required_providers`, `provider`, `variable`, `component`, `output`, `locals`, `removed` blocks | `references/component-blocks.md` |
| `deployment`, `deployment_group`, `deployment_auto_approve`, `identity_token`, `store` | `references/deployment-blocks.md` |
| Passing outputs between Stacks (`publish_output`, `upstream_input`) | `references/linked-stacks.md` |
| Complete repositories to copy from | `references/examples.md` |
| Reading run status through the API | `references/api-monitoring.md` |
| Errors and stuck runs | `references/troubleshooting.md` |

## Sources

- HashiCorp: Terraform language, standard module structure, style guide, version constraints, dependency lock file, `gcs` backend, workspaces, and Stacks documentation (developer.hashicorp.com/terraform).
- Google Cloud: "Best practices for using Terraform" (cloud.google.com/docs/terraform/best-practices), public access prevention and Object Lifecycle Management docs.
- `hashicorp/google` provider documentation on the Terraform Registry.
- CIS Google Cloud Platform Foundation Benchmark.
