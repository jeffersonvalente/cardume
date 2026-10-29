---
name: aws-cost-architecture
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Our B2B API runs on AWS in us-east-1: 8 on-demand m5.2xlarge EC2 instances behind an ALB in two AZs, always on. CloudWatch shows average CPU 18%, peaking near 60% for two hours each weekday morning; nights and weekends are almost idle. The instances sit in private subnets and reach S3 and ECR through a single NAT gateway, and the NAT line on the bill is about $3,900/month, mostly data processing. RDS PostgreSQL db.r6g.2xlarge Multi-AZ backs it. Our target is 99.9% availability. Someone proposed migrating everything to EKS to save money, and finance wants us to buy a 3-year Reserved Instance for the current fleet this month. What architecture and cost changes do you recommend?
