# Triage by Symptom

Everything here is read-only unless a line says **change**. A change follows the safety
principles in `SKILL.md`: preview, show, wait for an explicit yes, verify.

Set `NS`, `POD`, `DEPLOY`, and `NODE` as you go and always pass `--context` and `-n`.

Sections run from the bottom of the stack up: node, scheduling, image pull, the container
itself, then service, DNS and network, and finally storage. When several symptoms show at
once, start at the lowest layer that is unhealthy.

## Nodes: NotReady or under pressure

1. `kubectl get nodes -o wide` and `kubectl describe node $NODE`: Conditions
   (`MemoryPressure`, `DiskPressure`, `PIDPressure`, `Ready` reason) and the last heartbeat.
2. Is it one node, one zone, or all? One node points to the node; all nodes point to the
   control plane, network, or a cluster-wide agent.
3. Check node-level agents: `kubectl get pods -A -o wide --field-selector spec.nodeName=$NODE`
   (CNI, kube-proxy, CSI, logging daemonsets).
4. Provider view: GKE node auto-repair, EKS managed node group health, AKS node image and
   auto-repair. Cloud console or CLI shows VM state that Kubernetes cannot.

Cordoning or draining the node is a **change**; on managed node pools, replacing the node is
often safer than repairing it.

### Pods evicted or restarted without a crash

`kubectl get events -A --field-selector reason=Evicted` and node `DiskPressure` /
`MemoryPressure`. Pods with no requests are evicted first (BestEffort QoS). Preemption by a
higher PriorityClass also shows here.

## Scheduling: pods stuck in Pending

`kubectl describe pod` Events usually say why:
- `Insufficient cpu/memory`: requests exceed any node's free capacity. Check
  `kubectl describe node` Allocated resources and whether the cluster autoscaler is scaling
  (its events, or the provider's node pool status).
- `node(s) didn't match Pod's node affinity/selector` or `had untolerated taint`: scheduling
  constraints. Compare with node labels and taints.
- `unbound immediate PersistentVolumeClaims`: a storage problem; see the storage section below.
- `exceeded quota`: `kubectl describe resourcequota -n $NS`.

## Image pull: ImagePullBackOff or ErrImagePull

Events tell you which: `not found` (tag or digest wrong), `unauthorized` / `denied` (pull
secret or workload identity / IRSA / managed identity missing), `i/o timeout` (egress, private
registry endpoint, or registry outage). Check `imagePullSecrets` on the pod and service
account, and whether the node pool's identity can read the registry.

## Container start and run: CrashLoopBackOff

The container starts and exits repeatedly; the kubelet backs off restarts up to five minutes.

1. `kubectl describe pod $POD -n $NS` and read `Last State: Terminated` (reason, exit code).
2. `kubectl logs $POD -n $NS -c CONTAINER --previous` for the last crash's output.
3. Branch on what you find:
   - **`OOMKilled` / 137**: compare `kubectl top pod` and the memory limit; check whether the
     release changed the limit, JVM/runtime heap flags, or workload size. Fix is a higher limit
     or a memory fix in the app, not a restart.
   - **Exit 1 with a stack trace**: application error. Common after a release: missing env var,
     wrong config key, failed migration, unreachable dependency at startup.
   - **No logs, quick exit 0 or 127**: wrong `command`/`args`, wrong entrypoint, or missing
     binary in the image.
   - **Killed after N seconds, Events show `Liveness probe failed`**: the probe is too
     aggressive for startup time. A `startupProbe` or a longer `initialDelaySeconds` is the fix;
     that is a manifest change for `devops-engineer` or the owning team.
4. Compare the failing template with the previous one:
   `kubectl rollout history deploy/$DEPLOY -n $NS --revision=N` for the current and prior N.
   `kubectl get rs -n $NS -l app=...` shows which ReplicaSet is new.
5. Check references: `kubectl get configmap,secret -n $NS` for the names in the pod spec, and
   key names with `-o jsonpath='{.data}' | jq 'keys'` (never print values).

If the release caused it and users are affected, a rollback (**change**) is usually the fastest
mitigation; see `safe-changes.md`. Diagnose before you roll back so the evidence survives, and
capture `logs --previous` first because the old pods will be replaced.

### Rollout that does not finish

`kubectl rollout status deploy/$DEPLOY -n $NS` stalls or reports `ProgressDeadlineExceeded`.
Look at the new ReplicaSet's pods; the cause is usually one of the other symptoms in this file. Also check
`maxUnavailable`/`maxSurge` against a PDB or quota that blocks progress.

## Service and network: errors or no backends

1. `kubectl get svc $SVC -n $NS -o wide` and compare its `selector` with the pod labels.
2. `kubectl get endpointslices -n $NS -l kubernetes.io/service-name=$SVC -o wide`. No
   endpoints means the selector matches nothing or the pods are not Ready.
3. `targetPort` must match the container port (name or number).
4. Test from inside: `kubectl debug -it $POD -n $NS --image=busybox:1.36 --target=CONTAINER`
   or a temporary pod, then `wget -qO- http://$SVC.$NS.svc.cluster.local:PORT/health`. Running
   a debug container is a minor **change**; ask first in production.
5. In front of the Service: Ingress or Gateway/HTTPRoute status conditions
   (`kubectl describe httproute`, `kubectl get gateway -A`), the controller's logs, and any
   NetworkPolicy in the namespace.

### Name resolution (DNS)

`kubectl get pods -n kube-system -l k8s-app=kube-dns` (CoreDNS or kube-dns), their logs, and a
lookup from a debug pod (`nslookup kubernetes.default`). Check the pod's `dnsPolicy` and the
`ndots` setting if external names resolve slowly.

## Storage: volumes that do not bind or attach

`kubectl describe pod` Events show `unbound immediate PersistentVolumeClaims` (or a
mount/attach error). Run `kubectl get pvc -n $NS`, then read the StorageClass and the CSI
driver events. Zonal volumes pin pods to one zone.

## When the evidence runs out

Say what you checked and what it ruled out, list the remaining hypotheses with the next command
for each, and ask the user for what only they can see (dashboards, deploy notes, provider
console). Do not try remediations at random to see what sticks.
