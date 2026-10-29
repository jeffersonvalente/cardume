# Read-only evidence

Commands that observe without changing anything. Run them with an audit or viewer role, and
record each one (with filter) as the "how it was checked" line of the finding it supports.

Before running anything, confirm identity and scope:

```bash
aws sts get-caller-identity
gcloud config list --format='value(core.account,core.project)'
az account show --query '{sub:name,id:id,user:user.name}'
kubectl config current-context
```

Never print secret values. Avoid `kubectl get secret -o yaml`, `aws secretsmanager
get-secret-value`, `gcloud secrets versions access`, `az keyvault secret show`.

## AWS

```bash
# Organization shape and guardrails
aws organizations describe-organization
aws organizations list-accounts --query 'Accounts[].{id:Id,name:Name,status:Status}'
aws organizations list-policies --filter SERVICE_CONTROL_POLICY

# Root and identity
aws iam get-account-summary --query 'SummaryMap.{rootMFA:AccountMFAEnabled,rootKeys:AccountAccessKeysPresent}'
aws iam get-credential-report --query Content --output text | base64 -d   # only if a report was already generated
aws iam list-users --query 'Users[].UserName'
aws accessanalyzer list-findings --analyzer-arn <arn> --filter '{"status":{"eq":["ACTIVE"]}}'

# Audit and detection
aws cloudtrail describe-trails --query 'trailList[].{name:Name,multi:IsMultiRegionTrail,org:IsOrganizationTrail}'
aws cloudtrail get-trail-status --name <trail>
aws guardduty list-detectors
aws securityhub get-findings --filters '{"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}],"RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}]}' --max-items 50
aws configservice describe-configuration-recorder-status

# Exposure
aws s3control get-public-access-block --account-id <id>
aws ec2 describe-security-groups --filters Name=ip-permission.cidr,Values=0.0.0.0/0 --query 'SecurityGroups[].{id:GroupId,name:GroupName}'

# Reliability and recovery
aws rds describe-db-instances --query 'DBInstances[].{id:DBInstanceIdentifier,multiAZ:MultiAZ,retention:BackupRetentionPeriod,encrypted:StorageEncrypted,engine:EngineVersion}'
aws backup list-backup-plans
aws backup list-restore-jobs --max-results 20
aws eks list-clusters
aws eks describe-cluster --name <c> --query 'cluster.{version:version,public:resourcesVpcConfig.endpointPublicAccess,cidrs:resourcesVpcConfig.publicAccessCidrs}'

# Cost
aws ce get-cost-and-usage --time-period Start=<yyyy-mm-01>,End=<yyyy-mm-01> --granularity MONTHLY --metrics UnblendedCost --group-by Type=DIMENSION,Key=SERVICE
aws ce get-savings-plans-coverage --time-period Start=<..>,End=<..>
aws ec2 describe-volumes --filters Name=status,Values=available --query 'Volumes[].{id:VolumeId,gb:Size}'
aws ec2 describe-nat-gateways --query 'NatGateways[].{id:NatGatewayId,subnet:SubnetId,state:State}'
aws budgets describe-budgets --account-id <id>
aws compute-optimizer get-ec2-instance-recommendations   # needs prior opt-in
```

Provider tools worth reading: Well-Architected Tool workload reviews, Trusted Advisor checks,
Security Hub CSPM standards (CIS AWS Foundations Benchmark), Cost Explorer rightsizing.

## Google Cloud

```bash
# Hierarchy and guardrails
gcloud organizations list
gcloud resource-manager folders list --organization <org-id>
gcloud projects list --format='table(projectId,parent.id,lifecycleState)'
gcloud org-policies list --organization <org-id>

# Identity
gcloud organizations get-iam-policy <org-id> --format=json
gcloud projects get-iam-policy <project> --format=json
gcloud iam service-accounts list --project <project>
gcloud iam service-accounts keys list --iam-account <sa> --managed-by=user

# Audit and detection
gcloud logging sinks list --organization <org-id>
gcloud scc findings list <org-id> --filter='state="ACTIVE" AND severity="CRITICAL"' --limit 50

# Exposure
gcloud compute firewall-rules list --filter='sourceRanges:0.0.0.0/0 AND direction=INGRESS' --format='table(name,network,allowed[].map().firewall_rule().list())'
gcloud sql instances list --format='table(name,settings.ipConfiguration.ipv4Enabled,settings.availabilityType,settings.backupConfiguration.enabled)'

# Reliability
gcloud container clusters list --format='table(name,location,currentMasterVersion,releaseChannel.channel,privateClusterConfig.enablePrivateEndpoint)'
gcloud sql backups list --instance <instance> --limit 5

# Cost
gcloud billing budgets list --billing-account <id>
gcloud recommender recommendations list --project <p> --location <zone> --recommender google.compute.instance.MachineTypeRecommender
gcloud recommender recommendations list --project <p> --location <zone> --recommender google.compute.disk.IdleResourceRecommender
gcloud compute disks list --filter='-users:*' --format='table(name,zone,sizeGb)'
```

When Cloud Billing export to BigQuery exists, query it for cost by service, project and label
instead of estimating. Security Command Center and Active Assist recommendations are leads to
confirm.

## Azure

```bash
az account management-group list
az account list --query '[].{name:name,id:id,state:state}'
az role assignment list --all --include-inherited --query "[?roleDefinitionName=='Owner'].{who:principalName,scope:scope}"
az policy state summarize --subscription <id>
az security assessment list --query "[?status.code=='Unhealthy'].{name:displayName,res:resourceDetails.Id}"
az monitor diagnostic-settings subscription list
az network nsg list --query "[].securityRules[?sourceAddressPrefix=='*' && access=='Allow' && direction=='Inbound'].{name:name,port:destinationPortRange}"
az backup vault list
az aks list --query '[].{name:name,version:kubernetesVersion,private:apiServerAccessProfile.enablePrivateCluster}'
az advisor recommendation list --category Cost
az consumption budget list
```

Also read Microsoft Defender for Cloud secure score, Azure Advisor reliability and cost
recommendations, and Azure Well-Architected Review results if the team has run it.

## Kubernetes (estate-level only)

```bash
kubectl version
kubectl get nodes -o wide
kubectl get ns --show-labels | grep -c pod-security.kubernetes.io/enforce
kubectl get clusterrolebindings -o json | jq -r '.items[] | select(.roleRef.name=="cluster-admin") | .subjects[]? | "\(.kind)/\(.name)"'
kubectl get pdb -A
kubectl get networkpolicy -A
kubectl get pods -A -o json | jq -r '.items[] | select(any(.spec.containers[]; .resources.requests == null)) | "\(.metadata.namespace)/\(.metadata.name)"' | head -50
```

Anything deeper (live troubleshooting, full inventory, RCA) belongs to
`cardume-platform:kubernetes-operations`.

## When there is no live access

Use what exists: IaC repositories (Terraform state outputs, modules, policies), exported
reports (CSPM, billing CSV/FOCUS exports), architecture docs, and interviews. Mark each item
with how it was checked, for example "read from `envs/prod/rds.tf`; live state not verified".
