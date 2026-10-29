# HCP Terraform Stacks: troubleshooting

Only for HCP Terraform Stacks. Each entry: the symptom, the usual cause, the fix. Read the full diagnostic first (`stack-diagnostics`, see `api-monitoring.md`); the summary line rarely names the real cause.

## Configuration errors

**Cycle between components.** Two components reference each other's outputs, directly or through a third. Break the loop: move the shared value into a variable or local, or split one module so the dependency runs one way. `depends_on` cannot fix a cycle.

**Variable has no value / wrong type.** A deployment's `inputs` misses a key or passes a list where a set or map is declared. Every `variable` needs `type`; match the deployment inputs to it. Sets and maps from `for_each` must be known at plan time.

**Validation failure in a module.** Module `validation` blocks still run. The diagnostic names the module variable; trace it back through the component's `inputs`.

**Provider configured inside a module.** Modules used as components must not have `provider` blocks. Remove them and pass providers through the component's `providers` map. For several configurations of one provider, declare `configuration_aliases` in the module.

**Provider not found or wrong source.** The component's `providers` map key must match the provider's local name in the module's `required_providers`. Mismatched sources (`hashicorp/google` vs `hashicorp/google-beta`) need both declared.

**Output without type.** Stack `output` blocks require `type`.

## Plans and applies

**Plan stuck in planning or pending capacity.** The organization's concurrency is used up, or an agent pool is offline. Check other runs and the agent pool; cancel abandoned runs only with the user's consent.

**Run waiting on approval.** Status `*-pending-operator`: a plan failed the deployment group's auto-approve checks, or the group has none. Show the user the failed `reason` strings. A human approves in HCP Terraform.

**Deferred changes.** A plan shows some changes as deferred because a value (often a `for_each` key or a new resource's ID) is unknown until another part applies. Apply the partial plan; HCP Terraform replans and converges. Repeated deferrals point to a value that is never known in planning; restructure so `for_each` keys come from variables.

**Removed component errors.** Deleting a `component` block without a `removed` block fails. Add `removed` with the same `source` and providers, apply, then delete it.

## Authentication

**OIDC token rejected.** The `identity_token` audience does not match what the cloud trusts, or the trust condition does not match the token's claims. For Google Cloud, compare the audience with the workload identity pool provider and check its attribute condition; confirm the service account grants `roles/iam.workloadIdentityUser` to the pool principal. For AWS, check the role's trust policy `aud` and `sub` conditions.

**Permission denied after a successful login.** The federated identity authenticated but lacks the IAM role for that resource. Grant the narrowest role that covers the failing API call; do not grant `roles/owner` or `roles/editor` to get past it.

## Modules and dependencies

**Lock file mismatch.** `.terraform.lock.hcl` is missing a provider or a checksum for the HCP Terraform platform. Run `terraform stacks init` locally (the user runs it), commit the updated lock file, push.

**Registry module fails to load.** Wrong address or a version constraint that no release satisfies; private registry modules need the organization to have access. Check the address on the registry page and loosen or correct `version`.

**Local module path not found.** Paths are relative to the Stack root and the module must be committed. `../` outside the repository does not work in HCP Terraform.

**Published output missing downstream.** The upstream Stack has not applied since `publish_output` was added, or the name differs. See `linked-stacks.md`.

## CLI and CI

**`terraform stacks` command missing.** The installed Terraform is too old for the Stacks CLI. Upgrade Terraform; OpenTofu has no Stacks support.

**CI pipeline cannot authenticate.** Use a team token stored as a masked CI secret, scoped to the project. Do not use a user token in CI.

**Need more detail.** Set `TF_LOG=DEBUG` (or `TRACE`) for local `terraform stacks` commands and read the log; strip tokens before sharing it.
