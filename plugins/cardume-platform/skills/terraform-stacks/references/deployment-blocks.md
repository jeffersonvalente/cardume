# HCP Terraform Stacks: deployment configuration

Only for HCP Terraform Stacks. Deployment configuration lives in `.tfdeploy.hcl` files at the Stack root. It says how many copies of the Stack exist (deployments), with which inputs, how they authenticate and when plans may apply without a human.

Sections follow the order of the HashiCorp deployment-configuration docs (`deployment`, `deployment_group`, `deployment_auto_approve`, `identity_token`, `store`, then `locals`); `publish_output` and `upstream_input` are in `linked-stacks.md`.

Source: developer.hashicorp.com/terraform/language/stacks/deploy/config, developer.hashicorp.com/terraform/language/block/stack/tfdeploy and the identity-token examples in github.com/hashicorp-guides/terraform-stacks-identity-tokens.

## deployment

```hcl
deployment "prd" {
  inputs = {
    project_id          = local.project_ids.prd
    regions             = ["us-central1", "us-east1"]
    gcp_audience        = local.gcp_audience
    gcp_service_account = "hcp-stacks-sa@acme-orders-prd.iam.gserviceaccount.com"
    identity_token      = identity_token.gcp.jwt
  }
  deployment_group = deployment_group.production
}
```

- `inputs` keys must match component-configuration variables.
- Without `deployment_group`, the deployment gets its own default group.

## deployment_group and deployment_auto_approve

Groups share approval rules. Rules are `check` blocks evaluated against the plan's `context`.

```hcl
deployment_auto_approve "additive_only" {
  check {
    condition = context.plan.changes.remove == 0
    reason    = "The plan removes resources."
  }
  check {
    condition = context.plan.changes.total <= 10
    reason    = "More than ten changes need a human."
  }
}

deployment_group "non_production" {
  auto_approve_checks = [deployment_auto_approve.additive_only]
}

deployment_group "production" {
}
```

Useful context values: `context.plan.changes.{add,change,import,remove,total}`, `context.plan.component_changes["component.<name>"]`, `context.plan.mode` (`normal`, `refresh-only`, `import`, `destroy`), `context.plan.applyable`, `context.plan.replans`, `context.plan.deployment.deployment_name`, `context.success`, `context.errors`, `context.warnings`, `context.operation`.

All checks of all listed rules must pass for an automatic apply. Every Stack also approves empty plans by default. Leave production without auto-approval unless the user decides otherwise.

## identity_token (OIDC)

HCP Terraform mints a JWT per deployment run. The cloud trusts it through workload identity federation, so no long-lived keys live in HCP Terraform.

```hcl
identity_token "gcp" {
  audience = ["//iam.googleapis.com/projects/123456789012/locations/global/workloadIdentityPools/hcp-terraform/providers/hcp-terraform"]
}
```

Pass `identity_token.<name>.jwt` to an ephemeral variable through `inputs`, then to the provider:

| Cloud | Typical audience | Provider settings |
| --- | --- | --- |
| Google Cloud | Must match the audience accepted by the workload identity pool provider (often the provider's full resource name, or a custom value such as `hcp.workload.identity` if you configured one) | `external_credentials { audience, service_account_email, identity_token }` |
| AWS | `aws.workload.identity` | `assume_role_with_web_identity { role_arn, web_identity_token }` |
| Azure | `api://AzureADTokenExchange` | `use_oidc = true`, `oidc_token`, `client_id`, `subscription_id`, `tenant_id` |

Restrict the trust on the cloud side to your organization, project and Stack (claims such as `terraform_organization_name`, `terraform_project_name`, `terraform_stack_name`), not just the audience.

## store

Read values from an HCP Terraform variable set without copying them into the repository:

```hcl
store "varset" "shared" {
  name     = "platform-shared"
  category = "terraform"
}
```

Reference as `store.varset.shared.<variable_name>`.

## locals

```hcl
locals {
  gcp_audience = "//iam.googleapis.com/projects/123456789012/locations/global/workloadIdentityPools/hcp-terraform/providers/hcp-terraform"
  project_ids = {
    dev = "acme-orders-dev"
    prd = "acme-orders-prd"
  }
}
```

## Destroying a deployment

Set `destroy = true` on the deployment, push, and approve the destroy plan in HCP Terraform. Once it has applied, delete the block. Deleting the block first leaves the deployment's resources orphaned in HCP Terraform's eyes.

```hcl
deployment "sandbox" {
  inputs  = { project_id = "acme-orders-sbx", regions = ["us-central1"], gcp_audience = local.gcp_audience, gcp_service_account = "hcp-stacks-sa@acme-orders-sbx.iam.gserviceaccount.com", identity_token = identity_token.gcp.jwt }
  destroy = true
}
```

The user approves this in HCP Terraform. Do not trigger it through the API on their behalf.
