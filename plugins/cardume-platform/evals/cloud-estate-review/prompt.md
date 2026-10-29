---
name: cloud-estate-review
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Leadership wants a health check of our AWS platform before we sign two enterprise customers, and a prioritized plan for the next quarter. Here is what our platform lead pulled with a read-only role last week:

- 4 accounts (prod, staging, shared-services, payments) in an AWS Organization; no SCPs attached besides the default FullAWSAccess.
- `aws iam get-account-summary` in payments: AccountMFAEnabled 0, AccountAccessKeysPresent 1. Nine IAM users with console access in prod, some keys older than 2 years.
- CloudTrail: one single-region trail in prod only, logging to a bucket in prod.
- RDS PostgreSQL `orders-db` (prod): MultiAZ false, BackupRetentionPeriod 7. Nobody remembers a restore test.
- EKS cluster `platform` on Kubernetes 1.28, public API endpoint open to 0.0.0.0/0.
- GuardDuty enabled only in us-east-1 of prod. Security groups with 22/tcp open to 0.0.0.0/0 in staging.
- Monthly bill about $48k, growing 6% per month; no budgets, no cost allocation tags; 31 unattached EBS volumes.

Where are our biggest risks and what should we do in the next 30, 60 and 90 days?
