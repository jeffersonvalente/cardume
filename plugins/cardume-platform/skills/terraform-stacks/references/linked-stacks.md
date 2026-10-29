# HCP Terraform Stacks: linked Stacks

Only for HCP Terraform Stacks. A Stack can publish values that other Stacks in the same HCP Terraform project consume. When a published value changes, HCP Terraform queues runs for the consuming Stacks.

Typical split: a `network` Stack owns the VPC and subnets; an `apps` Stack consumes subnet self links.

## Producer: publish_output

In the producer's `.tfdeploy.hcl`. The value usually references an output of one deployment.

```hcl
publish_output "prd_subnet_self_link" {
  description = "Application subnet in prd."
  value       = deployment.prd.subnet_self_link
}

publish_output "dev_subnet_self_link" {
  description = "Application subnet in dev."
  value       = deployment.dev.subnet_self_link
}
```

`subnet_self_link` must be an `output` in the producer's component configuration. Publish one value per consumer need, and name it with the environment so consumers cannot pick the wrong one.

## Consumer: upstream_input

In the consumer's `.tfdeploy.hcl`:

```hcl
upstream_input "network" {
  type   = "stack"
  source = "app.terraform.io/acme/platform/network"
}

deployment "prd" {
  inputs = {
    subnet_self_link = upstream_input.network.prd_subnet_self_link
  }
}
```

- `type` is always `"stack"`.
- `source` is `app.terraform.io/<organization>/<project>/<stack>`; the upstream Stack must be in the same project.

## Practices

- Keep the dependency one-way. Two Stacks that consume each other cannot converge.
- Publish IDs and self links, not whole objects; a smaller contract changes less often.
- The upstream must have applied at least once before the downstream can plan with its values.
- Renaming or removing a published output breaks consumers: add the new name, migrate consumers, then remove the old one.
