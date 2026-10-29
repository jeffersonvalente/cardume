---
name: kubernetes-operations
description: "Guides work on live Kubernetes clusters with kubectl (GKE, EKS, AKS, on-prem): incident triage, cluster review and inventory, and careful changes. Read-only by default; every mutation is previewed with dry-run/diff and runs only after explicit confirmation. Use when diagnosing pods, nodes, rollouts or networking, or changing a running cluster."
allowed-tools: Read Glob Grep
---

# Kubernetes Operations

> Look first, explain what you see, change only what the user has agreed to change, and prove
> the change worked.

This skill covers clusters that are already running. Writing or refactoring manifests, Helm
charts, Kustomize overlays, Terraform for the cluster itself, and CI/CD pipelines belongs to
`devops-engineer`; say so and hand over when the request is really about authoring. For
telemetry-driven investigation (SLO burn, traces, PromQL) pair with
`cardume-platform:observability-patterns`.

## What the user wants

Most requests fall under one of three goals. Name the goal to yourself, then open the one
reference that serves it. Pull the others only if the conversation moves there.

| Goal | Typical asks | Reference |
| :--- | :--- | :--- |
| **Diagnose** something broken | CrashLoopBackOff, OOMKilled, Pending pods, NotReady node, 502s, stuck rollout | [references/triage-by-symptom.md](references/triage-by-symptom.md) |
| **Explain** a cluster | "What runs here?", health review, upgrade readiness, security posture, cost hot spots | [references/cluster-review.md](references/cluster-review.md) |
| **Change** a cluster | roll back, restart, scale, cordon/drain, patch a resource, rotate a secret | [references/safe-changes.md](references/safe-changes.md) |

During or after an incident, [references/incident-record.md](references/incident-record.md)
holds the timeline and postmortem format.

## Safety principles

There is one safety model for this skill, and it is the same whatever the goal. Each rule
exists because a live cluster has no undo button for some actions and shared blast radius for
all of them.

**Establish where you are before anything else.** Run `kubectl config current-context` and
`kubectl config view --minify -o jsonpath='{..namespace}'`, and say the context and namespace
out loud. Pass `--context` and `-n` explicitly on every command after that. Most cluster
accidents are a correct command against the wrong cluster.

**Reading is free; writing is a decision.** `get`, `describe`, `logs`, `events`, `top`,
`explain`, `auth can-i`, `rollout status`, `rollout history`, `diff`, and any `--dry-run` cost
nothing and change nothing. Run them freely to build evidence. Anything that creates, updates,
deletes, restarts, scales, evicts, or execs into a container is a change.

**Changes need an explicit yes for that specific change.** Before a mutation, show the exact
command, what it will do, how you expect to verify it, and how to undo it. Then stop and wait.
A general "go ahead and fix things" earlier in the conversation does not cover a production
mutation you have not yet shown. If the user only wants guidance, give the commands and let
them run them.

**Preview with Kubernetes' own tools.** Use `kubectl diff -f`, `--dry-run=server`, and
`rollout history --revision=N` so the API server, with its admission webhooks and validation,
tells you what would happen. A preview from the server beats your reading of YAML.

**Prefer the reversible move.** Roll back a Deployment instead of editing it live. Cordon
before draining. Scale a ReplicaSet-managed workload rather than deleting its pods. Patch with
a recorded change instead of `kubectl edit` on production, because `edit` leaves no diff to
review and fights with GitOps controllers that will revert it.

**Respect the owner of the object.** If Argo CD, Flux, Helm, or an operator manages a resource
(check `metadata.managedFields`, `app.kubernetes.io/managed-by`, owner references, and
annotations such as `argocd.argoproj.io/*`), a direct kubectl change will be reverted or will
cause drift. Make the change at the source, or pause the controller with the user's agreement
and record that you did.

**Keep secrets secret.** Do not print Secret values (`get secret -o yaml`, `describe` on
env-from-secret output, `exec ... env`). Check that a key exists with
`kubectl get secret NAME -o jsonpath='{.data}' | jq 'keys'` instead. Never paste cluster data
into third-party services.

**Production is slower on purpose.** One change at a time, smallest scope first (one pod, one
node, one namespace), watch the result before the next step, and avoid changes the team cannot
observe. This mirrors the progressive-rollout and fast-rollback guidance in Google's SRE
material: most outages are caused by changes, so make each change small, detectable, and
reversible.

**Escalate rather than improvise** for etcd, control-plane components, CNI or CSI drivers,
admission webhooks, cluster-wide RBAC, and node pool or cluster deletion. These have a blast
radius of the whole cluster; describe the situation, propose the step, and let a cluster admin
decide.

### The guard hook is a backstop, not the model

`cardume-core` ships a PreToolUse hook that asks the user before `kubectl delete`, `drain`,
`cordon`, and `replace --force` (and `helm uninstall/rollback`). It does **not** catch
`apply`, `patch`, `edit`, `scale`, `set`, `label`, `annotate`, `rollout undo`, or
`rollout restart`, and it prompts even for `--dry-run` variants of the commands it does catch.
So the hook's silence never means a command is safe; the principles above still apply to every
mutation.

## Diagnose: the top-down pass

Start broad and narrow down. Each step is read-only. Stop as soon as the evidence names a
cause, and say which evidence it was.

1. **Scope.** `kubectl get pods -n NS -o wide` and `kubectl get deploy,rs -n NS`. Which pods,
   which nodes, how many restarts, since when? One pod or all? One node or all?
2. **Events and state.** `kubectl describe pod POD -n NS`. Read `Last State` (reason, exit
   code, finished time), `Ready` conditions, probe failures, image pull errors, and the Events
   at the bottom. `kubectl events -n NS --for pod/POD` gives the same events sorted by time.
3. **Logs of the crashed container.** `kubectl logs POD -n NS -c CONTAINER --previous`. The
   current container may have just started and logged nothing useful; `--previous` shows the
   one that died.
4. **What changed.** `kubectl rollout history deploy/NAME -n NS`, then compare the new and
   previous templates with `--revision=N`. Look at image tag or digest, env vars, ConfigMap and
   Secret references, resource requests and limits, probes, command/args, and service account.
5. **Dependencies.** Do the referenced ConfigMaps and Secrets exist with the expected keys? Can
   the pod reach its database or upstream (`kubectl debug` with an ephemeral container, or a
   throwaway pod in the same namespace)? Did a NetworkPolicy, quota, or node pool change?
6. **Wider context.** `kubectl get nodes`, `kubectl top pods -n NS`, and the namespace's
   recent events (`kubectl get events -n NS --sort-by=.lastTimestamp`).

**Exit codes worth knowing:** `0` the process exited on its own (wrong command, or a job-like
container in a Deployment); `1` or another small number is an application error, so read the
logs; `126`/`127` the command is not executable or not found; `137` SIGKILL, usually
`OOMKilled` (confirm the reason field) or a failed liveness probe; `139` segfault; `143`
SIGTERM, a normal shutdown that took too long or a probe-driven restart.

Per-symptom detail (Pending, ImagePullBackOff, NotReady nodes, Services with no endpoints,
stuck rollouts, DNS, evictions) is in the triage reference.

## Explain: reviewing and inventorying

Answer the question asked, from the cluster, with the commands you ran. For a full review,
cover versions and support window, workloads and their owners, reliability settings (replicas,
PDBs, probes, requests/limits, topology spread), access (RBAC, service accounts, Pod Security
Admission labels), networking (Services, EndpointSlices, Ingress or Gateway API), and
deprecated APIs. Use `kubectl auth can-i --list` first so you know what you are able to see,
and state the gaps. Write long inventories to a file rather than the chat.

## Change: doing it carefully

1. **State the intent and the evidence** that justifies it.
2. **Preview** with `kubectl diff`, `--dry-run=server`, or `rollout history --revision=N`.
3. **Show the command, impact, verification, and undo.** Wait for an explicit yes.
4. **Apply one step,** then watch: `kubectl rollout status deploy/NAME -n NS --timeout=5m`,
   `kubectl get pods -w`, events, and the user-facing signal.
5. **Verify or roll back.** If the signal does not improve, undo and report rather than
   stacking a second change on top.
6. **Record** what ran and when for the incident timeline, and tell the owner of the source
   (Git, Helm values, GitOps repo) so the live change is not silently reverted.

Rollbacks, restarts, scaling, cordon/drain with PDBs, and resource patching each have recipes in
the change reference.

## Facts that age (verified 2026-10)

- Kubernetes supports roughly the three latest minor releases with about a year of patches each
  (1.35-1.37 at the time of writing; 1.34 reached end of life on 2026-10-27). Check
  kubernetes.io/releases and the provider's own schedule (GKE, EKS, AKS channels differ).
- `v1` Endpoints is deprecated since 1.33. Use `kubectl get endpointslices -l
  kubernetes.io/service-name=SVC` when checking a Service's backends.
- The community ingress-nginx controller was retired in March 2026: no further releases or
  security fixes. Flag it in reviews (`kubectl get pods -A -l
  app.kubernetes.io/name=ingress-nginx`) and point migration to Gateway API, for which
  `ingress2gateway` translates Ingress resources. Migration authoring goes to `devops-engineer`.
- PodSecurityPolicy is gone (removed in 1.25); Pod Security Admission namespace labels replace it.
