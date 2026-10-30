# Safe Changes

Every recipe below mutates the cluster. For each one: show the preview and the exact command,
explain impact, verification, and undo, then wait for the user's explicit yes for that change.
Pass `--context` and `-n` explicitly.

## Preview tools

- `kubectl diff -f FILE` shows what `apply` would change, computed by the server.
- `--dry-run=server` runs validation and admission webhooks without persisting. Supported by
  `apply`, `create`, `patch`, `scale`, `set`, `label`, `annotate`, `drain`, `delete`, and
  `rollout undo`, among others.
- `kubectl rollout history deploy/NAME --revision=N` shows the exact template you would roll
  back to.
- `kubectl auth can-i VERB RESOURCE -n NS` confirms you have permission before a half-done
  change fails midway.

The cardume guard hook passes `--dry-run=client` and `--dry-run=server` without a prompt and asks
for the real command, so the preview needs no approval and the change still gets one.

## Roll back a Deployment

Fastest mitigation when a release caused the problem.

```bash
kubectl rollout history deploy/NAME -n NS
kubectl rollout history deploy/NAME -n NS --revision=PREV      # inspect the target
kubectl rollout undo deploy/NAME -n NS --to-revision=PREV --dry-run=server
# after explicit yes:
kubectl rollout undo deploy/NAME -n NS --to-revision=PREV
kubectl rollout status deploy/NAME -n NS --timeout=5m
```

Caveats: a rollback restores the pod template, not ConfigMaps, Secrets, database migrations, or
CRDs the release changed. If the deployment is managed by Helm or GitOps, the controller will
re-apply the bad version; roll back there (`helm rollback` or reverting the commit) or pause
sync with the owner's agreement. Tell the team to fix the source so the next deploy does not
reintroduce it.

## Restart a workload

```bash
kubectl rollout restart deploy/NAME -n NS
kubectl rollout status deploy/NAME -n NS
```

A rolling restart respects `maxUnavailable` and readiness. Prefer it to deleting pods. Restarts
hide symptoms; capture `logs --previous` and describe output first.

## Scale

```bash
kubectl get hpa -n NS                     # an HPA will override manual replica counts
kubectl scale deploy/NAME -n NS --replicas=N --dry-run=server
kubectl scale deploy/NAME -n NS --replicas=N
```

If an HPA owns the workload, change its `minReplicas`/`maxReplicas` instead. Scaling down a
StatefulSet removes the highest ordinals first and keeps their PVCs. Record the original count
so you can restore it. Scaling to zero takes a service down: treat it as an outage the user has
chosen, with the people who depend on it informed.

## Cordon and drain a node

```bash
kubectl get pdb -A                        # ALLOWED DISRUPTIONS 0 will block the drain
kubectl get pods -A -o wide --field-selector spec.nodeName=NODE
kubectl cordon NODE
kubectl drain NODE --ignore-daemonsets --delete-emptydir-data --timeout=10m --dry-run=server
kubectl drain NODE --ignore-daemonsets --delete-emptydir-data --timeout=10m
kubectl uncordon NODE                     # when the node is back, or to undo the cordon
```

Drain uses the Eviction API, so PDBs are honoured; do not add `--disable-eviction` or `--force`
to get past them without understanding which pods lose data or availability. `--delete-emptydir-data`
discards emptyDir contents; say so. Drain one node at a time and watch the rescheduled pods
become Ready before the next. On managed node pools, the provider's surge upgrade or node
replacement often does this better.

## Patch a resource

```bash
kubectl patch deploy/NAME -n NS --type=strategic -p '{"spec":{...}}' --dry-run=server -o yaml   # inspect the result
kubectl patch deploy/NAME -n NS --type=strategic -p '{"spec":{...}}'
```

Prefer `kubectl set image|resources|env` for those fields; they are clearer to review. Avoid
`kubectl edit` in production: there is no preview and no record. Any live patch is drift until
the source (manifest, chart values, GitOps repo) carries the same change; hand that to
`devops-engineer` or the owning team.

## Apply a manifest the user provides

```bash
kubectl diff -f FILE
kubectl apply -f FILE --dry-run=server
kubectl apply -f FILE --server-side       # after explicit yes
```

Server-side apply records field ownership and reports conflicts with other managers rather than
silently overwriting them.

## Delete

Delete only what you can name precisely, never by broad label selector or `--all` in
production. Check owner references first: deleting a pod owned by a ReplicaSet just recreates
it; deleting a namespace deletes everything inside it, including PVCs whose volumes may be
reclaimed. Prefer scaling, suspending a CronJob (`kubectl patch cronjob NAME -p
'{"spec":{"suspend":true}}'`), or rolling back.

## Rotate a Secret or ConfigMap

Pods read env vars from Secrets and ConfigMaps only at start; mounted volumes update with a
delay and only if the app rereads them. Plan a rolling restart after the change and confirm the
new value is in use without printing it.

## After any change

Watch `rollout status`, pod readiness, events, and the user-facing signal (error rate, latency)
for long enough to see a regression. If it is not better, undo and report. Add the change to the
incident timeline with time, command, and result.
