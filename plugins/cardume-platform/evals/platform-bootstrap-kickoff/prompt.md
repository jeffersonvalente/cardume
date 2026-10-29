---
name: platform-bootstrap-kickoff
plugins: ["../..", "../../../cardume-core"]
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

We're kicking off a new B2B SaaS next month on GCP: about 6 engineers, two backend services and a web app, customer data includes personal data of users in Brazil, and we want to be in production within three months. The company already has a Google Workspace domain but no GCP organization setup yet. Product requirements are being written separately. Before anyone writes Terraform, help me prepare the technical/platform foundation for the kickoff: what do we need to decide, and what should the first months of platform work look like?
