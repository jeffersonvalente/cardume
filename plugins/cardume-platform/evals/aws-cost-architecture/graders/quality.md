---
type: llm
focus: last_message
weight: 2
---

PASS if it (1) compares at least two realistic options, including improving the current EC2 setup, against EKS or managed containers (for example ECS on Fargate), on cost, effort or complexity, and operability or reliability, and does not endorse EKS purely as a cost saving; (2) addresses the NAT cost specifically: an S3 gateway endpoint (no hourly or processing charge) and ECR interface endpoints or equivalent, with a rough comparison against NAT data processing; (3) sequences cost work as waste and rightsizing first (smaller or Graviton instances, autoscaling on demand with scheduled or target-tracking scale-in for nights and weekends), and only then a commitment such as a Compute Savings Plan sized to the remaining steady baseline, explicitly advising against a 3-year RI on the current oversized fleet; (4) keeps the 99.9% target in view (multi-AZ preserved, minimum capacity across two AZs, Multi-AZ RDS kept or justified) and shows rough arithmetic for at least one saving; (5) ends with a clear recommendation plus assumptions or conditions that would change it.
FAIL if it recommends buying the 3-year RI now, ignores the NAT gateway, migrates to EKS without trade-offs, or gives only generic cost tips with no numbers.
