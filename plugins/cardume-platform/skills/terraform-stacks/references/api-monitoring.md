# HCP Terraform Stacks: watching runs through the API

Only for HCP Terraform Stacks. Use the API to report status to the user: read-only calls by default. Approving, cancelling or re-running changes infrastructure; do it only when the user explicitly asks, and say what will happen first.

Source: developer.hashicorp.com/terraform/cloud-docs/api-docs/stacks (overview, configurations, deployments, states).

## Authentication

- Base URL: `https://app.terraform.io/api/v2` (or the user's HCP Terraform Enterprise host).
- Header: `Authorization: Bearer $TFE_TOKEN`, `Content-Type: application/vnd.api+json`.
- Read the token from an environment variable the user set. Never print it, write it to a file, or put it in a command that ends up in shell history.
- A team token scoped to the Stack's project is enough for reading.

```bash
curl -sS --fail-with-body \
  -H "Authorization: Bearer $TFE_TOKEN" \
  -H "Content-Type: application/vnd.api+json" \
  "https://app.terraform.io/api/v2/stacks/$STACK_ID"
```

## What to look at, in order

| Question | Call |
| --- | --- |
| Does the Stack exist, which configuration is latest? | `GET /stacks/:stack_id` |
| Did the latest push produce a valid configuration? | `GET /stacks/:stack_id/stack-configurations`, then `GET /stack-configurations/:id` (`status`) |
| Why did a configuration fail? | `GET /stack-configurations/:id/stack-diagnostics` |
| Which deployment groups exist for that configuration? | `GET /stack-configurations/:id/stack-deployment-groups` |
| Runs of a group | `GET /stack-deployment-groups/:id/stack-deployment-runs` |
| One run | `GET /stack-deployment-runs/:id` |
| Steps of a run (plan, apply…) | `GET /stack-deployment-runs/:id/stack-deployment-steps` |
| Errors and warnings of a step | `GET /stack-deployment-steps/:id/stack-diagnostics` |
| Plan or apply detail of a step | `GET /stack-deployment-steps/:id/artifacts?name=plan-description` (or `apply-description`) |
| Current outputs | `GET /stacks/:stack_id/stack-states`, then `GET /stack-states/:id/description` |
| Configuration source | `GET /stack-configurations/:id/source-bundle` |

Deployment run statuses include `pending`, `pre-deploying`, `pre-deploying-pending-operator`, `acquiring-lock`, `pending-capacity`, `deploying`, `deploying-pending-operator`, `succeeded`, `failed` and `abandoned`. The `*-pending-operator` states mean a human must approve in HCP Terraform; report that to the user instead of approving.

## Redirects

Artifacts, state descriptions and source bundles answer with a redirect (307 or 302) to a short-lived download URL. Follow it with `curl -L`, but do not resend the `Authorization` header to the redirect host; curl drops it on cross-host redirects by default, keep it that way. A `204` on a state description means nothing has been uploaded yet.

## Polling

- Poll a run every 10–15 seconds at first, then back off (double up to about 60 seconds).
- Stop when the run is `succeeded`, `failed` or `abandoned`, or when it reaches a `*-pending-operator` state.
- On `429 Too Many Requests`, wait for the `Retry-After` interval (or back off exponentially) before the next call.
- Set an overall time limit (for example 30 minutes) and report where the run stands when it is reached.
- Use `page[number]` and `page[size]` on list calls; default page size is 20.

## Actions (only on explicit request)

| Action | Call |
| --- | --- |
| Fetch the latest commit from VCS | `POST /stacks/:stack_id/fetch-latest-from-vcs` |
| Approve all pending plans of a run | `POST /stack-deployment-runs/:id/approve-all-plans` |
| Cancel a run | `POST /stack-deployment-runs/:id/cancel` |
| Re-run a deployment group | `POST /stack-deployment-groups/:id/rerun` |

Approving is the API equivalent of `terraform apply`. Treat it with the same rule: the user does it, or tells you in this conversation to do it for a specific run after seeing the plan.

## Reporting

Summarise per deployment: configuration ID and status, run status, steps with their status, the first error diagnostic in full, and the change counts from the plan description. Keep raw JSON out of the reply; save it under `.cardume/reports/` if the user wants it.
