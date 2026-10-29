---
name: pr-description-refund-branch
plugins: ["../.."]
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

I'm done with my branch `feat/PAY-142-refund-webhooks` and want to open a PR into `main`. Can you write the PR description? Here is what I have (I can't paste the whole diff, this is the relevant part):

```text
$ git log --no-merges --format='%h %s' origin/main..HEAD
9c1e7a2 fix: address review comments
4b8d0f3 test(refunds): cover duplicate webhook deliveries
e27a915 fix typo
1f3c6d8 feat(refunds)!: store refund status from provider webhooks
a0b4e51 wip

$ git diff --stat origin/main...HEAD
 src/refunds/refund-webhook.controller.ts       | 58 +++++++++++
 src/refunds/refund-webhook.service.ts          | 94 ++++++++++++++++++
 src/refunds/refund.entity.ts                   | 12 ++-
 src/refunds/refund-poller.job.ts               | 71 --------------
 migrations/20261020_add_refund_events.sql      | 18 ++++
 test/refunds/refund-webhook.service.spec.ts    | 120 +++++++++++++++++++++
 .env.example                                   |  1 +
 7 files changed, 302 insertions(+), 72 deletions(-)
```

Notes: the provider signs each webhook with HMAC-SHA256 (`REFUND_WEBHOOK_SECRET`, new env var); duplicate deliveries are ignored using the provider's event id (unique index in `refund_events`); the 10-minute poller job is removed, which is the breaking part because the `GET /refunds/sync` admin endpoint it exposed is gone too. The reason: polling delayed refund status by up to 10 minutes and support kept getting tickets about it. The unit tests pass locally. We have no PR template in this repo.
