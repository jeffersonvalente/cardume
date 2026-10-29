# HCP Terraform Stacks: component configuration

Only for HCP Terraform Stacks. Component configuration lives in files ending in `.tfcomponent.hcl` at the root of the Stack repository (older material calls them `.tfstack.hcl`). Terraform reads all of them together and resolves blocks by their references, not by file order, so split by concern: `providers.tfcomponent.hcl`, `variables.tfcomponent.hcl`, `components.tfcomponent.hcl`, `outputs.tfcomponent.hcl`. The Stack root also needs a `.terraform-version` file. Deployments live in separate `.tfdeploy.hcl` files (see `deployment-blocks.md`).

The sections below follow the order of the HashiCorp docs: providers first, then variables, components and outputs, then `locals` and `removed`.

Source: developer.hashicorp.com/terraform/language/stacks/component/config and the block references under /terraform/language/block/stack/tfcomponent.

## required_providers

```hcl
required_providers {
  google = {
    source  = "hashicorp/google"
    version = ">= 6.0, < 9.0"
  }
}
```

A top-level block in a component file, not inside `terraform {}`. Run `terraform stacks init` after changing it to refresh `.terraform.lock.hcl`, and commit the lock file.

## provider

Providers have two labels, type and name (alias), and every provider argument must sit inside a `config` block.

```hcl
provider "google" "main" {
  config {
    project = var.project_id
    region  = var.region

    external_credentials {
      audience              = var.gcp_audience
      service_account_email = var.gcp_service_account
      identity_token        = var.identity_token
    }
  }
}
```

One configuration per region with `for_each`:

```hcl
provider "google" "regional" {
  for_each = var.regions

  config {
    project = var.project_id
    region  = each.value

    external_credentials {
      audience              = var.gcp_audience
      service_account_email = var.gcp_service_account
      identity_token        = var.identity_token
    }
  }
}
```

Reference a provider as `provider.<type>.<name>`, or `provider.<type>.<name>[each.value]` with `for_each`.

## variable

```hcl
variable "regions" {
  type        = set(string)
  description = "Regions this deployment spans."
}

variable "identity_token" {
  type      = string
  ephemeral = true
}
```

- `type` is required in Stacks. Optional arguments: `default`, `description`, `sensitive`, `nullable`, `ephemeral`. A variable without a default must be set by every deployment.
- Mark tokens and secrets `ephemeral = true` so they are not persisted in state or plan files.
- Deployments set values through their `inputs` map.

## component

Each component wraps one module.

```hcl
component "bucket" {
  for_each = var.regions

  source = "./modules/storage"

  inputs = {
    project_id      = var.project_id
    name            = "${var.prefix}-${each.value}-bkt"
    location        = each.value
    lifecycle_rules = [{ action = "Delete", age = 30 }]
  }

  providers = {
    google = provider.google.regional[each.value]
  }
}
```

- `source`, `inputs` and `providers` are required; `version`, `depends_on` and `for_each` are optional.
- `source`: local path, Git URL, public registry or HCP Terraform private registry. `version` works only with registry sources.
- `inputs` maps module variables to values; `providers` maps the module's provider names to Stack providers.
- One `component` block per top-level module; child modules need no blocks of their own.
- Modules used as components must not contain `provider` blocks. They get providers from the component.
- Reference outputs as `component.<name>.<output>`, or `component.<name>[key].<output>` with `for_each`. References create the dependency; `depends_on` is for ordering without a data reference.

## output

```hcl
output "bucket_urls" {
  type        = map(string)
  description = "Bucket URL per region."
  value       = { for region, c in component.bucket : region => c.url }
}
```

`type` and `value` are required; `description`, `sensitive` and `ephemeral` are optional. Outputs show in the HCP Terraform UI and can be published to other Stacks from the deployment file.

## locals

```hcl
locals {
  name_prefix = "${var.project}-${var.environment}"
}
```

Same semantics as in Terraform; usable in components, providers and outputs.

## removed

Deleting a component block alone is an error, because Terraform would no longer know how to destroy its resources. Delete the `component` block and add a `removed` block in its place. `source`, `from` and `providers` are required, `source` must match the old component's source, and `providers` must include every provider the module needs to destroy its resources. Do not delete those provider blocks before the removal has applied.

```hcl
removed {
  source = "./modules/redis"
  from   = component.legacy_cache

  providers = {
    google = provider.google.main
  }
}
```

For instances of a `for_each` component, give `removed` its own `for_each` (for example `for_each = var.regions_to_remove`) and use `from = component.bucket[each.value]` with the matching `provider.google.regional[each.value]`. Remove the `removed` block once every deployment has applied the destroy.

## Provider references in modules

Inside modules, keep `required_providers` with a `source` (and a minimum version) so the mapping is unambiguous, and use `configuration_aliases` when a module needs more than one configuration of the same provider:

```hcl
terraform {
  required_providers {
    google = {
      source                = "hashicorp/google"
      version               = ">= 6.0"
      configuration_aliases = [google.primary, google.secondary]
    }
  }
}
```

The component then maps both: `providers = { google.primary = provider.google.regional["us-central1"], google.secondary = provider.google.regional["us-east1"] }`.

