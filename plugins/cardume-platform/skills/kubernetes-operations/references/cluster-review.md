# Cluster Review

Use this when the user wants to understand a cluster: what runs there, whether it is healthy,
whether it is ready for an upgrade, or how it measures against hardening guidance. All of it is
read-only.

## Before you start

- Confirm context and scope (whole cluster, some namespaces, one team).
- `kubectl auth can-i --list` (and `-n NS`) to learn what you can read. Report blind spots
  instead of guessing; cluster-scoped objects often need more access than namespaced ones.
- Large outputs go to a file (`.cardume/reports/` for scratch, `docs/` for a deliverable) and
  the chat gets the summary and the path.

## Questions a review answers

Pick the ones the user cares about; do not run all of them by reflex.

**What version and who supports it?** `kubectl version` and `kubectl get nodes -o wide`
(kubelet versions, OS image, container runtime). Compare with kubernetes.io/releases and the
provider's release channel. Node versions may lag the control plane by up to three minor
versions in current releases, but not lead it.

**What runs here and who owns it?** Workloads by namespace
(`kubectl get deploy,sts,ds,cronjob -A`), their images, and owner labels
(`app.kubernetes.io/*`, team labels). Helm releases (`helm list -A`) and GitOps applications
show which tool owns what, which matters before anyone changes anything.

**Will it survive a node loss or an upgrade?**
- Replicas below 2 for user-facing workloads.
- PDBs missing, or too strict to ever allow an eviction
  (`kubectl get pdb -A`; `ALLOWED DISRUPTIONS` stuck at 0 blocks drains).
- Readiness probes missing; liveness probes that check dependencies (they turn a database blip
  into a restart storm).
- Requests missing (BestEffort pods are evicted first and confuse the scheduler); limits much
  higher than requests on memory (overcommit leads to OOM kills under pressure).
- No topology spread or anti-affinity, so all replicas can land in one zone.

**Is access reasonable?** Cluster-admin bindings
(`kubectl get clusterrolebindings -o wide` and look for `cluster-admin`), wildcard verbs or
resources in Roles, workloads using the `default` service account, service account tokens
automounted where not needed. Pod Security Admission labels on namespaces
(`kubectl get ns -L pod-security.kubernetes.io/enforce`); `restricted` or at least `baseline`
for application namespaces. Privileged, hostPath, hostNetwork, or root containers outside
system namespaces deserve a line each.

These map to sections of the CIS Kubernetes Benchmark (RBAC and service accounts, Pod Security
Standards, network policies, secrets management) and the NSA/CISA Kubernetes Hardening Guide.
On managed clusters the provider owns most control-plane items; review the workload and policy
sections and point to the provider's benchmark (for example the GKE, EKS, or AKS CIS profiles)
for the rest.

**Is the network sane?** Services, their EndpointSlices, Ingress and Gateway resources, and
NetworkPolicies (namespaces with no policy at all are open by default). Flag the community
ingress-nginx controller if present: it was retired in March 2026 and receives no security
fixes; Gateway API is the recommended path, with `ingress2gateway` to translate existing Ingress
objects. Planning and writing that migration is `devops-engineer` work.

**What breaks on the next upgrade?** Deprecated API usage: the API server's
`apiserver_requested_deprecated_apis` metric, warnings returned by kubectl, or a tool such as
`pluto` or `kubent` against manifests and Helm releases. Compare with the Kubernetes deprecated
API migration guide. Reads of `v1` Endpoints now warn; scripts and operators should move to
EndpointSlices.

**Where is the money going?** Requests versus actual use (`kubectl top pods -A` against
requests), idle namespaces, oversized node pools, and PVCs not mounted by any pod. Hand pricing
analysis to the FinOps owner if one exists.

## Reporting a review

Lead with the three to five findings that matter most, each with the evidence (command and
output excerpt), the risk in plain words, and the suggested next step and its owner. Then a
short list of what you could not check and why. Keep the full inventory in the file.
