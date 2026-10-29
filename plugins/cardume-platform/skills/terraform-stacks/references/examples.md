# HCP Terraform Stacks: worked examples

Only for HCP Terraform Stacks. Each example lists the repository files and their contents. Values such as project IDs, pool names and service accounts are placeholders; replace them with the user's real values after asking.

## 1. One region, local module

Repository:

```text
variables.tfcomponent.hcl
providers.tfcomponent.hcl
components.tfcomponent.hcl
outputs.tfcomponent.hcl
deployments.tfdeploy.hcl
modules/storage/        (copied from gcp/templates-modules/storage)
.terraform.lock.hcl
```

`variables.tfcomponent.hcl`:

```hcl
variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "bucket_name" {
  type = string
}

variable "gcp_audience" {
  type = string
}

variable "gcp_service_account" {
  type = string
}

variable "identity_token" {
  type      = string
  ephemeral = true
}
```

`providers.tfcomponent.hcl`:

```hcl
required_providers {
  google = {
    source  = "hashicorp/google"
    version = ">= 6.0, < 9.0"
  }
}

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

`components.tfcomponent.hcl`:

```hcl
component "logs_bucket" {
  source = "./modules/storage"

  inputs = {
    project_id      = var.project_id
    name            = var.bucket_name
    location        = var.region
    lifecycle_rules = [{ action = "Delete", age = 30 }]
  }

  providers = {
    google = provider.google.main
  }
}
```

`outputs.tfcomponent.hcl`:

```hcl
output "bucket_url" {
  type  = string
  value = component.logs_bucket.url
}
```

`deployments.tfdeploy.hcl`:

```hcl
identity_token "gcp" {
  audience = ["//iam.googleapis.com/projects/123456789012/locations/global/workloadIdentityPools/hcp-terraform/providers/hcp-terraform"]
}

locals {
  gcp_audience = "//iam.googleapis.com/projects/123456789012/locations/global/workloadIdentityPools/hcp-terraform/providers/hcp-terraform"
}

deployment "dev" {
  inputs = {
    project_id          = "acme-logs-dev"
    region              = "us-central1"
    bucket_name         = "acme-logs-dev-app-logs-bkt"
    gcp_audience        = local.gcp_audience
    gcp_service_account = "hcp-stacks-sa@acme-logs-dev.iam.gserviceaccount.com"
    identity_token      = identity_token.gcp.jwt
  }
}

deployment "prd" {
  inputs = {
    project_id          = "acme-logs-prd"
    region              = "us-central1"
    bucket_name         = "acme-logs-prd-app-logs-bkt"
    gcp_audience        = local.gcp_audience
    gcp_service_account = "hcp-stacks-sa@acme-logs-prd.iam.gserviceaccount.com"
    identity_token      = identity_token.gcp.jwt
  }
}
```

## 2. Modules from a registry

Private registry module, pinned by version:

```hcl
component "network" {
  source  = "app.terraform.io/acme/vpc/google"
  version = "~> 2.3"

  inputs = {
    project_id = var.project_id
    name       = var.network_name
  }

  providers = {
    google = provider.google.main
  }
}
```

Public registry module (Cloud Foundation Toolkit):

```hcl
component "network" {
  source  = "terraform-google-modules/network/google"
  version = "~> 11.0"

  inputs = {
    project_id   = var.project_id
    network_name = var.network_name
    subnets      = var.subnets
  }

  providers = {
    google = provider.google.main
  }
}
```

Check the module's current major version on the registry before pinning; the number above is an example. Registry modules must not declare their own `provider` blocks to work as components; most CFT modules satisfy this.

A Git source works too and is pinned with `?ref=`:

```hcl
source = "git::https://github.com/acme/terraform-modules.git//gcp/vpc?ref=v1.4.0"
```

## 3. Several regions

Variables gain a set of regions; provider and component iterate over it.

```hcl
variable "regions" {
  type = set(string)
}

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

component "subnet" {
  for_each = var.regions

  source = "./modules/subnet"

  inputs = {
    project_id    = var.project_id
    region        = each.value
    network       = component.network.self_link
    name          = "${var.name_prefix}-${each.value}-snet"
    ip_cidr_range = var.subnet_cidrs[each.value]
  }

  providers = {
    google = provider.google.regional[each.value]
  }
}

output "subnet_self_links" {
  type  = map(string)
  value = { for region, s in component.subnet : region => s.self_link }
}
```

The deployment then sets `regions = ["us-central1", "europe-west1"]` and a `subnet_cidrs` map with one non-overlapping range per region. Adding a region is a one-line input change; removing one needs a `removed` block for that instance (see `component-blocks.md`).
